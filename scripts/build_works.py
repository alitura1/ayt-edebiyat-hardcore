"""
REV6 M4 — Eserler veritabanı: authors.json'daki diger_eserler + occurrences'tan üretilir.
Output: public/data/works.json
"""
import json, sys, io, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = Path(__file__).parent.parent
AUTHORS = BASE / 'public' / 'data' / 'authors.json'
OUT = BASE / 'public' / 'data' / 'works.json'


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
}


def main():
    authors = json.loads(AUTHORS.read_text(encoding='utf-8'))

    works = []
    seen = set()  # (slug, yazarSlug) tekrar engelle

    for author in authors:
        ad = author['name']
        yazarSlug = slugify(ad)
        donem = author.get('donem') or (author.get('konular') or ['cumhuriyet'])[0]

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

            # Tür belirle
            el = e.lower()
            tur = TUR_OVERRIDE.get(el) or guess_tur(e) or '—'

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
    print(f"  toplam eser: {len(works)}")
    print(f"  çıkmış işaretli: {sum(1 for w in works if w['cikmis'])}")
    # tür dağılımı
    from collections import Counter
    turler = Counter(w['tur'] for w in works)
    print(f"  tür dağılımı: {dict(turler.most_common(10))}")


if __name__ == '__main__':
    main()
