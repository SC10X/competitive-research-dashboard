from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    Brand,
    Category,
    BrandCategory,
    CompetitiveEvent,
    FinancialPerformance,
    DataSource,
    BrandPositioning,
)
from ..schemas import (
    ApiResponse,
    StatsOverview,
    PriceDistribution,
    CountryDistribution,
)
from datetime import date

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview", response_model=ApiResponse[StatsOverview])
def get_stats_overview(db: Session = Depends(get_db)):
    from datetime import date
    total_brands = db.execute(select(func.count()).select_from(Brand)).scalar() or 0
    active_brands = db.execute(
        select(func.count()).select_from(select(Brand).where(Brand.is_active == True).subquery())
    ).scalar() or 0
    total_categories = db.execute(select(func.count()).select_from(Category)).scalar() or 0
    total_events = db.execute(select(func.count()).select_from(CompetitiveEvent)).scalar() or 0
    total_financials = db.execute(select(func.count()).select_from(FinancialPerformance)).scalar() or 0
    data_sources_count = db.execute(select(func.count()).select_from(DataSource)).scalar() or 0

    # Count this month's events
    today = date.today()
    month_start = date(today.year, today.month, 1)
    events_this_month = db.execute(
        select(func.count()).select_from(CompetitiveEvent)
        .where(CompetitiveEvent.event_date >= month_start)
    ).scalar() or 0

    # Get last data update time
    last_updated = db.execute(
        select(Brand.updated_at).order_by(Brand.updated_at.desc()).limit(1)
    ).scalar()

    return ApiResponse(
        success=True,
        data=StatsOverview(
            total_brands=total_brands,
            active_brands=active_brands,
            total_categories=total_categories,
            total_events=total_events,
            total_financial_records=total_financials,
            data_sources_count=data_sources_count,
            events_this_month=events_this_month,
            last_updated_at=last_updated,
        ),
    )


@router.get("/price-distribution", response_model=ApiResponse[List[PriceDistribution]])
def get_price_distribution(db: Session = Depends(get_db)):
    stmt = (
        select(
            BrandPositioning.price_tier,
            func.count(BrandPositioning.id),
        )
        .where(BrandPositioning.price_tier.isnot(None))
        .group_by(BrandPositioning.price_tier)
        .order_by(BrandPositioning.price_tier)
    )
    rows = db.execute(stmt).all()

    data = [PriceDistribution(tier=r[0], count=r[1]) for r in rows]
    return ApiResponse(success=True, data=data)


@router.get("/country-distribution", response_model=ApiResponse[List[CountryDistribution]])
def get_country_distribution(db: Session = Depends(get_db)):
    stmt = (
        select(
            Brand.country,
            func.count(Brand.id),
        )
        .where(Brand.country.isnot(None))
        .group_by(Brand.country)
        .order_by(func.count(Brand.id).desc())
    )
    rows = db.execute(stmt).all()

    data = [CountryDistribution(country=r[0], count=r[1]) for r in rows]
    return ApiResponse(success=True, data=data)


@router.get("/event-types", response_model=ApiResponse[List[dict]])
def get_event_type_distribution(db: Session = Depends(get_db)):
    stmt = (
        select(
            CompetitiveEvent.event_type,
            func.count(CompetitiveEvent.id),
        )
        .group_by(CompetitiveEvent.event_type)
        .order_by(func.count(CompetitiveEvent.id).desc())
    )
    rows = db.execute(stmt).all()

    data = [{"event_type": r[0], "count": r[1]} for r in rows]
    return ApiResponse(success=True, data=data)


@router.get("/category-distribution", response_model=ApiResponse[List[dict]])
def get_category_distribution(db: Session = Depends(get_db)):
    """Get brand count per top-level category (Apparel, Footwear, Bags)"""
    # Get top-level categories
    top_cats = db.execute(
        select(Category).where(Category.level == 1)
    ).scalars().all()
    
    result = []
    for tc in top_cats:
        # Get all child category IDs
        children = db.execute(
            select(Category).where(Category.parent_id == tc.id)
        ).scalars().all()
        cat_ids = [tc.id] + [c.id for c in children]
        
        # Count distinct brands in this top-level category or any of its children
        count = db.execute(
            select(func.count(func.distinct(BrandCategory.brand_id)))
            .where(BrandCategory.category_id.in_(cat_ids))
        ).scalar() or 0
        
        result.append({
            "name": tc.name,
            "slug": tc.slug,
            "count": count,
        })
    
    return ApiResponse(success=True, data=result)
