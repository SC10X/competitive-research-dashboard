from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from ..database import get_db
from ..models import Brand, BrandCategory, ComparisonGroup
from ..schemas import (
    ApiResponse,
    CompareRequest,
    CompareResponse,
    CompareDimensionData,
    ComparisonGroupOut,
    ComparisonGroupCreate,
)

router = APIRouter(prefix="/compare", tags=["compare"])

DEFAULT_DIMENSIONS = [
    "positioning", "pricing", "demographics", "product_strategy",
    "channel_strategy", "social_media", "digital", "financials",
    "sentiment", "events",
]


def _fetch_brands_with_dimensions(db: Session, slugs: List[str], dimensions: List[str]):
    load_options = []
    if "brand_categories" in dimensions:
        load_options.append(joinedload(Brand.brand_categories).joinedload(BrandCategory.category))
    if "positioning" in dimensions:
        load_options.append(joinedload(Brand.positioning))
    if "pricing" in dimensions:
        load_options.append(selectinload(Brand.pricing))
    if "demographics" in dimensions:
        load_options.append(joinedload(Brand.demographics))
    if "product_strategy" in dimensions:
        load_options.append(joinedload(Brand.product_strategy))
    if "channel_strategy" in dimensions:
        load_options.append(joinedload(Brand.channel_strategy))
    if "social_media" in dimensions:
        load_options.append(selectinload(Brand.social_media))
    if "digital" in dimensions:
        load_options.append(joinedload(Brand.digital))
    if "financials" in dimensions:
        load_options.append(selectinload(Brand.financials))
    if "sentiment" in dimensions:
        load_options.append(selectinload(Brand.sentiment))
    if "events" in dimensions:
        load_options.append(selectinload(Brand.events))

    stmt = select(Brand).options(*load_options).where(Brand.slug.in_(slugs))
    brands = db.execute(stmt).unique().scalars().all()

    if len(brands) != len(slugs):
        found = {b.slug for b in brands}
        missing = [s for s in slugs if s not in found]
        raise HTTPException(status_code=404, detail=f"Brands not found: {', '.join(missing)}")

    return list(brands)


def _serialize_model_item(item):
    result = {}
    for col in item.__table__.columns:
        val = getattr(item, col.name)
        result[col.name] = val
    return result


def _extract_dimension_data(brand: Brand, dimension: str) -> dict:
    attr_map = {
        "positioning": "positioning",
        "pricing": "pricing",
        "demographics": "demographics",
        "product_strategy": "product_strategy",
        "channel_strategy": "channel_strategy",
        "social_media": "social_media",
        "digital": "digital",
        "financials": "financials",
        "sentiment": "sentiment",
        "events": "events",
    }
    attr_name = attr_map.get(dimension)
    if attr_name is None:
        return None
    data = getattr(brand, attr_name, None)
    if data is None:
        return None
    if isinstance(data, list):
        return [_serialize_model_item(item) for item in data]
    return _serialize_model_item(data)


def _perform_compare(
    db: Session,
    brand_slugs: List[str],
    dimensions: Optional[List[str]] = None,
) -> CompareResponse:
    dims = dimensions or DEFAULT_DIMENSIONS
    brands = _fetch_brands_with_dimensions(db, brand_slugs, dims)

    result_data = []
    for brand in brands:
        for dim in dims:
            dim_data = _extract_dimension_data(brand, dim)
            if dim_data is not None:
                result_data.append(CompareDimensionData(
                    brand_slug=brand.slug,
                    brand_name=brand.name,
                    dimension=dim,
                    data=dim_data,
                ))

    return CompareResponse(
        brand_slugs=brand_slugs,
        dimensions=dims,
        data=result_data,
    )


@router.post("/query", response_model=ApiResponse[CompareResponse])
def compare_instant(request: CompareRequest, db: Session = Depends(get_db)):
    result = _perform_compare(db, request.brand_slugs, request.dimensions)
    return ApiResponse(success=True, data=result)


@router.post("", response_model=ApiResponse[ComparisonGroupOut])
def create_comparison_group(group: ComparisonGroupCreate, db: Session = Depends(get_db)):
    new_group = ComparisonGroup(name=group.name, brand_ids=group.brand_ids)
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return ApiResponse(success=True, data=ComparisonGroupOut.model_validate(new_group))


@router.get("", response_model=ApiResponse[List[ComparisonGroupOut]])
def list_comparison_groups(db: Session = Depends(get_db)):
    stmt = select(ComparisonGroup).order_by(ComparisonGroup.created_at.desc())
    groups = db.execute(stmt).scalars().all()
    return ApiResponse(
        success=True,
        data=[ComparisonGroupOut.model_validate(g) for g in groups],
    )


@router.get("/{group_id}", response_model=ApiResponse[dict])
def get_comparison_group(group_id: int, db: Session = Depends(get_db)):
    stmt = select(ComparisonGroup).where(ComparisonGroup.id == group_id)
    group = db.execute(stmt).scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Comparison group not found")

    result = _perform_compare(db, group.brand_ids, None) if isinstance(group.brand_ids, list) else CompareResponse(brand_slugs=[], dimensions=[], data=[])

    return ApiResponse(
        success=True,
        data={
            "group": ComparisonGroupOut.model_validate(group),
            "comparison": result,
        },
    )


@router.delete("/{group_id}", response_model=ApiResponse[dict])
def delete_comparison_group(group_id: int, db: Session = Depends(get_db)):
    stmt = select(ComparisonGroup).where(ComparisonGroup.id == group_id)
    group = db.execute(stmt).scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Comparison group not found")
    db.delete(group)
    db.commit()
    return ApiResponse(success=True, data={"message": "Deleted successfully"})
