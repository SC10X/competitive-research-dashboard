from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Brand, FinancialPerformance, SocialMediaMetrics
from ..schemas import (
    ApiResponse,
    PaginationMeta,
    RevenueTrendItem,
    SocialTrendItem,
    TrendOverview,
)

router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("/revenue", response_model=ApiResponse[List[RevenueTrendItem]])
def get_revenue_trends(
    brand_slugs: Optional[str] = Query(None, description="Comma-separated brand slugs"),
    start_year: Optional[int] = Query(None),
    end_year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    stmt = (
        select(
            FinancialPerformance,
            Brand.name,
            Brand.slug,
        )
        .join(Brand, FinancialPerformance.brand_id == Brand.id)
        .where(Brand.is_active == True)
    )

    if brand_slugs:
        slugs = [s.strip() for s in brand_slugs.split(",") if s.strip()]
        if slugs:
            stmt = stmt.where(Brand.slug.in_(slugs))

    if start_year is not None:
        stmt = stmt.where(FinancialPerformance.fiscal_year >= start_year)
    if end_year is not None:
        stmt = stmt.where(FinancialPerformance.fiscal_year <= end_year)

    stmt = stmt.order_by(FinancialPerformance.fiscal_year, Brand.name)
    rows = db.execute(stmt).all()

    items = []
    for fp, brand_name, brand_slug in rows:
        items.append(RevenueTrendItem(
            brand_id=fp.brand_id,
            brand_name=brand_name,
            brand_slug=brand_slug,
            fiscal_year=fp.fiscal_year,
            revenue=fp.revenue,
            revenue_growth_pct=fp.revenue_growth_pct,
        ))

    return ApiResponse(success=True, data=items)


@router.get("/social", response_model=ApiResponse[List[SocialTrendItem]])
def get_social_trends(
    platform: Optional[str] = Query(None),
    brand_slugs: Optional[str] = Query(None, description="Comma-separated brand slugs"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = (
        select(SocialMediaMetrics, Brand.name, Brand.slug)
        .join(Brand, SocialMediaMetrics.brand_id == Brand.id)
        .where(Brand.is_active == True)
    )

    if platform:
        stmt = stmt.where(SocialMediaMetrics.platform == platform)

    if brand_slugs:
        slugs = [s.strip() for s in brand_slugs.split(",") if s.strip()]
        if slugs:
            stmt = stmt.where(Brand.slug.in_(slugs))

    # Count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0

    stmt = stmt.order_by(SocialMediaMetrics.data_as_of.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    rows = db.execute(stmt).all()

    items = []
    for sm, brand_name, brand_slug in rows:
        items.append(SocialTrendItem(
            brand_id=sm.brand_id,
            brand_name=brand_name,
            brand_slug=brand_slug,
            platform=sm.platform,
            followers=sm.followers,
            engagement_rate=sm.engagement_rate,
            data_as_of=sm.data_as_of,
        ))

    return ApiResponse(
        success=True,
        data=items,
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=(total + page_size - 1) // page_size if total > 0 else 0,
        ),
    )


@router.get("/overview", response_model=ApiResponse[TrendOverview])
def get_trend_overview(db: Session = Depends(get_db)):
    # Total brands
    total_brands = db.execute(
        select(func.count()).select_from(select(Brand).where(Brand.is_active == True).subquery())
    ).scalar() or 0

    # Total categories
    total_categories = db.execute(
        select(func.count()).select_from(select(Brand).subquery())
    ).scalar() or 0

    # Avg revenue growth - latest year per brand
    latest_financials = (
        select(
            FinancialPerformance.brand_id,
            func.max(FinancialPerformance.fiscal_year).label("max_year"),
        )
        .group_by(FinancialPerformance.brand_id)
        .subquery()
    )
    avg_growth_stmt = (
        select(func.avg(FinancialPerformance.revenue_growth_pct))
        .join(
            latest_financials,
            (FinancialPerformance.brand_id == latest_financials.c.brand_id)
            & (FinancialPerformance.fiscal_year == latest_financials.c.max_year),
        )
    )
    avg_revenue_growth = db.execute(avg_growth_stmt).scalar()

    # Top revenue brands - latest year
    top_revenue_stmt = (
        select(
            Brand.name,
            Brand.slug,
            FinancialPerformance.revenue,
            FinancialPerformance.fiscal_year,
        )
        .join(FinancialPerformance, Brand.id == FinancialPerformance.brand_id)
        .where(FinancialPerformance.revenue.isnot(None))
        .order_by(FinancialPerformance.revenue.desc())
        .limit(5)
    )
    top_rev_rows = db.execute(top_revenue_stmt).all()
    top_revenue_brands = [
        {"name": r[0], "slug": r[1], "revenue": r[2], "fiscal_year": r[3]}
        for r in top_rev_rows
    ]

    # Top engagement brands
    top_eng_stmt = (
        select(
            Brand.name,
            Brand.slug,
            SocialMediaMetrics.platform,
            SocialMediaMetrics.engagement_rate,
        )
        .join(SocialMediaMetrics, Brand.id == SocialMediaMetrics.brand_id)
        .where(SocialMediaMetrics.engagement_rate.isnot(None))
        .order_by(SocialMediaMetrics.engagement_rate.desc())
        .limit(5)
    )
    top_eng_rows = db.execute(top_eng_stmt).all()
    top_engagement_brands = [
        {"name": r[0], "slug": r[1], "platform": r[2], "engagement_rate": r[3]}
        for r in top_eng_rows
    ]

    return ApiResponse(
        success=True,
        data=TrendOverview(
            total_brands=total_brands,
            total_categories=total_categories,
            avg_revenue_growth=avg_revenue_growth,
            top_revenue_brands=top_revenue_brands,
            top_engagement_brands=top_engagement_brands,
        ),
    )
