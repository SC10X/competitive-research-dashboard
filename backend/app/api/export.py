from __future__ import annotations

import io
from datetime import datetime
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import (
    Brand,
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
    Category,
)
from ..schemas import ExportRequest

router = APIRouter(prefix="/export", tags=["export"])


def _model_to_dict(obj):
    result = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if isinstance(val, datetime):
            val = val.isoformat()
        elif isinstance(val, (list, dict)):
            val = str(val)
        result[col.name] = val
    return result


def _export_brands(db: Session, brand_ids: Optional[List[int]] = None) -> pd.DataFrame:
    stmt = (
        select(Brand)
        .options(
            joinedload(Brand.positioning),
            joinedload(Brand.demographics),
            joinedload(Brand.product_strategy),
            joinedload(Brand.channel_strategy),
            joinedload(Brand.digital),
        )
    )
    if brand_ids:
        stmt = stmt.where(Brand.id.in_(brand_ids))
    stmt = stmt.order_by(Brand.name)

    brands = db.execute(stmt).unique().scalars().all()
    rows = []
    for b in brands:
        row = {
            "id": b.id,
            "name": b.name,
            "slug": b.slug,
            "country": b.country,
            "founded_year": b.founded_year,
            "parent_company": b.parent_company,
            "headquarters": b.headquarters,
            "website": b.website,
            "description": b.description,
            "is_active": b.is_active,
            "price_tier": b.positioning.price_tier if b.positioning else None,
            "brand_tone": b.positioning.brand_tone if b.positioning else None,
            "core_value_proposition": b.positioning.core_value_proposition if b.positioning else None,
            "usp": b.positioning.usp if b.positioning else None,
            "age_range": b.demographics.age_range if b.demographics else None,
            "gender_skew": b.demographics.gender_skew if b.demographics else None,
            "income_level": b.demographics.income_level if b.demographics else None,
            "sku_count_estimate": b.product_strategy.sku_count_estimate if b.product_strategy else None,
            "has_sustainable_line": b.product_strategy.has_sustainable_line if b.product_strategy else False,
            "dtc_pct": b.channel_strategy.dtc_pct if b.channel_strategy else None,
            "wholesale_pct": b.channel_strategy.wholesale_pct if b.channel_strategy else None,
            "monthly_web_visits": b.digital.monthly_web_visits if b.digital else None,
            "app_rating": b.digital.app_rating if b.digital else None,
        }
        rows.append(row)
    return pd.DataFrame(rows)


def _export_financials(db: Session, brand_ids: Optional[List[int]] = None) -> pd.DataFrame:
    stmt = (
        select(
            FinancialPerformance,
            Brand.name,
            Brand.slug,
        )
        .join(Brand, FinancialPerformance.brand_id == Brand.id)
    )
    if brand_ids:
        stmt = stmt.where(FinancialPerformance.brand_id.in_(brand_ids))
    stmt = stmt.order_by(FinancialPerformance.fiscal_year.desc(), Brand.name)

    rows = db.execute(stmt).all()
    data = []
    for fp, brand_name, brand_slug in rows:
        data.append({
            "brand_name": brand_name,
            "brand_slug": brand_slug,
            "fiscal_year": fp.fiscal_year,
            "revenue": fp.revenue,
            "revenue_growth_pct": fp.revenue_growth_pct,
            "gross_margin_pct": fp.gross_margin_pct,
            "na_revenue_pct": fp.na_revenue_pct,
            "is_estimated": fp.is_estimated,
            "data_source": fp.data_source,
        })
    return pd.DataFrame(data)


def _export_events(db: Session, brand_ids: Optional[List[int]] = None,
                   date_from: Optional[str] = None, date_to: Optional[str] = None) -> pd.DataFrame:
    stmt = (
        select(CompetitiveEvent, Brand.name, Brand.slug)
        .join(Brand, CompetitiveEvent.brand_id == Brand.id)
    )
    if brand_ids:
        stmt = stmt.where(CompetitiveEvent.brand_id.in_(brand_ids))
    if date_from:
        stmt = stmt.where(CompetitiveEvent.event_date >= date_from)
    if date_to:
        stmt = stmt.where(CompetitiveEvent.event_date <= date_to)
    stmt = stmt.order_by(CompetitiveEvent.event_date.desc())

    rows = db.execute(stmt).all()
    data = []
    for evt, brand_name, brand_slug in rows:
        data.append({
            "brand_name": brand_name,
            "brand_slug": brand_slug,
            "event_type": evt.event_type,
            "title": evt.title,
            "description": evt.description,
            "event_date": evt.event_date.isoformat() if evt.event_date else None,
            "source_url": evt.source_url,
            "source_name": evt.source_name,
            "importance": evt.importance,
            "tags": str(evt.tags) if evt.tags else None,
        })
    return pd.DataFrame(data)


@router.post("", response_class=StreamingResponse)
def export_data(request: ExportRequest, db: Session = Depends(get_db)):
    export_handlers = {
        "brands": _export_brands,
        "financials": _export_financials,
        "events": _export_events,
    }

    handler = export_handlers.get(request.data_type)
    if handler is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported data type: {request.data_type}. Supported: {', '.join(export_handlers.keys())}",
        )

    try:
        df = handler(db, request.brand_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

    if request.format == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False)
        content = output.getvalue()
        media_type = "text/csv"
        filename = f"{request.data_type}_export.csv"
        return StreamingResponse(
            io.BytesIO(content.encode("utf-8-sig")),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    else:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=request.data_type)
        output.seek(0)
        filename = f"{request.data_type}_export.xlsx"
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
