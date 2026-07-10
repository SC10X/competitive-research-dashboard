"""
Admin API — 数据库管理端点
"""
import re
import sqlite3
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db, engine
from ..config import settings

router = APIRouter(prefix="/admin", tags=["admin"])


class DedupResult(BaseModel):
    success: bool
    message: str
    brands_before: int
    brands_after: int
    merged_pairs: int
    renamed_brands: int
    migrated_events: int
    migrated_social: int
    migrated_financials: int
    migrated_sentiment: int
    migrated_pricing: int
    orphan_records: int
    duplicate_names_remaining: int
    timestamp: str


def _clean_name(name: str) -> str:
    name = re.sub(r'\s*[（(][^)）]*[)）]\s*$', '', name)
    return name.strip()


def _clean_slug(slug: str) -> str:
    slug = re.sub(r'-na$', '', slug)
    slug = re.sub(r'-beimei$', '', slug)
    return slug


@router.post("/dedup", response_model=DedupResult)
def dedup_brands(
    dry_run: bool = Query(False, description="If true, only report what would change without modifying data"),
    db: Session = Depends(get_db),
):
    """
    品牌去重合并：
    1. 有配对的(北美)品牌 → 合并到不带后缀的版本，迁移关联数据，删除重复
    2. 无配对的(北美)品牌 → 去掉名称和slug中的后缀
    """
    db_path = Path(settings.DATA_DIR) / "competitive_research.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    brands_before = cur.execute("SELECT COUNT(*) FROM brands").fetchone()[0]

    # Find paired brands
    paired = cur.execute("""
        SELECT b1.id as beihei_id, b1.name as beihei_name,
               b2.id as normal_id, b2.name as normal_name
        FROM brands b1
        JOIN brands b2 ON REPLACE(REPLACE(b1.name, ' (北美)', ''), ' (北美线)', '') = b2.name
        WHERE b1.name LIKE '%(北美)%'
        ORDER BY b1.name
    """).fetchall()

    merged_pairs = 0
    migrated_events = 0
    migrated_social = 0
    migrated_financials = 0
    migrated_sentiment = 0
    migrated_pricing = 0

    if not dry_run:
        for beihei_id, beihei_name, normal_id, normal_name in paired:
            # 1. competitive_events - dedup by source_url
            beihei_events = cur.execute(
                "SELECT * FROM competitive_events WHERE brand_id = ?", (beihei_id,)
            ).fetchall()
            col_names = [desc[0] for desc in cur.description]
            existing_urls = set()
            for row in cur.execute(
                "SELECT source_url FROM competitive_events WHERE brand_id = ?", (normal_id,)
            ).fetchall():
                if row[0]:
                    existing_urls.add(row[0])
            for event_row in beihei_events:
                event_dict = dict(zip(col_names, event_row))
                source_url = event_dict.get('source_url', '')
                if source_url and source_url in existing_urls:
                    continue
                existing_urls.add(source_url)
                event_dict['brand_id'] = normal_id
                event_dict.pop('id', None)
                cols = ', '.join(event_dict.keys())
                placeholders = ', '.join(['?'] * len(event_dict))
                cur.execute(f"INSERT INTO competitive_events ({cols}) VALUES ({placeholders})", list(event_dict.values()))
                migrated_events += 1

            # 2. social_media_metrics - dedup by platform + data_as_of
            beihei_social = cur.execute(
                "SELECT * FROM social_media_metrics WHERE brand_id = ?", (beihei_id,)
            ).fetchall()
            col_names = [desc[0] for desc in cur.description]
            existing_combos = set()
            for row in cur.execute(
                "SELECT platform, data_as_of FROM social_media_metrics WHERE brand_id = ?", (normal_id,)
            ).fetchall():
                existing_combos.add((row[0], str(row[1]) if row[1] else ''))
            for social_row in beihei_social:
                social_dict = dict(zip(col_names, social_row))
                combo = (social_dict.get('platform', ''), str(social_dict.get('data_as_of', '') or ''))
                if combo in existing_combos:
                    continue
                existing_combos.add(combo)
                social_dict['brand_id'] = normal_id
                social_dict.pop('id', None)
                cols = ', '.join(social_dict.keys())
                placeholders = ', '.join(['?'] * len(social_dict))
                cur.execute(f"INSERT INTO social_media_metrics ({cols}) VALUES ({placeholders})", list(social_dict.values()))
                migrated_social += 1

            # 3. financial_performance - dedup by fiscal_year
            beihei_fin = cur.execute(
                "SELECT * FROM financial_performance WHERE brand_id = ?", (beihei_id,)
            ).fetchall()
            col_names = [desc[0] for desc in cur.description]
            existing_years = set()
            for row in cur.execute(
                "SELECT fiscal_year FROM financial_performance WHERE brand_id = ?", (normal_id,)
            ).fetchall():
                existing_years.add(row[0])
            for fin_row in beihei_fin:
                fin_dict = dict(zip(col_names, fin_row))
                year = fin_dict.get('fiscal_year')
                if year in existing_years:
                    continue
                existing_years.add(year)
                fin_dict['brand_id'] = normal_id
                fin_dict.pop('id', None)
                cols = ', '.join(fin_dict.keys())
                placeholders = ', '.join(['?'] * len(fin_dict))
                cur.execute(f"INSERT INTO financial_performance ({cols}) VALUES ({placeholders})", list(fin_dict.values()))
                migrated_financials += 1

            # 4. customer_sentiment - dedup by platform + data_as_of
            beihei_sent = cur.execute(
                "SELECT * FROM customer_sentiment WHERE brand_id = ?", (beihei_id,)
            ).fetchall()
            col_names = [desc[0] for desc in cur.description]
            existing_combos = set()
            for row in cur.execute(
                "SELECT platform, data_as_of FROM customer_sentiment WHERE brand_id = ?", (normal_id,)
            ).fetchall():
                existing_combos.add((row[0], str(row[1]) if row[1] else ''))
            for sent_row in beihei_sent:
                sent_dict = dict(zip(col_names, sent_row))
                combo = (sent_dict.get('platform', ''), str(sent_dict.get('data_as_of', '') or ''))
                if combo in existing_combos:
                    continue
                existing_combos.add(combo)
                sent_dict['brand_id'] = normal_id
                sent_dict.pop('id', None)
                cols = ', '.join(sent_dict.keys())
                placeholders = ', '.join(['?'] * len(sent_dict))
                cur.execute(f"INSERT INTO customer_sentiment ({cols}) VALUES ({placeholders})", list(sent_dict.values()))
                migrated_sentiment += 1

            # 5. pricing_strategy - dedup by category_name
            beihei_price = cur.execute(
                "SELECT * FROM pricing_strategy WHERE brand_id = ?", (beihei_id,)
            ).fetchall()
            col_names = [desc[0] for desc in cur.description]
            existing_cats = set()
            for row in cur.execute(
                "SELECT category_name FROM pricing_strategy WHERE brand_id = ?", (normal_id,)
            ).fetchall():
                existing_cats.add(row[0])
            for price_row in beihei_price:
                price_dict = dict(zip(col_names, price_row))
                cat = price_dict.get('category_name')
                if cat in existing_cats:
                    continue
                existing_cats.add(cat)
                price_dict['brand_id'] = normal_id
                price_dict.pop('id', None)
                cols = ', '.join(price_dict.keys())
                placeholders = ', '.join(['?'] * len(price_dict))
                cur.execute(f"INSERT INTO pricing_strategy ({cols}) VALUES ({placeholders})", list(price_dict.values()))
                migrated_pricing += 1

            # 6. brand_categories - dedup by category_id
            beihei_cats = cur.execute(
                "SELECT category_id, is_primary FROM brand_categories WHERE brand_id = ?", (beihei_id,)
            ).fetchall()
            existing_cat_ids = set()
            for row in cur.execute(
                "SELECT category_id FROM brand_categories WHERE brand_id = ?", (normal_id,)
            ).fetchall():
                existing_cat_ids.add(row[0])
            for cat_id, is_primary in beihei_cats:
                if cat_id not in existing_cat_ids:
                    cur.execute(
                        "INSERT INTO brand_categories (brand_id, category_id, is_primary) VALUES (?, ?, ?)",
                        (normal_id, cat_id, is_primary)
                    )
                    existing_cat_ids.add(cat_id)

            # Delete the duplicate (北美) brand
            cur.execute("DELETE FROM brands WHERE id = ?", (beihei_id,))
            merged_pairs += 1

        # Rename unpaired (北美) brands
        unpaired = cur.execute("""
            SELECT id, name, slug FROM brands
            WHERE name LIKE '%(北美)%' OR name LIKE '%(北美线)%'
            ORDER BY name
        """).fetchall()

        renamed_brands = 0
        for bid, name, slug in unpaired:
            new_name = _clean_name(name)
            new_slug = _clean_slug(slug)
            existing = cur.execute(
                "SELECT id FROM brands WHERE slug = ? AND id != ?", (new_slug, bid)
            ).fetchone()
            if existing:
                new_slug = f"{new_slug}-intl"
            cur.execute(
                "UPDATE brands SET name = ?, slug = ?, updated_at = datetime('now') WHERE id = ?",
                (new_name, new_slug, bid)
            )
            renamed_brands += 1

        conn.commit()
    else:
        renamed_brands = cur.execute(
            "SELECT COUNT(*) FROM brands WHERE name LIKE '%(北美)%' OR name LIKE '%(北美线)%'"
        ).fetchone()[0] - len(paired)
        if renamed_brands < 0:
            renamed_brands = 0

    brands_after = cur.execute("SELECT COUNT(*) FROM brands").fetchone()[0]

    # Check for issues
    orphan = 0
    for table in ['competitive_events', 'social_media_metrics', 'financial_performance',
                   'customer_sentiment', 'pricing_strategy', 'brand_categories']:
        orphan += cur.execute(
            f"SELECT COUNT(*) FROM {table} WHERE brand_id NOT IN (SELECT id FROM brands)"
        ).fetchone()[0]

    dup_names = cur.execute("""
        SELECT COUNT(*) FROM (
            SELECT name, COUNT(*) as c FROM brands GROUP BY name HAVING c > 1
        )
    """).fetchone()[0]

    conn.close()

    action = "模拟运行" if dry_run else "已执行"
    return DedupResult(
        success=True,
        message=f"品牌去重{action}完成：{len(paired)}对重复品牌{'将' if dry_run else ''}合并，{renamed_brands}个品牌{'将' if dry_run else ''}重命名",
        brands_before=brands_before,
        brands_after=brands_after,
        merged_pairs=len(paired),
        renamed_brands=renamed_brands,
        migrated_events=migrated_events,
        migrated_social=migrated_social,
        migrated_financials=migrated_financials,
        migrated_sentiment=migrated_sentiment,
        migrated_pricing=migrated_pricing,
        orphan_records=orphan,
        duplicate_names_remaining=dup_names,
        timestamp=datetime.now().isoformat(),
    )
