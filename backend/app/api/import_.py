from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy import select, func, text
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db, engine
from ..schemas import (
    ApiResponse,
    ImportPreviewOut,
    ImportExecuteRequest,
    ImportHistoryItem,
)

router = APIRouter(prefix="/import", tags=["import"])


ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".csv"}

TABLE_COLUMN_MAP = {
    "brands": ["name", "slug", "country", "founded_year", "parent_company", "headquarters", "logo_url", "website", "description", "is_active"],
    "financials": ["brand_id", "fiscal_year", "revenue", "revenue_growth_pct", "gross_margin_pct", "na_revenue_pct", "is_estimated", "data_source"],
    "events": ["brand_id", "event_type", "title", "description", "event_date", "source_url", "source_name", "importance", "tags"],
    "pricing": ["brand_id", "category_name", "price_range_min", "price_range_max", "avg_price", "discount_frequency", "typical_discount_pct", "has_membership", "membership_price", "membership_model", "data_as_of"],
    "social_media": ["brand_id", "platform", "followers", "engagement_rate", "avg_likes", "avg_comments", "post_frequency", "top_hashtags", "key_kols", "data_as_of"],
    "sentiment": ["brand_id", "platform", "rating", "review_count", "positive_themes", "negative_themes", "nps_score", "data_as_of"],
}

IMPORT_HISTORY = []  # In-memory storage for import history; in production use DB


def _read_file(file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
    ext = os.path.splitext(file_path)[1].lower()
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(file_path, sheet_name=sheet_name or 0)
    elif ext == ".csv":
        return pd.read_csv(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


@router.post("/upload", response_model=ApiResponse[dict])
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    safe_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_name)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    try:
        df = _read_file(file_path)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    return ApiResponse(
        success=True,
        data={
            "file_name": safe_name,
            "original_name": file.filename,
            "total_rows": len(df),
            "columns": list(df.columns),
            "file_path": file_path,
        },
    )


@router.post("/preview", response_model=ApiResponse[ImportPreviewOut])
def preview_import(
    file_name: str = Form(...),
    sheet_name: Optional[str] = Form(None),
    data_type: str = Form("brands"),
    db: Session = Depends(get_db),
):
    file_path = os.path.join(settings.UPLOAD_DIR, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        df = _read_file(file_path, sheet_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    expected_cols = TABLE_COLUMN_MAP.get(data_type, [])
    missing_cols = [c for c in expected_cols if c not in df.columns]
    valid_rows = len(df)
    invalid_rows = 0
    errors = []

    if missing_cols:
        invalid_rows = valid_rows
        valid_rows = 0
        errors.append({"message": f"Missing required columns: {missing_cols}"})

    sample_data = df.head(10).fillna("").to_dict(orient="records")

    return ApiResponse(
        success=True,
        data=ImportPreviewOut(
            file_name=file_name,
            sheet_name=sheet_name,
            total_rows=len(df),
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            columns=list(df.columns),
            sample_data=sample_data,
            errors=errors,
        ),
    )


@router.post("/execute", response_model=ApiResponse[ImportHistoryItem])
def execute_import(
    request: ImportExecuteRequest,
    db: Session = Depends(get_db),
):
    file_path = os.path.join(settings.UPLOAD_DIR, request.file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        df = _read_file(file_path, request.sheet_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    expected_cols = TABLE_COLUMN_MAP.get(request.data_type, [])
    missing_cols = [c for c in expected_cols if c not in df.columns]
    if missing_cols:
        raise HTTPException(status_code=400, detail=f"Missing columns: {missing_cols}")

    total_rows = len(df)
    imported_rows = 0
    skipped_rows = 0

    # Use only columns that exist in the table definition
    import_cols = [c for c in expected_cols if c in df.columns]
    import_df = df[import_cols].copy()

    # Handle JSON columns - convert string to proper format
    json_cols = ["tags", "top_hashtags", "key_kols", "positive_themes", "negative_themes",
                 "hero_products", "recent_collabs", "tech_innovations", "category_expansion",
                 "retail_partners", "ecommerce_platforms", "international_markets",
                 "lifestyle_tags", "core_scenarios", "ai_features"]
    for col in json_cols:
        if col in import_df.columns:
            import_df[col] = import_df[col].apply(
                lambda x: x if isinstance(x, (list, dict)) or pd.isna(x) else str(x)
            )

    # Handle date columns
    date_cols = ["data_as_of", "event_date", "created_at", "updated_at", "last_verified_at"]
    for col in date_cols:
        if col in import_df.columns:
            import_df[col] = pd.to_datetime(import_df[col], errors="coerce")

    # Handle boolean columns
    bool_cols = ["is_active", "is_primary", "is_estimated", "has_membership",
                 "has_sustainable_line", "has_personalization", "has_virtual_tryon",
                 "has_community_feature", "has_membership_program"]
    for col in bool_cols:
        if col in import_df.columns:
            import_df[col] = import_df[col].astype(bool)

    try:
        table_name = request.data_type
        imported_rows = len(import_df)
        import_df.to_sql(
            table_name,
            engine,
            if_exists="append",
            index=False,
            method="multi",
        )
    except Exception as e:
        skipped_rows = total_rows
        imported_rows = 0
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

    status = "completed" if skipped_rows == 0 else "partial"
    history_item = ImportHistoryItem(
        id=len(IMPORT_HISTORY) + 1,
        file_name=request.file_name,
        data_type=request.data_type,
        total_rows=total_rows,
        imported_rows=imported_rows,
        skipped_rows=skipped_rows,
        status=status,
        created_at=datetime.now(),
    )
    IMPORT_HISTORY.append(history_item)

    return ApiResponse(success=True, data=history_item)


@router.get("/history", response_model=ApiResponse[List[ImportHistoryItem]])
def get_import_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total = len(IMPORT_HISTORY)
    start = (page - 1) * page_size
    end = start + page_size
    items = IMPORT_HISTORY[start:end]

    return ApiResponse(
        success=True,
        data=items,
        meta={
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }
        },
    )
