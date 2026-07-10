from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Category
from ..schemas import ApiResponse, CategoryTreeNode

router = APIRouter(prefix="/categories", tags=["categories"])


def _build_tree(categories: List[Category], parent_id: Optional[int] = None) -> List[CategoryTreeNode]:
    nodes = []
    for cat in categories:
        if cat.parent_id == parent_id:
            children = _build_tree(categories, cat.id)
            nodes.append(CategoryTreeNode(
                id=cat.id,
                name=cat.name,
                slug=cat.slug,
                parent_id=cat.parent_id,
                level=cat.level,
                sort_order=cat.sort_order,
                children=children,
            ))
    return nodes


@router.get("", response_model=ApiResponse[List[CategoryTreeNode]])
def get_category_tree(db: Session = Depends(get_db)):
    stmt = select(Category).order_by(Category.level, Category.sort_order)
    categories = db.execute(stmt).scalars().all()

    tree = _build_tree(list(categories), parent_id=None)

    return ApiResponse(success=True, data=tree)
