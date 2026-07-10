#!/usr/bin/env python3
"""
品牌去重合并脚本

策略:
1. 对于有配对的36个品牌 (带"(北美)"和不带的各有一个):
   - 保留不带后缀的版本 (通常数据更丰富)
   - 将带后缀版本的多行关联数据 (events, social_media, financials, sentiment, pricing) 迁移到保留版本
   - 去重: events 按 source_url, social_media 按 platform+data_as_of, financials 按 fiscal_year, sentiment 按 platform+data_as_of, pricing 按 category_name
   - 删除带后缀的品牌 (CASCADE 会清理一对一关联表)

2. 对于100个无配对的品牌 (只有带"(北美)"的版本):
   - 去掉名称中的 "(北美)" / "(北美线)" 后缀
   - 更新 slug (去掉 "-na" 后缀)
"""

import sqlite3
import re
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'competitive_research.db')


def clean_name(name: str) -> str:
    """去掉品牌名中的 (北美) / (北美线) 后缀"""
    name = re.sub(r'\s*[（(][^)）]*[)）]\s*$', '', name)
    return name.strip()


def clean_slug(slug: str) -> str:
    """去掉 slug 中的 -na / -beimei 后缀"""
    slug = re.sub(r'-na$', '', slug)
    slug = re.sub(r'-beimei$', '', slug)
    return slug


def migrate_and_merge():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    # ── Step 0: Collect stats before merge ──
    stats_before = {}
    for table in ['brands', 'competitive_events', 'social_media_metrics',
                  'financial_performance', 'customer_sentiment', 'pricing_strategy',
                  'brand_positioning', 'target_demographics', 'product_strategy',
                  'channel_strategy', 'digital_capability', 'brand_categories']:
        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        stats_before[table] = count

    # ── Step 1: Find paired brands ──
    paired = cur.execute("""
        SELECT b1.id as beihei_id, b1.name as beihei_name, b1.slug as beihei_slug,
               b2.id as normal_id, b2.name as normal_name, b2.slug as normal_slug
        FROM brands b1
        JOIN brands b2 ON REPLACE(REPLACE(b1.name, ' (北美)', ''), ' (北美线)', '') = b2.name
        WHERE b1.name LIKE '%(北美)%'
        ORDER BY b1.name
    """).fetchall()

    print(f"找到 {len(paired)} 对重复品牌需要合并")

    merged_count = 0
    migrated_events = 0
    migrated_social = 0
    migrated_financials = 0
    migrated_sentiment = 0
    migrated_pricing = 0

    for beihei_id, beihei_name, beihei_slug, normal_id, normal_name, normal_slug in paired:
        print(f"\n  合并: {beihei_name} → {normal_name} (ID: {beihei_id} → {normal_id})")

        # ── Migrate multi-row tables (only add non-duplicate rows) ──

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

            # Insert with new brand_id
            event_dict['brand_id'] = normal_id
            event_dict.pop('id', None)  # Let autoincrement handle it
            cols = ', '.join(event_dict.keys())
            placeholders = ', '.join(['?'] * len(event_dict))
            cur.execute(
                f"INSERT INTO competitive_events ({cols}) VALUES ({placeholders})",
                list(event_dict.values())
            )
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
            cur.execute(
                f"INSERT INTO social_media_metrics ({cols}) VALUES ({placeholders})",
                list(social_dict.values())
            )
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
            cur.execute(
                f"INSERT INTO financial_performance ({cols}) VALUES ({placeholders})",
                list(fin_dict.values())
            )
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
            cur.execute(
                f"INSERT INTO customer_sentiment ({cols}) VALUES ({placeholders})",
                list(sent_dict.values())
            )
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
            cur.execute(
                f"INSERT INTO pricing_strategy ({cols}) VALUES ({placeholders})",
                list(price_dict.values())
            )
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
                # Merge: if either is primary, keep primary
                existing_is_primary = cur.execute(
                    "SELECT is_primary FROM brand_categories WHERE brand_id = ? AND category_id = ?",
                    (normal_id, cat_id)
                ).fetchone()
                final_primary = is_primary or (existing_is_primary[0] if existing_is_primary else False)
                if existing_is_primary:
                    cur.execute(
                        "UPDATE brand_categories SET is_primary = ? WHERE brand_id = ? AND category_id = ?",
                        (final_primary, normal_id, cat_id)
                    )
                else:
                    cur.execute(
                        "INSERT INTO brand_categories (brand_id, category_id, is_primary) VALUES (?, ?, ?)",
                        (normal_id, cat_id, final_primary)
                    )
                existing_cat_ids.add(cat_id)

        # ── Delete the duplicate (北美) brand ──
        # CASCADE will clean up one-to-one tables (brand_positioning, target_demographics,
        # product_strategy, channel_strategy, digital_capability) that belong to the 北美 brand
        cur.execute("DELETE FROM brands WHERE id = ?", (beihei_id,))
        merged_count += 1

    conn.commit()
    print(f"\n{'='*60}")
    print(f"合并完成: {merged_count} 个品牌已合并")
    print(f"  迁移事件: {migrated_events}")
    print(f"  迁移社交媒体: {migrated_social}")
    print(f"  迁移财务数据: {migrated_financials}")
    print(f"  迁移客户情感: {migrated_sentiment}")
    print(f"  迁移定价数据: {migrated_pricing}")

    # ── Step 2: Rename unpaired (北美) brands ──
    # Find brands that still have (北美) suffix (the 100 unpaired ones)
    unpaired = cur.execute("""
        SELECT id, name, slug FROM brands
        WHERE name LIKE '%(北美)%' OR name LIKE '%(北美线)%'
        ORDER BY name
    """).fetchall()

    print(f"\n找到 {len(unpaired)} 个无配对的(北美)品牌需要重命名")

    renamed_count = 0
    for bid, name, slug in unpaired:
        new_name = clean_name(name)
        new_slug = clean_slug(slug)

        # Ensure slug is unique
        existing = cur.execute(
            "SELECT id FROM brands WHERE slug = ? AND id != ?", (new_slug, bid)
        ).fetchone()
        if existing:
            # Append a suffix to make unique
            new_slug = f"{new_slug}-intl"

        cur.execute(
            "UPDATE brands SET name = ?, slug = ?, updated_at = datetime('now') WHERE id = ?",
            (new_name, new_slug, bid)
        )
        renamed_count += 1
        print(f"  {name} → {new_name} (slug: {slug} → {new_slug})")

    conn.commit()
    print(f"\n重命名完成: {renamed_count} 个品牌")

    # ── Step 3: Verify final stats ──
    stats_after = {}
    for table in ['brands', 'competitive_events', 'social_media_metrics',
                  'financial_performance', 'customer_sentiment', 'pricing_strategy',
                  'brand_positioning', 'target_demographics', 'product_strategy',
                  'channel_strategy', 'digital_capability', 'brand_categories']:
        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        stats_after[table] = count

    print(f"\n{'='*60}")
    print(f"数据统计对比:")
    print(f"{'表名':<30} {'合并前':>8} {'合并后':>8} {'变化':>8}")
    print(f"{'-'*56}")
    for table in stats_before:
        diff = stats_after[table] - stats_before[table]
        sign = '+' if diff > 0 else ''
        print(f"{table:<30} {stats_before[table]:>8} {stats_after[table]:>8} {sign}{diff:>7}")

    # Check for remaining duplicates
    remaining = cur.execute("""
        SELECT clean_name, COUNT(*) as cnt FROM (
            SELECT REPLACE(REPLACE(name, ' (北美)', ''), ' (北美线)', '') as clean_name
            FROM brands
        )
        GROUP BY clean_name
        HAVING COUNT(*) > 1
    """).fetchall()

    if remaining:
        print(f"\n⚠️ 仍有 {len(remaining)} 个重复品牌名:")
        for name, cnt in remaining:
            print(f"  {name}: {cnt} 个")
    else:
        print(f"\n✅ 无重复品牌名")

    # Check all brands have no (北美) suffix
    beihei_remaining = cur.execute(
        "SELECT COUNT(*) FROM brands WHERE name LIKE '%(北美)%' OR name LIKE '%(北美线)%'"
    ).fetchone()[0]
    print(f"带(北美)后缀的剩余品牌: {beihei_remaining}")

    conn.close()
    print(f"\n✅ 全部完成! 当前品牌总数: {stats_after['brands']}")


if __name__ == '__main__':
    print("=" * 60)
    print("品牌去重合并脚本")
    print(f"数据库: {DB_PATH}")
    print(f"时间: {datetime.now().isoformat()}")
    print("=" * 60)
    migrate_and_merge()
