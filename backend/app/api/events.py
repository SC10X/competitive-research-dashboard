from __future__ import annotations

import json
import random
import re
import subprocess
import urllib.parse
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CompetitiveEvent, Brand
from ..schemas import (
    ApiResponse,
    PaginationMeta,
    CompetitiveEventOut,
    EventListOut,
    EventTimelineItem,
    EventRefreshOut,
)

router = APIRouter(prefix="/events", tags=["events"])


def _event_to_out(event: CompetitiveEvent) -> CompetitiveEventOut:
    return CompetitiveEventOut(
        id=event.id,
        brand_id=event.brand_id,
        brand_name=event.brand.name if event.brand else None,
        brand_slug=event.brand.slug if event.brand else None,
        event_type=event.event_type,
        title=event.title,
        description=event.description,
        event_date=event.event_date,
        source_url=event.source_url,
        source_name=event.source_name,
        source_quote=event.source_quote,
        importance=event.importance,
        tags=event.tags,
        created_at=event.created_at,
    )


@router.get("", response_model=ApiResponse[EventListOut])
def list_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
    brand_slug: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    importance: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    stmt = select(CompetitiveEvent).join(Brand)

    if brand_slug:
        stmt = stmt.where(Brand.slug == brand_slug)
    if event_type:
        stmt = stmt.where(CompetitiveEvent.event_type == event_type)
    if importance:
        stmt = stmt.where(CompetitiveEvent.importance == importance)
    if date_from:
        stmt = stmt.where(CompetitiveEvent.event_date >= date_from)
    if date_to:
        stmt = stmt.where(CompetitiveEvent.event_date <= date_to)
    if search:
        term = f"%{search}%"
        stmt = stmt.where(
            CompetitiveEvent.title.ilike(term)
            | CompetitiveEvent.description.ilike(term)
        )

    # Count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0

    stmt = stmt.order_by(CompetitiveEvent.event_date.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    events = db.execute(stmt).scalars().all()
    items = [_event_to_out(e) for e in events]

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return ApiResponse(
        success=True,
        data=EventListOut(items=items, total=total),
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/timeline", response_model=ApiResponse[List[EventTimelineItem]])
def get_event_timeline(
    brand_slugs: Optional[str] = Query(None, description="Comma-separated brand slugs"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    stmt = (
        select(
            CompetitiveEvent.id,
            Brand.name,
            CompetitiveEvent.event_type,
            CompetitiveEvent.title,
            CompetitiveEvent.event_date,
            CompetitiveEvent.importance,
        )
        .join(Brand, CompetitiveEvent.brand_id == Brand.id)
        .where(CompetitiveEvent.event_date.isnot(None))
    )

    if brand_slugs:
        slugs = [s.strip() for s in brand_slugs.split(",") if s.strip()]
        if slugs:
            stmt = stmt.where(Brand.slug.in_(slugs))

    stmt = stmt.order_by(CompetitiveEvent.event_date.desc()).limit(limit)
    rows = db.execute(stmt).all()

    items = [
        EventTimelineItem(
            id=row[0],
            brand_name=row[1],
            event_type=row[2],
            title=row[3],
            event_date=row[4],
            importance=row[5],
        )
        for row in rows
    ]

    return ApiResponse(success=True, data=items)


@router.get("/{event_id}", response_model=ApiResponse[CompetitiveEventOut])
def get_event(event_id: int, db: Session = Depends(get_db)):
    stmt = select(CompetitiveEvent).where(CompetitiveEvent.id == event_id)
    event = db.execute(stmt).scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return ApiResponse(success=True, data=_event_to_out(event))


# ============================================================
# 一键刷新：真实联网搜索品牌最新动态
# ============================================================

# 优先搜索的热门/趋势品牌（每次刷新从中随机选取）
PRIORITY_BRANDS = [
    "Nike", "Adidas", "Lululemon", "Hoka", "On Running", "New Balance",
    "Arc'teryx", "Patagonia", "The North Face", "Vuori", "Alo Yoga",
    "Skechers", "Under Armour", "Crocs", "Birkenstock", "UGG",
    "Canada Goose", "Moncler", "Ralph Lauren", "Levi's", "Carhartt",
    "Salomon", "Columbia", "Allbirds", "Everlane", "Reformation",
    "Shein", "Zara", "Uniqlo", "Gap", "American Eagle",
    "Abercrombie & Fitch", "Dickies", "Vans", "Converse", "Puma",
    "Dr. Martens", "Timberland", "Merrell", "Keen", "Teva",
    "Gymshark", "Outdoor Voices", "Fabletics", "Sweaty Betty",
    "Aritzia", "Revolve", "Fashion Nova", "SKIMS", "Good American",
    "Bombas", "Mack Weldon", "Rhone", "Ten Thousand", "Vuori",
]


def _run_fetcher(brand_names: List[str], max_per_brand: int = 3) -> List[dict]:
    """调用 brand_news_fetcher.py 子进程获取真实新闻"""
    fetcher_path = Path(__file__).parent.parent / "services" / "brand_news_fetcher.py"
    if not fetcher_path.exists():
        return []
    
    brands_str = ",".join(brand_names)
    try:
        result = subprocess.run(
            ["python3", str(fetcher_path),
             "--brands", brands_str,
             "--max-per-brand", str(max_per_brand),
             "--output", "json"],
            capture_output=True, text=True, timeout=60,
            cwd=str(fetcher_path.parent.parent.parent),
        )
        if result.returncode != 0:
            return []
        return json.loads(result.stdout) if result.stdout.strip() else []
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        return []


@router.post("/refresh", response_model=ApiResponse[EventRefreshOut])
def refresh_events(
    brand_id: Optional[int] = Query(None, description="If specified, only refresh for this brand"),
    count: int = Query(8, ge=1, le=20, description="How many brands to search"),
    db: Session = Depends(get_db),
):
    """
    一键刷新：真实联网搜索品牌最新动态。
    从 Google News RSS 获取品牌真实新闻，确保每条有可验证的来源。
    """
    today = date.today()
    
    # 获取已有 source_url，用于去重
    existing_urls = set()
    url_rows = db.execute(
        select(CompetitiveEvent.source_url).where(CompetitiveEvent.source_url.isnot(None))
    ).all()
    for row in url_rows:
        if row[0]:
            existing_urls.add(row[0])
    
    # 选择要搜索的品牌
    if brand_id:
        brand = db.execute(select(Brand).where(Brand.id == brand_id)).scalar_one_or_none()
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        search_names = [_clean_brand_name(brand.name).title()]
        if not search_names[0]:
            search_names = [brand.name]
    else:
        # 从优先品牌中随机选取
        selected = random.sample(PRIORITY_BRANDS, min(count, len(PRIORITY_BRANDS)))
        search_names = selected
    
    # 调用搜索脚本获取真实新闻
    news_items = _run_fetcher(search_names, max_per_brand=2)
    
    if not news_items:
        return ApiResponse(
            success=True,
            data=EventRefreshOut(
                refreshed_count=0,
                new_events=[],
                refreshed_at=today,
                message="未搜索到新动态，请稍后再试。已搜索品牌: " + ", ".join(search_names[:5]),
            ),
        )
    
    # 匹配品牌名 → brand_id
    brand_map = {}
    all_brands = db.execute(select(Brand).where(Brand.is_active == True)).scalars().all()
    for b in all_brands:
        brand_map[b.name.lower()] = b.id
        # 也加入清理后的名字
        clean = _clean_brand_name(b.name)
        if clean:
            brand_map[clean] = b.id
    
    new_events: List[CompetitiveEvent] = []
    skipped_duplicate = 0
    skipped_no_brand = 0
    
    for item in news_items:
        bn = item.get("brand_name", "").strip().lower()
        bid = brand_map.get(bn)
        if not bid:
            # 模糊匹配
            for k, v in brand_map.items():
                if bn in k or k in bn:
                    bid = v
                    break
        if not bid:
            skipped_no_brand += 1
            continue
        
        source_url = item.get("source_url", "")
        # 同一 source_url 不重复创建
        if source_url in existing_urls:
            skipped_duplicate += 1
            continue
        existing_urls.add(source_url)
        
        event_date_str = item.get("event_date", today.isoformat())
        try:
            event_date = date.fromisoformat(event_date_str)
        except (ValueError, TypeError):
            event_date = today
        
        new_event = CompetitiveEvent(
            brand_id=bid,
            event_type=item.get("event_type", "Product Launch"),
            title=item.get("title_zh", item.get("title", "")),
            description=item.get("description_zh", item.get("description", "")),
            event_date=event_date,
            source_url=source_url,
            source_name=item.get("source_name", ""),
            source_quote=item.get("source_quote_zh", item.get("source_quote", "")),
            importance=item.get("importance", "medium"),
            tags=[item.get("event_type", "")],
        )
        db.add(new_event)
        new_events.append(new_event)
    
    db.commit()
    for ev in new_events:
        db.refresh(ev)
    
    items = [_event_to_out(e) for e in new_events]
    
    message = f"搜索 {len(search_names)} 个品牌，新增 {len(items)} 条真实动态"
    if skipped_duplicate > 0:
        message += f"（跳过 {skipped_duplicate} 条重复）"
    
    return ApiResponse(
        success=True,
        data=EventRefreshOut(
            refreshed_count=len(items),
            new_events=items,
            refreshed_at=today,
            message=message,
        ),
    )


def _clean_brand_name(name: str) -> str:
    """提取纯英文品牌名，移除中文后缀和括号"""
    name = re.sub(r'\s*[（(][^)）]*[)）]\s*', '', name)
    name = re.sub(r'[\u4e00-\u9fff]+', '', name)
    return name.strip().lower()
