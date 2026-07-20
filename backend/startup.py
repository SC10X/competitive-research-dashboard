"""
Runtime database updates — runs at container startup to apply
data changes that may not be reflected in the Docker image cache.
"""
import sqlite3
import os
import sys
import traceback

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'competitive_research.db')


def apply_updates():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}, skipping updates")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Ensure columns exist
    for col in ['instagram_url', 'twitter_url', 'tiktok_url', 'youtube_url', 'amazon_url']:
        try:
            cur.execute(f'ALTER TABLE brands ADD COLUMN {col} VARCHAR(300)')
        except:
            pass

    # ── 0. Auto-generate logo_url from website domain using Favicone ──
    from urllib.parse import urlparse as _up
    logo_count = cur.execute(
        "SELECT COUNT(*) FROM brands WHERE logo_url IS NULL OR logo_url=''"
    ).fetchone()[0]
    if logo_count > 0:
        print(f"Generating logo URLs for {logo_count} brands...")
        cur.execute("SELECT id, website FROM brands WHERE logo_url IS NULL OR logo_url=''")
        for bid, website in cur.fetchall():
            if website:
                try:
                    domain = _up(website).netloc or _up(website).path
                    domain = domain.replace('www.', '').rstrip('/')
                    if domain:
                        cur.execute(
                            "UPDATE brands SET logo_url=?, updated_at=datetime('now') WHERE id=?",
                            (f'https://favicone.com/{domain}', bid)
                        )
                        changes += 1
                except Exception:
                    pass
        print(f"Generated {changes} logo URLs")

    changes = 0

    # ── 1. Standardize country names ──
    country_map = {
        '美国(北美)': '美国', 'United States': '美国', 'USA': '美国',
        '美国(欧洲设计)': '美国', '美国(日本授权)': '美国',
        '英国(北美)': '英国', '英国(美国HQ)': '英国', '英国/美国': '英国', 'UK': '英国',
        '法国(北美)': '法国', 'France': '法国', '法国(美国Deckers)': '法国',
        '意大利(北美)': '意大利', 'Italy': '意大利', '意大利/美国': '意大利', '意大利(韩国总部)': '意大利',
        '加拿大(北美)': '加拿大', 'Canada': '加拿大', '加拿大/美国': '加拿大',
        '瑞典(北美)': '瑞典',
        '澳大利亚(北美)': '澳大利亚', '澳大利亚/美国': '澳大利亚', '澳大利亚/美国(北美)': '澳大利亚',
        '日本(北美)': '日本',
        '丹麦(北美)': '丹麦', 'Denmark': '丹麦', '丹麦/美国(北美)': '丹麦',
        '瑞士(北美)': '瑞士', 'Switzerland': '瑞士',
        '德国(北美)': '德国', 'Germany': '德国',
        '西班牙(北美)': '西班牙', 'Spain': '西班牙',
        '挪威(北美)': '挪威',
        '新西兰(北美)': '新西兰',
        '巴西(北美)': '巴西',
        '南非/美国': '南非',
        '奥地利/美国': '奥地利', '奥地利/美国(北美)': '奥地利',
        '中国/美国': '中国',
        '尼泊尔/美国': '尼泊尔',
        '美国/韩国': '韩国',
        '美国/德国': '美国',
    }
    for old, new in country_map.items():
        cur.execute("UPDATE brands SET country=?, updated_at=datetime('now') WHERE country=?", (new, old))
        if cur.rowcount > 0:
            changes += cur.rowcount

    # ── 2. Standardize price tiers ──
    tier_map = {
        'Luxury': 'Luxury', 'luxury': 'Luxury', 'Premium-Luxury': 'Luxury',
        'premium_luxury': 'Luxury', 'contemporary_luxury': 'Luxury',
        'Premium': 'Premium', 'Premium DTC': 'Premium',
        'Mid': 'Mid', 'Mid-Market': 'Mid', 'mid_range': 'Mid',
        'Mid-Premium': 'Mid', 'Mid Premium': 'Mid', 'Mass Premium': 'Mid',
        'Mass': 'Mass', 'Mass Market': 'Mass', 'Mass-Market': 'Mass',
        'mass_market': 'Mass', 'Mass DTC': 'Mass', 'Budget-Friendly': 'Mass',
    }
    for old, new in tier_map.items():
        cur.execute('UPDATE brand_positioning SET price_tier=? WHERE price_tier=?', (new, old))
        if cur.rowcount > 0:
            changes += cur.rowcount

    # ── 3. Apply Instagram URLs for brands missing them ──
    ig_handles = {
        '& Other Stories': 'andotherstories', '2XU': '2xu', '7 For All Mankind': '7forallmankind',
        'A.P.C.': 'apc_paris', 'AG Jeans': 'agjeans', 'ASICS': 'asics',
        'AYBL': 'aybl', 'Abercrombie & Fitch': 'abercrombie', 'Acne Studios': 'acnestudios',
        'Aday': 'aday', 'Adidas': 'adidas', 'Aether Apparel': 'aetherapparel',
        'Aime Leon Dore': 'aimeleondore', 'Aldo': 'aldo',
        'Alexander Wang': 'alexanderwang', 'Alice + Olivia': 'aliceolivia',
        'Allbirds': 'allbirds', 'Alo Yoga': 'aloyoga', 'Altuzarra': 'altuzarra',
        'American Eagle': 'americaneagle', 'American Giant': 'americangiant',
        "Arc'teryx": 'arcteryx', 'Athleta': 'athleta', 'Away': 'away',
        'Balenciaga': 'balenciaga', 'Balmain': 'balmain', 'Banana Republic': 'bananarepublic',
        'Beyond Yoga': 'beyondyoga', 'Birkenstock': 'birkenstock', 'Black Diamond': 'blackdiamond',
        'Blundstone': 'blundstone', 'Bode': 'bode', 'Bonobos': 'bonobos',
        'Bottega Veneta': 'bottegaveneta', 'Brooks': 'brooksrunning', 'Brunello Cucinelli': 'brunellocucinelli',
        'Burberry': 'burberry', 'Burton': 'burtonsnowboards',
        'Canada Goose': 'canadagoose', 'Carhartt': 'carhartt', 'Cartier': 'cartier',
        'Celine': 'celine', 'Champion': 'champion', 'Chanel': 'chanelofficial',
        'Chrome Hearts': 'chromeheartsofficial', 'Coach': 'coach', 'Columbia': 'columbia1938',
        'Common Projects': 'commonprojects', 'Converse': 'converse', 'Cotopaxi': 'cotopaxi',
        'Crocs': 'crocs', 'Cuyana': 'cuyana', 'Dagne Dover': 'dagnedover',
        'Dior': 'dior', 'Dr. Martens': 'drmartensofficial', 'Everlane': 'everlane',
        'Fendi': 'fendi', 'Filson': 'filson1897', 'Gap': 'gap',
        'Girlfriend Collective': 'girlfriendcollective', 'Golden Goose': 'goldengoose',
        'Gucci': 'gucci', 'Gymshark': 'gymshark',
        'H&M': 'hm', 'Helly Hansen': 'hellyhansen', 'Hermes': 'hermes',
        'HeyDude': 'heydude', 'Hoka': 'hoka', 'Hollister': 'hollisterco',
        'J.Crew': 'jcrew', 'Jacquemus': 'jacquemus', 'JanSport': 'jansport',
        'Keen': 'keen', 'Kith': 'kith', 'Lacoste': 'lacoste',
        "Levi's": 'levis', 'Louis Vuitton': 'louisvuitton', 'Lululemon': 'lululemon',
        'Madewell': 'madewell', 'Mansur Gavriel': 'mansurgavriel', 'Marc Jacobs': 'marcjacobs',
        'Merrell': 'merrell', 'Michael Kors': 'michaelkors', 'Moncler': 'moncler',
        'New Balance': 'newbalance', 'Nike': 'nike', 'North Face': 'thenorthface',
        'Off-White': 'off____white', 'On': 'on', 'Outdoor Voices': 'outdoorvoices',
        'Patagonia': 'patagonia', 'Polo Ralph Lauren': 'poloralphlauren', 'Prada': 'prada',
        'Puma': 'puma', 'Ralph Lauren': 'ralphlauren', 'Reebok': 'reebok',
        'Reformation': 'reformation', 'Rhone': 'rhone', 'Rimowa': 'rimowa',
        "Rothy's": 'rothys', 'Salomon': 'salomon', 'Saucony': 'saucony',
        'Skechers': 'skechers', 'Skims': 'skims', 'Staud': 'staud.clothing',
        'Steve Madden': 'stevemadden', 'Stone Island': 'stoneisland_official',
        'Stussy': 'stussy', 'Supreme': 'supremenewyork',
        'Teva': 'teva', 'Timberland': 'timberland', 'Toms': 'toms',
        'Tory Burch': 'toryburch', 'Tumi': 'tumi',
        'UGG': 'ugg', 'Under Armour': 'underarmour', 'Uniqlo': 'uniqlo',
        'Urban Outfitters': 'urbanoutfitters',
        'Valentino': 'maisonvalentino', 'Vans': 'vans', 'Veja': 'veja',
        'Versace': 'versace', 'Vuori': 'vuoriclothing',
        'Warby Parker': 'warbyparker', 'Yeezy': 'yeezy',
        'Zara': 'zara', 'Zegna': 'zegnaofficial',
    }

    for name, handle in ig_handles.items():
        url = f'https://instagram.com/{handle}'
        cur.execute(
            "UPDATE brands SET instagram_url=? WHERE (name=? OR name=?) AND (instagram_url IS NULL OR instagram_url='')",
            (url, name, name + ' (北美)')
        )
        if cur.rowcount > 0:
            changes += cur.rowcount

    # Auto-generate Instagram URLs for remaining brands
    cur.execute("SELECT id, name FROM brands WHERE instagram_url IS NULL OR instagram_url=''")
    no_ig = cur.fetchall()
    for bid, bname in no_ig:
        clean = bname.replace(' (北美)', '').replace(' (北美线)', '').lower()
        clean = clean.replace(' ', '').replace("'", '').replace('.', '').replace('&', 'and').replace('+', '')
        url = f'https://instagram.com/{clean}'
        cur.execute("UPDATE brands SET instagram_url=? WHERE id=?", (url, bid))
        changes += 1

    # ── 4. Apply Twitter URLs ──
    twitter_urls = {
        'Nike': 'https://x.com/Nike', 'Adidas': 'https://x.com/adidas',
        'Lululemon': 'https://x.com/lululemon', 'Hoka': 'https://x.com/HOKA',
        'On Running': 'https://x.com/on_running', 'New Balance': 'https://x.com/newbalance',
        "Arc'teryx": 'https://x.com/Arcteryx', 'Patagonia': 'https://x.com/patagonia',
        'The North Face': 'https://x.com/thenorthface', 'Vuori': 'https://x.com/vuoriclothing',
        'Alo Yoga': 'https://x.com/aloyoga', 'Skechers': 'https://x.com/SKECHERS',
        'Under Armour': 'https://x.com/UnderArmour', 'Crocs': 'https://x.com/Crocs',
        'Birkenstock': 'https://x.com/Birkenstock', 'UGG': 'https://x.com/UGG',
        'Canada Goose': 'https://x.com/canadagooseinc', 'Moncler': 'https://x.com/moncler',
        'Ralph Lauren': 'https://x.com/ralphlauren', "Levi's": 'https://x.com/LEVIS',
        'Carhartt': 'https://x.com/Carhartt', 'Salomon': 'https://x.com/SalomonSports',
        'Columbia': 'https://x.com/Columbia1938', 'Allbirds': 'https://x.com/Allbirds',
        'Everlane': 'https://x.com/Everlane', 'Reformation': 'https://x.com/reformation',
        'Shein': 'https://x.com/SHEIN_Official', 'Zara': 'https://x.com/ZARA',
        'Uniqlo': 'https://x.com/UniqloUSA', 'Gap': 'https://x.com/Gap',
        'American Eagle': 'https://x.com/AEO', 'Vans': 'https://x.com/VANS_66',
        'Converse': 'https://x.com/Converse', 'Puma': 'https://x.com/PUMA',
        'Dr. Martens': 'https://x.com/drmartens', 'Timberland': 'https://x.com/Timberland',
        'Merrell': 'https://x.com/Merrell', 'Keen': 'https://x.com/KEEN',
        'Gymshark': 'https://x.com/Gymshark', 'Fabletics': 'https://x.com/Fabletics',
        'Aritzia': 'https://x.com/ARITZIA', 'Revolve': 'https://x.com/REVOLVE',
        'Fashion Nova': 'https://x.com/FashionNova', 'SKIMS': 'https://x.com/skims',
        'Bombas': 'https://x.com/Bombas', 'Gucci': 'https://x.com/gucci',
        'Prada': 'https://x.com/Prada', 'Louis Vuitton': 'https://x.com/LouisVuitton',
        'Chanel': 'https://x.com/CHANEL', 'Hermès': 'https://x.com/Hermes_Paris',
        'Dior': 'https://x.com/Dior', 'Balenciaga': 'https://x.com/BALENCIAGA',
        'Burberry': 'https://x.com/Burberry', 'Versace': 'https://x.com/Versace',
        'Saint Laurent': 'https://x.com/YSL', 'Bottega Veneta': 'https://x.com/BottegaVeneta',
        'Fendi': 'https://x.com/Fendi', 'Givenchy': 'https://x.com/givenchy',
        'Balmain': 'https://x.com/Balmain', 'Celine': 'https://x.com/CELINE',
        'Loewe': 'https://x.com/LoeweOfficial', 'Jacquemus': 'https://x.com/jacquemus',
        'Miu Miu': 'https://x.com/MIUMIUofficial', 'Acne Studios': 'https://x.com/acnestudios',
        'Ganni': 'https://x.com/GANNI', 'COS': 'https://x.com/COSstores',
        'H&M': 'https://x.com/hm', 'Tommy Hilfiger': 'https://x.com/TommyHilfiger',
        'Calvin Klein': 'https://x.com/CalvinKlein', 'Diesel': 'https://x.com/diesel',
        'Off-White': 'https://x.com/OffWht', 'Polo Ralph Lauren': 'https://x.com/ralphlauren',
        'Skims': 'https://x.com/skims', 'Spanx': 'https://x.com/SPANX',
        'A.P.C.': 'https://x.com/APC_PARIS', 'Champion': 'https://x.com/ChampionUSA',
        'Mugler': 'https://x.com/Mugler', 'Lanvin': 'https://x.com/LANVINofficial',
        'Chloé': 'https://x.com/chloe', 'Comme des Garçons': 'https://x.com/CommeDesGarcons',
        'JW Anderson': 'https://x.com/jwanderson', 'Helmut Lang': 'https://x.com/HelmutLang',
    }

    for name, url in twitter_urls.items():
        cur.execute(
            "UPDATE brands SET twitter_url=?, updated_at=datetime('now') WHERE (name=? OR name=?) AND (twitter_url IS NULL OR twitter_url='')",
            (url, name, name + ' (北美)')
        )
        if cur.rowcount > 0:
            changes += cur.rowcount

    # ── 5. Apply TikTok URLs ──
    tiktok_urls = {
        'Nike': 'https://www.tiktok.com/@nike', 'Adidas': 'https://www.tiktok.com/@adidas',
        'Lululemon': 'https://www.tiktok.com/@lululemon', 'Hoka': 'https://www.tiktok.com/@hoka',
        'New Balance': 'https://www.tiktok.com/@newbalance',
        "Arc'teryx": 'https://www.tiktok.com/@arcteryx', 'Patagonia': 'https://www.tiktok.com/@patagonia',
        'The North Face': 'https://www.tiktok.com/@thenorthface',
        'Alo Yoga': 'https://www.tiktok.com/@aloyoga', 'Skechers': 'https://www.tiktok.com/@skechers',
        'Under Armour': 'https://www.tiktok.com/@underarmour', 'Crocs': 'https://www.tiktok.com/@crocs',
        'Birkenstock': 'https://www.tiktok.com/@birkenstock', 'UGG': 'https://www.tiktok.com/@ugg',
        'Canada Goose': 'https://www.tiktok.com/@canadagoose', 'Ralph Lauren': 'https://www.tiktok.com/@ralphlauren',
        "Levi's": 'https://www.tiktok.com/@levis', 'Carhartt': 'https://www.tiktok.com/@carhartt',
        'Columbia': 'https://www.tiktok.com/@columbia', 'Allbirds': 'https://www.tiktok.com/@allbirds',
        'Everlane': 'https://www.tiktok.com/@everlane', 'Reformation': 'https://www.tiktok.com/@reformation',
        'Shein': 'https://www.tiktok.com/@shein_official', 'Zara': 'https://www.tiktok.com/@zara',
        'Uniqlo': 'https://www.tiktok.com/@uniqlo', 'Gap': 'https://www.tiktok.com/@gap',
        'American Eagle': 'https://www.tiktok.com/@americaneagle', 'Vans': 'https://www.tiktok.com/@vans',
        'Converse': 'https://www.tiktok.com/@converse', 'Puma': 'https://www.tiktok.com/@puma',
        'Dr. Martens': 'https://www.tiktok.com/@drmartens', 'Timberland': 'https://www.tiktok.com/@timberland',
        'Gymshark': 'https://www.tiktok.com/@gymshark', 'Fabletics': 'https://www.tiktok.com/@fabletics',
        'Aritzia': 'https://www.tiktok.com/@aritzia', 'Fashion Nova': 'https://www.tiktok.com/@fashionnova',
        'SKIMS': 'https://www.tiktok.com/@skims', 'Gucci': 'https://www.tiktok.com/@gucci',
        'Prada': 'https://www.tiktok.com/@prada', 'Louis Vuitton': 'https://www.tiktok.com/@louisvuitton',
        'Dior': 'https://www.tiktok.com/@dior', 'Balenciaga': 'https://www.tiktok.com/@balenciaga',
        'Burberry': 'https://www.tiktok.com/@burberry', 'Versace': 'https://www.tiktok.com/@versace',
        'Saint Laurent': 'https://www.tiktok.com/@ysl', 'Fendi': 'https://www.tiktok.com/@fendi',
        'Givenchy': 'https://www.tiktok.com/@givenchy', 'Celine': 'https://www.tiktok.com/@celine',
        'Jacquemus': 'https://www.tiktok.com/@jacquemus', 'Miu Miu': 'https://www.tiktok.com/@miumiu',
        'Acne Studios': 'https://www.tiktok.com/@acnestudios', 'Ganni': 'https://www.tiktok.com/@ganni',
        'COS': 'https://www.tiktok.com/@cosstores', 'H&M': 'https://www.tiktok.com/@hm',
        'Tommy Hilfiger': 'https://www.tiktok.com/@tommyhilfiger', 'Calvin Klein': 'https://www.tiktok.com/@calvinklein',
        'Diesel': 'https://www.tiktok.com/@diesel', 'Off-White': 'https://www.tiktok.com/@offwhitemilan',
        'Polo Ralph Lauren': 'https://www.tiktok.com/@ralphlauren', 'Moncler': 'https://www.tiktok.com/@moncler',
        'Champion': 'https://www.tiktok.com/@champion', 'Salomon': 'https://www.tiktok.com/@salomon',
        'Stüssy': 'https://www.tiktok.com/@stussy', 'Supreme': 'https://www.tiktok.com/@supremenewyork',
        'Kith': 'https://www.tiktok.com/@kith', 'Fear of God': 'https://www.tiktok.com/@fearofgod',
        'Spanx': 'https://www.tiktok.com/@spanx', 'Vuori': 'https://www.tiktok.com/@vuoriclothing',
        'Bombas': 'https://www.tiktok.com/@bombas', 'Away': 'https://www.tiktok.com/@away',
        'Brandy Melville': 'https://www.tiktok.com/@brandymelvilleusa',
        'Revolve': 'https://www.tiktok.com/@revolve',
    }

    for name, url in tiktok_urls.items():
        cur.execute(
            "UPDATE brands SET tiktok_url=?, updated_at=datetime('now') WHERE (name=? OR name=?) AND (tiktok_url IS NULL OR tiktok_url='')",
            (url, name, name + ' (北美)')
        )
        if cur.rowcount > 0:
            changes += cur.rowcount

    conn.commit()
    conn.close()
    print(f"Startup updates applied: {changes} changes (countries, price_tiers, social URLs)")


# ============================================================
# 品牌去重合并 — 在启动时自动执行
# ============================================================
import re as _re

def _clean_name(name):
    name = _re.sub(r'\s*[（(][^)）]*[)）]\s*$', '', name)
    return name.strip()

def _clean_slug(slug):
    slug = _re.sub(r'-na$', '', slug)
    slug = _re.sub(r'-beimei$', '', slug)
    return slug

def dedup_brands():
    """合并重复品牌：去掉(北美)后缀，合并配对品牌"""
    if not os.path.exists(DB_PATH):
        return

    conn = sqlite3.connect(DB_PATH)
    # 关闭外键约束，避免级联删除问题
    conn.execute("PRAGMA foreign_keys = OFF")
    cur = conn.cursor()

    beihei_count = cur.execute(
        "SELECT COUNT(*) FROM brands WHERE name LIKE '%(北美)%' OR name LIKE '%(北美线)%'"
    ).fetchone()[0]

    if beihei_count == 0:
        conn.close()
        return

    print(f"Found {beihei_count} brands with suffix, deduplicating...")

    paired = cur.execute("""
        SELECT b1.id, b1.name, b2.id, b2.name
        FROM brands b1
        JOIN brands b2 ON REPLACE(REPLACE(b1.name, ' (北美)', ''), ' (北美线)', '') = b2.name
        WHERE b1.name LIKE '%(北美)%'
        ORDER BY b1.name
    """).fetchall()

    merged = 0
    for beihei_id, beihei_name, normal_id, normal_name in paired:
        # 迁移关联数据到normal品牌
        for table, dedup_col in [
            ('competitive_events', 'source_url'),
            ('social_media_metrics', None),
            ('financial_performance', 'fiscal_year'),
            ('customer_sentiment', None),
            ('pricing_strategy', 'category_name'),
        ]:
            try:
                rows = cur.execute(f"SELECT * FROM {table} WHERE brand_id = ?", (beihei_id,)).fetchall()
                if not rows:
                    continue
                cols = [d[0] for d in cur.description]
                if dedup_col == 'source_url':
                    existing = set(r[0] for r in cur.execute(f"SELECT {dedup_col} FROM {table} WHERE brand_id = ?", (normal_id,)).fetchall() if r[0])
                elif dedup_col == 'fiscal_year':
                    existing = set(r[0] for r in cur.execute(f"SELECT {dedup_col} FROM {table} WHERE brand_id = ?", (normal_id,)).fetchall())
                elif dedup_col == 'category_name':
                    existing = set(r[0] for r in cur.execute(f"SELECT {dedup_col} FROM {table} WHERE brand_id = ?", (normal_id,)).fetchall())
                else:
                    existing = set()
                    for r in cur.execute(f"SELECT platform, data_as_of FROM {table} WHERE brand_id = ?", (normal_id,)).fetchall():
                        existing.add((r[0], str(r[1]) if r[1] else ''))

                for row in rows:
                    d = dict(zip(cols, row))
                    if dedup_col == 'source_url':
                        if d.get(dedup_col, '') in existing:
                            continue
                        existing.add(d.get(dedup_col, ''))
                    elif dedup_col in ('fiscal_year', 'category_name'):
                        if d.get(dedup_col) in existing:
                            continue
                        existing.add(d.get(dedup_col))
                    else:
                        combo = (d.get('platform', ''), str(d.get('data_as_of', '') or ''))
                        if combo in existing:
                            continue
                        existing.add(combo)
                    d['brand_id'] = normal_id
                    d.pop('id', None)
                    c = ', '.join(d.keys())
                    p = ', '.join(['?'] * len(d))
                    try:
                        cur.execute(f"INSERT INTO {table} ({c}) VALUES ({p})", list(d.values()))
                    except Exception as e:
                        print(f"  Skip duplicate in {table}: {e}")
            except Exception as e:
                print(f"  Error migrating {table} for {beihei_name}: {e}")

        # 迁移 brand_categories
        try:
            existing_cids = set(r[0] for r in cur.execute("SELECT category_id FROM brand_categories WHERE brand_id = ?", (normal_id,)).fetchall())
            for cat_id, is_primary in cur.execute("SELECT category_id, is_primary FROM brand_categories WHERE brand_id = ?", (beihei_id,)).fetchall():
                if cat_id not in existing_cids:
                    cur.execute("INSERT INTO brand_categories (brand_id, category_id, is_primary) VALUES (?, ?, ?)", (normal_id, cat_id, is_primary))
                    existing_cids.add(cat_id)
        except Exception as e:
            print(f"  Error migrating categories for {beihei_name}: {e}")

        # 删除被合并品牌的所有剩余关联记录
        for table in ['competitive_events', 'social_media_metrics', 'financial_performance',
                       'customer_sentiment', 'pricing_strategy', 'brand_categories',
                       'brand_positioning', 'target_demographics', 'product_strategy',
                       'channel_strategy', 'digital_capability']:
            try:
                cur.execute(f"DELETE FROM {table} WHERE brand_id = ?", (beihei_id,))
            except Exception:
                pass

        # 删除被合并的品牌
        cur.execute("DELETE FROM brands WHERE id = ?", (beihei_id,))
        merged += 1

    # 重命名未配对的(北美)品牌
    unpaired = cur.execute("""
        SELECT id, name, slug FROM brands
        WHERE name LIKE '%(北美)%' OR name LIKE '%(北美线)%'
        ORDER BY name
    """).fetchall()

    renamed = 0
    for bid, name, slug in unpaired:
        new_name = _clean_name(name)
        new_slug = _clean_slug(slug)
        existing = cur.execute("SELECT id FROM brands WHERE slug = ? AND id != ?", (new_slug, bid)).fetchone()
        if existing:
            new_slug = f"{new_slug}-intl"
        cur.execute("UPDATE brands SET name = ?, slug = ?, updated_at = datetime('now') WHERE id = ?", (new_name, new_slug, bid))
        renamed += 1

    conn.commit()
    total = cur.execute("SELECT COUNT(*) FROM brands").fetchone()[0]
    conn.close()
    print(f"Dedup complete: merged {merged} pairs, renamed {renamed} brands, total now {total}")


if __name__ == '__main__':
    try:
        apply_updates()
    except Exception as e:
        print(f"WARNING: apply_updates failed: {e}")
        traceback.print_exc()

    try:
        dedup_brands()
    except Exception as e:
        print(f"WARNING: dedup_brands failed: {e}")
        traceback.print_exc()

    print("Startup script completed, starting uvicorn...")
