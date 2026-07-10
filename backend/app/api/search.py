from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Brand, Category, CompetitiveEvent
from ..schemas import ApiResponse, SearchResult

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=ApiResponse[List[SearchResult]])
def global_search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    results: List[SearchResult] = []
    term = f"%{q}%"

    # Search brands
    brand_stmt = (
        select(Brand)
        .where(
            or_(
                Brand.name.ilike(term),
                Brand.description.ilike(term),
                Brand.country.ilike(term),
            )
        )
        .limit(limit)
    )
    brands = db.execute(brand_stmt).scalars().all()
    for b in brands:
        results.append(SearchResult(
            type="brand",
            id=b.id,
            title=b.name,
            subtitle=f"{b.country or ''}",
            slug=b.slug,
        ))

    # Search categories
    cat_stmt = (
        select(Category)
        .where(Category.name.ilike(term))
        .limit(limit)
    )
    categories = db.execute(cat_stmt).scalars().all()
    for c in categories:
        results.append(SearchResult(
            type="category",
            id=c.id,
            title=c.name,
            subtitle=f"Level {c.level}",
            slug=c.slug,
        ))

    # Search events
    evt_stmt = (
        select(CompetitiveEvent)
        .where(
            or_(
                CompetitiveEvent.title.ilike(term),
                CompetitiveEvent.description.ilike(term),
            )
        )
        .limit(limit)
    )
    events = db.execute(evt_stmt).scalars().all()
    for e in events:
        results.append(SearchResult(
            type="event",
            id=e.id,
            title=e.title,
            subtitle=f"{e.event_type} - {e.event_date}",
        ))

    # Deduplicate and limit
    seen = set()
    unique_results = []
    for r in results:
        key = (r.type, r.id)
        if key not in seen:
            seen.add(key)
            unique_results.append(r)

    return ApiResponse(success=True, data=unique_results[:limit])
