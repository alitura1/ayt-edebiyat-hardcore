# -*- coding: utf-8 -*-
"""
REV20 — Edebî Terimler/Kavramlar Taksonomisi

Her dönemin kendine özgü terim/tür/kavramları (fütüvvetname, sefaretname, sagu,
koşuk, gazel, tezkire...) tek çatıda. İki çıktı:
  1. data/terimler_kaynak.json        → generate_data.gen_terim_cards() kart üretir
  2. public/data/edebiyat/terimler.json → /terimler sayfası (sözlük) gösterir

Tanımlar MEBİ özet + ÖSYM kanonundan; SPOILER-FREE (tanım, terimin adını içermez →
'tanım → terim' sorusu çözülebilir kalır).

Aşamalı: REV20a = divan_nesir + isl_oncesi. REV20b/c diğer kategorileri ekler.
"""
import json
import sys
import io
import re
import unicodedata
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent.parent          # Edebiyat Analiz/
SITE = ROOT / 'edebiyat-site' / 'public' / 'data' / 'edebiyat'
OUT_KAYNAK = ROOT / 'data' / 'terimler_kaynak.json'
OUT_PAGE = SITE / 'terimler.json'

# Kategori → (etiket, topic-konu kodu, dönem etiketi, sıra)
KATEGORI = {
    'isl_oncesi':       ('İslamiyet Öncesi Türleri', 'islamiyet_oncesi_gecis', 'İslamiyet Öncesi / Sözlü Dönem', 10),
    'divan_nesir':      ('Divan Nesir Türleri',      'nesir_bilgisi',          'Divan Edebiyatı',                40),
}
DONEM_SIRA = {
    'İslamiyet Öncesi / Sözlü Dönem': 10,
    'Geçiş Dönemi': 15,
    'Halk Edebiyatı': 20,
    'Divan Edebiyatı': 40,
    'Tanzimat': 50,
    'Servet-i Fünun / Fecr-i Âti': 55,
    'Milli Edebiyat': 60,
    'Cumhuriyet': 70,
    'Genel / Şiir Bilgisi': 80,
    'Söz Sanatları': 82,
    'Batı Edebiyatı Akımları': 90,
}

# =====================================================================
# TERİMLER — (terim, kategori, tanim, ornek, ayirt_edici, ozellikler[])
#   tanim: terim adını GEÇİRMEZ (spoiler-free)
#   ozellikler: terim→özellik + negatif eleme için doğru özellikler
# =====================================================================
TERIMLER = [
    # ============ İSLAMİYET ÖNCESİ / SÖZLÜ DÖNEM ============
    ("Koşuk", "isl_oncesi",
     "Sığır ve şölen gibi törenlerde kopuz eşliğinde söylenen; aşk, doğa, yiğitlik konularını işleyen lirik şiir.",
     "Halk edebiyatındaki koşmanın atası sayılır.",
     "Sagu ÖLÜM/yas içindir; bu tür aşk-doğa-coşku içindir.",
     ["lirik", "kopuz eşliğinde", "aşk-doğa-yiğitlik", "sığır/şölen töreni"]),
    ("Sagu", "isl_oncesi",
     "Ölen bir kişinin ardından yuğ töreninde söylenen, yas ve övgü içeren ağıt niteliğindeki şiir.",
     "Alp Er Tunga Sagusu.",
     "Halk edebiyatında 'ağıt', Divan'da 'mersiye' karşılığıdır.",
     ["ağıt", "yuğ töreni", "ölüm/yas teması", "övgü"]),
    ("Sav", "isl_oncesi",
     "Geçmiş deneyimlerden doğan, kısa ve özlü söz; günümüz atasözünün karşılığı.",
     "Divânü Lugâti't-Türk'te birçok örneği geçer.",
     "Atasözünün İslamiyet öncesi adıdır; bir şiir türü değil özlü sözdür.",
     ["özlü söz", "atasözü karşılığı", "didaktik", "kısa"]),
    ("Destan (Sözlü Dönem)", "isl_oncesi",
     "Bir milletin hafızasında yer etmiş olağanüstü olayları, kahramanlıkları anlatan uzun manzum anlatı.",
     "Oğuz Kağan, Bozkurt, Ergenekon.",
     "Yapma destandan farkı: anonim ve sözlü gelenekten doğmasıdır.",
     ["uzun manzum", "kahramanlık", "olağanüstü öğeler", "anonim"]),
    ("Sığır", "isl_oncesi",
     "İslamiyet öncesi Türklerde yapılan sürek avı niteliğindeki tören; bu törenlerde şiirler söylenirdi.",
     "",
     "Şölen ziyafet/kurban töreni; bu ise AV törenidir.",
     ["sürek avı töreni", "şiir söylenir", "dini-toplumsal"]),
    ("Şölen (Toy)", "isl_oncesi",
     "İslamiyet öncesi Türklerde kurban sunulan dini ziyafet ve toplanma töreni.",
     "",
     "Yuğ yas, sığır av; bu ise ziyafet/kurban törenidir.",
     ["dini ziyafet", "kurban", "toplanma", "toy"]),
    ("Yuğ", "isl_oncesi",
     "Ölen kişinin ardından düzenlenen yas ve cenaze töreni; bu törende sagular söylenirdi.",
     "",
     "Sığır av, şölen ziyafet; bu ise YAS törenidir, sagu burada söylenir.",
     ["yas/cenaze töreni", "sagu söylenir", "ölüm"]),
    ("Ozan", "isl_oncesi",
     "Kopuz eşliğinde şiir söyleyen, destan anlatan sözlü dönem sanatçısı; halk edebiyatında 'âşık'ın karşılığı.",
     "",
     "Kam/baksı şair+hekim+büyücü; ozan ise daha çok şiir/destan söyleyendir.",
     ["şiir/destan söyler", "kopuz", "âşığın atası", "sözlü gelenek"]),
    ("Kam (Baksı / Şaman)", "isl_oncesi",
     "İslamiyet öncesi Türklerde hem şair hem hekim hem büyücü olan; dini törenleri yöneten sanatçı-din adamı.",
     "",
     "Ozan sadece şiir/destan söyler; bu kişi ayrıca hekimlik+büyü+din görevi taşır.",
     ["şair-hekim-büyücü", "dini tören yöneticisi", "çok işlevli"]),

    # ============ DİVAN NESİR TÜRLERİ ============
    ("Tezkire", "divan_nesir",
     "Şairlerin hayatlarını, eserlerini ve sanatlarını tanıtan; günümüz biyografi/antoloji karşılığı eser.",
     "Sehî Bey'in Heşt Behişt'i (Anadolu'da ilk örnek).",
     "Menakıbname VELİ kerameti anlatır; bu ŞAİR biyografisidir.",
     ["şair biyografisi", "antoloji", "sanat değerlendirmesi"]),
    ("Münşeat", "divan_nesir",
     "Resmi ve özel mektup ile çeşitli düzyazı örneklerinin bir araya getirildiği derleme.",
     "",
     "Tezkire şair biyografisi; bu MEKTUP/yazı örnekleri derlemesidir.",
     ["mektup derlemesi", "düzyazı örnekleri", "üslup örneği"]),
    ("Fütüvvetname", "divan_nesir",
     "Ahilik/fütüvvet teşkilatının görgü, ahlak ve âdâb kurallarını anlatan öğretici düzyazı.",
     "",
     "Menakıbname keramet, siyasetname devlet yönetimi; bu AHİ/meslek ahlakı kurallarıdır.",
     ["ahi teşkilatı", "meslek ahlakı", "görgü/âdâb", "öğretici"]),
    ("Gazavatname", "divan_nesir",
     "Orduların akınlarını, savaşlarını ve zaferlerini manzum ya da mensur anlatan; tarihe kaynaklık eden eser.",
     "",
     "Sefaretname elçilik, seyahatname gezi; bu SAVAŞ/zafer anlatısıdır.",
     ["savaş/zafer", "ordu akınları", "tarihsel kaynak"]),
    ("Sefaretname", "divan_nesir",
     "Yabancı ülkeye gönderilen elçinin gözlem ve izlenimlerini aktardığı rapor/anı niteliğindeki eser.",
     "Yirmisekiz Mehmed Çelebi'nin Paris Sefaretnamesi.",
     "Seyahatname genel gezi; bu ELÇİLİK görevi raporudur.",
     ["elçi raporu", "yabancı ülke gözlemi", "XVII. yy sonrası"]),
    ("Sûrnâme", "divan_nesir",
     "Şehzadelerin sünnet, doğum ya da evlenme şenliklerini ayrıntılı biçimde anlatan eser.",
     "",
     "Gazavatname savaş; bu DÜĞÜN/şenlik anlatısıdır.",
     ["düğün/şenlik", "saray töreni", "protokol/ayrıntı"]),
    ("Siyasetname", "divan_nesir",
     "Devlet yönetimi, hükümdarlık ve adalet üzerine öğütler veren öğretici eser.",
     "Nizamülmülk'ün Siyasetnamesi.",
     "Pendname genel ahlak öğüdü; bu DEVLET YÖNETİMİ öğütleridir.",
     ["devlet yönetimi", "hükümdara öğüt", "adalet", "öğretici"]),
    ("Pendname (Nasihatname)", "divan_nesir",
     "Ahlak, erdem ve doğru yaşam üzerine genel öğütler içeren öğretici eser.",
     "Güvâhî'nin Pend-nâmesi.",
     "Siyasetname devlet yönetimi; bu GENEL ahlak/erdem öğütleridir.",
     ["genel ahlak öğüdü", "erdem", "didaktik"]),
    ("Kıyafetname", "divan_nesir",
     "İnsanın dış görünüşünden (yüz, beden) karakter ve huy çıkarımı yapan eser; fizyonomi.",
     "",
     "Tezkire biyografi; bu dış görünüş→KARAKTER okumasıdır (fizyonomi).",
     ["fizyonomi", "dış görünüş→huy", "öğretici"]),
    ("Seyahatname", "divan_nesir",
     "Gezilip görülen yerleri; halkları, gelenekleri ve coğrafyayı ayrıntılı gözlemle anlatan eser.",
     "Evliya Çelebi'nin Seyahatnamesi.",
     "Sefaretname elçilik raporu; bu GENEL gezi gözlemidir.",
     ["gezi gözlemi", "mekan/halk tasviri", "coğrafya"]),
    ("Menakıbname (Velayetname)", "divan_nesir",
     "Bir din büyüğünün, velinin olağanüstü hâllerini ve kerametlerini anlatan eser.",
     "Hacı Bektaş Veli Velâyetnâmesi.",
     "Tezkire şair biyografisi; bu VELİ kerameti anlatısıdır.",
     ["veli kerameti", "din büyüğü", "olağanüstü hâller", "menkıbe"]),
    ("Siyer", "divan_nesir",
     "Hz. Muhammed'in hayatını, kişiliğini ve savaşlarını anlatan eser.",
     "",
     "Menakıbname veli kerameti; bu HZ. MUHAMMED'in hayatıdır.",
     ["Hz. Muhammed'in hayatı", "İslam tarihi", "biyografik"]),
    ("Münazara", "divan_nesir",
     "İki kavramın, varlığın ya da kişinin karşılıklı üstünlük tartışmasını konu alan eser.",
     "",
     "Bir tartışma/karşılaştırma metnidir; öğüt veya biyografi değildir.",
     ["karşılıklı tartışma", "üstünlük iddiası", "iki taraf"]),
    ("Lugat (Sözlük)", "divan_nesir",
     "Sözcüklerin anlamlarını veren; iki dil arasında karşılık sunabilen başvuru eseri.",
     "Divânü Lugâti't-Türk, Muhakemetü'l-Lugateyn.",
     "Tezkire biyografi; bu SÖZCÜK/anlam başvuru eseridir.",
     ["sözlük", "kelime anlamı", "başvuru eseri"]),
]


def slugify(s):
    s = unicodedata.normalize('NFD', str(s))
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace('ı', 'i').replace('ş', 's').replace('ç', 'c').replace('ğ', 'g').replace('ö', 'o').replace('ü', 'u')
    return re.sub(r'^-|-$', '', re.sub(r'[^a-z0-9]+', '-', s))


def main():
    # Spoiler kontrolü: tanım, terim adını (veya ana kökünü) içermemeli
    spoiler = []
    kaynak = []
    for terim, kat, tanim, ornek, ayirt, ozellikler in TERIMLER:
        if kat not in KATEGORI:
            print(f"⚠ Bilinmeyen kategori: {kat} ({terim})")
            continue
        kat_label, konu, donem_label, _ = KATEGORI[kat]
        # spoiler: terimin ilk kelimesinin kökü tanımda geçiyor mu
        ana = slugify(terim.split('(')[0].split(' ')[0])
        if ana and ana in slugify(tanim):
            spoiler.append(terim)
        kaynak.append({
            'terim': terim,
            'slug': slugify(terim),
            'kategori': kat,
            'kategori_label': kat_label,
            'konu': konu,
            'donem': donem_label,
            'tanim': tanim,
            'ornek': ornek,
            'ayirt_edici': ayirt,
            'ozellikler': ozellikler,
        })

    OUT_KAYNAK.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_KAYNAK, 'w', encoding='utf-8') as f:
        json.dump({'_meta': {'toplam': len(kaynak), 'kategori_sayisi': len(set(t['kategori'] for t in kaynak))},
                   'terimler': kaynak}, f, ensure_ascii=False, indent=2)

    # Sayfa görüntü yapısı: dönem → kategori → terimler
    from collections import OrderedDict
    by_donem = OrderedDict()
    for t in kaynak:
        by_donem.setdefault(t['donem'], OrderedDict())
        by_donem[t['donem']].setdefault((t['kategori'], t['kategori_label']), [])
        by_donem[t['donem']][(t['kategori'], t['kategori_label'])].append({
            'terim': t['terim'], 'tanim': t['tanim'], 'ornek': t['ornek'], 'ayirt_edici': t['ayirt_edici'],
        })
    page = {'donemler': []}
    for donem in sorted(by_donem, key=lambda d: DONEM_SIRA.get(d, 99)):
        kats = []
        for (kat, kat_label), terimler in by_donem[donem].items():
            kats.append({'kategori': kat, 'kategori_label': kat_label, 'terimler': terimler})
        page['donemler'].append({'donem': donem, 'kategoriler': kats})
    with open(OUT_PAGE, 'w', encoding='utf-8') as f:
        json.dump(page, f, ensure_ascii=False, indent=2)

    print(f"✓ terimler_kaynak.json: {len(kaynak)} terim, {len(set(t['kategori'] for t in kaynak))} kategori")
    print(f"✓ terimler.json (sayfa): {len(page['donemler'])} dönem")
    if spoiler:
        print(f"⚠ SPOILER riski (tanım terim adını içeriyor): {spoiler}")
    else:
        print("✓ Spoiler kontrolü temiz (tanımlar terim adını içermiyor)")


if __name__ == '__main__':
    main()
