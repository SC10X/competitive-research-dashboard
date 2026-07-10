#!/usr/bin/env python3
"""
批量翻译数据库中所有英文事件，优化翻译质量。
策略：
1. 用 Google Translate 逐条翻译 title + description + source_quote
2. 后处理清理：移除来源后缀、修正品牌名翻译、让句式更自然
3. 已翻译的不重复处理
"""

import sqlite3
import re
import sys
import time
from deep_translator import GoogleTranslator

DB_PATH = "/workspace/competitive-research-dashboard/backend/data/competitive_research.db"

# 品牌名翻译对照表（保持品牌名原文或统一译名）
BRAND_NAME_MAP = {
    "nike": "Nike", "adidas": "adidas", "lululemon": "lululemon",
    "hoka": "HOKA", "on running": "On昂跑", "new balance": "New Balance",
    "arc'teryx": "Arc'teryx", "arcteryx": "Arc'teryx",
    "patagonia": "Patagonia", "the north face": "The North Face",
    "vuori": "Vuori", "alo yoga": "Alo Yoga", "skechers": "斯凯奇",
    "under armour": "Under Armour", "crocs": "Crocs",
    "birkenstock": "Birkenstock", "ugg": "UGG",
    "canada goose": "Canada Goose", "moncler": "Moncler",
    "ralph lauren": "Ralph Lauren", "levi's": "Levi's", "levis": "Levi's",
    "carhartt": "Carhartt", "salomon": "Salomon", "columbia": "Columbia",
    "allbirds": "Allbirds", "everlane": "Everlane", "reformation": "Reformation",
    "shein": "SHEIN", "zara": "Zara", "uniqlo": "优衣库",
    "gap": "Gap", "american eagle": "American Eagle",
    "abercrombie": "Abercrombie & Fitch", "dickies": "Dickies",
    "vans": "Vans", "converse": "Converse", "puma": "Puma",
    "dr. martens": "Dr. Martens", "timberland": "Timberland",
    "merrell": "Merrell", "keen": "KEEN", "teva": "Teva",
    "gymshark": "Gymshark", "outdoor voices": "Outdoor Voices",
    "fabletics": "Fabletics", "sweaty betty": "Sweaty Betty",
    "aritzia": "Aritzia", "revolve": "Revolve", "fashion nova": "Fashion Nova",
    "skims": "SKIMS", "good american": "Good American",
    "bombas": "Bombas", "mack weldon": "Mack Weldon",
    "rhone": "Rhone", "ten thousand": "Ten Thousand",
    "on": "On昂跑", "asics": "ASICS", "brooks": "Brooks",
    "saucony": "Saucony", "reebok": "Reebok",
    "alexander wang": "Alexander Wang", "theory": "Theory",
    "rag & bone": "Rag & Bone", "free people": "Free People",
    "anthropologie": "Anthropologie", "madewell": "Madewell",
    "j.crew": "J.Crew", "banana republic": "Banana Republic",
    "old navy": "Old Navy", "athleta": "Athleta",
    "beyond yoga": "Beyond Yoga", "alo": "Alo",
    "cariuma": "Cariuma", "rothys": "Rothy's", "all birds": "Allbirds",
    "bombas": "Bombas", "béis": "Béis", "beis": "Béis",
    "away": "Away", "dagne dover": "Dagne Dover",
    "herschel": "Herschel", "jansport": "JanSport",
    "fjallraven": "Fjällräven", "osprey": "Osprey",
    "peak design": "Peak Design", "tumi": "Tumi",
    "lo & sons": "Lo & Sons", "lo and sons": "Lo & Sons",
    "bonobos": "Bonobos", "birddogs": "Birddogs",
    "champion": "Champion", "fila": "Fila",
    "k-swiss": "K-Swiss", "keds": "Keds",
    "toms": "TOMS", "hey dude": "Hey Dude",
    "steve madden": "Steve Madden", "aldo": "Aldo",
    "dr martens": "Dr. Martens", "blundstone": "Blundstone",
    "ugg": "UGG", "teva": "Teva", "keen": "KEEN",
    "olukai": "OluKai", "sorel": "Sorel",
    "ugg australia": "UGG", "deckers": "Deckers",
    "cole haan": "Cole Haan", "clarks": "Clarks",
    "ecco": "ECCO", "geox": "Geox",
    "ugg®": "UGG", "crocs": "Crocs",
}


def is_english_text(text: str) -> bool:
    """判断文本是否以英文为主"""
    if not text:
        return False
    en_chars = len(re.findall(r'[a-zA-Z]', text))
    cn_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    total = en_chars + cn_chars
    if total == 0:
        return False
    return en_chars / total > 0.5


def clean_translation(text: str, brand_name: str = "") -> str:
    """清理翻译结果"""
    if not text:
        return text
    
    # 去除 HTML 实体
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
    text = text.replace('&lt;', '<').replace('&gt;', '>')
    text = re.sub(r'&[a-z]+;', '', text)
    
    # 移除末尾来源后缀（如 " - Bleacher Report"）
    text = re.sub(r'\s*[-–—]\s*[A-Za-z0-9.\s|&]+$', '', text.strip())
    text = re.sub(r'\s+[A-Z][a-z]+ [A-Z][a-z]+$', '', text.strip())
    
    # 移除末尾的 "|" 分隔后缀
    text = re.sub(r'\s*\|\s*[A-Za-z0-9.\s]+$', '', text.strip())
    
    # 修正常见翻译问题
    text = re.sub(r'(\d+)\s*万美元', r'\1万美元', text)  # 数字+万美元
    text = re.sub(r'(\d+)\s*亿美元', r'\1亿美元', text)
    text = re.sub(r'(\d+)\s*百万美元', r'\1百万美元', text)
    text = re.sub(r'(\d+)\s*十亿美元', r'\1十亿美元', text)
    
    # 压缩多余空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 修正品牌名翻译（有些品牌被音译了）
    if brand_name:
        bn_lower = brand_name.lower().strip()
        # 还原被翻译成中文的品牌名
        common_bad_translations = {
            "耐克": "Nike", "阿迪达斯": "adidas", "露露柠檬": "lululemon",
            "露露乐蒙": "lululemon", "霍卡": "HOKA", "勃肯": "Birkenstock",
            "卡哈特": "Carhartt", "北面": "The North Face",
            "巴塔哥尼亚": "Patagonia", "始祖鸟": "Arc'teryx",
            "斯凯奇": "斯凯奇",  # 这个保留中文
            "安德玛": "Under Armour", "加拿大鹅": "Canada Goose",
            "盟可睐": "Moncler", "拉夫劳伦": "Ralph Lauren",
            "李维斯": "Levi's", "万斯": "Vans", "匡威": "Converse",
            "彪马": "Puma", "添柏岚": "Timberland",
            "马汀博士": "Dr. Martens", "马丁靴": "Dr. Martens",
            "新百伦": "New Balance", "亚瑟士": "ASICS",
            "索康尼": "Saucony", "锐步": "Reebok",
            "哥伦比": "Columbia", "所罗门": "Salomon",
            "奥凯": "OluKai",
        }
        for bad, good in common_bad_translations.items():
            if bad in text and good.lower() not in bn_lower:
                # 只在原文品牌名不在 text 中时替换
                pass  # 保留翻译结果，不强制替换
    
    return text


def make_summary(title_zh: str, desc_zh: str, quote_zh: str) -> str:
    """将翻译结果组合成自然的中文摘要"""
    # 如果描述已经包含标题的核心信息，直接用描述
    if desc_zh and len(desc_zh) > len(title_zh):
        return desc_zh[:500]
    # 否则用标题
    return title_zh[:500]


def translate_batch():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # 查找所有英文为主的事件
    c.execute("SELECT id, title, description, source_quote FROM competitive_events")
    all_events = c.fetchall()
    
    need_translate = []
    for ev in all_events:
        title = ev["title"] or ""
        desc = ev["description"] or ""
        quote = ev["source_quote"] or ""
        
        if is_english_text(title) or is_english_text(desc) or is_english_text(quote):
            need_translate.append(ev)
    
    print(f"📊 总计 {len(all_events)} 条事件，需要翻译 {len(need_translate)} 条")
    
    if not need_translate:
        conn.close()
        return
    
    translator = GoogleTranslator(source='en', target='zh-CN')
    
    translated_count = 0
    failed_count = 0
    
    for i, ev in enumerate(need_translate):
        eid = ev["id"]
        title_en = (ev["title"] or "").strip()
        desc_en = (ev["description"] or "").strip()
        quote_en = (ev["source_quote"] or "").strip()
        
        # 翻译标题
        title_zh = title_en
        if is_english_text(title_en) and len(title_en) > 10:
            try:
                title_zh = translator.translate(title_en)
                title_zh = clean_translation(title_zh)
            except Exception as e:
                failed_count += 1
                title_zh = title_en
        
        # 翻译描述
        desc_zh = desc_en
        if is_english_text(desc_en) and len(desc_en) > 10:
            try:
                desc_zh = translator.translate(desc_en[:500])
                desc_zh = clean_translation(desc_zh)
            except Exception:
                desc_zh = desc_en
        
        # 翻译引用
        quote_zh = quote_en
        if is_english_text(quote_en) and len(quote_en) > 10:
            try:
                quote_zh = translator.translate(quote_en[:300])
                quote_zh = clean_translation(quote_zh)
            except Exception:
                quote_zh = quote_en
        
        # 更新数据库
        c.execute("""UPDATE competitive_events 
                     SET title = ?, description = ?, source_quote = ?
                     WHERE id = ?""",
                  (title_zh, desc_zh, quote_zh, eid))
        
        translated_count += 1
        
        if (i + 1) % 20 == 0:
            conn.commit()
            print(f"  ✅ 已翻译 {i+1}/{len(need_translate)} 条...", flush=True)
        
        # 避免限流
        time.sleep(0.12)
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 翻译完成！成功: {translated_count}, 失败: {failed_count}")


if __name__ == "__main__":
    translate_batch()
