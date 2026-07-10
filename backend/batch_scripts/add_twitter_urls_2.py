"""
第二轮Twitter URL补充 - 覆盖剩余225个品牌
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'competitive_research.db')

twitter_map_2 = {
    # A
    # B
    'bonobos-na': 'https://x.com/Bonobos',
    'brooks': 'https://x.com/brooksrunning',
    'brunello-cucinelli': 'https://x.com/BrunelloCucinel',
    'buck-mason': 'https://x.com/buckmason',
    'burts-bees-baby': 'https://x.com/burtsbeesbaby',
    'beis': 'https://x.com/beistravel',
    
    # C
    'cep': 'https://x.com/CEP_Compression',
    'cos-na': 'https://x.com/COSstores',
    'csb-crop-shop-boutique': 'https://x.com/cropshopboutiq',
    'cabelas-redhead': 'https://x.com/Cabelas',
    'calpak': 'https://x.com/calpak',
    'calvin-klein-na': 'https://x.com/CalvinKlein',
    'carbon38': 'https://x.com/Carbon38',
    'carhartt-wip': 'https://x.com/CarharttWIP',
    'catbird': 'https://x.com/catbirdnyc',
    'cecilie-bahnsen': 'https://x.com/CecilieBahnsen',
    'champion-hanes': 'https://x.com/ChampionUSA',
    'clarks-na': 'https://x.com/clarksshoes',
    'coach': 'https://x.com/Coach',
    'compressport': 'https://x.com/compressport',
    'converse-nike': 'https://x.com/Converse',
    'courreges': 'https://x.com/courreges',
    'craft-sportswear': 'https://x.com/CraftSportswear',
    'crap-eyewear': 'https://x.com/crapeyewear',
    
    # D
    'dkny-na': 'https://x.com/dkny',
    'dsw-designer-shoe-warehouse': 'https://x.com/dsw',
    'dagne-dover': 'https://x.com/dagnedover',
    'daily-drills': 'https://x.com/dailydrills',
    'danner': 'https://x.com/Danner',
    'darn-tough': 'https://x.com/DarnTough',
    'deuter': 'https://x.com/Deuter_USA',
    'dickies-vf': 'https://x.com/Dickies',
    'dickies-na': 'https://x.com/Dickies',
    'diff-eyewear': 'https://x.com/diffeyewear',
    'doyoueven': 'https://x.com/doyoueven',
    'duer': 'https://x.com/DUER',
    'duluth-pack': 'https://x.com/DuluthPack',
    'duluth-trading-co': 'https://x.com/DuluthTrading',
    
    # E
    'eberjey': 'https://x.com/eberjey',
    'eddie-bauer-na': 'https://x.com/eddiebauer',
    'eloquii': 'https://x.com/eloquii',
    'express-na': 'https://x.com/Express',
    
    # F
    'fabletics-na': 'https://x.com/Fabletics',
    'fear-of-god-essentials': 'https://x.com/fearofgod',
    'fila-na': 'https://x.com/FILAUSA',
    'fjallraven-na': 'https://x.com/Fjallraven_US',
    'fleo': 'https://x.com/fleo',
    'flint-and-tinder': 'https://x.com/flintandtinder',
    'frankies-bikinis': 'https://x.com/frankiesbikinis',
    'free-people-na': 'https://x.com/FreePeople',
    
    # G
    'ganni-na': 'https://x.com/ganni',
    'gap-na': 'https://x.com/Gap',
    'girlfriend-collective': 'https://x.com/gfcollective',
    'goldwin-na': 'https://x.com/goldwin',
    'goyard': 'https://x.com/Goyard',
    'gramicci-na': 'https://x.com/Gramicci',
    'gregory': 'https://x.com/GregoryPacks',
    'guess': 'https://x.com/GUESS',
    'gymboree-na': 'https://x.com/gymboree',
    
    # H
    'hm-na': 'https://x.com/hm',
    'haglofs': 'https://x.com/HAGLOFS',
    'head': 'https://x.com/head_tennis',
    'heydude': 'https://x.com/heydude',
    'hollister': 'https://x.com/hollisterco',
    'hudson-jeans': 'https://x.com/hudsonjeans',
    
    # I
    'injinji': 'https://x.com/Injinji',
    'italic': 'https://x.com/italic',
    
    # J
    'jcrew': 'https://x.com/jcrew',
    'jcrew-na': 'https://x.com/jcrew',
    'jaanuu': 'https://x.com/jaanuu',
    'jacquemus-na': 'https://x.com/jacquemus',
    'jansport': 'https://x.com/JanSport',
    'janie-and-jack-na': 'https://x.com/janieandjack',
    'jjjjound': 'https://x.com/JJJJOUND',
    
    # K
    'keen': 'https://x.com/KEEN',
    'kate-spade': 'https://x.com/katespadeny',
    'kate-spade-na': 'https://x.com/katespadeny',
    'kavu': 'https://x.com/kavu',
    'keds': 'https://x.com/Keds',
    'kickee-pants': 'https://x.com/KickeePants',
    'kit-and-ace': 'https://x.com/kitandace',
    'knix': 'https://x.com/knixwear',
    'krost': 'https://x.com/krostnewyork',
    'kuru-footwear': 'https://x.com/KuruFootwear',
    'kyte-baby': 'https://x.com/kytebaby',
    
    # L
    'llbean-na': 'https://x.com/LLBean',
    'lndr': 'https://x.com/lndr',
    'la-sportiva-na': 'https://x.com/LaSportivaNA',
    'lee-na': 'https://x.com/leejeans',
    'left-on-friday': 'https://x.com/leftonfriday',
    'les-tien': 'https://x.com/lestien',
    'levi-strauss-co': 'https://x.com/LEVIS',
    'little-sleepies': 'https://x.com/littlesleepies',
    'longchamp': 'https://x.com/Longchamp',
    'loro-piana': 'https://x.com/LoroPiana',
    'loro-piana-na': 'https://x.com/LoroPiana',
    
    # M
    'mgemi': 'https://x.com/MGemi',
    'mmlafleur': 'https://x.com/mmlafleur',
    'mate-the-label': 'https://x.com/matethelabel',
    'mvmt': 'https://x.com/MVMT',
    'mz-wallace': 'https://x.com/mzwallacenyc',
    'maje-na': 'https://x.com/Maje',
    'mammut-na': 'https://x.com/mammut',
    'mansur-gavriel': 'https://x.com/mansurgavriel',
    'marc-jacobs-na': 'https://x.com/marcjacobs',
    'margaux': 'https://x.com/margaux',
    'marine-layer': 'https://x.com/marinelayer',
    'max-mara': 'https://x.com/maxmara',
    'mcdavid': 'https://x.com/McDavidSports',
    'meundies': 'https://x.com/meundies',
    'michael-kors': 'https://x.com/MichaelKors',
    'mini-boden': 'https://x.com/miniboden',
    'ministry-of-supply': 'https://x.com/ministryofsuppl',
    'missoma-na': 'https://x.com/missoma',
    'monday-swimwear': 'https://x.com/mondayswimwear',
    'monica-andy': 'https://x.com/monicaandy',
    'moose-knuckles': 'https://x.com/mooseknuckles',
    'mother-denim': 'https://x.com/motherdenim',
    'mott-bow': 'https://x.com/mottandbow',
    'mountain-equipment': 'https://x.com/mountainequip',
    'mountain-hardwear': 'https://x.com/MountainHardwear',
    'moving-comfort-brooks': 'https://x.com/brooksrunning',
    'muck-boot': 'https://x.com/MuckBootCo',
    'muscle-nation': 'https://x.com/MuscleNation',
    'myles-apparel': 'https://x.com/MylesApparel',
    
    # N
    'nvgtn': 'https://x.com/nvgtn',
    'naturalizer': 'https://x.com/Naturalizer',
    'negative-underwear': 'https://x.com/NegativeUnder',
    'new-era': 'https://x.com/NewEraCap',
    'nisolo': 'https://x.com/nisolo',
    'nobull': 'https://x.com/nobull',
    'north-face': 'https://x.com/thenorthface',
    
    # O
    'odlo': 'https://x.com/odlo',
    'oiselle': 'https://x.com/Oiselle',
    'old-navy': 'https://x.com/OldNavy',
    'old-navy-active': 'https://x.com/OldNavy',
    'oliver-cabell': 'https://x.com/OliverCabell',
    'on-na': 'https://x.com/on_running',
    'oofos': 'https://x.com/oofos',
    'osprey': 'https://x.com/osprey_packs',
    
    # P
    'pe-nation': 'https://x.com/PE_Nation',
    'pact': 'https://x.com/pact',
    'paige-na': 'https://x.com/paige_denim',
    'parachute-home': 'https://x.com/parachutehome',
    'paravel': 'https://x.com/paravel',
    'peak-design': 'https://x.com/peakdesignlabs',
    'peak-performance-na': 'https://x.com/peakperformance',
    'peter-millar-na': 'https://x.com/PeterMillar',
    'polene': 'https://x.com/poleneparis',
    'prana': 'https://x.com/prAna',
    
    # Q
    'quay': 'https://x.com/quayaustralia',
    'quince': 'https://x.com/quince',
    
    # R
    'rab': 'https://x.com/rab_equipment',
    'rag-bone-na': 'https://x.com/rag_bone',
    'reebok': 'https://x.com/Reebok',
    'reef': 'https://x.com/reef',
    'relwen': 'https://x.com/relwen',
    'rent-the-runway': 'https://x.com/RenttheRunway',
    'roa-hiking': 'https://x.com/roahiking',
    'roark': 'https://x.com/roark',
    'rotate': 'https://x.com/rotatebirg',
    'royal-robbins': 'https://x.com/RoyalRobbins',
    'russell-athletic-na': 'https://x.com/RussellAthletic',
    'ryderwear': 'https://x.com/ryderwear',
    'rylee-cru': 'https://x.com/ryleeandcru',
    
    # S
    'salming': 'https://x.com/Salming',
    'sam-edelman': 'https://x.com/samedelman',
    'sam-edelman-na': 'https://x.com/samedelman',
    'sandro-na': 'https://x.com/Sandro',
    'sanuk-deckers': 'https://x.com/sanuk',
    'sarah-flint': 'https://x.com/sarahflint_nyc',
    'satisfy-running': 'https://x.com/satisfyrunning',
    'self-portrait': 'https://x.com/selfportrait',
    'senreve': 'https://x.com/senreve',
    'set-active': 'https://x.com/setactive',
    'sherpa-adventure-gear': 'https://x.com/SherpaGear',
    'shock-doctor': 'https://x.com/ShockDoctor',
    'skagen-na': 'https://x.com/Skagen',
    'skins': 'https://x.com/SkinsCompress',
    'solid-and-striped': 'https://x.com/solidandstriped',
    'spalding': 'https://x.com/Spalding',
    'spalding-na': 'https://x.com/Spalding',
    'sperry': 'https://x.com/Sperry',
    'state-bags': 'https://x.com/statebags',
    'steve-madden': 'https://x.com/SteveMadden',
    'stone-island-na': 'https://x.com/stoneisland',
    
    # T
    'tala': 'https://x.com/tala',
    'target-all-in-motion': 'https://x.com/Target',
    'tea-collection': 'https://x.com/teacollection',
    'tentree': 'https://x.com/tentree',
    'teva-deckers': 'https://x.com/Teva',
    'the-honest-company': 'https://x.com/Honest',
    'the-north-face-na': 'https://x.com/thenorthface',
    'the-row': 'https://x.com/therow',
    'theory': 'https://x.com/Theory',
    'thursday-boots': 'https://x.com/thursdayboots',
    'timberland-na': 'https://x.com/Timberland',
    'timbuk2': 'https://x.com/timbuk2',
    'tods-na': 'https://x.com/Tods',
    'tommy-john': 'https://x.com/tommyjohn',
    'toms': 'https://x.com/TOMS',
    'topo-designs': 'https://x.com/topodesigns',
    'torrid': 'https://x.com/torrid',
    'tory-sport': 'https://x.com/torysport',
    'tradlands': 'https://x.com/tradlands',
    'tumi': 'https://x.com/TUMI',
    
    # U
    'ugg-deckers': 'https://x.com/UGG',
    'universal-standard': 'https://x.com/universalstand',
    'untuckit': 'https://x.com/untuckit',
    'urban-outfitters-na': 'https://x.com/UrbanOutfitters',
    
    # V
    'veja-na': 'https://x.com/veja',
    'vans-vf': 'https://x.com/VANS',
    'varley': 'https://x.com/varley',
    'versace-na': 'https://x.com/Versace',
    'vetements': 'https://x.com/vetements',
    'vince-na': 'https://x.com/vince',
    'vionic': 'https://x.com/vionicshoes',
    
    # W
    'western-rise': 'https://x.com/westernrise',
    'wilson': 'https://x.com/WilsonSportingG',
    'wolven': 'https://x.com/wolventhreads',
    'wrangler-na': 'https://x.com/Wrangler',
    
    # X
    'x-bionic': 'https://x.com/xbionic',
    
    # Y
    'year-of-ours': 'https://x.com/yearofours',
    'yeezy-adidas': 'https://x.com/yeezy',
    
    # Z
    'zegna': 'https://x.com/Zegna',
}

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    cursor = conn.cursor()
    
    updated = 0
    not_found = []
    
    for slug, url in twitter_map_2.items():
        cursor.execute(
            'UPDATE brands SET twitter_url = ? WHERE slug = ? AND (twitter_url IS NULL OR twitter_url = "")',
            (url, slug)
        )
        if cursor.rowcount > 0:
            updated += 1
        else:
            not_found.append(slug)
    
    conn.commit()
    
    cursor.execute('SELECT COUNT(*) FROM brands WHERE twitter_url IS NOT NULL AND twitter_url != ""')
    has = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM brands')
    total = cursor.fetchone()[0]
    
    print(f'=== Twitter URL 第二轮补充 ===')
    print(f'本次更新: {updated}')
    print(f'未匹配: {len(not_found)}')
    print(f'当前覆盖: {has}/{total} ({has*100//total}%)')
    
    if not_found:
        print(f'\n未匹配品牌:')
        for s in not_found:
            print(f'  {s}')
    
    conn.close()

if __name__ == '__main__':
    main()
