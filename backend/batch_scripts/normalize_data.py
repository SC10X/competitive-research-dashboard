#!/usr/bin/env python3
"""
一次性标准化所有品牌数据：
1. 国家名称标准化
2. 扩展短描述
3. 添加 Twitter/TikTok 链接
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "competitive_research.db"

# ============================================================
# 国家名称标准化映射
# ============================================================
COUNTRY_MAP = {
    # 美国
    '美国': '美国',
    '美国(北美)': '美国',
    'United States': '美国',
    'USA': '美国',
    '美国(欧洲设计)': '美国',
    '美国(日本授权)': '美国',
    '美国(美国HQ)': '美国',  # will be handled below
    # 英国
    '英国': '英国',
    '英国(北美)': '英国',
    '英国(美国HQ)': '英国',
    '英国/美国': '英国',
    'UK': '英国',
    # 法国
    '法国': '法国',
    '法国(北美)': '法国',
    'France': '法国',
    '法国(美国Deckers)': '法国',
    # 意大利
    '意大利': '意大利',
    '意大利(北美)': '意大利',
    'Italy': '意大利',
    '意大利/美国': '意大利',
    '意大利(韩国总部)': '意大利',
    # 加拿大
    '加拿大': '加拿大',
    'Canada': '加拿大',
    '加拿大(北美)': '加拿大',
    '加拿大/美国': '加拿大',
    # 瑞典
    '瑞典': '瑞典',
    '瑞典(北美)': '瑞典',
    # 澳大利亚
    '澳大利亚': '澳大利亚',
    '澳大利亚(北美)': '澳大利亚',
    '澳大利亚/美国': '澳大利亚',
    '澳大利亚/美国(北美)': '澳大利亚',
    # 日本
    '日本(北美)': '日本',
    # 丹麦
    '丹麦': '丹麦',
    '丹麦(北美)': '丹麦',
    'Denmark': '丹麦',
    '丹麦/美国(北美)': '丹麦',
    # 瑞士
    '瑞士': '瑞士',
    '瑞士(北美)': '瑞士',
    'Switzerland': '瑞士',
    # 德国
    '德国': '德国',
    '德国(北美)': '德国',
    'Germany': '德国',
    # 西班牙
    '西班牙(北美)': '西班牙',
    'Spain': '西班牙',
    # 挪威
    '挪威': '挪威',
    # 新西兰
    '新西兰(北美)': '新西兰',
    # 巴西
    '巴西(北美)': '巴西',
    # 南非
    '南非/美国': '南非',
    # 奥地利
    '奥地利/美国': '奥地利',
    '奥地利/美国(北美)': '奥地利',
    # 中国
    '中国/美国': '中国',
    # 尼泊尔
    '尼泊尔/美国': '尼泊尔',
    # 匈牙利
    '匈牙利': '匈牙利',
    # 韩国
    '美国/韩国': '韩国',
    '美国/德国': '美国',
}

# ============================================================
# 短描述扩展（<50字符的47个品牌）
# ============================================================
DESC_EXTENSIONS = {
    'A.P.C.': '法国简约时尚品牌，由Jean Touitou于1987年创立，以经典丹宁、极简设计和高品质面料著称，深受巴黎文艺青年和极简主义者喜爱。',
    'Acne Studios': '瑞典斯德哥尔摩的时尚品牌，以创意剪裁、大胆色彩和前卫设计闻名，涵盖男女成衣、鞋履和配饰，是北欧时尚的代表性力量。',
    'Ami Paris': '法国设计师Alexandre Mattiussi创立的巴黎品牌，以轻松优雅的男装和"AMI"爱心Logo闻名，融合法式精致与都市休闲。',
    'Ann Demeulemeester': '比利时先锋设计师品牌，以暗黑浪漫主义、不对称剪裁和诗意美学著称，是安特卫普六君子中最具代表性的品牌之一。',
    'Balmain': '法国奢侈时装屋，由Pierre Balmain于1945年创立，以华丽刺绣、军装风剪裁和强势女性形象闻名，是巴黎高级定制的代表。',
    'Bode': '美国男装品牌，设计师Emily Bode以复古面料、手工缝制和怀旧叙事著称，将古董布料与当代设计完美融合。',
    'Brandy Melville': '意大利快时尚品牌，以"均码"策略、加州少女风格和社交媒体营销闻名，深受全球年轻女性消费者追捧。',
    'Brunello Cucinelli': '意大利奢侈羊绒品牌，以顶级面料、人文哲学和"人文资本主义"理念闻名，被誉为"羊绒之王"。',
    'Celine': '法国奢侈品牌，由Céline Vipiana于1945年创立，现属LVMH集团，以极简优雅的成衣和标志性手袋闻名全球。',
    'Champion': '美国经典运动服饰品牌，创立于1919年，以卫衣和Reverse Weave技术闻名，从运动场走向街头潮流的代表。',
    'Chloé': '法国奢侈时装屋，由Gaby Aghion于1952年创立，以浪漫柔美的女性气质和标志性手袋系列闻名，是巴黎左岸风格的代表。',
    'Christopher Esber': '澳大利亚设计师品牌，以精准剪裁、雕塑感设计和解构美学闻名，是澳大利亚时尚界最具国际影响力的新锐品牌之一。',
    'Comme des Garçons': '日本前卫时尚品牌，由川久保玲于1969年创立，以解构主义、不对称设计和黑色美学颠覆时尚界。',
    'Coperni': '法国新锐品牌，由Sébastien Meyer和Arnaud Vaillant创立，以科技感设计、3D打印和喷漆连衣裙闻名。',
    'COS': 'H&M集团旗下的高端极简品牌，以建筑感剪裁、优质面料和永续设计理念著称，是北欧极简美学的代表。',
    'Dion Lee': '澳大利亚设计师品牌，以建筑感剪裁、解构西装和实验性设计闻名，将工业美学与女性气质完美融合。',
    'Dries Van Noten': '比利时设计师品牌，安特卫普六君子之一，以繁复印花、色彩碰撞和艺术感设计闻名全球。',
    'Eckhaus Latta': '美国先锋品牌，由Mike Eckhaus和Zoe Latta创立，以实验性针织、非传统剪裁和多元性别表达著称。',
    'Eileen Fisher': '美国可持续女装品牌，以简约舒适、环保面料和循环时尚理念闻名，是可持续时尚的先驱。',
    'Fendi': '意大利奢侈品牌，由Adele和Edoardo Fendi于1925年创立，以皮草工艺、Baguette手袋和双F Logo闻名，现属LVMH集团。',
    'Filippa K': '瑞典极简品牌，由Filippa Knutsson于1993年创立，以经典剪裁、中性色调和可持续理念闻名，是北欧风格的代表。',
    'Frame': '美国洛杉矶品牌，由瑞典设计师创立，以高端牛仔、简约衬衫和当代女装闻名，融合加州轻松与欧洲精致。',
    'Ganni': '丹麦哥本哈根品牌，以俏皮印花、女性化剪裁和可持续发展的"负责任奢侈"理念闻名，是北欧It-girl风格的代表。',
    'Givenchy': '法国奢侈时装屋，由Hubert de Givenchy于1952年创立，以优雅高级定制和Audrey Hepburn的经典造型闻名，现属LVMH集团。',
    'Helmut Lang': '奥地利设计师品牌，以极简主义、解构剪裁和前卫设计闻名，是90年代时装革命的标志性力量。',
    'Isabel Marant': '法国设计师品牌，以波西米亚风格、轻松巴黎气质和标志性坡跟运动鞋闻名，完美融合法式优雅与都市休闲。',
    'Jacquemus': '法国设计师品牌，由Simon Porte Jacquemus创立，以南法风情、不对称设计和超迷你手袋闻名，是社交媒体时代最成功的独立品牌之一。',
    'JW Anderson': '英国设计师品牌，由Jonathan Anderson创立，以性别流动设计、实验性剪裁和艺术跨界闻名，同时也是Loewe创意总监。',
    'Khaite': '美国纽约设计师品牌，由Catherine Holstein创立，以奢华面料、雕塑感剪裁和现代女性气质闻名，是CFDA年度女装设计师品牌。',
    'Lanvin': '法国最古老的时装屋，由Jeanne Lanvin于1889年创立，以优雅女性气质和母女装设计闻名，是巴黎高级定制的传奇。',
    'Loewe': '西班牙奢侈皮具品牌，创立于1846年，现由Jonathan Anderson执掌创意，以Puzzle手袋和工艺创新闻名，属LVMH集团。',
    'Maje': '法国巴黎女装品牌，SMCP集团旗下，以巴黎风格、精致印花和现代女性气质闻名，深受都市女性喜爱。',
    'Margaret Howell': '英国设计师品牌，以经典英伦风格、高品质面料和永续设计理念闻名，是英国当代设计的代表。',
    'Marine Serre': '法国新锐设计师品牌，以新月Logo、升级再造面料和未来主义设计闻名，是可持续时尚的先锋力量。',
    'Miu Miu': 'Prada集团旗下品牌，由Miuccia Prada于1993年创立，以叛逆少女风格、实验性设计和当代艺术跨界闻名。',
    'Mugler': '法国设计师品牌，由Thierry Mugler创立，以戏剧化剪裁、强势女性形象和标志性香水闻名，现由Casey Cadwallader执掌。',
    'Nanushka': '匈牙利布达佩斯品牌，由Sandra Sandor创立，以纯素皮革、现代波西米亚和可持续设计闻名，是东欧时尚的代表。',
    'Our Legacy': '瑞典斯德哥尔摩男装品牌，以解构经典、升级再造和北欧极简美学闻名，是当代男装文化的代表。',
    'Polo Ralph Lauren': '美国经典品牌，由Ralph Lauren于1967年创立，以马球Logo、常春藤风格和美式生活方式闻名，是美国时尚的象征。',
    'Proenza Schouler': '美国纽约设计师品牌，由Jack McCollough和Lazaro Hernandez创立，以PS1手袋和当代艺术灵感闻名。',
    'Sacai': '日本设计师品牌，由阿部千登势创立，以混搭拼接、实验性剪裁和Nike联名系列闻名全球。',
    'Salomon': '法国户外运动品牌，创立于1947年，以越野跑鞋、滑雪装备和Gorpcore潮流闻名，是功能性与时尚的完美结合。',
    'Sandy Liang': '美国华裔设计师品牌，以少女风格、复古元素和纽约下东区美学闻名，融合怀旧与当代设计。',
    'Simone Rocha': '爱尔兰设计师品牌，以浪漫珍珠装饰、维多利亚风格和女性气质设计闻名，是伦敦时装周的代表性力量。',
    'Staud': '美国洛杉矶品牌，由Sarah Staudinger创立，以复古现代融合、色彩丰富和标志性水桶包闻名，是Instagram时代的It-brand。',
    'Toteme': '瑞典斯德哥尔摩品牌，以极简奢华、精准剪裁和胶囊衣橱理念闻名，是北欧现代女性的衣橱首选。',
}

# ============================================================
# Twitter/X 链接（知名品牌，使用已知 handle）
# ============================================================
TWITTER_URLS = {
    'Nike': 'https://x.com/Nike',
    'Adidas': 'https://x.com/adidas',
    'Lululemon': 'https://x.com/lululemon',
    'Hoka': 'https://x.com/HOKA',
    'On Running': 'https://x.com/on_running',
    'New Balance': 'https://x.com/newbalance',
    "Arc'teryx": 'https://x.com/Arcteryx',
    'Patagonia': 'https://x.com/patagonia',
    'The North Face': 'https://x.com/thenorthface',
    'Vuori': 'https://x.com/vuoriclothing',
    'Alo Yoga': 'https://x.com/aloyoga',
    'Skechers': 'https://x.com/SKECHERS',
    'Under Armour': 'https://x.com/UnderArmour',
    'Crocs': 'https://x.com/Crocs',
    'Birkenstock': 'https://x.com/Birkenstock',
    'UGG': 'https://x.com/UGG',
    'Canada Goose': 'https://x.com/canadagooseinc',
    'Moncler': 'https://x.com/moncler',
    'Ralph Lauren': 'https://x.com/ralphlauren',
    "Levi's": 'https://x.com/LEVIS',
    'Carhartt': 'https://x.com/Carhartt',
    'Salomon': 'https://x.com/SalomonSports',
    'Columbia': 'https://x.com/Columbia1938',
    'Allbirds': 'https://x.com/Allbirds',
    'Everlane': 'https://x.com/Everlane',
    'Reformation': 'https://x.com/reformation',
    'Shein': 'https://x.com/SHEIN_Official',
    'Zara': 'https://x.com/ZARA',
    'Uniqlo': 'https://x.com/UniqloUSA',
    'Gap': 'https://x.com/Gap',
    'American Eagle': 'https://x.com/AEO',
    'Dickies': 'https://x.com/Dickies',
    'Vans': 'https://x.com/VANS_66',
    'Converse': 'https://x.com/Converse',
    'Puma': 'https://x.com/PUMA',
    'Dr. Martens': 'https://x.com/drmartens',
    'Timberland': 'https://x.com/Timberland',
    'Merrell': 'https://x.com/Merrell',
    'Keen': 'https://x.com/KEEN',
    'Teva': 'https://x.com/Teva',
    'Gymshark': 'https://x.com/Gymshark',
    'Fabletics': 'https://x.com/Fabletics',
    'Sweaty Betty': 'https://x.com/SweatyBetty',
    'Aritzia': 'https://x.com/ARITZIA',
    'Revolve': 'https://x.com/REVOLVE',
    'Fashion Nova': 'https://x.com/FashionNova',
    'SKIMS': 'https://x.com/skims',
    'Bombas': 'https://x.com/Bombas',
    'Gucci': 'https://x.com/gucci',
    'Prada': 'https://x.com/Prada',
    'Louis Vuitton': 'https://x.com/LouisVuitton',
    'Chanel': 'https://x.com/CHANEL',
    'Hermès': 'https://x.com/Hermes_Paris',
    'Dior': 'https://x.com/Dior',
    'Balenciaga': 'https://x.com/BALENCIAGA',
    'Burberry': 'https://x.com/Burberry',
    'Versace': 'https://x.com/Versace',
    'Saint Laurent': 'https://x.com/YSL',
    'Bottega Veneta': 'https://x.com/BottegaVeneta',
    'Fendi': 'https://x.com/Fendi',
    'Valentino': 'https://x.com/Valentino',
    'Givenchy': 'https://x.com/givenchy',
    'Balmain': 'https://x.com/Balmain',
    'Celine': 'https://x.com/CELINE',
    'Loewe': 'https://x.com/LoeweOfficial',
    'Jacquemus': 'https://x.com/jacquemus',
    'Miu Miu': 'https://x.com/MIUMIUofficial',
    'Comme des Garçons': 'https://x.com/CommeDesGarcons',
    'Isabel Marant': 'https://x.com/IsabelMarant',
    'Acne Studios': 'https://x.com/acnestudios',
    'Ganni': 'https://x.com/GANNI',
    'COS': 'https://x.com/COSstores',
    'Mango': 'https://x.com/Mango',
    'H&M': 'https://x.com/hm',
    'Tommy Hilfiger': 'https://x.com/TommyHilfiger',
    'Calvin Klein': 'https://x.com/CalvinKlein',
    'Diesel': 'https://x.com/diesel',
    'Marni': 'https://x.com/Marni',
    'Off-White': 'https://x.com/OffWht',
    'Palm Angels': 'https://x.com/PalmAngels',
    'Ami Paris': 'https://x.com/amiparis',
    'Stone Island': 'https://x.com/stoneisland',
    'Yeezy': 'https://x.com/yeezy',
    'Supreme': 'https://x.com/Supreme_NYC',
    'Stüssy': 'https://x.com/STUSSY',
    'Palace': 'https://x.com/PalaceSkate',
    'Kith': 'https://x.com/Kith',
    'Aimé Leon Dore': 'https://x.com/aimeleondore',
    'Noah': 'https://x.com/NOAHNY',
    'Fear of God': 'https://x.com/FearofGod',
    'Rhude': 'https://x.com/RHUDE',
    'Bape': 'https://x.com/BAPE_OFFICIAL',
    'A Bathing Ape': 'https://x.com/BAPE_OFFICIAL',
    'Amiri': 'https://x.com/Amiri',
    'Gallery Dept.': 'https://x.com/GalleryDept',
    'Represent': 'https://x.com/REPRESENTCLO',
    'Pangaia': 'https://x.com/pangaia',
    'Marine Serre': 'https://x.com/marineserre',
    'Coperni': 'https://x.com/COPERNI',
    'Jil Sander': 'https://x.com/JilSander',
    'Ann Demeulemeester': 'https://x.com/AnnDemeule',
    'Dries Van Noten': 'https://x.com/DriesVanNoten',
    'Rick Owens': 'https://x.com/RickOwensonline',
    'Thom Browne': 'https://x.com/ThomBrowneNY',
    'JW Anderson': 'https://x.com/jwanderson',
    'Simone Rocha': 'https://x.com/Simone_Rocha_',
    'Molly Goddard': 'https://x.com/MollyGoddard',
    'Proenza Schouler': 'https://x.com/ProenzaSchouler',
    'Frame': 'https://x.com/Frame',
    'Toteme': 'https://x.com/TOTEME',
    'Khaite': 'https://x.com/KHAITE',
    'Staud': 'https://x.com/ST AUD',
    'Nanushka': 'https://x.com/Nanushka',
    'Filippa K': 'https://x.com/FilippaK',
    'Our Legacy': 'https://x.com/ourlegacy',
    'Margaret Howell': 'https://x.com/Margaret_Howell',
    'Eileen Fisher': 'https://x.com/EileenFisher',
    'Sézane': 'https://x.com/sezane',
    'Rouje': 'https://x.com/Rouje',
    'Goldsign': 'https://x.com/Goldsign',
    'Ksubi': 'https://x.com/ksubi',
    'Agolde': 'https://x.com/AGOLDE',
    'Re/Done': 'https://x.com/RE_DONE',
    'Citizens of Humanity': 'https://x.com/citizensofhuman',
    'Rag & Bone': 'https://x.com/rag_bone',
    'Mother': 'https://x.com/MOTHERDenim',
    'Paige': 'https://x.com/PAIGE',
    '7 For All Mankind': 'https://x.com/7FAM',
    'DL1961': 'https://x.com/DL1961',
    'Boyish': 'https://x.com/boyishjeans',
    'Outdoor Voices': 'https://x.com/OutdoorVoices',
    'Ten Thousand': 'https://x.com/tenthousandcc',
    'Rhone': 'https://x.com/rhone',
    'Mack Weldon': 'https://x.com/mackweldon',
    'Good American': 'https://x.com/goodamerican',
    'Spanx': 'https://x.com/SPANX',
    'ThirdLove': 'https://x.com/ThirdLove',
    'Parade': 'https://x.com/Parade',
    'Cuup': 'https://x.com/cuup',
    'Lively': 'https://x.com/wearlively',
    'Away': 'https://x.com/away',
    'A.P.C.': 'https://x.com/APC_PARIS',
    'Dion Lee': 'https://x.com/_DionLee',
    'Sandy Liang': 'https://x.com/sandyliang',
    'Eckhaus Latta': 'https://x.com/EckhausLatta',
    'Christopher Esber': 'https://x.com/Chr_Esber',
    'Bode': 'https://x.com/BODE',
    'Helmut Lang': 'https://x.com/HelmutLang',
    'Mugler': 'https://x.com/Mugler',
    'Lanvin': 'https://x.com/LANVINofficial',
    'Chloé': 'https://x.com/chloe',
    'Polo Ralph Lauren': 'https://x.com/ralphlauren',
}

# ============================================================
# TikTok 链接
# ============================================================
TIKTOK_URLS = {
    'Nike': 'https://www.tiktok.com/@nike',
    'Adidas': 'https://www.tiktok.com/@adidas',
    'Lululemon': 'https://www.tiktok.com/@lululemon',
    'Hoka': 'https://www.tiktok.com/@hoka',
    'New Balance': 'https://www.tiktok.com/@newbalance',
    "Arc'teryx": 'https://www.tiktok.com/@arcteryx',
    'Patagonia': 'https://www.tiktok.com/@patagonia',
    'The North Face': 'https://www.tiktok.com/@thenorthface',
    'Alo Yoga': 'https://www.tiktok.com/@aloyoga',
    'Skechers': 'https://www.tiktok.com/@skechers',
    'Under Armour': 'https://www.tiktok.com/@underarmour',
    'Crocs': 'https://www.tiktok.com/@crocs',
    'Birkenstock': 'https://www.tiktok.com/@birkenstock',
    'UGG': 'https://www.tiktok.com/@ugg',
    'Canada Goose': 'https://www.tiktok.com/@canadagoose',
    'Ralph Lauren': 'https://www.tiktok.com/@ralphlauren',
    "Levi's": 'https://www.tiktok.com/@levis',
    'Carhartt': 'https://www.tiktok.com/@carhartt',
    'Columbia': 'https://www.tiktok.com/@columbia',
    'Allbirds': 'https://www.tiktok.com/@allbirds',
    'Everlane': 'https://www.tiktok.com/@everlane',
    'Reformation': 'https://www.tiktok.com/@reformation',
    'Shein': 'https://www.tiktok.com/@shein_official',
    'Zara': 'https://www.tiktok.com/@zara',
    'Uniqlo': 'https://www.tiktok.com/@uniqlo',
    'Gap': 'https://www.tiktok.com/@gap',
    'American Eagle': 'https://www.tiktok.com/@americaneagle',
    'Vans': 'https://www.tiktok.com/@vans',
    'Converse': 'https://www.tiktok.com/@converse',
    'Puma': 'https://www.tiktok.com/@puma',
    'Dr. Martens': 'https://www.tiktok.com/@drmartens',
    'Timberland': 'https://www.tiktok.com/@timberland',
    'Gymshark': 'https://www.tiktok.com/@gymshark',
    'Fabletics': 'https://www.tiktok.com/@fabletics',
    'Aritzia': 'https://www.tiktok.com/@aritzia',
    'Fashion Nova': 'https://www.tiktok.com/@fashionnova',
    'SKIMS': 'https://www.tiktok.com/@skims',
    'Gucci': 'https://www.tiktok.com/@gucci',
    'Prada': 'https://www.tiktok.com/@prada',
    'Louis Vuitton': 'https://www.tiktok.com/@louisvuitton',
    'Dior': 'https://www.tiktok.com/@dior',
    'Balenciaga': 'https://www.tiktok.com/@balenciaga',
    'Burberry': 'https://www.tiktok.com/@burberry',
    'Versace': 'https://www.tiktok.com/@versace',
    'Saint Laurent': 'https://www.tiktok.com/@ysl',
    'Fendi': 'https://www.tiktok.com/@fendi',
    'Givenchy': 'https://www.tiktok.com/@givenchy',
    'Celine': 'https://www.tiktok.com/@celine',
    'Jacquemus': 'https://www.tiktok.com/@jacquemus',
    'Miu Miu': 'https://www.tiktok.com/@miumiu',
    'Acne Studios': 'https://www.tiktok.com/@acnestudios',
    'Ganni': 'https://www.tiktok.com/@ganni',
    'COS': 'https://www.tiktok.com/@cosstores',
    'H&M': 'https://www.tiktok.com/@hm',
    'Tommy Hilfiger': 'https://www.tiktok.com/@tommyhilfiger',
    'Calvin Klein': 'https://www.tiktok.com/@calvinklein',
    'Diesel': 'https://www.tiktok.com/@diesel',
    'Off-White': 'https://www.tiktok.com/@offwhitemilan',
    'Polo Ralph Lauren': 'https://www.tiktok.com/@ralphlauren',
    'Moncler': 'https://www.tiktok.com/@moncler',
    'Champion': 'https://www.tiktok.com/@champion',
    'Salomon': 'https://www.tiktok.com/@salomon',
    'Carhartt WIP': 'https://www.tiktok.com/@carharttwip',
    'Stüssy': 'https://www.tiktok.com/@stussy',
    'Supreme': 'https://www.tiktok.com/@supremenewyork',
    'Palace': 'https://www.tiktok.com/@palaceskateboards',
    'Kith': 'https://www.tiktok.com/@kith',
    'Aimé Leon Dore': 'https://www.tiktok.com/@aimeleondore',
    'Fear of God': 'https://www.tiktok.com/@fearofgod',
    'Amiri': 'https://www.tiktok.com/@amiri',
    'Represent': 'https://www.tiktok.com/@represent',
    'Pangaia': 'https://www.tiktok.com/@pangaia',
    'Spanx': 'https://www.tiktok.com/@spanx',
    'Skims': 'https://www.tiktok.com/@skims',
    'Vuori': 'https://www.tiktok.com/@vuoriclothing',
    'Alo': 'https://www.tiktok.com/@aloyoga',
    'Outdoor Voices': 'https://www.tiktok.com/@outdoorvoices',
    'Bombas': 'https://www.tiktok.com/@bombas',
    'Away': 'https://www.tiktok.com/@away',
    'Brandy Melville': 'https://www.tiktok.com/@brandymelvilleusa',
    'Sézane': 'https://www.tiktok.com/@sezane',
    'Rouje': 'https://www.tiktok.com/@rouje',
    'Good American': 'https://www.tiktok.com/@goodamerican',
    'ThirdLove': 'https://www.tiktok.com/@thirdlove',
    'Parade': 'https://www.tiktok.com/@parade',
    'Revolve': 'https://www.tiktok.com/@revolve',
    'Aritzia': 'https://www.tiktok.com/@aritzia',
}

# ============================================================
# 品牌描述额外补充（针对需要改善的品牌）
# ============================================================
DESC_FIXES = {
    # 品牌名: 正确描述
    'Hoka': 'Hoka One One 由法国越野跑者 Nicolas Mermoud 和 Jean-Luc Diard 于2009年创立，以超厚底缓震跑鞋闻名。现为美国 Deckers Brands 旗下品牌，是跑鞋和户外运动领域增长最快的品牌之一。',
    'UGG': 'UGG 由澳大利亚冲浪者 Brian Smith 于1978年在南加州创立，以经典羊皮靴闻名全球。现为美国 Deckers Brands 旗下品牌，已从单一靴款扩展为涵盖鞋履、服饰和配件的全方位生活方式品牌。',
    "Arc'teryx": 'Arc\'teryx 始祖鸟由 Dave Lane 和 Jeremy Guard 于1989年在加拿大温哥华创立，以顶级户外装备和极致工艺闻名。2019年被安踏体育收购，是户外机能与都市潮流融合的代表性品牌。',
    'Everlane': 'Everlane 由 Michael Preysman 于2010年在旧金山创立，以"Radical Transparency"（彻底透明化）为核心理念，主打高品质基础款和高性价比。2024年确认由快时尚巨头 Shein 收购。',
    'On Running': 'On 昂跑由瑞士前铁人三项运动员 Olivier Bernhard 与 David Allemann、Caspar Coppetti 于2010年共同创立，以 CloudTec 专利缓震技术和独特的鞋底设计闻名，是高端跑鞋和运动生活方式的代表品牌。',
}

def normalize():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    changes = {'countries': 0, 'descriptions': 0, 'twitter': 0, 'tiktok': 0, 'desc_fixes': 0}
    
    # 1. 标准化国家名称
    print("=== 1. 标准化国家名称 ===")
    cursor.execute("SELECT id, name, country FROM brands")
    for row in cursor.fetchall():
        current = row['country']
        if current in COUNTRY_MAP and current != COUNTRY_MAP[current]:
            new_country = COUNTRY_MAP[current]
            conn.execute(
                "UPDATE brands SET country = ?, updated_at = datetime('now') WHERE id = ?",
                (new_country, row['id'])
            )
            changes['countries'] += 1
            print(f"  {row['name']}: {current} -> {new_country}")
    
    conn.commit()
    print(f"  → 共修复 {changes['countries']} 个品牌的国家名称\n")
    
    # 2. 扩展短描述
    print("=== 2. 扩展短描述 ===")
    for name, desc in DESC_EXTENSIONS.items():
        result = conn.execute(
            "UPDATE brands SET description = ?, updated_at = datetime('now') WHERE name = ? AND (description IS NULL OR LENGTH(description) < 50)",
            (desc, name)
        )
        if result.rowcount > 0:
            changes['descriptions'] += 1
            print(f"  {name}: 描述已扩展")
    
    conn.commit()
    print(f"  → 共扩展 {changes['descriptions']} 个品牌的描述\n")
    
    # 3. 修复特定品牌描述
    print("=== 3. 修复特定品牌描述 ===")
    for name, desc in DESC_FIXES.items():
        conn.execute(
            "UPDATE brands SET description = ?, updated_at = datetime('now') WHERE name = ?",
            (desc, name)
        )
        changes['desc_fixes'] += 1
        print(f"  {name}: 描述已更新")
    
    conn.commit()
    print(f"  → 共修复 {changes['desc_fixes']} 个品牌描述\n")
    
    # 4. 添加 Twitter URL
    print("=== 4. 添加 Twitter URL ===")
    for name, url in TWITTER_URLS.items():
        result = conn.execute(
            "UPDATE brands SET twitter_url = ?, updated_at = datetime('now') WHERE name = ? AND (twitter_url IS NULL OR twitter_url = '')",
            (url, name)
        )
        if result.rowcount > 0:
            changes['twitter'] += 1
    
    conn.commit()
    print(f"  → 共添加 {changes['twitter']} 个品牌的 Twitter URL\n")
    
    # 5. 添加 TikTok URL
    print("=== 5. 添加 TikTok URL ===")
    for name, url in TIKTOK_URLS.items():
        result = conn.execute(
            "UPDATE brands SET tiktok_url = ?, updated_at = datetime('now') WHERE name = ? AND (tiktok_url IS NULL OR tiktok_url = '')",
            (url, name)
        )
        if result.rowcount > 0:
            changes['tiktok'] += 1
    
    conn.commit()
    print(f"  → 共添加 {changes['tiktok']} 个品牌的 TikTok URL\n")
    
    # 6. 统计结果
    print("=== 最终统计 ===")
    total = conn.execute("SELECT COUNT(*) FROM brands").fetchone()[0]
    ig = conn.execute("SELECT COUNT(*) FROM brands WHERE instagram_url IS NOT NULL AND instagram_url != ''").fetchone()[0]
    tw = conn.execute("SELECT COUNT(*) FROM brands WHERE twitter_url IS NOT NULL AND twitter_url != ''").fetchone()[0]
    tk = conn.execute("SELECT COUNT(*) FROM brands WHERE tiktok_url IS NOT NULL AND tiktok_url != ''").fetchone()[0]
    
    country_counts = conn.execute("SELECT country, COUNT(*) FROM brands GROUP BY country ORDER BY COUNT(*) DESC").fetchall()
    
    desc_short = conn.execute("SELECT COUNT(*) FROM brands WHERE description IS NOT NULL AND LENGTH(description) < 50").fetchone()[0]
    
    print(f"品牌总数: {total}")
    print(f"Instagram: {ig}/{total} | Twitter: {tw}/{total} | TikTok: {tk}/{total}")
    print(f"短描述(<50字符): {desc_short}")
    print(f"国家分布:")
    for c in country_counts[:15]:
        print(f"  {c[0]:20s} -> {c[1]}")
    
    print(f"\n总计修改: {sum(changes.values())} 条")
    conn.close()

if __name__ == '__main__':
    normalize()
