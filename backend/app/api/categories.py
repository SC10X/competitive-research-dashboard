from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Category, BrandCategory
from ..schemas import ApiResponse, CategoryTreeNode

router = APIRouter(prefix="/categories", tags=["categories"])


def _build_tree(categories: List[Category], parent_id: Optional[int] = None,
                brand_counts: Optional[dict] = None) -> List[CategoryTreeNode]:
    nodes = []
    for cat in categories:
        if cat.parent_id == parent_id:
            children = _build_tree(categories, cat.id, brand_counts)
            count = brand_counts.get(cat.id, 0) if brand_counts else 0
            nodes.append(CategoryTreeNode(
                id=cat.id,
                name=cat.name,
                slug=cat.slug,
                parent_id=cat.parent_id,
                level=cat.level,
                sort_order=cat.sort_order,
                children=children,
                brand_count=count,
            ))
    return nodes


@router.get("", response_model=ApiResponse[List[CategoryTreeNode]])
def get_category_tree(
    db: Session = Depends(get_db),
    dimension: Optional[str] = Query(None, description="分类维度: product(产品大类), scenario(运动场景), product-cat(细化品类)"),
):
    if dimension:
        # 按维度返回特定子树
        dimension_slugs = {
            'scenario': 'sports-scenarios',
            'product-cat': 'product-categories',
        }
        root_slug = dimension_slugs.get(dimension)
        if root_slug:
            # 找到维度根节点
            root = db.execute(
                select(Category).where(Category.slug == root_slug)
            ).scalar_one_or_none()
            if root:
                # 获取该维度下所有分类
                all_cats = db.execute(
                    select(Category).order_by(Category.level, Category.sort_order)
                ).scalars().all()
                all_cats = list(all_cats)
                # 计算每个分类的品牌数
                from sqlalchemy import func
                brand_counts = {}
                for cat in all_cats:
                    count = db.execute(
                        select(func.count()).where(BrandCategory.category_id == cat.id)
                    ).scalar()
                    brand_counts[cat.id] = count
                tree = _build_tree(all_cats, root.id, brand_counts)
                return ApiResponse(success=True, data=tree)

        # 产品大类: 只返回 level>0 的传统分类
        all_cats = db.execute(
            select(Category).where(Category.level > 0).order_by(Category.level, Category.sort_order)
        ).scalars().all()
        all_cats = list(all_cats)
        from sqlalchemy import func
        brand_counts = {}
        for cat in all_cats:
            count = db.execute(
                select(func.count()).where(BrandCategory.category_id == cat.id)
            ).scalar()
            brand_counts[cat.id] = count
        tree = _build_tree(all_cats, None, brand_counts)
        return ApiResponse(success=True, data=tree)

    # 默认：返回全部（不含新维度）
    all_cats = db.execute(
        select(Category).where(Category.level > 0).order_by(Category.level, Category.sort_order)
    ).scalars().all()
    all_cats = list(all_cats)
    from sqlalchemy import func
    brand_counts = {}
    for cat in all_cats:
        count = db.execute(
            select(func.count()).where(BrandCategory.category_id == cat.id)
        ).scalar()
        brand_counts[cat.id] = count
    tree = _build_tree(all_cats, None, brand_counts)
    return ApiResponse(success=True, data=tree)
