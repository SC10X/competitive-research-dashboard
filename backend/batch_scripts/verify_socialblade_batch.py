"""
批量 Social Blade 验证脚本 — Instagram + YouTube
逐品牌抓取 Social Blade 页面，提取粉丝数，更新数据库
"""
import sqlite3
import re
import time
import sys
import json
from datetime import date
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

DB_PATH = '/workspace/competitive-research-dashboard/backend/data/competitive_research.db'
TODAY = date.today().isoformat()

def extract_ig_handle(url):
    """从 IG URL 提取 handle"""
    if not url:
        return None
    url = url.rstrip('/')
    parts = url.split('/')
    handle = parts[-1] if parts else ''
    # 清理常见问题
    handle = handle.replace('@', '').strip()
    if not handle or handle in ('instagram.com', 'www.instagram.com'):
        return None
    return handle

def extract_yt_handle(url):
    """从 YouTube URL 提取 handle/channel"""
    if not url:
        return None
    url = url.rstrip('/')
    # youtube.com/@handle 或 youtube.com/channel/xxx 或 youtube.com/user/xxx
    if '/@' in url:
        return url.split('/@')[-1]
    elif '/channel/' in url:
        return url.split('/channel/')[-1]
    elif '/user/' in url:
        return url.split('/user/')[-1]
    elif '/c/' in url:
        return url.split('/c/')[-1]
    return None

def fetch_socialblade_ig(handle):
    """从 Social Blade 抓取 IG 粉丝数"""
    url = f'https://socialblade.com/instagram/user/{handle}'
    try:
        req = Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        with urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        # 查找 followers 数字 — 在页面中有多种格式
        # 格式1: "followers\n\n291,789,858"
        # 格式2: <span>291.7M</span> 
        
        # 尝试多种匹配方式
        patterns = [
            r'followers\s*\n\s*\n\s*([\d,]+)',  # 主要格式
            r'"followersCount":\s*(\d+)',        # JSON
            r'(\d[\d,]*)\s*followers',           # 反向
        ]
        
        for pat in patterns:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                raw = m.group(1).replace(',', '')
                return int(raw)
        
        # 如果都匹配不到，可能是 404
        if 'not found' in html.lower() or '404' in html[:200]:
            return None, 'not_found'
        
        return None, 'parse_failed'
    
    except HTTPError as e:
        if e.code == 404:
            return None, 'not_found'
        return None, f'http_{e.code}'
    except Exception as e:
        return None, f'error: {str(e)[:50]}'

def fetch_socialblade_yt(handle):
    """从 Social Blade 抓取 YouTube 订阅数"""
    url = f'https://socialblade.com/youtube/user/{handle}'
    try:
        req = Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        })
        with urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        patterns = [
            r'subscribers\s*\n\s*\n\s*([\d,]+)',
            r'"subscriberCount":\s*(\d+)',
            r'(\d[\d,]*)\s*subscribers',
        ]
        
        for pat in patterns:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                raw = m.group(1).replace(',', '')
                return int(raw)
        
        if 'not found' in html.lower():
            return None, 'not_found'
        return None, 'parse_failed'
    
    except HTTPError as e:
        if e.code == 404:
            return None, 'not_found'
        return None, f'http_{e.code}'
    except Exception as e:
        return None, f'error: {str(e)[:50]}'

def upsert_metric(conn, brand_id, platform, followers, source_type, source_url):
    """插入或更新社媒数据"""
    cur = conn.cursor()
    
    # 删除同品牌同平台同来源的旧数据
    cur.execute("""
        DELETE FROM social_media_metrics 
        WHERE brand_id = ? AND platform = ? AND source_type = ?
    """, (brand_id, platform, source_type))
    
    # 插入新数据
    cur.execute("""
        INSERT INTO social_media_metrics 
        (brand_id, platform, followers, data_as_of, source_url, source_type)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (brand_id, platform, followers, TODAY, source_url, source_type))
    
    return cur.rowcount

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    cur = conn.cursor()
    
    # === Instagram ===
    print("=" * 60)
    print("INSTAGRAM 验证")
    print("=" * 60)
    
    cur.execute("""
        SELECT DISTINCT b.id, b.name, b.instagram_url
        FROM brands b
        WHERE b.instagram_url IS NOT NULL AND b.instagram_url != ''
        ORDER BY b.name
    """)
    ig_brands = cur.fetchall()
    
    # 去重：同 handle 只抓一次
    seen_handles = {}
    unique_ig = []
    for brand_id, name, url in ig_brands:
        handle = extract_ig_handle(url)
        if handle and handle.lower() not in seen_handles:
            seen_handles[handle.lower()] = True
            unique_ig.append((brand_id, name, url, handle))
    
    print(f"总品牌: {len(ig_brands)}, 唯一 handle: {len(unique_ig)}")
    
    ig_success = 0
    ig_fail = 0
    ig_not_found = 0
    ig_results = []
    
    for i, (brand_id, name, url, handle) in enumerate(unique_ig):
        print(f"[{i+1}/{len(unique_ig)}] {name} (@{handle})", end=' ')
        
        result = fetch_socialblade_ig(handle)
        
        if isinstance(result, tuple):
            # 失败
            err = result[1]
            if 'not_found' in str(err):
                print(f"❌ 未收录")
                ig_not_found += 1
            elif 'http_429' in str(err):
                print(f"⏳ 限流，等待30秒...")
                time.sleep(30)
                result = fetch_socialblade_ig(handle)
                if isinstance(result, int):
                    print(f"✅ {result:,}")
                    ig_success += 1
                    upsert_metric(conn, brand_id, 'Instagram', result, 'socialblade', 
                                 f'https://socialblade.com/instagram/user/{handle}')
                    ig_results.append((name, handle, result))
                else:
                    print(f"❌ 仍然失败")
                    ig_fail += 1
            else:
                print(f"❌ {err}")
                ig_fail += 1
        else:
            followers = result
            print(f"✅ {followers:,}")
            ig_success += 1
            upsert_metric(conn, brand_id, 'Instagram', followers, 'socialblade',
                         f'https://socialblade.com/instagram/user/{handle}')
            ig_results.append((name, handle, followers))
        
        # 限流控制：每5个暂停2秒
        if (i + 1) % 5 == 0:
            time.sleep(2)
        
        # 每50个提交一次
        if (i + 1) % 50 == 0:
            conn.commit()
            print(f"  --- 已提交 [{i+1}], 成功: {ig_success}, 未收录: {ig_not_found}, 失败: {ig_fail} ---")
    
    conn.commit()
    
    # === YouTube ===
    print("\n" + "=" * 60)
    print("YOUTUBE 验证")
    print("=" * 60)
    
    cur.execute("""
        SELECT DISTINCT b.id, b.name, b.youtube_url
        FROM brands b
        WHERE b.youtube_url IS NOT NULL AND b.youtube_url != ''
        ORDER BY b.name
    """)
    yt_brands = cur.fetchall()
    
    seen_yt = {}
    unique_yt = []
    for brand_id, name, url in yt_brands:
        handle = extract_yt_handle(url)
        if handle and handle.lower() not in seen_yt:
            seen_yt[handle.lower()] = True
            unique_yt.append((brand_id, name, url, handle))
    
    print(f"总品牌: {len(yt_brands)}, 唯一 handle: {len(unique_yt)}")
    
    yt_success = 0
    yt_fail = 0
    yt_not_found = 0
    
    for i, (brand_id, name, url, handle) in enumerate(unique_yt):
        print(f"[{i+1}/{len(unique_yt)}] {name} (@{handle})", end=' ')
        
        result = fetch_socialblade_yt(handle)
        
        if isinstance(result, tuple):
            err = result[1]
            if 'not_found' in str(err):
                print(f"❌ 未收录")
                yt_not_found += 1
            else:
                print(f"❌ {err}")
                yt_fail += 1
        else:
            subs = result
            print(f"✅ {subs:,}")
            yt_success += 1
            upsert_metric(conn, brand_id, 'YouTube', subs, 'socialblade',
                         f'https://socialblade.com/youtube/user/{handle}')
        
        if (i + 1) % 5 == 0:
            time.sleep(2)
        
        if (i + 1) % 50 == 0:
            conn.commit()
            print(f"  --- 已提交 [{i+1}], 成功: {yt_success}, 未收录: {yt_not_found}, 失败: {yt_fail} ---")
    
    conn.commit()
    
    # === 汇总 ===
    print("\n" + "=" * 60)
    print("验证完成！")
    print(f"Instagram: 成功 {ig_success}, 未收录 {ig_not_found}, 失败 {ig_fail}")
    print(f"YouTube:   成功 {yt_success}, 未收录 {yt_not_found}, 失败 {yt_fail}")
    
    # 保存详细结果
    with open('/tmp/socialblade_ig_results.json', 'w') as f:
        json.dump([{'name': r[0], 'handle': r[1], 'followers': r[2]} for r in ig_results], f, indent=2)
    
    conn.close()

if __name__ == '__main__':
    main()
