#!/usr/bin/env python3
"""
品牌新闻实时搜索器
使用 Google News RSS 搜索品牌最新动态，返回结构化新闻数据。

用法:
    python3 brand_news_fetcher.py --brands "Nike,Adidas,Lululemon" --max-per-brand 3 --output json
"""

import argparse
import json
import re
import sys
import time
import feedparser
import urllib.parse
from datetime import datetime, date
from typing import Optional

# 关注的关键事件关键词 → 事件类型映射
KEYWORD_TYPE_MAP = [
    (r'\b(IPO|IPO\s+filing|goes?\s+public|files?\s+for\s+IPO|public\s+listing)\b', 'IPO / Funding'),
    (r'\b(acquires?|acquisition|merger|merged|takeover|bought|buyout)\b', 'Acquisition'),
    (r'\b(layoffs?|lay\s+off|job\s+cuts?|downsiz|restructur)\b', 'Layoffs'),
    (r'\b(CEO|CFO|CMO|president|chief\s+\w+\s+officer|appoints?|named|hires?|resign|step\s+down|depart)\b', 'Leadership'),
    (r'\b(earnings|revenue|quarterly\s+results|fiscal|profit|sales\s+grew|sales\s+rose|sales\s+up|sales\s+down)\b', 'Financial Report'),
    (r'\b(collab|partnership|partner|teamed\s+up|tie-up)\b', 'Collaboration'),
    (r'\b(launch|unveil|debut|releases?|introduces?|new\s+collection|new\s+line|new\s+shoe|new\s+sneaker)\b', 'Product Launch'),
    (r'\b(store\s+open|flagship|retail\s+expansion|new\s+location|opens\s+in)\b', 'Store Opening'),
    (r'\b(sustainab|recycl|carbon|ESG|circular|eco-friendly|green)\b', 'Sustainability'),
    (r'\b(expand|expansion|enters?\s+market|international|China|Asia|Europe)\b', 'Market Expansion'),
    (r'\b(campaign|marketing|ad\s+campaign|ambassador|endorsement|celebrity)\b', 'Marketing Campaign'),
    (r'\b(lawsuit|sued|sues|litigation|court|patent|trademark)\b', 'Lawsuit'),
    (r'\b(rebrand|new\s+logo|name\s+change|refresh|overhaul)\b', 'Rebranding'),
    (r'\b(AI|artificial\s+intelligence|digital\s+transformation|app\s+launch|tech\s+platform)\b', 'Digital Innovation'),
    (r'\b(bankruptcy|chapter\s+11|restructuring|debt)\b', 'Acquisition'),
    (r'\b(funding|series\s+[A-D]|raised?\s+\$|valuation|investor|venture)\b', 'IPO / Funding'),
]

IMPORTANCE_KEYWORDS_HIGH = [
    r'\b(IPO|acqui|merger|CEO|billion|bankruptcy|lawsuit|layoff)',
    r'\b(record\s+(revenue|sales|profit|high))',
]
IMPORTANCE_KEYWORDS_LOW = [
    r'\b(new\s+color|new\s+colour|new\s+shade|slight|minor)',
]


def classify_event(title: str, description: str) -> str:
    text = f"{title} {description}".lower()
    for pattern, etype in KEYWORD_TYPE_MAP:
        if re.search(pattern, text, re.IGNORECASE):
            return etype
    return "Product Launch"


def classify_importance(title: str, description: str) -> str:
    text = f"{title} {description}".lower()
    for pattern in IMPORTANCE_KEYWORDS_HIGH:
        if re.search(pattern, text, re.IGNORECASE):
            return "high"
    for pattern in IMPORTANCE_KEYWORDS_LOW:
        if re.search(pattern, text, re.IGNORECASE):
            return "low"
    return "medium"


def extract_date(entry) -> Optional[str]:
    """从 RSS entry 提取日期"""
    for attr in ('published_parsed', 'updated_parsed'):
        tp = getattr(entry, attr, None)
        if tp:
            try:
                return datetime(*tp[:6]).strftime('%Y-%m-%d')
            except Exception:
                pass
    return date.today().strftime('%Y-%m-%d')


def clean_title(title: str, brand_name: str) -> str:
    """清理标题，移除 ' - SourceName' 后缀"""
    # 先清理 HTML 实体
    title = title.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    title = title.replace('&quot;', '"').replace('&#39;', "'").replace('&apos;', "'")
    title = re.sub(r'&[a-z]+;', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    # 移除 RSS 标题中的来源后缀: "Title - SourceName"
    title = re.sub(r'\s*[-–—]\s*[A-Z][a-zA-Z0-9.\s&]+$', '', title.strip())
    # 再次清理可能残留的尾部空白和短横线
    title = title.rstrip(' -–—')
    # 截断过长标题
    if len(title) > 200:
        title = title[:197] + '...'
    return title.strip()


def clean_text(text: str, max_len: int = 500) -> str:
    """通用文本清理：去除 HTML 标签和实体"""
    if not text:
        return ''
    # 去除 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)
    # 去除 HTML 实体
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#39;', "'").replace('&apos;', "'")
    text = re.sub(r'&[a-z]+;', '', text)
    # 压缩空白
    text = re.sub(r'\s+', ' ', text).strip()
    if max_len and len(text) > max_len:
        text = text[:max_len-3] + '...'
    return text


def clean_description(entry, max_len: int = 500) -> str:
    """从 entry 提取并清理描述"""
    desc = getattr(entry, 'summary', '') or getattr(entry, 'description', '') or ''
    return clean_text(desc, max_len)


# 需要过滤的无关新闻关键词（对品牌建设无借鉴意义）
IRRELEVANT_KEYWORDS = [
    r'\bstolen\b', r'\btheft\b', r'\brobbed\b', r'\barrest(ed)?\b',
    r'\bfactory\s+location', r'\bfactories\s+are\s+located',
    r'\bstock\s+price\b', r'\bshares\s+(fall|rise|drop|up|down)\b',
    r'\bcoupon\b', r'\bdiscount\s+code\b', r'\bpromo\s+code\b',
    r'\bhow\s+to\s+(buy|get|find|spot)\b', r'\bwhere\s+to\s+buy\b',
    r'\bclearance\b', r'\boutlet\s+sale\b',
    r'\bdied\b', r'\bobituary\b', r'\bdeath\b', r'\bpassed\s+away\b',
    r'\bfuneral\b', r'\bmemorial\b', r'\brip\b',
    r'\bcruise\b', r'\briver\s+cruise\b', r'\bvineyard\b',
    r'\belection\b', r'\bpoll\b', r'\bcampaign\b', r'\bdemocrat\b', r'\brepublican\b',
    r'\bsenator\b', r'\bcongress\b', r'\bpolitic\b', r'\bgovernor\b',
    r'\bminimum\s+import\b', r'\btariff\b', r'\btrade\s+war\b',
]

# 品牌名相关的正面关键词（标题必须包含其中之一才算真正相关）
BUSINESS_KEYWORDS = [
    r'\b(launch|unveil|debut|releases?|introduces?|drops?|rolls?\s+out)\b',
    r'\b(collection|capsule|collab|partnership|limited\s+edition)\b',
    r'\b(earnings|revenue|sales|profit|quarterly|fiscal|growth)\b',
    r'\b(store|flagship|retail|expansion|opens?|opening)\b',
    r'\b(CEO|CFO|CMO|president|appoints?|hires?|named)\b',
    r'\b(sustainab|ESG|recycl|circular|eco|green|carbon)\b',
    r'\b(campaign|marketing|ambassador|endorsement)\b',
    r'\b(AI|tech|digital|app|platform|innovation)\b',
    r'\b(IPO|funding|acqui|merger|invest|valuation)\b',
    r'\b(lawsuit|sues?|sued|bankruptcy|restructuring)\b',
    r'\b(rebrand|logo|refresh|overhaul|redesign)\b',
    r'\b(sale|discount|deal|price|clearance)\b',
    r'\b(review|best|top|ranking|rated|comparison)\b',
]


def is_relevant(title: str, description: str, brand_name: str = "") -> bool:
    """判断新闻是否对品牌建设有借鉴意义"""
    text = f"{title} {description}".lower()
    brand_lower = brand_name.lower().strip()
    
    # 1. 过滤明显无关的
    for pattern in IRRELEVANT_KEYWORDS:
        if re.search(pattern, text, re.IGNORECASE):
            return False
    
    # 2. 品牌名必须在标题中（核心检查）
    brand_words = brand_lower.split()
    # 取前两个词作为品牌核心
    brand_core = ' '.join(brand_words[:2])
    if len(brand_core) < 3 and len(brand_words) > 2:
        brand_core = ' '.join(brand_words[:3])
    
    title_lower = title.lower()
    if brand_core not in title_lower:
        # 对于短品牌名（如On, Gap），检查每个独立词
        found = False
        for w in brand_words:
            if len(w) >= 3 and w in title_lower:
                found = True
                break
        if not found:
            return False
    
    # 3. 标题必须包含至少一个商业关键词（确保是品牌动态而非一般提及）
    has_biz_keyword = any(re.search(p, text, re.IGNORECASE) for p in BUSINESS_KEYWORDS)
    if not has_biz_keyword:
        return False
    
    return True


def extract_source_name(entry, url: str) -> str:
    """提取来源名称"""
    source = getattr(entry, 'source', None)
    if source and getattr(source, 'title', None):
        return source.title
    # 从 URL 提取域名
    try:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        return domain.split('.')[0].capitalize()
    except Exception:
        return 'News'


def extract_source_quote(entry) -> str:
    """从 RSS entry 提取引用内容。
    Google News RSS 的 summary 只包含标题链接没有正文，
    因此用 cleaned title 作为关键引用。
    """
    title = entry.get('title', '')
    title = clean_title(title, '')
    return title[:300]


def search_brand(brand_name: str, max_results: int = 5) -> list:
    """搜索单个品牌的最新新闻"""
    # 对短品牌名/易歧义品牌用更精确的搜索词
    brand_clean = brand_name.strip()
    ambiguous_brands = {
        'Columbia': 'sportswear outdoor apparel',
        'Gap': 'clothing brand retail',
        'On': 'running shoes sportswear',
        'On Running': 'running shoes sportswear',
        'Theory': 'fashion brand clothing',
        'Free People': 'clothing brand',
        'Good American': 'denim clothing brand',
        'Outdoor Voices': 'activewear brand',
        'Satisfy Running': 'running apparel',
        'Ten Thousand': 'activewear brand',
        'District Vision': 'sportswear brand',
        'Rhone': 'menswear clothing brand',
        'Merrell': 'footwear outdoor',
        'American Eagle': 'clothing brand retail',
        'Away': 'luggage travel brand',
        'Reformation': 'clothing brand sustainable',
        'Allbirds': 'footwear brand',
        'Everlane': 'clothing brand',
        'Bombas': 'sock brand',
        'Birddogs': 'shorts brand',
        'Cotopaxi': 'outdoor gear brand',
        'Peak Design': 'camera bag brand',
        'Lo & Sons': 'bag brand',
        'Lo and Sons': 'bag brand',
        'Dagne Dover': 'bag brand',
        'Herschel': 'backpack brand',
        'JanSport': 'backpack brand',
        'Osprey': 'backpack brand',
        'Tumi': 'luggage brand',
        'Béis': 'luggage brand',
        'Beis': 'luggage brand',
    }
    
    if brand_clean in ambiguous_brands:
        extra = ambiguous_brands[brand_clean]
        query = urllib.parse.quote(f'"{brand_clean}" {extra}')
    elif len(brand_clean.split()) == 1 and len(brand_clean) <= 3:
        query = urllib.parse.quote(f'"{brand_clean}" brand clothing')
    else:
        query = urllib.parse.quote(f'"{brand_clean}"')
    
    url = f'https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en&sort=date'
    
    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print(f'  ⚠️ RSS解析失败 ({brand_name}): {e}', file=sys.stderr)
        return []
    
    if feed.get('status') != 200 and not feed.entries:
        return []
    
    results = []
    seen_urls = set()
    brand_lower = brand_name.lower()
    
    for entry in feed.entries:
        link = entry.get('link', '')
        # 去重
        if link in seen_urls:
            continue
        seen_urls.add(link)
        
        raw_title = entry.get('title', '')
        title = clean_title(raw_title, brand_name)
        description = clean_description(entry)
        event_date = extract_date(entry)
        source_quote_en = extract_source_quote(entry)
        
        # 跳过太短的标题
        if len(title) < 15:
            continue
        
        # 品牌名必须出现在标题中（确保相关性）
        if brand_lower not in title.lower():
            continue
        
        # 过滤无关新闻
        if not is_relevant(title, description, brand_name):
            continue
        
        results.append({
            'brand_name': brand_name,
            'title': title,
            'description': description,
            'event_date': event_date,
            'source_url': link,
            'source_name': extract_source_name(entry, link),
            'source_quote': source_quote_en,
            'event_type': classify_event(title, description),
            'importance': classify_importance(title, description),
        })
        
        if len(results) >= max_results:
            break
    
    return results


def translate_results(results: list) -> list:
    """将搜索结果的标题、描述和引用翻译为中文"""
    if not results:
        return results
    
    from deep_translator import GoogleTranslator
    
    try:
        translator = GoogleTranslator(source='en', target='zh-CN')
    except Exception:
        return results
    
    for r in results:
        brand_name = r.get('brand_name', '')
        
        # 翻译标题（保护品牌名不被翻译）
        title_en = r.get('title', '')
        if title_en.strip():
            try:
                title_zh = _translate_preserving_brands(translator, title_en, brand_name)
                r['title_zh'] = clean_translated_text(title_zh)
            except Exception:
                r['title_zh'] = title_en
        else:
            r['title_zh'] = title_en
        
        # 翻译描述
        desc_en = r.get('description', '')
        if desc_en.strip():
            try:
                desc_zh = _translate_preserving_brands(translator, desc_en[:300], brand_name)
                r['description_zh'] = clean_translated_text(desc_zh)
            except Exception:
                r['description_zh'] = desc_en
        else:
            r['description_zh'] = desc_en
        
        # 翻译引用
        quote_en = r.get('source_quote', '')
        if quote_en.strip():
            try:
                quote_zh = _translate_preserving_brands(translator, quote_en, brand_name)
                r['source_quote_zh'] = clean_translated_text(quote_zh)
            except Exception:
                r['source_quote_zh'] = quote_en
        else:
            r['source_quote_zh'] = quote_en
        
        time.sleep(0.15)
    
    return results


def _translate_preserving_brands(translator, text: str, brand_name: str) -> str:
    """翻译文本，但保护品牌名不被翻译"""
    # 用占位符替换品牌名
    placeholder = f"__BRAND__"
    text_with_placeholder = text
    
    # 对于复合品牌名（如 "Sweaty Betty"），逐词替换
    brand_words = brand_name.split()
    if len(brand_words) > 1:
        for i, word in enumerate(brand_words):
            if len(word) > 1:
                ph = f"__BW{i}__"
                text_with_placeholder = re.sub(
                    r'\b' + re.escape(word) + r'\b',
                    ph,
                    text_with_placeholder,
                    flags=re.IGNORECASE
                )
        # 也替换完整品牌名
        text_with_placeholder = re.sub(
            r'\b' + re.escape(brand_name) + r'\b',
            placeholder,
            text_with_placeholder,
            flags=re.IGNORECASE
        )
    else:
        text_with_placeholder = re.sub(
            r'\b' + re.escape(brand_name) + r'\b',
            placeholder,
            text_with_placeholder,
            flags=re.IGNORECASE
        )
    
    # 翻译
    translated = translator.translate(text_with_placeholder)
    
    # 还原品牌名
    if len(brand_words) > 1:
        for i, word in enumerate(brand_words):
            ph = f"__BW{i}__"
            translated = translated.replace(ph, word)
        translated = translated.replace(placeholder, brand_name)
    else:
        translated = translated.replace(placeholder, brand_name)
    
    return translated


def clean_translated_text(text: str) -> str:
    """清理翻译后的文本，让表达更自然"""
    if not text:
        return text
    
    # 去除 HTML 实体
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
    text = text.replace('&lt;', '<').replace('&gt;', '>')
    text = re.sub(r'&[a-z]+;', '', text)
    
    # 移除末尾来源后缀
    text = re.sub(r'\s*[-–—]\s*.+$', '', text.strip())
    text = re.sub(r'\s*\|\s*.+$', '', text.strip())
    
    # 移除末尾多余的公司名/网站名
    text = re.sub(r'\s+(Yahoo|CNN|WWD|Reuters|Bloomberg|Inc\.?|Rolling\s+Stone|Business\s+of\s+Fashion|Forbes|WSJ|华尔街日报|路透社?|雅虎|彭博社?)(\s+.+)?$', '', text.strip(), flags=re.IGNORECASE)
    
    # 修正不自然的翻译
    # "XX 运动鞋将篮球鞋带入未来" → 更自然的表达
    text = re.sub(r'将(.+?)带入未来', r'引领\1的未来', text)
    text = re.sub(r'推出(.+?)系列', r'推出\1系列', text)
    text = re.sub(r'发布(.+?)系列', r'发布\1系列', text)
    
    # 压缩空白
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def search_brands(brand_names: list, max_per_brand: int = 3, delay: float = 0.5) -> list:
    """批量搜索多个品牌，并翻译为中文"""
    all_results = []
    for i, name in enumerate(brand_names):
        try:
            results = search_brand(name, max_per_brand)
            all_results.extend(results)
            print(f'  ✅ {name}: {len(results)} 条', file=sys.stderr)
        except Exception as e:
            print(f'  ❌ {name}: {e}', file=sys.stderr)
        
        if i < len(brand_names) - 1:
            time.sleep(delay)
    
    # 翻译为中文
    if all_results:
        print(f'🌐 翻译 {len(all_results)} 条新闻为中文...', file=sys.stderr)
        all_results = translate_results(all_results)
    
    return all_results


def main():
    parser = argparse.ArgumentParser(description='品牌新闻实时搜索')
    parser.add_argument('--brands', type=str, required=True, help='逗号分隔的品牌名列表')
    parser.add_argument('--max-per-brand', type=int, default=3, help='每个品牌最大新闻数')
    parser.add_argument('--output', choices=['json', 'text'], default='json')
    args = parser.parse_args()
    
    brand_names = [b.strip() for b in args.brands.split(',') if b.strip()]
    if not brand_names:
        print(json.dumps([]))
        return
    
    print(f'🔍 搜索 {len(brand_names)} 个品牌...', file=sys.stderr)
    results = search_brands(brand_names, args.max_per_brand)
    
    if args.output == 'json':
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"\n🏷 {r['brand_name']} | {r['event_type']} | {r['importance']}")
            print(f"   {r['title']}")
            print(f"   📅 {r['event_date']} | 📰 {r['source_name']}")
            print(f"   {r['source_url']}")
            print(f"   💬 {r['source_quote'][:100]}")


if __name__ == '__main__':
    main()
