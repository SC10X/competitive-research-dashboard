#!/usr/bin/env python3
"""扩展所有47个短描述品牌"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "competitive_research.db"

ALL_EXTENSIONS = {
    'Dickies (VF Corp)': 'Dickies 是美国经典工装品牌，由C.N. Williamson和E.E. "Colonel" Dickie于1922年在德克萨斯州创立。现为VF Corp旗下品牌，以874工装裤和耐用工装闻名全球，年营收约8亿美元。',
    'Goldwin (北美)': 'Goldwin 是日本高端户外运动品牌，成立于1958年，以极简设计、技术面料和日本匠人工艺著称。品牌从滑雪装备起家，现已发展为涵盖户外、城市机能和运动生活方式的综合性品牌。',
    'Gramicci (北美)': 'Gramicci 由攀岩者Mike Graham于1982年在加州创立，以标志性G-Pants和独创腰带设计闻名。品牌在日本潮流化后全球流行，融合户外机能与都市街头风格。',
    'Heydude': 'Heydude 由Alessandro Rosano于2008年在意大利创立，以超轻便、可折叠的休闲鞋闻名。2022年被Crocs以25亿美元收购，成为其增长最快的子品牌之一。',
    'Icebreaker (VF Corp)': 'Icebreaker 由Jeremy Moon于1995年在新西兰创立，是美利奴羊毛户外服饰的先驱品牌。现为VF Corp旗下品牌，以天然、可再生的高性能面料和可持续发展理念著称。',
    'KÜHL': 'KÜHL 由Kevin Boyle于1983年在美国犹他州创立，以专利面料、山地文化灵感和精湛工艺著称。品牌定位高端户外休闲，受户外爱好者和都市冒险者青睐。',
    'Les Tien': 'Les Tien 由Courtney Michelle Ogilvie于2017年在洛杉矶创立，以厚重棉质面料、极简设计和复古色调闻名。品牌主打DTC高端基础款，深受极简主义者喜爱。',
    'MZ Wallace': 'MZ Wallace 由Monica Zwirner和Lucy Wallace Eustice于1999年在纽约创立，以轻量尼龙材质、标志性Metro Tote和时尚功能设计著称，是都市女性包袋的首选品牌。',
    'Mammut (北美)': 'Mammut 猛犸象由Kaspar Tanner于1862年在瑞士创立，是世界上最古老的户外品牌之一。以顶级攀登装备、雪崩安全设备和高性能户外服饰闻名，是瑞士精工的象征。',
    'Marine Layer': 'Marine Layer 由Michael Natenshon于2009年在旧金山创立，以超柔软面料、休闲加州风格和创新的旧衣回收计划著称。品牌从T恤起家，已扩展为全方位DTC休闲品牌。',
    'Mizzen+Main': 'Mizzen+Main 由Kevin Lavelle于2012年创立，以高性能运动面料制作正装衬衫闻名。品牌将运动服的舒适与正装的外观完美融合，是美国DTC男装领域的革新者。',
    'Moncler (北美)': 'Moncler 由René Ramillon于1952年在法国Monestier-de-Clermont创立，以奢华羽绒服闻名。品牌从登山装备起家，现已发展为全球顶级奢侈外套品牌，北美是其最重要增长市场。',
    'Mountain Hardwear': 'Mountain Hardwear 由前The North Face员工于1993年创立，现为Columbia Sportswear旗下高端品牌。以极限登山装备、帐篷和技术外套著称，服务专业攀登者。',
    'Myles Apparel': 'Myles Apparel 由Nick Cienski于2012年在旧金山创立，以高性能运动短裤起家。品牌定位DTC男士运动休闲市场，以多功能、耐用和简洁设计著称。',
    'Naadam': 'Naadam 由Matthew Scanlan和Diederik Rijsemus于2013年创立，直接从蒙古牧民采购羊绒，绕过中间商。品牌以可持续、亲民价格和透明供应链闻名，是DTC羊绒领域的领导者。',
    'Nobull': 'Nobull 由Marcus Wilson和Michael Schaeffer于2015年在波士顿创立，专注于CrossFit和功能性训练鞋服。品牌以极简设计、耐用性和社群文化著称，是健身领域增长最快的品牌之一。',
    'Nomatic': 'Nomatic 由Jacob Durham和Jon Richards于2014年在盐湖城创立，以Kickstarter起家。品牌专注模块化、功能性背包和旅行配件，以创新设计和极致收纳闻名。',
    'Norrona': 'Norrona 由Jørgen Jørgensen于1929年在挪威创立，是北欧最古老的高端户外品牌之一。以极端天气技术、北欧极简美学和可持续发展理念著称，被誉为"户外界的爱马仕"。',
    'Odlo': 'Odlo 由Odd Roar Lofterød于1946年在挪威创立，是欧洲运动功能内衣的先驱。现总部位于瑞士，以高性能底层、跑步和越野滑雪服饰闻名，服务全球运动员。',
    'OluKai': 'OluKai 由Bill Worthington和Matt Till于2005年在夏威夷创立，以高端凉鞋和海洋文化著称。品牌融合夏威夷精神与舒适科技，每双鞋都体现Aina（土地）和Aloha的价值观。',
    'Outdoor Research': 'Outdoor Research 由核物理学家Ron Gregg于1981年在西雅图创立，以功能性手套和GORE-TEX技术外套闻名。品牌以"Infinite Guarantee"终身保修承诺著称。',
    'Pangaia': 'Pangaia 由Miroslava Duma等人于2018年在英国创立，是可持续材料科学品牌。以创新生物基面料、鲜艳配色和环保使命著称，涵盖服饰、配饰和生活方式产品。',
    'Paravel': 'Paravel 由Indré Rockefeller和Andy Krantz于2016年在纽约创立，以可持续旅行箱包著称。品牌使用回收材料和环保面料，是DTC旅行生活方式领域的新锐力量。',
    'Pas Normal Studios': 'Pas Normal Studios 由Karl Oskar Olsen于2015年在哥本哈根创立，以极简北欧设计和高端骑行服饰闻名。品牌融合当代美学与技术性能，是骑行时尚化的代表。',
    'Public Rec': 'Public Rec 由Zach Goldstein于2015年在芝加哥创立，以All Day Every Day裤闻名。品牌定位DTC男士运动休闲，主打既舒适又得体的日常服饰。',
    'Quince': 'Quince 由Sid Gupta于2018年在旧金山创立，以工厂直销模式和极致性价比著称。品牌直接与工厂合作，以远低于传统奢侈品牌的价格提供高端羊绒、丝绸和亚麻制品。',
    'Rapha (北美)': 'Rapha 由Simon Mottram于2004年在伦敦创立，是高端骑行服饰的标杆品牌。以经典设计、优质面料和骑行文化社群著称，改变了人们对骑行装备的认知。',
    'Reef': 'Reef 由Fernando和Santiago Aguerre兄弟于1984年在阿根廷创立，以冲浪文化和标志性Fanning人字拖闻名。品牌融合冲浪、沙滩和轻松生活方式。',
    'Relwen': 'Relwen 由Greg Warr于2008年在美国中西部创立，以经典工装和军装风格为灵感。品牌使用耐用面料和复古设计，打造经得起时间考验的美式男装。',
    'Rhude': 'Rhude 由Rhuigi Villaseñor于2015年在洛杉矶创立，以复古美式美学和奢华面料著称。品牌融合街头文化与高端时装，是当代最具影响力的独立设计师品牌之一。',
    'Roa Hiking': 'Roa Hiking 由意大利设计师创立，以时尚户外美学和Vibram大底技术著称。品牌将意大利工艺与户外功能完美融合，是Gorpcore潮流的代表品牌。',
    'Roark': 'Roark 由Ryan Hitzel于2010年在加州创立，以冒险旅行文化为核心。品牌融合冲浪、攀岩和摩托车文化，打造兼具功能性和叙事性的男装服饰。',
    'Salomon (北美)': 'Salomon 由Georges Salomon于1947年在法国安纳西创立，以越野跑鞋和滑雪装备闻名。品牌XT-6等鞋款成功跨界时尚，是Gorpcore户外潮流的核心品牌。',
    'Sanuk (Deckers)': 'Sanuk 由Jeff Kelley于1997年在加州创立，以Yoga Mat瑜伽垫鞋垫和趣味舒适凉鞋闻名。现为Deckers Brands旗下品牌，传递"微笑"和"快乐"的品牌精神。',
    'Senreve': 'Senreve 由Coral Chung和Wendy Wen于2016年在旧金山创立，以多功能奢侈包袋著称。品牌Maestra大师包系列可手提、双肩、斜挎，专为现代女性设计。',
    'Skechers': 'Skechers 由Robert Greenberg于1992年在加州创立，是美国第三大运动鞋品牌。以舒适科技和大众定位著称，涵盖休闲鞋、跑鞋和童鞋，FY2025营收约82亿美元。',
    'State Bags': 'State Bags 由Jacqueline和Scot Tatelman于2012年在纽约创立，以买一捐一公益模式著称。品牌每售出一个包袋即为美国贫困儿童捐赠一个装满学习用品的书包。',
    'Stutterheim (北美)': 'Stutterheim 由Alexander Stutterheim于2010年在斯德哥尔摩创立，以手工雨衣闻名。品牌受北欧渔民传统雨衣启发，以极简设计和匠人工艺打造功能性外套。',
    'Summersalt': 'Summersalt 由Lori Coulter和Reshma Chattaram Chamberlin于2017年创立，以数据驱动合身性著称。品牌通过1万多名女性身体数据设计泳装和度假服饰，营收约5000万美元。',
    'Taylor Stitch': 'Taylor Stitch 由Michael Maher等人于2009年在旧金山创立，以众筹预售模式著称。品牌通过Workshop平台让消费者预购，减少浪费并降低价格，主打经典美式男装。',
    'ThirdLove': 'ThirdLove 由Heidi Zak和David Spector于2013年在旧金山创立，以半杯尺码和包容性著称。品牌通过Fit Finder问卷帮助女性找到完美内衣，营收约1.5亿美元。',
    'Thursday Boots': 'Thursday Boots 由Nolan Walsh和Connor Wilson于2014年在纽约创立，以高品质手工皮靴和亲民价格著称。品牌直接面向消费者，被誉为"互联网时代最好的入门级皮靴"。',
    'Timbuk2': 'Timbuk2 由自行车信使Rob Honeycutt于1989年在旧金山创立，以经典三面板邮差包闻名。品牌提供定制化服务，是城市骑行和通勤文化的标志性品牌。',
    'Topo Designs': 'Topo Designs 由Jedd Rose和Mark Hansen于2008年在科罗拉多创立，以复古户外美学和鲜艳配色著称。品牌融合户外功能与都市风格，是科罗拉多户外文化的代表。',
    'Toteme': 'Toteme 由Elin Kling和Karl Lindman于2014年在斯德哥尔摩创立，以极简奢华和精准剪裁著称。品牌倡导胶囊衣橱理念，是北欧现代女性的衣橱首选，Instagram时代的It-brand。',
    'Tracksmith': 'Tracksmith 由Matt Taylor于2014年在波士顿创立，以常春藤复古美学致敬跑步文化。品牌融合新英格兰学院风格与高性能面料，服务热爱跑步的业余跑者。',
    'VEJA (北美)': 'VEJA 由Sébastien Kopp和François-Ghislain Morillion于2004年在巴黎创立，以环保材料和公平贸易著称。品牌直接从巴西采购有机棉和野生橡胶，2025年全球营收约2亿美元。',
}

def extend_descriptions():
    conn = sqlite3.connect(str(DB_PATH))
    count = 0
    
    for name, desc in ALL_EXTENSIONS.items():
        result = conn.execute(
            "UPDATE brands SET description = ?, updated_at = datetime('now') WHERE name = ?",
            (desc, name)
        )
        if result.rowcount > 0:
            count += 1
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name} (未找到)")
    
    conn.commit()
    
    # Verify
    short_remaining = conn.execute(
        "SELECT COUNT(*) FROM brands WHERE description IS NOT NULL AND LENGTH(description) < 50"
    ).fetchone()[0]
    
    print(f"\n扩展完成: {count} 个品牌")
    print(f"剩余短描述: {short_remaining}")
    
    conn.close()

if __name__ == '__main__':
    extend_descriptions()
