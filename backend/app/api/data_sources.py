from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import DataSource
from ..schemas import (
    ApiResponse,
    PaginationMeta,
    DataSourceOut,
    DataSourceCreate,
    DataSourceUpdate,
)

router = APIRouter(prefix="/data-sources", tags=["data_sources"])


@router.get("", response_model=ApiResponse[List[DataSourceOut]])
def list_data_sources(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    stmt = select(DataSource)

    if source_type:
        stmt = stmt.where(DataSource.source_type == source_type)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0

    stmt = stmt.order_by(DataSource.name).offset((page - 1) * page_size).limit(page_size)
    sources = db.execute(stmt).scalars().all()

    return ApiResponse(
        success=True,
        data=[DataSourceOut.model_validate(s) for s in sources],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=(total + page_size - 1) // page_size if total > 0 else 0,
        ),
    )


@router.get("/{source_id}", response_model=ApiResponse[DataSourceOut])
def get_data_source(source_id: int, db: Session = Depends(get_db)):
    stmt = select(DataSource).where(DataSource.id == source_id)
    source = db.execute(stmt).scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    return ApiResponse(success=True, data=DataSourceOut.model_validate(source))


@router.post("", response_model=ApiResponse[DataSourceOut])
def create_data_source(source: DataSourceCreate, db: Session = Depends(get_db)):
    new_source = DataSource(**source.model_dump())
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    return ApiResponse(success=True, data=DataSourceOut.model_validate(new_source))


@router.put("/{source_id}", response_model=ApiResponse[DataSourceOut])
def update_data_source(source_id: int, source: DataSourceUpdate, db: Session = Depends(get_db)):
    stmt = select(DataSource).where(DataSource.id == source_id)
    existing = db.execute(stmt).scalar_one_or_none()
    if not existing:
        raise HTTPException(status_code=404, detail="Data source not found")

    update_data = source.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing, key, value)

    db.commit()
    db.refresh(existing)
    return ApiResponse(success=True, data=DataSourceOut.model_validate(existing))


@router.delete("/{source_id}", response_model=ApiResponse[dict])
def delete_data_source(source_id: int, db: Session = Depends(get_db)):
    stmt = select(DataSource).where(DataSource.id == source_id)
    source = db.execute(stmt).scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    db.delete(source)
    db.commit()
    return ApiResponse(success=True, data={"message": "Data source deleted successfully"})
