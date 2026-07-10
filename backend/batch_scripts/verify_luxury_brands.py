#!/usr/bin/env python3
"""
批量核实品牌数据：搜索 Instagram URL 和最新公开信息
Phase 1: 奢侈品牌
"""
import sqlite3
import json
import re
import time
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

DB = '/workspace/competitive-research-dashboard/backend/data/competitive_research.db'

def get_luxury_brands():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT b.id, b.name, b.slug, b.country, b.founded_year, b.parent_company,
               b.website, b.description, b.headquarters
        FROM brands b
        LEFT JOIN brand_positioning bp ON b.id = bp.brand_id
        WHERE bp.price_tier = 'Luxury'
        ORDER BY b.name
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def search_instagram(brand_name):
    """Search for brand Instagram URL via Google"""
    query = f"{brand_name} official instagram"
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            # Look for instagram.com/BRAND patterns
            matches = re.findall(r'instagram\.com/([a-zA-Z0-9._]+)[/"]', html)
            if matches:
                # Filter out generic pages
                ignore = {'p', 'explore', 'accounts', 'about', 'developer', 'help'}
                for m in matches:
                    if m.lower() not in ignore and len(m) > 1:
                        return f"https://instagram.com/{m}"
    except Exception:
        pass
    return None

def verify_website(url):
    """Check if website is accessible"""
    if not url:
        return None
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return url if resp.status == 200 else None
    except Exception:
        return None

def update_brand(brand_id, updates):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    sets = ', '.join(f"{k}=?" for k in updates.keys())
    values = list(updates.values()) + [brand_id]
    cur.execute(f"UPDATE brands SET {sets} WHERE id=?", values)
    conn.commit()
    conn.close()

def main():
    brands = get_luxury_brands()
    print(f"Found {len(brands)} luxury brands\n")
    
    results = []
    for i, b in enumerate(brands):
        brand_id, name, slug, country, founded, parent, website, desc, hq = b
        clean_name = name.replace(' (北美)', '').replace(' (北美线)', '')
        
        print(f"[{i+1}/{len(brands)}] {clean_name}...")
        
        # Search Instagram
        ig_url = search_instagram(clean_name)
        if ig_url:
            update_brand(brand_id, {'instagram_url': ig_url})
            print(f"  Instagram: {ig_url}")
        
        results.append({
            'id': brand_id,
            'name': clean_name,
            'instagram_url': ig_url,
        })
        
        time.sleep(1.5)  # Rate limit
    
    # Save results
    with open('/tmp/luxury_brand_ig.json', 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    found = sum(1 for r in results if r['instagram_url'])
    print(f"\nDone! Found Instagram for {found}/{len(results)} brands")

if __name__ == '__main__':
    main()
