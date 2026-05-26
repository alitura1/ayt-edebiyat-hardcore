"""
REV6 M4 — Eserler veritabanı: authors.json'daki diger_eserler + occurrences'tan üretilir.
Output: public/data/works.json
"""
import json, sys, io, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = Path(__file__).parent.parent
# REV17: subject-aware path
AUTHORS = BASE / 'public' / 'data' / 'edebiyat' / 'authors.json'
OUT = BASE / 'public' / 'data' / 'edebiyat' / 'works.json'
MEBI_WORKS = BASE.parent / 'data' / 'mebi_works_raw.json'  # M2.a OCR çıktısı
COVERAGE_GAP = BASE.parent / 'data' / 'coverage_gap.json'  # M2.b transparency


def slugify(s):
    s = s.lower()
    table = str.maketrans({'ş':'s','ç':'c','ğ':'g','ı':'i','ö':'o','ü':'u','â':'a','î':'i','û':'u'})
    s = s.translate(table)
    out = []
    for ch in s:
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != '-':
            out.append('-')
    return ''.join(out).strip('-')


def guess_tur(name):
    """Eser adından türünü tahmin et (heuristik)."""
    nl = name.lower()
    # Bilinen pattern'ler
    if any(x in nl for x in ['divan', 'mesnevi', 'gazel', 'kaside', 'rubai']):
        return 'Şiir Kitabı / Divan'
    if any(x in nl for x in ['oyun', 'tiyatro', 'piyes']):
        return 'Oyun'
    if any(x in nl for x in ['hikaye', 'hikâye', 'öykü']):
        return 'Hikaye Kitabı'
    if any(x in nl for x in ['anı', 'hatıra', 'günlük', 'gezi', 'seyahat', 'mektup']):
        return 'Anı / Gezi / Mektup'
    if any(x in nl for x in ['deneme', 'makale', 'eleştir', 'inceleme']):
        return 'Deneme / İnceleme'
    return None


# Manuel tür override (bilinen eserler)
TUR_OVERRIDE = {
    'aşk-ı memnu': 'Roman', 'aşk_ı memnu': 'Roman', 'mai ve siyah': 'Roman',
    'kırık hayatlar': 'Roman', 'çalıkuşu': 'Roman', 'sinekli bakkal': 'Roman',
    'huzur': 'Roman', 'saatleri ayarlama enstitüsü': 'Roman', 'tutunamayanlar': 'Roman',
    'kürk mantolu madonna': 'Roman', 'ince memed': 'Roman', 'küçük ağa': 'Roman',
    'devlet ana': 'Roman', 'osmancık': 'Roman', 'yaprak dökümü': 'Roman',
    'yaban': 'Roman', 'kiralık konak': 'Roman', 'sodom ve gomore': 'Roman',
    'nur baba': 'Roman', 'sergüzeşt': 'Roman', 'karabibik': 'Roman',
    'araba sevdası': 'Roman', 'intibah': 'Roman', 'cezmi': 'Roman',
    'taaşşuk-ı talat ve fitnat': 'Roman', 'felatun bey ile rakım efendi': 'Roman',
    'üç istanbul': 'Roman', 'dokuzuncu hariciye koğuşu': 'Roman',
    'matmazel noraliya\'nın koltuğu': 'Roman', 'kuyucaklı yusuf': 'Roman',
    'içimizdeki şeytan': 'Roman', 'bereketli topraklar üzerinde': 'Roman',
    'cemile': 'Roman', 'murtaza': 'Roman', 'yorgun savaşçı': 'Roman',
    'esir şehrin insanları': 'Roman', 'asılacak kadın': 'Roman', 'sevgili arsız ölüm': 'Roman',
    'berci kristin çöp masalları': 'Roman', 'bir düğün gecesi': 'Roman',
    'ölmeye yatmak': 'Roman', 'aganta burina burinata': 'Roman',
    'mavi sürgün': 'Roman', 'eylül': 'Roman', 'frankenstein': 'Roman',
    'leyla vü mecnun': 'Mesnevi', 'hüsn ü aşk': 'Mesnevi', 'iskendername': 'Mesnevi',
    'cemşid ü hurşid': 'Mesnevi', 'harname': 'Mesnevi', 'hüsrev ü şirin': 'Mesnevi',
    'mevlid': 'Mesnevi', 'vesiletü\'n-necat': 'Mesnevi', 'mesnevi': 'Mesnevi',
    'su kasidesi': 'Kaside', 'kanunî mersiyesi': 'Mersiye',
    'safahat': 'Şiir Kitabı', 'piyale': 'Şiir Kitabı', 'göl saatleri': 'Şiir Kitabı',
    'kendi gök kubbemiz': 'Şiir Kitabı', 'çile': 'Şiir Kitabı', 'mona roza': 'Şiir',
    'han duvarları': 'Şiir', 'sis': 'Şiir', 'sessiz gemi': 'Şiir',
    'memleketimden insan manzaraları': 'Şiir Destanı', 'kuvâyi milliye destanı': 'Şiir Destanı',
    'şeyh bedreddin destanı': 'Şiir Destanı',
    'vatan yahut silistre': 'Tiyatro', 'şair evlenmesi': 'Tiyatro',
    'keşanlı ali destanı': 'Tiyatro', 'bir adam yaratmak': 'Tiyatro',
    'köşebaşı': 'Tiyatro', 'eşber': 'Tiyatro', 'tezer': 'Tiyatro',
    'falaka': 'Hikaye', 'kaşağı': 'Hikaye', 'bomba': 'Hikaye', 'pembe incili kaftan': 'Hikaye',
    'memleket hikayeleri': 'Hikaye Kitabı', 'gurbet hikayeleri': 'Hikaye Kitabı',
    'ayaşlı ve kiracıları': 'Roman',
    'divan-ı hikmet': 'Tasavvuf Şiiri', 'kutadgu bilig': 'Mesnevi',
    'divânü lügâti\'t-türk': 'Sözlük', 'atabetü\'l-hakayık': 'Mesnevi',
    'kamus-ı türki': 'Sözlük', 'kamusu\'l-alam': 'Ansiklopedi',
    'lehçe-i osmani': 'Sözlük', 'şecere-i türki': 'Tarih',
    'cenge giderken': 'Şiir', 'türkçülüğün esasları': 'Fikir Kitabı',
    'kızıl elma': 'Şiir Destanı', 'beyaz lale': 'Hikaye',
    'tercüman-ı ahval': 'Gazete', 'tasvir-i efkar': 'Gazete',
    'makber': 'Şiir', 'tarih-i kadim': 'Şiir',
    'çağlayanlar': 'Hikaye Kitabı', 'dikmen yıldızı': 'Roman',
    'aşk masalları': 'Hikaye Kitabı', 'beş şehir': 'Deneme',
    'çankaya': 'Anı', 'zeytindağı': 'Anı',
    'üç şehitler destanı': 'Şiir', 'çocuk ve allah': 'Şiir Kitabı',
    # REV17 — 198 boş tur'dan en sık çıkanlar (yazar bazlı pozisyon fallback'in eksikleri için)
    # Attila İlhan (Çok yönlü — pozisyon fallback yok)
    'bela çiçeği': 'Şiir Kitabı', 'ben sana mecburum': 'Şiir Kitabı',
    'duvar': 'Şiir Kitabı', 'sisler bulvarı': 'Şiir Kitabı',
    'yağmur kaçağı': 'Şiir Kitabı', 'sırtlan payı': 'Roman',
    'kurtlar sofrası': 'Roman',
    # Taşlıcalı Yahya mesnevileri (Şair fallback "Şiir Kitabı" yerine "Mesnevi")
    'gencîne-i râz': 'Mesnevi', 'gencine-i raz': 'Mesnevi',
    'gülşen-i envâr': 'Mesnevi', 'gulsen-i envar': 'Mesnevi',
    'kitab-ı usul': 'Mesnevi', 'yusuf u züleyha': 'Mesnevi',
    'şah u geda': 'Mesnevi', 'şehzade mustafa mersiyesi': 'Mersiye',
    # Aşık Paşa
    'garibname': 'Mesnevi', 'garibnâme': 'Mesnevi',
    'fakrname': 'Mesnevi',
    # Hamdullah Hamdi mesnevileri
    'ahmediyye': 'Mesnevi', 'kıyafetname': 'Mesnevi',
    "tuhfetü'l-uşşak": 'Mesnevi', 'leyla vü mecnun': 'Mesnevi',
    # Nabi
    'hayrabad': 'Mesnevi', 'hayriye': 'Mesnevi',
    'sur-name': 'Mesnevi', "tuhfetü'l-haremeyn": 'Anı/Seyahat',
    # Ziya Paşa
    'harabat': 'Antoloji', 'terci-i bend': 'Şiir',
    'terkib-i bend': 'Şiir', 'şiir ve inşa': 'Deneme/Eleştiri',
    # Sehi Bey
    'heşt bihişt': 'Tezkire',
    # Şeyhülislam Yahya, Zati, Neşati (Şair → "Şiir Kitabı" fallback uyar)
    'şem ü pervane': 'Mesnevi', 'edirne şehrengizi': 'Şehrengiz',
    'şitaiyye': 'Kaside',
    # Hüseyin Rahmi Gürpınar (Romancı fallback "Roman" — OK ama tek tek de işaretleyelim)
    'gulyabani': 'Roman', 'kuyruklu yıldız altında bir izdivaç': 'Roman',
    'mürebbiye': 'Roman', 'şıpsevdi': 'Roman',
    'şık': 'Roman', 'ben deli miyim?': 'Roman', 'ben deli miyim': 'Roman',
    'cadı': 'Roman',
    # Sevgi Soysal (Hikayeci — bazıları roman)
    'tante rosa': 'Hikaye Kitabı', 'tutkulu perçem': 'Hikaye Kitabı',
    "yenişehir'de bir öğle vakti": 'Roman', 'yürümek': 'Roman',
    'şafak': 'Roman',
    # İsmet Özel
    'erbain': 'Şiir Kitabı', 'şair erbain': 'Şiir Kitabı',
    'bir yusuf masalı': 'Şiir Kitabı', 'of not being a jew': 'Deneme',
    # Cevat Fehmi Başkut (Tiyatrocu fallback "Oyun" — OK)
    'buzlar çözülmeden': 'Oyun', 'paydos': 'Oyun',
    'küçük şehir': 'Oyun', 'hacı kaptan': 'Oyun',
    'sana rey veriyorum': 'Oyun',
    # Yaşar Kemal
    'demirciler çarşısı cinayeti': 'Roman', 'ince memed': 'Roman',
    'ortadirek': 'Roman', 'yer demir gök bakır': 'Roman',
    # Halide Edip
    'ateşten gömlek': 'Roman', 'handan': 'Roman',
    "mev'ud hüküm": 'Roman', 'vurun kahpeye': 'Roman',
    # Orhan Veli (Şair fallback Şiir Kitabı OK)
    'garip': 'Şiir Kitabı', 'karşı': 'Şiir Kitabı',
    'vazgeçemediğim': 'Şiir Kitabı', 'yenisi': 'Şiir Kitabı',
    # Peyami Safa
    '9. hariciye koğuşu': 'Roman', 'dokuzuncu hariciye koğuşu': 'Roman',
    'fatih harbiye': 'Roman', 'yalnızız': 'Roman',
    # Reşat Nuri
    'acımak': 'Roman', 'dudaktan kalbe': 'Roman', 'yeşil gece': 'Roman',
    # Molière
    'tartif': 'Oyun', 'tartüf': 'Oyun', 'cimri': 'Oyun', 'zoraki tabip': 'Oyun',
    # Yusuf Has Hacip, Kaşgarlı (Sözlük yazarı fallback Sözlük — OK)
    'kutadgu bilig': 'Mesnevi',
    "divânü lügâti't-türk": 'Sözlük', "divanü lügatit-türk": 'Sözlük',
    # Aristoteles
    'poetika': 'Eleştiri/Teori', 'retorik': 'Felsefe',
    "nikomakhos'a etik": 'Felsefe',
    # Halit Ziya, Mehmet Rauf vs (ekstra eksikler)
    'sefile': 'Roman', 'nemide': 'Roman', 'ferdi ve şürekası': 'Roman',
    'bir ölünün defteri': 'Roman', 'nesl-i ahir': 'Roman',
    'kırk yıl': 'Anı', 'eylül': 'Roman',
    'edebî hatıralarım': 'Anı', 'edebi hatıralarım': 'Anı',
    # Sait Faik
    "alemdağ'da var bir yılan": 'Hikaye Kitabı',
    'son kuşlar': 'Hikaye Kitabı',
    'lüzumsuz adam': 'Hikaye Kitabı',
    'havuz başı': 'Hikaye Kitabı',
}


def main():
    authors = json.loads(AUTHORS.read_text(encoding='utf-8'))

    # REV17 — MEBİ OCR'dan tür bilgisi (lookup tablosu)
    # mebi_lookup[yazar_norm][eser_norm] = tur
    mebi_lookup = {}
    if MEBI_WORKS.exists():
        try:
            mw = json.loads(MEBI_WORKS.read_text(encoding='utf-8'))
            def norm_key(s):
                return slugify(s)  # ASCII slug — alias match
            for yazar, info in mw.items():
                yk = norm_key(yazar)
                if yk not in mebi_lookup:
                    mebi_lookup[yk] = {}
                for e in info.get('eserler', []):
                    title = e.get('title', '')
                    tur = e.get('tur')
                    if tur and title:
                        mebi_lookup[yk][norm_key(title)] = tur
            total_pairs = sum(len(v) for v in mebi_lookup.values())
            print(f"  REV17 MEBİ lookup: {len(mebi_lookup)} yazar, {total_pairs} eser-tur eşleşmesi")
        except Exception as e:
            print(f"⚠ MEBİ lookup: {e}")

    works = []
    seen = set()  # (slug, yazarSlug) tekrar engelle

    # REV17 — Pozisyon → varsayılan tür mapping
    POZISYON_DEFAULT_TUR = {
        'Romancı': 'Roman',
        'Hikayeci': 'Hikaye Kitabı',
        'Tiyatrocu': 'Oyun',
        'Şair': 'Şiir Kitabı',
        'Tezkire yazarı': 'Tezkire',
        'Sözlük yazarı': 'Sözlük',
        'Filozof/Eleştirmen': 'Felsefe/Eleştiri',
        'Bilim insanı': 'Bilim',
    }

    for author in authors:
        ad = author['name']
        yazarSlug = slugify(ad)
        donem = author.get('donem') or (author.get('konular') or ['cumhuriyet'])[0]
        pozisyon = author.get('pozisyon', '')
        pozisyon_tur = POZISYON_DEFAULT_TUR.get(pozisyon)

        # diger_eserler virgülle ayrılmış string
        raw = author.get('diger_eserler') or ''
        if not raw or raw == '—':
            continue

        # Bazı ayırıcılar: virgül + nokta + ' ve '
        eserler_raw = re.split(r'[,;]', raw)
        for e in eserler_raw:
            e = e.strip()
            # Parantezli ek bilgi (örn: "(1900)") ayır
            yil = None
            m = re.search(r'\((\d{4})\)', e)
            if m:
                yil = m.group(1)
                e = re.sub(r'\s*\(\d{4}\)', '', e).strip()
            if not e or len(e) < 3:
                continue

            slug = slugify(e)
            key = (slug, yazarSlug)
            if key in seen:
                continue
            seen.add(key)

            # Tür belirle — Öncelik: MEBİ (REV17) > TUR_OVERRIDE > guess_tur > pozisyon_default > '—'
            el = e.lower()
            mebi_tur = mebi_lookup.get(yazarSlug, {}).get(slug)
            tur = mebi_tur or TUR_OVERRIDE.get(el) or guess_tur(e) or pozisyon_tur or '—'

            work = {
                'title': e,
                'slug': slug,
                'yazar': ad,
                'yazarSlug': yazarSlug,
                'donem': donem,
                'tur': tur,
                'yil': yil,
                'cikmis': False,  # ÖSYM'de geçti mi (varsayılan: hayır)
            }
            works.append(work)

    # occurrences'tan ÖSYM'de soruları geçen eserleri işaretle (yazar-eser eşleşmesi olmadığından şimdilik atla)
    # Mevcut Halit Ziya'nın Aşk-ı Memnu'su gibi ÇIKMIŞ eserleri tek tek işaretle (manuel):
    BILINEN_CIKMIS = {
        'ask-i-memnu', 'mai-ve-siyah', 'kirik-hayatlar', 'calikusu', 'sinekli-bakkal',
        'huzur', 'tutunamayanlar', 'yaban', 'kiralik-konak', 'sergüzest',
        'karabibik', 'intibah', 'arabasevdasi', 'araba-sevdasi', 'taassuk-i-talat-ve-fitnat',
        'kurk-mantolu-madonna', 'kuyucakli-yusuf', 'ince-memed', 'kucuk-aga',
        'devlet-ana', 'asilacak-kadin', 'safahat', 'piyale', 'kendi-gok-kubbemiz',
        'cile', 'mona-roza', 'han-duvarlari', 'sis', 'sessiz-gemi',
        'memleketimden-insan-manzaralari', 'vatan-yahut-silistre',
        'sair-evlenmesi', 'kesanli-ali-destani', 'falaka', 'kasagi',
        'memleket-hikayeleri', 'leyla-vu-mecnun', 'su-kasidesi', 'husn-u-ask',
        'mevlid', 'harname', 'kanuni-mersiyesi', 'safahat', 'cenge-giderken',
    }
    for w in works:
        if w['slug'] in BILINEN_CIKMIS:
            w['cikmis'] = True

    # alfabetik sırala
    works.sort(key=lambda x: x['title'].lower())

    OUT.write_text(json.dumps(works, ensure_ascii=False, indent=2), encoding='utf-8')
    size_kb = OUT.stat().st_size / 1024
    print(f"✓ {OUT.name} ({size_kb:.1f} KB)")

    # REV17 M2.b — Coverage gap raporu: authors.json'da olup MEBİ'de olmayan yazarlar
    # + MEBİ'de var ama eserleri 0 yazarlar (kısmi eksiklik)
    if mebi_lookup:
        coverage = {'authors_not_in_mebi': [], 'authors_no_eserler': [], 'mebi_only_extra': []}
        site_yazar_slugs = {slugify(a['name']): a['name'] for a in authors}
        mebi_yazar_slugs = set(mebi_lookup.keys())
        # Site'da var ama MEBİ'de hiç yok
        for slug, name in site_yazar_slugs.items():
            if slug not in mebi_yazar_slugs:
                # MEBİ'de tam eşleşme yoksa substring kontrolü (alias için)
                substring_match = any(slug in mk or mk in slug for mk in mebi_yazar_slugs if len(mk) >= 5)
                if not substring_match:
                    coverage['authors_not_in_mebi'].append(name)
        # MEBİ'de var ama eser çıkmamış (kapsam boşluğu)
        try:
            mw = json.loads(MEBI_WORKS.read_text(encoding='utf-8'))
            for mname, mdata in mw.items():
                if not mdata.get('eserler'):
                    coverage['authors_no_eserler'].append(mname)
                # Site'da olmayan ama MEBİ'de geçen yazarlar
                mslug = slugify(mname)
                if mslug not in site_yazar_slugs:
                    substring_match = any(mslug in s or s in mslug for s in site_yazar_slugs if len(s) >= 5)
                    if not substring_match:
                        coverage['mebi_only_extra'].append(mname)
        except Exception as e:
            print(f"⚠ Coverage gap: {e}")
        COVERAGE_GAP.parent.mkdir(parents=True, exist_ok=True)
        COVERAGE_GAP.write_text(
            json.dumps(coverage, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        print(f"  REV17 coverage_gap.json: site-not-in-mebi={len(coverage['authors_not_in_mebi'])}, no-eserler={len(coverage['authors_no_eserler'])}, mebi-only={len(coverage['mebi_only_extra'])}")
    print(f"  toplam eser: {len(works)}")
    print(f"  çıkmış işaretli: {sum(1 for w in works if w['cikmis'])}")
    # tür dağılımı
    from collections import Counter
    turler = Counter(w['tur'] for w in works)
    print(f"  tür dağılımı: {dict(turler.most_common(10))}")


if __name__ == '__main__':
    main()
