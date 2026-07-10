from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session, joinedload, selectinload

from ..database import get_db
from ..models import (
    Brand,
    Category,
    BrandCategory,
    BrandPositioning,
    PricingStrategy,
    TargetDemographics,
    ProductStrategy,
    ChannelStrategy,
    SocialMediaMetrics,
    DigitalCapability,
    FinancialPerformance,
    CustomerSentiment,
    CompetitiveEvent,
)
from ..schemas import (
    ApiResponse,
    PaginationMeta,
    BrandOut,
    BrandDetailOut,
    BrandListOut,
    BrandCategoryOut,
    BrandPositioningOut,
    PricingStrategyOut,
    TargetDemographicsOut,
    ProductStrategyOut,
    ChannelStrategyOut,
    SocialMediaMetricsOut,
    DigitalCapabilityOut,
    FinancialPerformanceOut,
    CustomerSentimentOut,
    CompetitiveEventOut,
)

router = APIRouter(prefix="/brands", tags=["brands"])


def _brand_out_with_summary(brand: Brand) -> BrandOut:
    """Build BrandOut with summary fields from positioning/social/digital."""
    price_tier = None
    if brand.positioning:
        price_tier = brand.positioning.price_tier

    instagram_followers = None
    for sm in brand.social_media or []:
        if sm.platform and sm.platform.lower() == "instagram":
            instagram_followers = sm.followers
            break

    monthly_web_visits = None
    if brand.digital:
        monthly_web_visits = brand.digital.monthly_web_visits

    return BrandOut(
        id=brand.id,
        name=brand.name,
        slug=brand.slug,
        country=brand.country,
        founded_year=brand.founded_year,
        parent_company=brand.parent_company,
        headquarters=brand.headquarters,
        logo_url=brand.logo_url,
        website=brand.website,
        instagram_url=brand.instagram_url,
        twitter_url=brand.twitter_url,
        tiktok_url=brand.tiktok_url,
        description=brand.description,
        is_active=brand.is_active,
        price_tier=price_tier,
        instagram_followers=instagram_followers,
        monthly_web_visits=monthly_web_visits,
        created_at=brand.created_at,
        updated_at=brand.updated_at,
    )


def _build_brand_base_query(
    db: Session,
    category_slug: Optional[str] = None,
    price_tier: Optional[str] = None,
    country: Optional[str] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
):
    """Build base brand query with optional filters."""
    stmt = select(Brand)

    if category_slug is not None:
        stmt = (
            stmt.join(Brand.brand_categories)
            .join(BrandCategory.category)
            .where(Category.slug == category_slug)
        )

    if price_tier is not None:
        stmt = stmt.join(Brand.positioning).where(BrandPositioning.price_tier == price_tier)

    if country is not None:
        stmt = stmt.where(Brand.country == country)

    if is_active is not None:
        stmt = stmt.where(Brand.is_active == is_active)

    if search is not None:
        search_term = f"%{search}%"
        stmt = stmt.where(
            or_(
                Brand.name.ilike(search_term),
                Brand.description.ilike(search_term),
                Brand.country.ilike(search_term),
            )
        )

    return stmt


def _serialize_brand_categories(brand: Brand) -> List[BrandCategoryOut]:
    result = []
    for bc in brand.brand_categories:
        result.append(BrandCategoryOut(
            category_id=bc.category_id,
            category_name=bc.category.name if bc.category else None,
            category_slug=bc.category.slug if bc.category else None,
            is_primary=bc.is_primary,
        ))
    return result


def _brand_to_detail(brand: Brand) -> BrandDetailOut:
    # Extract summary fields (same logic as _brand_out_with_summary)
    price_tier = brand.positioning.price_tier if brand.positioning else None
    instagram_followers = None
    for sm in brand.social_media or []:
        if sm.platform and sm.platform.lower() == "instagram":
            instagram_followers = sm.followers
            break
    monthly_web_visits = brand.digital.monthly_web_visits if brand.digital else None

    return BrandDetailOut(
        id=brand.id,
        name=brand.name,
        slug=brand.slug,
        country=brand.country,
        founded_year=brand.founded_year,
        parent_company=brand.parent_company,
        headquarters=brand.headquarters,
        logo_url=brand.logo_url,
        website=brand.website,
        instagram_url=brand.instagram_url,
        twitter_url=brand.twitter_url,
        tiktok_url=brand.tiktok_url,
        description=brand.description,
        is_active=brand.is_active,
        price_tier=price_tier,
        instagram_followers=instagram_followers,
        monthly_web_visits=monthly_web_visits,
        created_at=brand.created_at,
        updated_at=brand.updated_at,
        categories=_serialize_brand_categories(brand),
        positioning=BrandPositioningOut.model_validate(brand.positioning) if brand.positioning else None,
        pricing=[PricingStrategyOut.model_validate(p) for p in (brand.pricing or [])],
        demographics=TargetDemographicsOut.model_validate(brand.demographics) if brand.demographics else None,
        product_strategy=ProductStrategyOut.model_validate(brand.product_strategy) if brand.product_strategy else None,
        channel_strategy=ChannelStrategyOut.model_validate(brand.channel_strategy) if brand.channel_strategy else None,
        social_media=[SocialMediaMetricsOut.model_validate(s) for s in (brand.social_media or [])],
        digital=DigitalCapabilityOut.model_validate(brand.digital) if brand.digital else None,
        financials=[FinancialPerformanceOut.model_validate(f) for f in (brand.financials or [])],
        sentiment=[CustomerSentimentOut.model_validate(s) for s in (brand.sentiment or [])],
        events=[CompetitiveEventOut.model_validate(e) for e in (brand.events or [])],
    )


def _get_dimension_data(brand: Brand, dimension: str) -> dict:
    dimension_map = {
        "positioning": brand.positioning,
        "pricing": brand.pricing,
        "demographics": brand.demographics,
        "product_strategy": brand.product_strategy,
        "channel_strategy": brand.channel_strategy,
        "social_media": brand.social_media,
        "digital": brand.digital,
        "financials": brand.financials,
        "sentiment": brand.sentiment,
        "events": brand.events,
    }

    data = dimension_map.get(dimension)
    if data is None:
        raise HTTPException(status_code=404, detail=f"Dimension '{dimension}' not found")

    if isinstance(data, list):
        return {
            "dimension": dimension,
            "items": [_serialize_model_item(item) for item in data],
        }
    else:
        return {
            "dimension": dimension,
            "data": _serialize_model_item(data),
        }


def _serialize_model_item(item):
    """Serialize any model instance to dict, handling JSON and date types."""
    result = {}
    for col in item.__table__.columns:
        val = getattr(item, col.name)
        result[col.name] = val
    return result


@router.get("", response_model=ApiResponse[BrandListOut])
def list_brands(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
    category: Optional[str] = Query(None, description="Filter by category slug"),
    price_tier: Optional[str] = Query(None, description="Filter by price tier (Luxury, Premium, Mid, Mass)"),
    country: Optional[str] = Query(None, description="Filter by country"),
    search: Optional[str] = Query(None, description="Search by name, description, country"),
    sort_by: str = Query("name", description="Sort field: name, founded_year, country"),
    sort_order: str = Query("asc", description="Sort direction: asc or desc"),
    db: Session = Depends(get_db),
):
    stmt = _build_brand_base_query(db, category, price_tier, country, search)

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0

    # Apply sorting and pagination to the filtered query while keeping eager loads
    sort_col = getattr(Brand, sort_by, Brand.name)
    if sort_order == "desc":
        stmt = stmt.order_by(sort_col.desc())
    else:
        stmt = stmt.order_by(sort_col.asc())

    stmt = stmt.options(
        joinedload(Brand.positioning),
        selectinload(Brand.social_media),
        joinedload(Brand.digital),
    ).distinct().offset((page - 1) * page_size).limit(page_size)

    brands = db.execute(stmt).unique().scalars().all()
    items = [_brand_out_with_summary(b) for b in brands]

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return ApiResponse(
        success=True,
        data=BrandListOut(items=items, total=total),
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        ),
    )


@router.get("/{slug}", response_model=ApiResponse[BrandDetailOut])
def get_brand(slug: str, db: Session = Depends(get_db)):
    stmt = (
        select(Brand)
        .options(
            joinedload(Brand.brand_categories).joinedload(BrandCategory.category),
            joinedload(Brand.positioning),
            selectinload(Brand.pricing),
            joinedload(Brand.demographics),
            joinedload(Brand.product_strategy),
            joinedload(Brand.channel_strategy),
            selectinload(Brand.social_media),
            joinedload(Brand.digital),
            selectinload(Brand.financials),
            selectinload(Brand.sentiment),
            selectinload(Brand.events),
        )
        .where(Brand.slug == slug)
    )
    brand = db.execute(stmt).unique().scalar_one_or_none()

    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand '{slug}' not found")

    return ApiResponse(success=True, data=_brand_to_detail(brand))


@router.get("/{slug}/dimensions", response_model=ApiResponse[dict])
def get_brand_dimensions(slug: str, db: Session = Depends(get_db)):
    stmt = (
        select(Brand)
        .options(
            joinedload(Brand.positioning),
            selectinload(Brand.pricing),
            joinedload(Brand.demographics),
            joinedload(Brand.product_strategy),
            joinedload(Brand.channel_strategy),
            selectinload(Brand.social_media),
            joinedload(Brand.digital),
            selectinload(Brand.financials),
            selectinload(Brand.sentiment),
            selectinload(Brand.events),
        )
        .where(Brand.slug == slug)
    )
    brand = db.execute(stmt).unique().scalar_one_or_none()

    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand '{slug}' not found")

    dimensions = {
        "positioning": _serialize_model_item(brand.positioning) if brand.positioning else None,
        "pricing": [_serialize_model_item(p) for p in (brand.pricing or [])],
        "demographics": _serialize_model_item(brand.demographics) if brand.demographics else None,
        "product_strategy": _serialize_model_item(brand.product_strategy) if brand.product_strategy else None,
        "channel_strategy": _serialize_model_item(brand.channel_strategy) if brand.channel_strategy else None,
        "social_media": [_serialize_model_item(s) for s in (brand.social_media or [])],
        "digital": _serialize_model_item(brand.digital) if brand.digital else None,
        "financials": [_serialize_model_item(f) for f in (brand.financials or [])],
        "sentiment": [_serialize_model_item(s) for s in (brand.sentiment or [])],
        "events": [_serialize_model_item(e) for e in (brand.events or [])],
    }

    return ApiResponse(success=True, data=dimensions)


@router.get("/{slug}/dimensions/{dimension}", response_model=ApiResponse[dict])
def get_brand_dimension(slug: str, dimension: str, db: Session = Depends(get_db)):
    load_options = {
        "positioning": joinedload(Brand.positioning),
        "pricing": selectinload(Brand.pricing),
        "demographics": joinedload(Brand.demographics),
        "product_strategy": joinedload(Brand.product_strategy),
        "channel_strategy": joinedload(Brand.channel_strategy),
        "social_media": selectinload(Brand.social_media),
        "digital": joinedload(Brand.digital),
        "financials": selectinload(Brand.financials),
        "sentiment": selectinload(Brand.sentiment),
        "events": selectinload(Brand.events),
    }

    loader = load_options.get(dimension)
    if loader is None:
        raise HTTPException(status_code=400, detail=f"Invalid dimension: {dimension}")

    stmt = select(Brand).options(loader).where(Brand.slug == slug)
    brand = db.execute(stmt).unique().scalar_one_or_none()

    if not brand:
        raise HTTPException(status_code=404, detail=f"Brand '{slug}' not found")

    return ApiResponse(success=True, data=_get_dimension_data(brand, dimension))
