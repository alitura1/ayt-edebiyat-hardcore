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
    'isl_oncesi':         ('İslamiyet Öncesi Türleri',   'islamiyet_oncesi_gecis', 'İslamiyet Öncesi / Sözlü Dönem', 10),
    # Halk Edebiyatı
    'halk_anonim':        ('Anonim Halk Şiiri',          'halk_edebiyati',         'Halk Edebiyatı', 20),
    'halk_asik_bicim':    ('Âşık Edebiyatı Nazım Biçimleri', 'halk_edebiyati',     'Halk Edebiyatı', 21),
    'halk_asik_tur':      ('Âşık Edebiyatı Nazım Türleri (Koşma Konuları)', 'halk_edebiyati', 'Halk Edebiyatı', 22),
    'halk_tekke':         ('Tekke / Tasavvuf Nazım Türleri', 'halk_edebiyati',     'Halk Edebiyatı', 23),
    'halk_nesir':         ('Halk Nesri / Anonim Türler',  'masal_fabl_destan',     'Halk Edebiyatı', 24),
    'halk_seyirlik':      ('Geleneksel Türk Tiyatrosu',   'geleneksel_tiyatro',    'Halk Edebiyatı', 25),
    'tasavvuf_kavram':    ('Tasavvuf Kavramları',         'halk_edebiyati',        'Halk Edebiyatı', 26),
    # Divan Edebiyatı
    'divan_nazim_bicim':  ('Divan Nazım Biçimleri',       'divan_edebiyati',       'Divan Edebiyatı', 41),
    'divan_nazim_tur':    ('Divan Nazım Türleri (Konuya Göre)', 'divan_edebiyati',  'Divan Edebiyatı', 42),
    'divan_gazel_terim':  ('Gazel/Kaside Terimleri',      'divan_edebiyati',       'Divan Edebiyatı', 43),
    'divan_uslup':        ('Divan Üslupları',             'divan_edebiyati',       'Divan Edebiyatı', 44),
    'divan_nesir':        ('Divan Nesir Türleri',         'nesir_bilgisi',          'Divan Edebiyatı', 45),
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

    # ============ HALK — ANONİM ŞİİR ============
    ("Mâni", "halk_anonim",
     "Çoğunlukla yedi heceli, dört dizeli (aaxa); ilk iki dizesi doldurma olan, asıl anlamın son iki dizede verildiği anonim ürün.",
     "Düz, kesik (cinaslı), yedekli türleri vardır.",
     "Koşma on bir heceli ve âşık ürünüdür; bu yedi heceli ve anonimdir.",
     ["anonim", "yedi heceli", "aaxa uyak", "dört dize", "ilk iki dize doldurma"]),
    ("Türkü", "halk_anonim",
     "Bir ezgiyle söylenen; bentlerden ve her bendin sonunda yinelenen kavuştaktan (nakarat) oluşan anonim ürün.",
     "",
     "Mâni tek dörtlüktür; bu bent + kavuştak yapısındadır.",
     ["ezgiyle söylenir", "kavuştak/nakarat", "bent yapısı", "anonim"]),
    ("Ninni", "halk_anonim",
     "Çocuğu uyutmak amacıyla ezgiyle söylenen; annenin duygularını yansıtan anonim ürün.",
     "",
     "Ağıt ölüm acısı içindir; bu uyutma/sevgi amaçlıdır.",
     ["çocuğu uyutmak", "ezgili", "anne duygusu", "anonim"]),
    ("Ağıt (Anonim)", "halk_anonim",
     "Ölüm, hastalık, doğal afet gibi acı olaylar karşısında duyulan üzüntüyü dile getiren anonim söyleyiş.",
     "",
     "İslamiyet öncesi karşılığı sagu, Divan'da mersiyedir.",
     ["ölüm/acı teması", "üzüntü", "anonim", "yas"]),
    ("Bilmece", "halk_anonim",
     "Bir nesne ya da kavramı kapalı biçimde tanımlayıp buldurmayı amaçlayan, kalıplaşmış anonim söz.",
     "",
     "Tekerleme ses oyunudur; bu buldurma amaçlıdır.",
     ["buldurma amaçlı", "kapalı tanım", "kalıplaşmış", "anonim"]),
    ("Tekerleme", "halk_anonim",
     "Ses ve sözcük benzerliğine dayanan, çoğu zaman mantık dışı, oyun ve masal başlarında söylenen ritmik söz.",
     "Masal döşemesi (bir varmış bir yokmuş...).",
     "Bilmece buldurur; bu ritim/ses oyunu içindir.",
     ["ses oyunu", "mantık dışı", "ritmik", "masal döşemesi"]),

    # ============ HALK — ÂŞIK NAZIM BİÇİMLERİ ============
    ("Koşma", "halk_asik_bicim",
     "On birli hece ölçüsüyle, dört dizeli bentlerden oluşan; aşk, doğa ve özlem konularını işleyen âşık şiiri biçimi.",
     "Karacaoğlan'ın koşmaları.",
     "Mâni yedi heceli ve anonimdir; bu on bir heceli ve âşık ürünüdür.",
     ["on bir hece", "dörtlük bentler", "âşık ürünü", "aşk-doğa", "son dörtlükte mahlas"]),
    ("Semai (Âşık)", "halk_asik_bicim",
     "Sekizli hece ölçüsüyle, kendine özgü bir ezgiyle söylenen; koşmaya benzeyen lirik âşık şiiri biçimi.",
     "",
     "Koşma on bir, bu sekiz hecelidir; varsağıdan farkı yiğitçe eda taşımamasıdır.",
     ["sekiz hece", "özel ezgi", "âşık ürünü", "lirik"]),
    ("Varsağı", "halk_asik_bicim",
     "Sekizli hece ölçüsüyle, yiğitçe ve mertçe bir edayla; 'bre, behey' gibi seslenişlerle söylenen âşık şiiri biçimi.",
     "Dadaloğlu, Karacaoğlan.",
     "Semai lirik/yumuşak; bu yiğitçe/mertçe edalıdır.",
     ["sekiz hece", "yiğitçe eda", "bre/behey nidası", "âşık ürünü"]),
    ("Destan (Âşık)", "halk_asik_bicim",
     "Aşıkların savaş, kahramanlık, salgın ya da mizah gibi konuları uzun uzun anlattığı; en uzun âşık şiiri biçimi.",
     "",
     "Koşma kısadır; bu en uzun biçimdir ve olay anlatır.",
     ["en uzun biçim", "olay anlatımı", "dörtlük", "çok konulu"]),

    # ============ HALK — ÂŞIK NAZIM TÜRLERİ (KOŞMA KONULARI) ============
    ("Güzelleme", "halk_asik_tur",
     "Bir kişiyi, doğayı ya da sevgiliyi övmek; güzelliği yüceltmek amacıyla söylenen koşma konusu.",
     "Karacaoğlan.",
     "Koçaklama kahramanlık; bu güzellik/övgü içindir.",
     ["övgü", "sevgili-doğa güzelliği", "lirik", "Karacaoğlan"]),
    ("Koçaklama", "halk_asik_tur",
     "Savaş, kahramanlık ve yiğitlik konularını coşkulu bir dille işleyen koşma konusu.",
     "Köroğlu, Dadaloğlu.",
     "Güzelleme aşk/övgü; bu kahramanlık/coşkudur.",
     ["kahramanlık", "yiğitlik", "coşku", "Köroğlu-Dadaloğlu"]),
    ("Taşlama", "halk_asik_tur",
     "Bir kişiyi ya da toplumsal düzeni eleştirmek, yermek amacıyla söylenen koşma konusu.",
     "Seyrani.",
     "Divan'daki hicviyenin karşılığıdır.",
     ["yergi/eleştiri", "toplumsal", "Seyrani"]),

    # ============ HALK — TEKKE / TASAVVUF NAZIM TÜRLERİ ============
    ("İlahi", "halk_tekke",
     "Allah aşkını, dini ve tasavvufi düşünceyi; tarikat ayrımı gözetmeden ezgiyle dile getiren tekke şiiri.",
     "Yunus Emre.",
     "Nefes Bektaşilere özgüdür; bu tarikat ayrımı gözetmez.",
     ["Allah aşkı", "ezgili", "tasavvuf", "Yunus Emre"]),
    ("Nefes", "halk_tekke",
     "Bektaşi şairlerinin söylediği; varlık birliğini ve tasavvufi neşeyi kimi zaman iğneli bir dille işleyen tekke şiiri.",
     "Pir Sultan Abdal.",
     "İlahi genel tasavvuf; bu özellikle Bektaşi geleneğindendir.",
     ["Bektaşi", "varlık birliği", "kimi zaman iğneli", "Pir Sultan"]),
    ("Nutuk", "halk_tekke",
     "Tarikata yeni girenlere yol ve âdâbı öğretmek için söylenen öğretici tekke şiiri.",
     "",
     "Devriye 'devir' felsefesini anlatır; bu öğüt/öğreti içindir.",
     ["öğretici", "tarikat âdâbı", "didaktik", "yeni dervişlere"]),
    ("Devriye", "halk_tekke",
     "Varlığın Hak'tan çıkıp tekrar Hakk'a dönüşü (devir) inancını anlatan tekke şiiri.",
     "",
     "Nutuk öğüt verir; bu 'devir' felsefesini işler.",
     ["devir felsefesi", "Hak'tan çıkış-dönüş", "tasavvufi", "felsefi"]),
    ("Şathiye", "halk_tekke",
     "Dini konuları, ilk bakışta aykırı/saçma görünen ama derinde tasavvufi anlam taşıyan iğneli ve mizahi bir dille işleyen tekke şiiri.",
     "Kaygusuz Abdal.",
     "İlahi ciddi/lirik; bu mizahi ve görünüşte aykırıdır.",
     ["mizahi/iğneli", "görünüşte aykırı", "derinde tasavvuf", "Kaygusuz Abdal"]),

    # ============ HALK NESRİ / ANONİM TÜRLER ============
    ("Halk Hikâyesi", "halk_nesir",
     "Genellikle aşk ya da kahramanlık konulu; nazım-nesir karışık, âşıklarca anlatılan, destandan romana geçiş sayılan tür.",
     "Kerem ile Aslı, Köroğlu.",
     "Destan tümüyle manzumdur; bu nazım-nesir karışıktır.",
     ["nazım-nesir karışık", "aşk/kahramanlık", "âşık anlatır", "destan-roman geçişi"]),
    ("Masal", "halk_nesir",
     "Olağanüstü olay ve kişilerin yer aldığı; belirli bir zaman-mekâna bağlı olmayan, tekerlemeli anonim anlatı.",
     "",
     "Efsane gerçeklik iddialıdır; bu tümüyle hayalîdir.",
     ["olağanüstü", "hayalî", "tekerleme/döşeme", "anonim", "ders verir"]),
    ("Efsane", "halk_nesir",
     "Bir varlığın, yerin ya da olayın oluşumunu; inanış ögesiyle ve gerçek olduğu iddiasıyla açıklayan anlatı.",
     "",
     "Masal hayalîdir; bu gerçeklik iddiası taşır. Menkıbe veli kerameti içindir.",
     ["oluşum açıklar", "gerçeklik iddiası", "inanış ögesi", "olağanüstü"]),
    ("Menkıbe", "halk_nesir",
     "Bir din büyüğünün ya da velinin kerametlerini anlatan, inanca dayalı anlatı.",
     "",
     "Efsane genel oluşum; bu veli kerameti anlatır.",
     ["veli kerameti", "din büyüğü", "inanç", "olağanüstü hâl"]),
    ("Fıkra (Halk)", "halk_nesir",
     "Toplumsal bir gerçeği güldürü ve nükteyle, kısa bir olay çevresinde anlatan anonim/sözlü tür.",
     "Nasreddin Hoca, Bektaşi fıkraları.",
     "Gazete fıkrası yazılı ve imzalıdır; bu sözlü ve anonimdir.",
     ["güldürü/nükte", "kısa olay", "sözlü-anonim", "ders verir"]),

    # ============ GELENEKSEL TÜRK TİYATROSU ============
    ("Karagöz", "halk_seyirlik",
     "Deriden yapılmış tasvirlerin perde arkasından ışıkla yansıtıldığı gölge oyunu; giriş-muhavere-fasıl-bitiş bölümlerinden oluşur.",
     "",
     "Orta oyununda canlı oyuncu vardır; bu gölge/tasvir oyunudur.",
     ["gölge oyunu", "tasvir/perde", "dört bölüm", "Hacivat-Karagöz"]),
    ("Orta Oyunu", "halk_seyirlik",
     "Çevresi seyircilerle çevrili açık alanda (palanga), canlı oyuncularla doğaçlama oynanan geleneksel oyun.",
     "",
     "Karagöz gölge oyunudur; bu canlı oyuncularla oynanır.",
     ["açık alan/palanga", "canlı oyuncu", "doğaçlama", "Pişekâr-Kavuklu"]),
    ("Meddah", "halk_seyirlik",
     "Tek kişilik anlatıcının; mendil ve sopa kullanarak taklitlerle bir hikâye anlattığı seyirlik tür.",
     "",
     "Karagöz/orta oyunu çok kişilik; bu tek kişiliktir.",
     ["tek kişilik", "mendil-sopa", "taklit", "kahvehane"]),
    ("Köy Seyirlik Oyunu", "halk_seyirlik",
     "Tarım toplumunda düğün, bayram ve mevsim geçişlerinde; bolluk-bereket dileğiyle amatörce oynanan törensel/ritüel oyunlar.",
     "",
     "Karagöz/meddah profesyonelce şehirde oynanır; bu kırsalda amatör ve ritüeldir.",
     ["amatör oyuncu", "mevsim ritüeli", "bolluk-bereket dileği", "törensel"]),

    # ============ TASAVVUF KAVRAMLARI ============
    ("Vahdet-i Vücud", "tasavvuf_kavram",
     "Varlığın tek olduğu; var olan her şeyin Hakk'ın bir görünümü/yansıması sayıldığı tasavvuf anlayışı.",
     "İbnü'l-Arabî.",
     "Fenafillah bireyin yok oluşu hâlidir; bu bir varlık öğretisidir.",
     ["varlık birliği", "her şey Hakk'ın yansıması", "İbnü'l-Arabî", "öğreti"]),
    ("Fenafillah", "tasavvuf_kavram",
     "Kişinin kendi benliğinden geçip varlığını Allah'ta yok etmesi/eritmesi hâli.",
     "",
     "Vahdet-i vücud bir öğretidir; bu bireysel bir manevi hâldir.",
     ["benlikten geçiş", "Allah'ta yok oluş", "manevi hâl", "tasavvuf hedefi"]),
    ("Tecelli", "tasavvuf_kavram",
     "İlahi varlığın evrendeki nesne ve olaylarda görünür/belirir hâle gelmesi.",
     "",
     "Fenafillah yok oluş; bu görünür olma/belirmedir.",
     ["ilahi görünüm", "belirme", "vahdet-i vücud ile ilişkili"]),
    ("İnsan-ı Kâmil", "tasavvuf_kavram",
     "Tasavvufta olgunluğun zirvesine ulaşmış; Hakk'ı kendinde yansıtan ideal, olgun insan.",
     "",
     "Bir kavram/insandır, hâl değildir.",
     ["olgun insan", "manevi zirve", "Hakk'ı yansıtır"]),

    # ============ DİVAN NAZIM BİÇİMLERİ ============
    ("Gazel", "divan_nazim_bicim",
     "Beyitlerle yazılan; ilk beyti kendi arasında, sonraki beyitleri 'aa-ba-ca' düzeninde uyaklı; çoğunlukla aşk-şarap-güzellik konulu biçim.",
     "",
     "Kaside uzun ve övgü amaçlıdır; bu kısa ve aşk konuludur.",
     ["beyit", "aa-ba-ca uyak", "beş-on beş beyit", "aşk-şarap", "matla-makta"]),
    ("Kaside", "divan_nazim_bicim",
     "Genellikle bir büyüğü övmek için yazılan; gazelle aynı uyak düzeninde ama daha uzun (otuz üç-doksan dokuz beyit) biçim.",
     "",
     "Gazel kısa ve aşk konuludur; bu uzun ve övgü amaçlıdır.",
     ["övgü/methiye", "uzun (33-99 beyit)", "aa-ba-ca uyak", "nesib-girizgâh-methiye bölümleri"]),
    ("Mesnevi", "divan_nazim_bicim",
     "Her beyti kendi içinde uyaklı (aa-bb-cc) olan; uzun aşk, kahramanlık ya da öğretici konuların işlendiği biçim.",
     "Leyla vü Mecnun, Hüsn ü Aşk.",
     "Gazel/kasidede tek uyak sürer; bu her beyitte ayrı uyaktır.",
     ["aa-bb-cc uyak", "uzun konu", "hikâye/öğreti", "her beyit ayrı uyak"]),
    ("Rubai", "divan_nazim_bicim",
     "Tek dörtlükten oluşan; kendine özgü aruz kalıplarıyla yazılan, felsefi-tasavvufi düşünceyi yoğun anlatan biçim.",
     "Mevlana, Ömer Hayyam.",
     "Tuyuğ Türklere özgü ve cinaslıdır; bu İran kökenlidir.",
     ["tek dörtlük", "aaxa", "felsefi düşünce", "İran kökenli"]),
    ("Tuyuğ", "divan_nazim_bicim",
     "Türklerin Divan edebiyatına kazandırdığı; tek dörtlükten oluşan, cinaslı uyak kullanılan, mâni etkili biçim.",
     "Kadı Burhanettin, Nesimî.",
     "Rubai İran kökenlidir; bu Türklere özgü ve cinaslıdır.",
     ["Türklere özgü", "tek dörtlük", "cinaslı uyak", "mâni etkili"]),
    ("Şarkı", "divan_nazim_bicim",
     "Bestelenmek üzere yazılan; dörtlük bentli, nakaratlı (her bendin belli dizesi yinelenen) biçim.",
     "Nedim.",
     "Murabba bestelenmek için değildir; bu bestelenir ve nakaratlıdır.",
     ["bestelenir", "nakarat", "dörtlük bent", "Nedim"]),
    ("Müstezat", "divan_nazim_bicim",
     "Bir gazelin her dizesine kısa bir dize (ziyade) eklenerek oluşturulan biçim.",
     "",
     "Gazelden farkı her dizeye eklenen kısa ziyade dizelerdir.",
     ["gazel + ziyade dize", "uzun-kısa dize", "Divan biçimi"]),
    ("Terkib-i Bend", "divan_nazim_bicim",
     "Bentlerden oluşan; her bendin sonunda farklı bir vasıta beyti bulunan; çoğunlukla mersiye/toplumsal eleştiri konulu biçim.",
     "Bağdatlı Ruhi, Ziya Paşa.",
     "Terci-i bendde vasıta beyti aynıdır; burada her bentte farklıdır.",
     ["bentler", "farklı vasıta beyti", "mersiye/eleştiri"]),
    ("Terci-i Bend", "divan_nazim_bicim",
     "Bentlerden oluşan; her bendin sonunda aynı vasıta beyti yinelenen biçim.",
     "Ziya Paşa.",
     "Terkib-i bendde vasıta beyti değişir; burada aynı beyit tekrarlanır.",
     ["bentler", "aynı vasıta beyti tekrar", "Divan biçimi"]),

    # ============ DİVAN NAZIM TÜRLERİ (KONUYA GÖRE) ============
    ("Tevhid", "divan_nazim_tur",
     "Allah'ın birliğini ve yüceliğini anlatan Divan şiiri konusu.",
     "",
     "Münacat yakarış/duadır; bu Allah'ın birliğini anlatır.",
     ["Allah'ın birliği", "dini", "yüceltme"]),
    ("Münacat", "divan_nazim_tur",
     "Allah'a yakarış, dua ve yalvarışı içeren Divan şiiri konusu.",
     "",
     "Tevhid birliği anlatır; bu yakarış/duadır.",
     ["Allah'a yakarış", "dua", "dini"]),
    ("Naat", "divan_nazim_tur",
     "Hz. Muhammed'i övmek için yazılan Divan şiiri konusu.",
     "Fuzuli, Su Kasidesi.",
     "Methiye devlet büyüğünü över; bu peygamberi över.",
     ["Hz. Muhammed övgüsü", "dini", "Su Kasidesi"]),
    ("Methiye", "divan_nazim_tur",
     "Bir devlet büyüğünü ya da ileri geleni övmek için yazılan; kasidenin de bir bölümü olan tür.",
     "",
     "Naat peygamberi över; bu devlet büyüğünü över.",
     ["devlet büyüğü övgüsü", "kasidede bölüm", "övgü"]),
    ("Mersiye", "divan_nazim_tur",
     "Bir kişinin ölümünden duyulan üzüntüyü anlatan; ölenin meziyetlerini öven tür.",
     "Baki, Kanuni Mersiyesi.",
     "Halk şiirinde ağıt, İslam öncesinde sagu karşılığıdır.",
     ["ölüm/yas", "övgü", "Baki Kanuni Mersiyesi"]),
    ("Hicviye", "divan_nazim_tur",
     "Bir kişiyi ya da durumu yermek, eleştirmek amacıyla yazılan tür.",
     "Nef'i, Siham-ı Kaza.",
     "Halk şiirindeki taşlamanın karşılığıdır.",
     ["yergi/eleştiri", "Nef'i Siham-ı Kaza", "alay"]),
    ("Fahriye", "divan_nazim_tur",
     "Şairin kendini ve sanatını övdüğü bölüm/tür.",
     "",
     "Methiye başkasını över; bu şairin kendini övmesidir.",
     ["şairin kendini övmesi", "kasidede bölüm", "övünme"]),

    # ============ GAZEL / KASİDE TERİMLERİ ============
    ("Matla", "divan_gazel_terim",
     "Gazel ya da kasidenin, iki dizesi de birbiriyle uyaklı olan ilk beyti.",
     "",
     "Makta son beyittir; bu ilk beyittir.",
     ["ilk beyit", "iki dize uyaklı", "gazel başı"]),
    ("Makta", "divan_gazel_terim",
     "Gazelin, şairin takma adının (mahlas) geçtiği son beyti.",
     "",
     "Matla ilk beyittir; bu son beyittir, şair adı burada geçer.",
     ["son beyit", "mahlas burada", "gazel sonu"]),
    ("Mahlas", "divan_gazel_terim",
     "Divan şairinin şiirlerinde kullandığı takma ad; çoğunlukla son beyitte geçer.",
     "",
     "Bir beyit değil, şairin takma adıdır.",
     ["takma ad", "son beyitte", "tac beyit"]),
    ("Beytü'l-gazel (Şah Beyit)", "divan_gazel_terim",
     "Bir gazelin en güzel, en başarılı sayılan beyti.",
     "",
     "Yeri sabit değildir; en güzel beyittir.",
     ["en güzel beyit", "şah beyit"]),

    # ============ DİVAN ÜSLUPLARI ============
    ("Sebk-i Hindi", "divan_uslup",
     "On yedinci yüzyılda yaygınlaşan; derin hayaller, ince/karmaşık mazmunlar ve kapalı söyleyişe dayanan üslup.",
     "Naili, Şeyh Galip.",
     "Mahallileşme yerlilik/sadelik; bu kapalılık/derin hayaldir.",
     ["derin hayal", "kapalı söyleyiş", "ince mazmun", "Naili-Şeyh Galip"]),
    ("Mahallileşme", "divan_uslup",
     "Divan şiirine günlük yaşamdan, halk söyleyişinden ve yerli unsurlardan ögeler katma eğilimi.",
     "Nedim.",
     "Sebk-i Hindi kapalı/derindir; bu yerli/sade/günlüktür.",
     ["yerlilik", "günlük yaşam", "halk söyleyişi", "Nedim"]),
    ("Türkî-i Basit", "divan_uslup",
     "Divan şiirinde Arapça-Farsça tamlamalardan kaçınıp sade Türkçeyle yazma akımı.",
     "Aydınlı Visali, Tatavlalı Mahremi.",
     "Mahallileşme yerli ögelerdir; bu özellikle sade Türkçe/terkipsizliktir.",
     ["sade Türkçe", "terkipsiz", "yabancı tamlamadan kaçınma"]),

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
