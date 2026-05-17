"""
Tüm site verilerini üret:
- cards-auto.json     (~300 quiz kartı, ÖSYM tarzı çeldiricilerle)
- topics-index.json   (13 konu meta)
- authors.json        (85 yazar)
- predictions.json    (Bölüm 5)
- program.json        (Bölüm 6)
- glossary.json       (Bölüm 7)
"""
import json
import sys
import io
import random
import re
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # Edebiyat Analiz/
from mebi_map import MEBI_TOPIC, MEBI_SUB, MEBI_AUTHOR

BASE = Path(__file__).parent.parent.parent  # Edebiyat Analiz/
SITE = Path(__file__).parent.parent / 'public' / 'data'
SITE.mkdir(parents=True, exist_ok=True)

ANNOTATED = json.load(open(BASE / 'annotated_questions.json', encoding='utf-8'))

random.seed(42)  # deterministic kart sırası

TOPIC_LABEL = {
    'divan_edebiyati': 'Divan Edebiyatı',
    'cumhuriyet': 'Cumhuriyet Dönemi',
    'siir_bilgisi': 'Şiir Bilgisi',
    'soz_sanatlari': 'Söz Sanatları',
    'nesir_bilgisi': 'Nesir Bilgisi',
    'tanzimat': 'Tanzimat',
    'servet_i_funun_fecr_i_ati': 'Servet-i Fünun / Fecr-i Âti',
    'milli_edebiyat': 'Milli Edebiyat',
    'halk_edebiyati': 'Halk Edebiyatı',
    'islamiyet_oncesi_gecis': 'İslamiyet Öncesi / Geçiş',
    'geleneksel_tiyatro': 'Geleneksel Tiyatro',
    'masal_fabl_destan': 'Masal / Fabl / Destan',
    'edebi_akimlar': 'Edebi Akımlar',
}

# Yazar → Eserler veritabanı (kart üretimi için)
YAZAR_ESERLERI = {
    # Divan
    'Fuzuli': ['Leyla vü Mecnun', 'Su Kasidesi', 'Şikayetname', 'Beng ü Bâde', "Hadîkatü's-Suedâ", 'Rind u Zahid'],
    'Baki': ['Kanuni Mersiyesi', "Mealimü'l-Yakin"],
    'Nedim': ['Divan-ı Nedim', 'Şarkıları'],
    "Nef'i": ['Siham-ı Kaza', "Tuhfetü'l-Uşşak"],
    'Şeyh Galip': ['Hüsn ü Aşk', 'Şerh-i Cezîre-i Mesnevî'],
    'Nabi': ['Hayriye', 'Hayrabad', 'Sur-Name', "Tuhfetü'l-Haremeyn"],
    'Şeyhi': ['Harname', 'Hüsrev ü Şirin'],
    'Ahmedi': ['İskendername', 'Cemşid ü Hurşid'],
    'Süleyman Çelebi': ['Vesîletü\'n-Necât (Mevlid)'],
    'Hoca Dehhani': ['Divan'],
    'Necati Bey': ['Divan'],
    'Hayali Bey': ['Divan'],
    # Tekke / Halk
    'Yunus Emre': ['Divan', "Risaletü'n-Nushiyye"],
    'Mevlana': ['Mesnevî', 'Divan-ı Kebir', 'Fihi Mâ Fih', "Mecâlis-i Seb'a"],
    'Pir Sultan Abdal': ['Nefesler'],
    'Kaygusuz Abdal': ['Divan', 'Saraynâme', 'Budalanâme'],
    'Karacaoğlan': ['Şiirleri (güzelleme)'],
    'Köroğlu': ['Şiirleri (koçaklama)', 'Halk Hikayesi'],
    'Dadaloğlu': ['Şiirleri'],
    'Seyrani': ['Şiirleri (taşlama)'],
    'Aşık Veysel Şatıroğlu': ['Kara Toprak', 'Uzun İnce Bir Yoldayım'],
    'Bayburtlu Zihni': ['Şiirler'],
    # Tanzimat
    'Şinasi': ['Şair Evlenmesi', "Müntehabat-ı Eş'ar", 'Durub-ı Emsal-i Osmaniye', 'Tercüman-ı Ahvâl Mukaddimesi'],
    'Namık Kemal': ['İntibah', 'Cezmi', 'Vatan yahut Silistre', 'Gülnihal', 'Akif Bey', 'Zavallı Çocuk', 'Celaleddin Harzemşah'],
    'Ziya Paşa': ['Harabat', 'Şiir ve İnşa', 'Terkib-i Bend', 'Terci-i Bend'],
    'Ahmet Mithat Efendi': ['Felâtun Bey ile Râkım Efendi', 'Letaif-i Rivayet', 'Hasan Mellah'],
    'Şemsettin Sami': ['Taaşşuk-ı Talat ve Fitnat', 'Kamus-ı Türki', 'Kamus-ı Alâm'],
    'Recaizade Mahmut Ekrem': ['Araba Sevdası', 'Talim-i Edebiyat', 'Zemzeme', 'Pejmurde'],
    'Abdülhak Hamit Tarhan': ['Makber', 'Sahra', 'Belde', 'Tarık', 'Eşber', 'Finten'],
    'Samipaşazade Sezai': ['Sergüzeşt', 'Küçük Şeyler'],
    'Nabizade Nazım': ['Karabibik', 'Zehra'],
    'Muallim Naci': ['Demdeme', 'Lugat-i Naci'],
    'Ahmet Vefik Paşa': ['Cimri (çeviri)', 'Zoraki Tabip (çeviri)', 'Lehçe-i Osmani'],
    # SF
    'Halit Ziya Uşaklıgil': ['Mai ve Siyah', 'Aşk-ı Memnu', 'Kırık Hayatlar', 'Sefile', 'Nemide', 'Ferdi ve Şürekası', 'Bir Ölünün Defteri', 'Nesl-i Ahir', 'Kırk Yıl'],
    'Tevfik Fikret': ['Rübab-ı Şikeste', "Halûk'un Defteri", 'Sis', 'Tarih-i Kadim', 'Şermin'],
    'Cenap Şahabettin': ['Elhan-ı Şita', 'Tâmâtî', 'Hac Yolunda'],
    'Mehmet Rauf': ['Eylül'],
    'Hüseyin Cahit Yalçın': ['Edebî Hatıralarım'],
    'Süleyman Nazif': ['Çal Çoban Çal'],
    # Fecr-i Âti
    'Ahmet Haşim': ['Piyale', 'Göl Saatleri', 'Bize Göre', 'Frankfurt Seyahatnamesi'],
    # Milli Ed.
    'Ömer Seyfettin': ['Bomba', 'Pembe İncili Kaftan', 'Falaka', 'Kaşağı', 'Diyet', 'Yüksek Ökçeler', 'Forsa', 'Başını Vermeyen Şehit'],
    'Ziya Gökalp': ['Türkçülüğün Esasları', 'Kızılelma', 'Yeni Hayat', 'Altın Işık'],
    'Mehmet Emin Yurdakul': ['Türk Sazı', 'Cenge Giderken'],
    'Yakup Kadri Karaosmanoğlu': ['Yaban', 'Kiralık Konak', 'Nur Baba', 'Hüküm Gecesi', 'Ankara', 'Sodom ve Gomore', 'Panorama', 'Bir Serencam'],
    'Halide Edip Adıvar': ['Sinekli Bakkal', 'Ateşten Gömlek', 'Vurun Kahpeye', 'Handan', "Mev'ud Hüküm"],
    'Reşat Nuri Güntekin': ['Çalıkuşu', 'Yaprak Dökümü', 'Yeşil Gece', 'Dudaktan Kalbe', 'Acımak', 'Damga', 'Anadolu Notları'],
    'Refik Halit Karay': ['Memleket Hikayeleri', 'Gurbet Hikayeleri', 'Sürgün', 'Yezidin Kızı', 'Bugünün Saraylısı', 'Nilgün'],
    'Memduh Şevket Esendal': ['Çakıcının İlk Kurşunu', 'Otlakçı', 'Mendil Altında', 'Ayaşlı ve Kiracıları'],
    'Mithat Cemal Kuntay': ['Üç İstanbul'],
    'Ahmet Hikmet Müftüoğlu': ['Çağlayanlar', 'Gönül Hanım'],
    # Beş Hececiler
    'Faruk Nafiz Çamlıbel': ['Han Duvarları', 'Çoban Çeşmesi', 'Sanat'],
    'Halit Fahri Ozansoy': ['Cenk Duyguları', 'Baykuş', 'Sulara Doğru'],
    'Enis Behiç Koryürek': ['Miras'],
    'Yusuf Ziya Ortaç': ['Akından Akına'],
    'Orhan Seyfi Orhon': ['Fırtına ve Kar', 'Peri Kızı ile Çoban Hikayesi'],
    # Yedi Meşaleciler
    'Cevdet Kudret': ['Karagözler'],
    'Ziya Osman Saba': ['Sebil ve Güvercinler', 'Geçen Zaman'],
    'Sabri Esat Siyavuşgil': ['Odalar ve Sofalar'],
    'Yaşar Nabi Nayır': ['Kahramanlar'],
    'Vasfi Mahir Kocatürk': ['Varidat-ı Süleyman', 'Hayat Şarkıları'],
    'Kenan Hulusi Koray': ['Bahar Hikayeleri'],
    # Saf şiir / Bağımsızlar
    'Yahya Kemal Beyatlı': ['Kendi Gök Kubbemiz', 'Eski Şiirin Rüzgârıyle', 'Aziz İstanbul'],
    'Mehmet Akif Ersoy': ['Safahat', 'Süleymaniye Kürsüsünde'],
    'Cahit Sıtkı Tarancı': ['Otuz Beş Yaş', 'Düşten Güzel', 'Sonrası'],
    'Ahmet Hamdi Tanpınar': ['Huzur', 'Saatleri Ayarlama Enstitüsü', 'Beş Şehir', 'Mahur Beste', 'Sahnenin Dışındakiler'],
    'Ahmet Muhip Dıranas': ['Şiirler'],
    'Necip Fazıl Kısakürek': ['Çile', 'Kaldırımlar', 'Sakarya Türküsü', 'Bir Adam Yaratmak'],
    'Asaf Halet Çelebi': ['Lamelif', 'He'],
    'Behçet Necatigil': ['Eski Toprak', 'Divançe'],
    'Fazıl Hüsnü Dağlarca': ['Toprak Ana', "Çakır'ın Destanı", 'Üç Şehitler Destanı', 'Havaya Çizilen Dünya'],
    'Arif Nihat Asya': ['Bayrak', 'Heykeltıraş'],
    'Ahmet Kutsi Tecer': ['Şehnaz Faslı', 'Köşebaşı'],
    'Bedri Rahmi Eyüboğlu': ['Karadut'],
    'Cahit Külebi': ['Adamın Biri', 'Yangın'],
    # Garip
    'Orhan Veli Kanık': ['Garip', 'Yenisi', 'Vazgeçemediğim', 'Karşı'],
    'Oktay Rifat': ['Garip', 'Yaşayıp Ölmek Aşk ve Avarelik Üstüne Şiirler'],
    'Melih Cevdet Anday': ['Garip', 'Rahatı Kaçan Ağaç'],
    # II. Yeni
    'Cemal Süreya': ['Üvercinka', 'Göçebe', 'Beni Öp Sonra Doğur Beni'],
    'Edip Cansever': ['Yerçekimli Karanfil', 'Tragedyalar'],
    'Turgut Uyar': ['Tütünler Islak', 'Divan'],
    'İlhan Berk': ['Galile Denizi'],
    'Sezai Karakoç': ['Mona Roza', 'Hızırla Kırk Saat'],
    'Ece Ayhan': ['Bakışsız Bir Kedi Kara'],
    # Toplumcu
    'Nazım Hikmet': ['Memleketimden İnsan Manzaraları', 'Kuvâyi Milliye Destanı', 'Şeyh Bedrettin Destanı'],
    'Rıfat Ilgaz': ['Hababam Sınıfı'],
    'Ahmed Arif': ['Hasretinden Prangalar Eskittim'],
    'Ataol Behramoğlu': ['Bir Ermeni General'],
    # Hisar/Mavi
    'Munis Faik Ozansoy': ['Hayalden Hakikate'],
    'Mehmet Çınarlı': ['Gerçek Hayali Aştı'],
    'Attila İlhan': ['Ben Sana Mecburum', 'Duvar', 'Sisler Bulvarı', 'Yağmur Kaçağı', 'Bela Çiçeği'],
    # Roman / Hikaye - Toplumcu
    'Sabahattin Ali': ['Kuyucaklı Yusuf', 'Kürk Mantolu Madonna', 'İçimizdeki Şeytan', 'Değirmen', 'Kağnı', 'Ses', 'Yeni Dünya', 'Sırça Köşk'],
    'Yaşar Kemal': ['İnce Memed', 'Yer Demir Gök Bakır', 'Ortadirek', 'Demirciler Çarşısı Cinayeti'],
    'Orhan Kemal': ['Bereketli Topraklar Üzerinde', 'Murtaza', 'Eskici ve Oğulları', 'Cemile', 'Hanımın Çiftliği'],
    'Kemal Tahir': ['Devlet Ana', 'Esir Şehrin İnsanları', 'Yorgun Savaşçı', 'Köyün Kamburu'],
    'Fakir Baykurt': ['Yılanların Öcü'],
    'Talip Apaydın': ['Sarı Traktör'],
    'Mahmut Makal': ['Bizim Köy'],
    # Bireyin iç dünyası
    'Peyami Safa': ['9. Hariciye Koğuşu', 'Fatih Harbiye', "Matmazel Noraliya'nın Koltuğu", 'Yalnızız'],
    'Tarık Buğra': ['Küçük Ağa', 'Osmancık', 'Dönemeçte', 'Yağmur Beklerken', 'Firavun İmanı'],
    'Mustafa Kutlu': ['Sır', 'Yokuşa Akan Sular', 'Beyhude Ömrüm', 'Kapıları Açmak'],
    'Samiha Ayverdi': ['İbrahim Efendi Konağı', 'Mesihpaşa İmamı'],
    # Modernist
    'Oğuz Atay': ['Tutunamayanlar', 'Tehlikeli Oyunlar', 'Korkuyu Beklerken', 'Bir Bilim Adamının Romanı'],
    'Yusuf Atılgan': ['Aylak Adam', 'Anayurt Oteli'],
    'Bilge Karasu': ['Uzun Sürmüş Bir Günün Akşamı', 'Göçmüş Kediler Bahçesi', 'Gece'],
    'Orhan Pamuk': ['Beyaz Kale', 'Kara Kitap', 'Benim Adım Kırmızı', 'Kar', 'Masumiyet Müzesi'],
    'İhsan Oktay Anar': ['Puslu Kıtalar Atlası', "Kitabü'l-Hiyel", 'Suskunlar'],
    'Latife Tekin': ['Sevgili Arsız Ölüm', 'Berci Kristin Çöp Masalları'],
    'Hasan Ali Toptaş': ['Gölgesizler', 'Bin Hüzünlü Haz'],
    # Sait Faik & diğer
    'Sait Faik Abasıyanık': ['Semaver', 'Sarnıç', 'Şahmerdan', 'Lüzumsuz Adam', 'Mahalle Kahvesi', 'Havada Bulut', "Alemdağ'da Var Bir Yılan", 'Son Kuşlar', 'Medarı Maişet Motoru'],
    'Halikarnas Balıkçısı': ['Aganta Burina Burinata', 'Mavi Sürgün', "Anadolu'nun Sesi"],
    # Tiyatro
    'Haldun Taner': ['Keşanlı Ali Destanı', 'Sersem Kocanın Kurnaz Karısı', 'Eşeğin Gölgesi', 'Gözlerimi Kaparım Vazifemi Yaparım', 'On İkiye Bir Var'],
    'Turgut Özakman': ['Şu Çılgın Türkler', 'Ocak', 'Üç Destan'],
    'Necati Cumalı': ['Susuz Yaz', 'Mine'],
    'Güngör Dilmen': ["Midas'ın Kulakları", 'Canlı Maymun Lokantası'],
    'Turan Oflazoğlu': ['IV. Murat', 'Genç Osman'],
    # Deneme/Anı
    'Nurullah Ataç': ['Karalama Defteri', 'Günlerin Getirdiği'],
    'Suut Kemal Yetkin': ['Edebiyat Üzerine'],
    'Falih Rıfkı Atay': ['Çankaya', 'Zeytindağı', "Atatürk'ün Bana Anlattıkları"],
    # Geçiş dönemi
    'Yusuf Has Hacip': ['Kutadgu Bilig'],
    'Kaşgarlı Mahmut': ["Divânü Lügâti't-Türk"],
    'Edip Ahmet Yükneki': ["Atabetü'l Hakayık"],
    'Ahmet Yesevi': ['Divan-ı Hikmet'],
}

# Eser → Yazar reverse map
ESER_YAZAR = {}
for y, eserler in YAZAR_ESERLERI.items():
    for e in eserler:
        ESER_YAZAR[e] = y

# Yazar → Dönem
YAZAR_DONEM = {
    # Divan
    **{y: 'divan' for y in ['Fuzuli','Baki','Nedim',"Nef'i",'Şeyh Galip','Nabi','Şeyhi','Ahmedi','Süleyman Çelebi','Hoca Dehhani','Necati Bey','Hayali Bey']},
    # Tekke/Halk
    **{y: 'halk' for y in ['Yunus Emre','Mevlana','Pir Sultan Abdal','Kaygusuz Abdal','Karacaoğlan','Köroğlu','Dadaloğlu','Seyrani','Aşık Veysel Şatıroğlu','Bayburtlu Zihni']},
    # Tanzimat
    **{y: 'tanzimat' for y in ['Şinasi','Namık Kemal','Ziya Paşa','Ahmet Mithat Efendi','Şemsettin Sami','Recaizade Mahmut Ekrem','Abdülhak Hamit Tarhan','Samipaşazade Sezai','Nabizade Nazım','Muallim Naci','Ahmet Vefik Paşa']},
    # SF + Fecr-i Âti
    **{y: 'sf_fecr' for y in ['Halit Ziya Uşaklıgil','Tevfik Fikret','Cenap Şahabettin','Mehmet Rauf','Hüseyin Cahit Yalçın','Süleyman Nazif','Ahmet Haşim']},
    # Milli Ed.
    **{y: 'milli' for y in ['Ömer Seyfettin','Ziya Gökalp','Mehmet Emin Yurdakul','Yakup Kadri Karaosmanoğlu','Halide Edip Adıvar','Reşat Nuri Güntekin','Refik Halit Karay','Memduh Şevket Esendal','Mithat Cemal Kuntay','Ahmet Hikmet Müftüoğlu','Faruk Nafiz Çamlıbel','Halit Fahri Ozansoy','Enis Behiç Koryürek','Yusuf Ziya Ortaç','Orhan Seyfi Orhon']},
    # Cumhuriyet
    **{y: 'cumhuriyet' for y in ['Cevdet Kudret','Ziya Osman Saba','Sabri Esat Siyavuşgil','Yaşar Nabi Nayır','Vasfi Mahir Kocatürk','Kenan Hulusi Koray','Yahya Kemal Beyatlı','Mehmet Akif Ersoy','Cahit Sıtkı Tarancı','Ahmet Hamdi Tanpınar','Ahmet Muhip Dıranas','Necip Fazıl Kısakürek','Asaf Halet Çelebi','Behçet Necatigil','Fazıl Hüsnü Dağlarca','Arif Nihat Asya','Ahmet Kutsi Tecer','Bedri Rahmi Eyüboğlu','Cahit Külebi','Orhan Veli Kanık','Oktay Rifat','Melih Cevdet Anday','Cemal Süreya','Edip Cansever','Turgut Uyar','İlhan Berk','Sezai Karakoç','Ece Ayhan','Nazım Hikmet','Rıfat Ilgaz','Ahmed Arif','Ataol Behramoğlu','Munis Faik Ozansoy','Mehmet Çınarlı','Attila İlhan','Sabahattin Ali','Yaşar Kemal','Orhan Kemal','Kemal Tahir','Fakir Baykurt','Talip Apaydın','Mahmut Makal','Peyami Safa','Tarık Buğra','Mustafa Kutlu','Samiha Ayverdi','Oğuz Atay','Yusuf Atılgan','Bilge Karasu','Orhan Pamuk','İhsan Oktay Anar','Latife Tekin','Hasan Ali Toptaş','Sait Faik Abasıyanık','Halikarnas Balıkçısı','Haldun Taner','Turgut Özakman','Necati Cumalı','Güngör Dilmen','Turan Oflazoğlu','Nurullah Ataç','Suut Kemal Yetkin','Falih Rıfkı Atay']},
    # Geçiş
    **{y: 'gecis' for y in ['Yusuf Has Hacip','Kaşgarlı Mahmut','Edip Ahmet Yükneki','Ahmet Yesevi']},
}

# Dönem → topic kodu mapping
DONEM_TOPIC = {
    'divan': 'divan_edebiyati',
    'halk': 'halk_edebiyati',
    'tanzimat': 'tanzimat',
    'sf_fecr': 'servet_i_funun_fecr_i_ati',
    'milli': 'milli_edebiyat',
    'cumhuriyet': 'cumhuriyet',
    'gecis': 'islamiyet_oncesi_gecis',
}

# Akım → temsilciler
AKIM_TEMSILCI = {
    'Klasisizm': ['Molière', 'Racine', 'Corneille', 'La Fontaine', 'Boileau'],
    'Romantizm': ['Victor Hugo', 'Lamartine', 'Goethe', 'Schiller', 'Byron', 'Alfred de Musset'],
    'Realizm': ['Balzac', 'Stendhal', 'Flaubert', 'Dostoyevski', 'Tolstoy', 'Charles Dickens'],
    'Natüralizm': ['Émile Zola', 'Guy de Maupassant', 'Goncourt Kardeşler', 'Alphonse Daudet'],
    'Parnasizm': ['Théophile Gautier', 'Leconte de Lisle', 'José Maria de Heredia', 'François Coppée'],
    'Sembolizm': ['Charles Baudelaire', 'Paul Verlaine', 'Arthur Rimbaud', 'Stéphane Mallarmé', 'Edgar Allan Poe'],
    'Fütürizm': ['Marinetti'],
    'Dadaizm': ['Tristan Tzara', 'Hugo Ball', 'Hans Arp'],
    'Sürrealizm': ['André Breton', 'Louis Aragon', 'Paul Éluard', 'Salvador Dali'],
    'Egzistansiyalizm': ['Jean-Paul Sartre', 'Albert Camus', 'Kierkegaard', 'Heidegger'],
    'Ekspresyonizm': ['Franz Kafka', 'Strindberg', 'Trakl'],
}

AKIM_OZELLIK = {
    'Klasisizm': 'Akıl, sağduyu, antik kaynaklar, 3 birlik (zaman-mekan-eylem), soylu insan',
    'Romantizm': 'Duygu, hayal, doğa, kişisellik, halk, üç birlik reddi',
    'Realizm': 'Gözlem, gerçeklik, sıradan insan, günlük yaşam, bilim gibi yaklaşım',
    'Natüralizm': 'Bilimsel determinizm, çevre+genetik tutsağı, çirkin/hastalıklı yaşam, Émile Zola',
    'Parnasizm': 'Şiir + biçim mükemmelliği + objektif anlatım, antik konular, sanat sanat içindir',
    'Sembolizm': 'Sembol, sezgi, müzikalite, kapalılık, iç alem, ruh hali',
    'Fütürizm': 'Hız, makine, gelecek, geçmişin reddi, müze-kütüphane karşıtlığı',
    'Dadaizm': 'Sanat karşıtı, anlamsızlık, savaş tepkisi, kural yok',
    'Sürrealizm': 'Bilinçaltı, rüya, Freud, otomatik yazım, akıl reddi',
    'Egzistansiyalizm': 'Varoluş özden önce gelir, seçim, bireysel sorumluluk',
    'Ekspresyonizm': 'İç dünya dışa vurma, sübjektif anlatım, Kafka',
}

# Halk koşma türleri
KOSMA_TUR = {
    'Güzelleme': ('Karacaoğlan', 'aşk, doğa, sevgili güzelliği'),
    'Koçaklama': ('Köroğlu', 'kahramanlık, savaş, yiğitlik'),
    'Taşlama': ('Seyrani', 'yergi, eleştiri, toplumsal sorun'),
    'Ağıt': ('Anonim', 'ölüm üzerine yakılan'),
}

# Nazım biçimleri (kavram-tanım)
NAZIM_BICIMI = {
    'Gazel': 'Beyitlerle yazılır, 5-15 beyit, aa-ba-ca kafiye, AŞK konulu, Divan',
    'Kaside': 'Beyitlerle yazılır, 33-99 beyit, aa-ba-ca kafiye, METHİYE/MERSİYE/MÜNACAT konulu, Divan',
    'Mesnevi': 'Beyitlerle yazılır, aa-bb-cc-dd kafiye (her beyit kendi içinde), uzun konular',
    'Rubai': '4 mısra, aa-xa veya aa-aa, felsefi/tasavvufi, Fars kökenli',
    'Tuyuğ': '4 mısra, aa-xa, Türk şairlerine özgü, mani etkisi + aruz',
    'Koşma': 'Halk şiiri, 11 heceli (6+5 veya 4+4+3), 4 dörtlük, abab-cccb-dddb-eeeb',
    'Mani': 'Halk şiiri, 7 heceli, 4 mısra, aaxa kafiye, son 2 mısrada asıl mesaj',
    'Semai': 'Halk şiiri, 8 heceli, koşma yapısı',
    'Varsağı': 'Halk şiiri, 8 heceli, Toros Varsak Türklerine ait, mertçe eda, "bre" ünlemleri',
    'Şarkı': 'Divan, bestelenmek için, murabbadan türemiş, nakaratlı, Nedim ustası',
    'Terkib-i Bend': 'Bentlerden + her bent sonunda VASITA BEYTİ (her bende DEĞİŞİR), mersiye/hicviye',
    'Terci-i Bend': 'Bentlerden + her bent sonunda VASITA BEYTİ (TEKRARLANIR)',
}

# Söz sanatları
SOZ_SANATI_TANIM = {
    'Benzetme (Teşbih)': "Bir varlığı başka varlığa benzetme. 4 unsur: benzeyen, kendisine benzetilen, yön, edat (\"gibi\", \"kadar\").",
    'İstiare (Açık)': 'Sadece KENDİSİNE BENZETİLEN söylenir. "Aslan geliyor" (kahraman için).',
    'İstiare (Kapalı)': 'BENZEYEN söylenir + kendisine benzetilenin özelliği verilir. "Gül açtı, saçları dağıldı" (sevgili için).',
    'Mecaz-ı Mürsel': 'Benzetme amacı OLMADAN ilgi yoluyla aktarma. "Sobayı yaktım" (yakıtı).',
    'Teşhis-İntak': 'Cansıza canlı özellikleri (teşhis) / konuşturma (intak). "Ağaç bana dedi ki..."',
    'Tezat': 'Karşıt anlamlı sözcükler bir arada. "Akşamda dağ, sabahta ova"',
    'Tenasüp': 'Anlamca İLGİLİ sözcükler bir arada. (Savaş-asker-kılıç)',
    'Telmih': 'Tarihi/dini bir olaya gönderme. "Mecnun gibi çöllerde"',
    'Hüsn-i Talil': 'Gerçek bir olaya hayali güzel bir sebep yakıştırma. "Gül açtı çünkü sevgili geldi"',
    'Tevriye': 'Sözcüğün YAKIN ve UZAK iki anlamından UZAK olanını kastetme (Divan)',
    'Mübalağa': 'Aşırı abartma. "Sesi dağları yıkıyor"',
    'Kinaye': 'Açık ve gizli iki anlam, gizli anlam kastedilir',
    'Tariz': 'İğneleme, tersini söyleme',
    'Nida': 'Ünlem (ey, hey, ah!)',
    'Tecahül-i Ârif': 'Bilineni bilmiyormuş gibi sorma',
}

# Tanzimat "ilk"leri (kavram-tanım)
ILK_LER = {
    'İlk yerli roman': ('Taaşşuk-ı Talat ve Fitnat', 'Şemsettin Sami'),
    'İlk roman çevirisi': ('Telemak', 'Yusuf Kamil Paşa'),
    'İlk edebi roman': ('İntibah', 'Namık Kemal'),
    'İlk tarihi roman': ('Cezmi', 'Namık Kemal'),
    'İlk realist roman': ('Araba Sevdası', 'Recaizade Mahmut Ekrem'),
    'İlk köy romanı': ('Karabibik', 'Nabizade Nazım'),
    'İlk psikolojik roman denemesi': ('Zehra', 'Nabizade Nazım'),
    'İlk psikolojik roman': ('Eylül', 'Mehmet Rauf'),
    'İlk tiyatro (sahnelenen)': ('Şair Evlenmesi', 'Şinasi'),
    'İlk makale': ('Tercüman-ı Ahvâl Mukaddimesi', 'Şinasi'),
    'İlk özel Türk gazetesi': ('Tercüman-ı Ahvâl', 'Şinasi + Agah Efendi'),
    'İlk pastoral şiir': ('Sahra', 'Abdülhak Hamit'),
    'İlk büyük Türk-İslam mesnevisi': ('Kutadgu Bilig', 'Yusuf Has Hacip'),
}


def shuffle_seed(items, seed_str):
    """Deterministik karıştırma (kart id ile)."""
    s = random.Random(hash(seed_str) % 100000)
    a = list(items)
    s.shuffle(a)
    return a


def card(id_, konu, alt, tip, soru, dogru_text, celdiriciler, aciklama, tuzak='', mebi_sayfa='', zorluk='orta'):
    """Bir kart oluştur."""
    opts = celdiriciler[:4]  # max 4 çeldirici → 5 toplam şık (1 doğru + 4)
    opts.append(dogru_text)
    opts = shuffle_seed(opts, id_)
    secenekler = []
    dogru_id = None
    for i, txt in enumerate(opts):
        letter = chr(ord('A') + i)
        secenekler.append({'id': letter, 'text': txt})
        if txt == dogru_text:
            dogru_id = letter
    return {
        'id': id_,
        'konu': konu,
        'alt_konu': alt,
        'tip': tip,
        'soru': soru,
        'secenekler': secenekler,
        'dogru': dogru_id,
        'aciklama': aciklama,
        'tuzak': tuzak,
        'mebi_sayfa': mebi_sayfa,
        'zorluk': zorluk,
        'kaynak': 'otomatik',
    }


def get_donem_yazarlar(donem):
    return [y for y, d in YAZAR_DONEM.items() if d == donem]


def celdirici_yazar_ayni_donem(dogru_yazar, n=3):
    donem = YAZAR_DONEM.get(dogru_yazar, 'cumhuriyet')
    candidates = [y for y in get_donem_yazarlar(donem) if y != dogru_yazar]
    return shuffle_seed(candidates, dogru_yazar + '-celdirici')[:n]


def celdirici_eser_ayni_yazar_donem(dogru_eser, n=3):
    """Eser çeldiricisi: doğru eserin yazarının dönemindeki başka eserler."""
    dogru_yazar = ESER_YAZAR.get(dogru_eser, '')
    donem = YAZAR_DONEM.get(dogru_yazar, 'cumhuriyet')
    pool = []
    for y, eserler in YAZAR_ESERLERI.items():
        if YAZAR_DONEM.get(y) == donem and y != dogru_yazar:
            pool.extend(eserler)
    if len(pool) < n:
        # Genişlet → yakın dönem
        for y, eserler in YAZAR_ESERLERI.items():
            if y != dogru_yazar and eserler:
                pool.append(eserler[0])
    pool = list(dict.fromkeys(pool))  # dedupe
    return shuffle_seed(pool, dogru_eser + '-celdirici')[:n]


# =====================================================
# Kart üretim fonksiyonları
# =====================================================

def gen_eser_yazar_cards():
    cards = []
    # Genel/muğlak eser adlarını eleme (birden çok yazara ait olabilir)
    GENERIC = {'Divan', 'Şiirleri', 'Şiirler', 'Şarkıları', 'Nefesler'}
    for yazar, eserler in YAZAR_ESERLERI.items():
        if not eserler: continue
        # Generic eserleri parantezle ayırt et
        spesifik = []
        for e in eserler:
            base = e.split(' (')[0].strip()
            if base in GENERIC: continue
            spesifik.append(e)
        for i, eser in enumerate(spesifik[:3]):  # en bilinen 3 eseri
            celdiriciler = celdirici_yazar_ayni_donem(yazar, 4)
            if len(celdiriciler) < 3: continue
            donem = YAZAR_DONEM.get(yazar, 'cumhuriyet')
            konu = DONEM_TOPIC.get(donem, 'cumhuriyet')
            mebi = MEBI_AUTHOR.get(yazar, '—')
            id_ = f"ey_{len(cards):04d}"
            c = card(
                id_=id_,
                konu=konu,
                alt=yazar.lower().replace(' ', '_'),
                tip='eser-yazar',
                soru=f"<strong>«{eser}»</strong> adlı eserin yazarı aşağıdakilerden hangisidir?",
                dogru_text=yazar,
                celdiriciler=celdiriciler,
                aciklama=f"<strong>{eser}</strong> → <strong>{yazar}</strong>. {yazar}'ın {TOPIC_LABEL[konu]} dönemindeki önemli eserlerinden.",
                tuzak=f"Çeldiriciler aynı döneme ait yazarlar. Karıştırmamak için yazarın ESER REPERTUARINI bilmek gerek.",
                mebi_sayfa=mebi if mebi != '—' else '',
                zorluk='orta',
            )
            cards.append(c)
    return cards


def gen_yazar_eser_cards():
    cards = []
    seen = set()
    GENERIC = {'Divan', 'Şiirleri', 'Şiirler', 'Şarkıları', 'Nefesler'}
    for yazar, eserler in YAZAR_ESERLERI.items():
        if not eserler: continue
        donem = YAZAR_DONEM.get(yazar, 'cumhuriyet')
        konu = DONEM_TOPIC.get(donem, 'cumhuriyet')
        # En ünlü spesifik eser
        spesifik = [e for e in eserler if e.split(' (')[0].strip() not in GENERIC]
        if not spesifik: continue
        dogru_eser = spesifik[0]
        if dogru_eser in seen: continue
        seen.add(dogru_eser)
        # Çeldirici eserler: aynı dönem farklı yazar
        celdiriciler = celdirici_eser_ayni_yazar_donem(dogru_eser, 4)
        if len(celdiriciler) < 3: continue
        mebi = MEBI_AUTHOR.get(yazar, '—')
        id_ = f"ye_{len(cards):04d}"
        c = card(
            id_=id_,
            konu=konu,
            alt=yazar.lower().replace(' ', '_'),
            tip='yazar-eser',
            soru=f"<strong>{yazar}</strong>'a ait olan eser aşağıdakilerden hangisidir?",
            dogru_text=dogru_eser,
            celdiriciler=celdiriciler,
            aciklama=f"<strong>{yazar}</strong>'ın eserleri arasında <strong>{dogru_eser}</strong> bulunur. Çeldiriciler aynı döneme ait diğer yazarların eserleri.",
            tuzak=f"{TOPIC_LABEL[konu]} döneminde birden çok yazar var. Hangi eser kime ait olduğunu ezberlemek gerek.",
            mebi_sayfa=mebi if mebi != '—' else '',
            zorluk='orta',
        )
        cards.append(c)
    return cards


def gen_akim_temsilci_cards():
    cards = []
    for akim, temsilciler in AKIM_TEMSILCI.items():
        if not temsilciler: continue
        dogru = temsilciler[0]  # En öncü temsilci
        # Çeldirici: başka akımlardan
        celdiriciler = []
        for ak2, ts2 in AKIM_TEMSILCI.items():
            if ak2 != akim and ts2:
                celdiriciler.append(ts2[0])
        celdiriciler = shuffle_seed(celdiriciler, akim + '-c')[:4]
        id_ = f"at_{len(cards):04d}"
        c = card(
            id_=id_,
            konu='edebi_akimlar',
            alt=akim.lower(),
            tip='akim-temsilci',
            soru=f"<strong>{akim}</strong> akımının önde gelen temsilcisi aşağıdakilerden hangisidir?",
            dogru_text=dogru,
            celdiriciler=celdiriciler,
            aciklama=f"<strong>{akim}</strong> → <strong>{dogru}</strong>. {AKIM_OZELLIK.get(akim, '')}",
            tuzak=f"Akım temsilcileri sürekli karıştırılır. {akim} özelliği: {AKIM_OZELLIK.get(akim, '')[:60]}...",
            mebi_sayfa='186-190',
            zorluk='orta',
        )
        cards.append(c)
    return cards


def gen_akim_tanim_cards():
    cards = []
    for akim, ozellik in AKIM_OZELLIK.items():
        celdiriciler = [a for a in AKIM_OZELLIK.keys() if a != akim]
        celdiriciler = shuffle_seed(celdiriciler, akim + '-tanim')[:4]
        id_ = f"akt_{len(cards):04d}"
        c = card(
            id_=id_,
            konu='edebi_akimlar',
            alt=akim.lower(),
            tip='akim-tanim',
            soru=f"\"{ozellik}\" özellikleri aşağıdaki akımlardan hangisine aittir?",
            dogru_text=akim,
            celdiriciler=celdiriciler,
            aciklama=f"<strong>{akim}</strong> → bu özelliklerle tanımlanır. Temsilciler: {', '.join(AKIM_TEMSILCI.get(akim, [])[:3])}.",
            tuzak=f"Bazı akımlar birbirine yakın (realizm-natüralizm; romantizm-sembolizm). Anahtar kelime: {ozellik.split(',')[0]}",
            mebi_sayfa='186-190',
            zorluk='orta',
        )
        cards.append(c)
    return cards


def gen_donem_yazar_cards():
    cards = []
    # Her yazar için "hangi dönem" sorusu
    # Sadece tekrar eden / favori yazarlar için
    favorites = [
        ('Fuzuli', 'divan'), ('Baki', 'divan'), ('Nedim', 'divan'), ('Şeyh Galip', 'divan'),
        ('Halit Ziya Uşaklıgil', 'sf_fecr'), ('Tevfik Fikret', 'sf_fecr'), ('Mehmet Rauf', 'sf_fecr'),
        ('Ahmet Haşim', 'sf_fecr'),
        ('Şinasi', 'tanzimat'), ('Namık Kemal', 'tanzimat'), ('Ahmet Mithat Efendi', 'tanzimat'),
        ('Recaizade Mahmut Ekrem', 'tanzimat'), ('Abdülhak Hamit Tarhan', 'tanzimat'),
        ('Ömer Seyfettin', 'milli'), ('Yakup Kadri Karaosmanoğlu', 'milli'), ('Reşat Nuri Güntekin', 'milli'),
        ('Halide Edip Adıvar', 'milli'), ('Refik Halit Karay', 'milli'),
        ('Sabahattin Ali', 'cumhuriyet'), ('Yaşar Kemal', 'cumhuriyet'), ('Orhan Kemal', 'cumhuriyet'),
        ('Sait Faik Abasıyanık', 'cumhuriyet'), ('Oğuz Atay', 'cumhuriyet'),
        ('Yunus Emre', 'halk'), ('Karacaoğlan', 'halk'),
    ]
    donem_label = {
        'divan': 'Divan Edebiyatı', 'halk': 'Halk Edebiyatı', 'tanzimat': 'Tanzimat',
        'sf_fecr': 'Servet-i Fünun / Fecr-i Âti', 'milli': 'Milli Edebiyat',
        'cumhuriyet': 'Cumhuriyet Dönemi', 'gecis': 'Geçiş Dönemi'
    }
    for yazar, donem in favorites:
        dogru = donem_label[donem]
        celdiriciler = [v for k, v in donem_label.items() if k != donem]
        celdiriciler = shuffle_seed(celdiriciler, yazar + '-d')[:4]
        konu = DONEM_TOPIC.get(donem, 'cumhuriyet')
        id_ = f"dy_{len(cards):04d}"
        c = card(
            id_=id_,
            konu=konu,
            alt=yazar.lower().replace(' ', '_'),
            tip='donem-yazar',
            soru=f"<strong>{yazar}</strong> aşağıdaki edebi dönemlerden hangisine aittir?",
            dogru_text=dogru,
            celdiriciler=celdiriciler,
            aciklama=f"<strong>{yazar}</strong> → <strong>{dogru}</strong> döneminin yazarlarındandır.",
            tuzak=f"Bazı yazarlar dönem geçişinde kaldığı için karıştırılır (örn. Ahmet Haşim → Fecr-i Âti, ama Cumhuriyet bağımsızı kabul edilir).",
            mebi_sayfa=MEBI_AUTHOR.get(yazar, '') if MEBI_AUTHOR.get(yazar, '—') != '—' else '',
            zorluk='kolay',
        )
        cards.append(c)
    return cards


def gen_nazim_bicim_cards():
    cards = []
    for bicim, tanim in NAZIM_BICIMI.items():
        celdiriciler = [b for b in NAZIM_BICIMI.keys() if b != bicim]
        celdiriciler = shuffle_seed(celdiriciler, bicim)[:4]
        konu = 'divan_edebiyati' if bicim in ('Gazel','Kaside','Mesnevi','Rubai','Tuyuğ','Şarkı','Terkib-i Bend','Terci-i Bend') else 'halk_edebiyati'
        id_ = f"nb_{len(cards):04d}"
        c = card(
            id_=id_,
            konu=konu,
            alt=bicim.lower(),
            tip='nazim-bicim',
            soru=f"\"{tanim}\" özellikleri aşağıdaki nazım biçimlerinden hangisine aittir?",
            dogru_text=bicim,
            celdiriciler=celdiriciler,
            aciklama=f"<strong>{bicim}</strong> → {tanim}",
            tuzak=f"Nazım biçimleri sürekli karıştırılır. En sık tuzak: gazel-kaside (ikisi de aa-ba-ca kafiye, fark uzunluk-konuda).",
            mebi_sayfa='47-52' if konu == 'divan_edebiyati' else '36-37',
            zorluk='orta',
        )
        cards.append(c)
    return cards


def gen_kosma_turleri_cards():
    cards = []
    for tur, (sair, konu_aciklama) in KOSMA_TUR.items():
        celdiriciler = [t for t in KOSMA_TUR.keys() if t != tur]
        # Konu sorusu
        id_ = f"kt_{len(cards):04d}"
        c1 = card(
            id_=id_,
            konu='halk_edebiyati',
            alt='kosma',
            tip='kosma-tur',
            soru=f"\"{konu_aciklama}\" konularını işleyen koşma türü aşağıdakilerden hangisidir?",
            dogru_text=tur,
            celdiriciler=celdiriciler,
            aciklama=f"<strong>{tur}</strong> → {konu_aciklama}. Ustası: {sair}.",
            tuzak="Koşma türleri konu farkıyla ayrılır. Güzelleme (aşk), Koçaklama (kahramanlık), Taşlama (yergi), Ağıt (ölüm).",
            mebi_sayfa='36-37',
            zorluk='kolay',
        )
        cards.append(c1)
        # Şair sorusu
        if sair != 'Anonim':
            id_2 = f"kt_{len(cards):04d}"
            sair_celdiriciler = [s[0] for t, s in KOSMA_TUR.items() if s[0] != sair and s[0] != 'Anonim'] + ['Karacaoğlan', 'Köroğlu', 'Dadaloğlu', 'Seyrani']
            sair_celdiriciler = [s for s in sair_celdiriciler if s != sair]
            sair_celdiriciler = shuffle_seed(sair_celdiriciler, sair + tur)[:4]
            c2 = card(
                id_=id_2,
                konu='halk_edebiyati',
                alt='asik_edebiyati',
                tip='kosma-sair',
                soru=f"<strong>{tur}</strong> türünün en bilinen aşığı aşağıdakilerden hangisidir?",
                dogru_text=sair,
                celdiriciler=sair_celdiriciler,
                aciklama=f"<strong>{tur} ↔ {sair}</strong>. {konu_aciklama} konuları işleyen aşıkların en bilineni.",
                tuzak="Aşıkları türleriyle eşle: Karacaoğlan = güzelleme, Köroğlu/Dadaloğlu = koçaklama, Seyrani = taşlama.",
                mebi_sayfa='38-40',
                zorluk='orta',
            )
            cards.append(c2)
    return cards


def gen_soz_sanati_cards():
    cards = []
    for sanat, tanim in SOZ_SANATI_TANIM.items():
        celdiriciler = [s for s in SOZ_SANATI_TANIM.keys() if s != sanat]
        celdiriciler = shuffle_seed(celdiriciler, sanat)[:4]
        id_ = f"ss_{len(cards):04d}"
        c = card(
            id_=id_,
            konu='soz_sanatlari',
            alt=sanat.lower().replace(' ', '_').replace('(','').replace(')',''),
            tip='soz-sanati-tanim',
            soru=f"\"{tanim}\" tanımı aşağıdaki söz sanatlarından hangisine aittir?",
            dogru_text=sanat,
            celdiriciler=celdiriciler,
            aciklama=f"<strong>{sanat}</strong> → {tanim}",
            tuzak="İstiare ↔ Benzetme ↔ Mecaz-ı mürsel ayrımı en sık tuzak. Benzetme yok → mecaz-ı mürsel. Benzetme var ama tek unsur → istiare.",
            mebi_sayfa='22-25',
            zorluk='orta',
        )
        cards.append(c)
    return cards


def gen_siir_bilgisi_cards():
    """Şiir Bilgisi: kafiye, ölçü, redif, nazım birimi, şiir türleri"""
    cards = []
    # Kafiye türleri
    kafiye = {
        'Yarım kafiye': '1 ses (sessiz) benzerliği. "yol-bel"',
        'Tam kafiye': '2 ses (sessiz+sesli) benzerliği. "bağ-dağ"',
        'Zengin kafiye': '3 veya daha fazla ses benzerliği. "karaltı-yeraltı"',
        'Tunç kafiye': 'Bir sözcük diğerinin İÇİNDE. "kar-bahar"',
        'Cinaslı kafiye': 'Aynı yazılış farklı anlam. "el(yabancı)-el(organ)"',
    }
    for k, t in kafiye.items():
        cel = [x for x in kafiye if x != k]
        id_ = f"sb_{len(cards):04d}"
        cards.append(card(id_, 'siir_bilgisi', 'kafiye', 'kafiye',
            f'"{t}" tanımı hangi kafiye türüne aittir?',
            k, cel, f"<strong>{k}</strong> → {t}",
            "Kafiye türlerinde ses sayısı ve yapı dikkat. Yarım=1 ses, Tam=2 ses, Zengin=3+ ses.",
            '16', 'orta'))
    # Şiir türleri
    siir_tur = {
        'Lirik': 'Bireysel duygu, aşk, hüzün, sevinç temalı şiir',
        'Epik': 'Kahramanlık, savaş, destan temalı şiir',
        'Didaktik': 'Öğretici, bilgi verici, ahlaki ders veren şiir',
        'Pastoral': 'Doğa, kır, çoban yaşamı temalı şiir',
        'Dramatik': 'Sahnelenebilir, olaylı, dialog ağırlıklı şiir',
        'Satirik': 'Eleştirel, alaylı, taşlama amaçlı şiir',
    }
    for k, t in siir_tur.items():
        cel = [x for x in siir_tur if x != k]
        id_ = f"sb_{len(cards):04d}"
        cards.append(card(id_, 'siir_bilgisi', 'siir_turu', 'siir-tur',
            f'"{t}" özelliği hangi şiir türüne aittir?',
            k, cel, f"<strong>{k}</strong> → {t}",
            "Şiir türlerini konuyla eşleştir: lirik=duygu, epik=kahramanlık, didaktik=öğretici, pastoral=doğa, dramatik=olay, satirik=eleştiri.",
            '21', 'orta'))
    # Ölçü
    olculer = [
        ('Hece ölçüsü', 'Mısralardaki HECE SAYISI eşittir. Halk şiirinde kullanılır. 7/8/11/14\'lü',
            ['Aruz ölçüsü', 'Serbest nazım', 'Aliterasyon ölçüsü', 'Klasik ölçü']),
        ('Aruz ölçüsü', 'Hecelerin UZUN/KISA olmasına göre kalıp. Divan şiirinde kullanılır',
            ['Hece ölçüsü', 'Serbest nazım', 'Kafiye ölçüsü', 'Bent ölçüsü']),
        ('Serbest nazım', 'Ne hece ne aruz. Mısra uzunlukları farklı. Cumhuriyet sonrası, Nazım Hikmet öncü',
            ['Hece ölçüsü', 'Aruz ölçüsü', 'Vezinsiz nazım', 'Tonik ölçü']),
    ]
    for k, t, cel in olculer:
        id_ = f"sb_{len(cards):04d}"
        cards.append(card(id_, 'siir_bilgisi', 'olcu', 'olcu',
            f'"{t}" özelliği hangi ölçü türüne aittir?',
            k, cel, f"<strong>{k}</strong> → {t}",
            "Hece halk şiiri (eşit hece), aruz divan (uzun-kısa), serbest Cumhuriyet (kuralsız).",
            '14-15', 'kolay'))
    # Redif vs kafiye
    id_ = f"sb_{len(cards):04d}"
    cards.append(card(id_, 'siir_bilgisi', 'redif', 'redif',
        "Mısra sonlarında kafiyeden SONRA gelen, AYNI olan sözcük veya ek aşağıdaki kavramlardan hangisidir?",
        'Redif', ['Kafiye', 'Durak', 'Mahlas', 'Beyit'],
        '<strong>Redif</strong> = kafiyeden sonra aynı tekrarlanan kelime/ek. Önce REDİF bul, geriye kalan KAFİYE.',
        "Redif ↔ Kafiye karıştırma. Redif AYNI sözcük/ek, Kafiye ses benzerliği.",
        '16', 'orta'))
    return cards


def gen_nesir_bilgisi_cards():
    cards = []
    # Roman türleri
    roman_tur = [
        ('Psikolojik roman', 'Karakterin İÇ DÜNYASI, ruhsal süreçleri merkez. Eylül (Mehmet Rauf), 9. Hariciye Koğuşu (Peyami Safa)',
            ['Tarihi roman', 'Sosyal roman', 'Töre romanı', 'Köy romanı']),
        ('Tarihi roman', 'Geçmiş bir dönemi/olayı konu alır. Cezmi (Namık Kemal — ilk), Devlet Ana (Kemal Tahir), Küçük Ağa (Tarık Buğra)',
            ['Psikolojik roman', 'Sosyal roman', 'Macera romanı', 'Otobiyografik roman']),
        ('Sosyal roman', 'Toplumsal sorunları işler. Yaban (Yakup Kadri), Sefiller (Hugo)',
            ['Psikolojik roman', 'Tarihi roman', 'Töre romanı', 'Köy romanı']),
        ('Töre/Aile romanı', 'Belirli bir toplum kesiminin değer ve yaşamı. Aşk-ı Memnu (Halit Ziya), Yaprak Dökümü (Reşat Nuri)',
            ['Psikolojik roman', 'Tarihi roman', 'Köy romanı', 'Macera romanı']),
        ('Köy romanı', 'Anadolu köylüsü merkezde. Karabibik (Nabizade Nazım — ilk), Yılanların Öcü (Fakir Baykurt)',
            ['Psikolojik roman', 'Tarihi roman', 'Töre romanı', 'Sosyal roman']),
    ]
    for k, t, cel in roman_tur:
        id_ = f"nb_{len(cards):04d}"
        cards.append(card(id_, 'nesir_bilgisi', 'roman_turu', 'roman-tur',
            f'"{t}" özelliği aşağıdaki roman türlerinden hangisine aittir?',
            k, cel, f"<strong>{k}</strong> → {t}",
            "Roman türleri konuya göre ayrılır. Psikolojik=iç dünya, Tarihi=geçmiş, Sosyal=toplum, Töre=aile, Köy=Anadolu.",
            '124-126', 'orta'))
    # Bakış açısı
    bakis = [
        ('Hâkim (İlahi) bakış açısı', 'Anlatıcı her şeyi bilir, karakterlerin geçmişini ve iç dünyasını anlatır. 3. tekil şahıs',
            ['Gözlemci bakış açısı', 'Kahraman bakış açısı', 'Çoğul anlatıcı', 'Ben anlatıcı']),
        ('Gözlemci bakış açısı', 'Anlatıcı DIŞTAN görür, karakterlerin içini bilmez. Sadece dış davranış/söz aktarır. Kamera tarzı',
            ['Hâkim bakış açısı', 'Kahraman bakış açısı', 'Çoğul anlatıcı', 'Birinci kişi']),
        ('Kahraman bakış açısı', 'Anlatıcı = karakter. 1. tekil şahıs (ben). Kendi gözünden anlatır. Çalıkuşu (Feride), Eylül (Necip)',
            ['Hâkim bakış açısı', 'Gözlemci bakış açısı', 'Çoğul anlatıcı', 'İlahi bakış']),
    ]
    for k, t, cel in bakis:
        id_ = f"nb_{len(cards):04d}"
        cards.append(card(id_, 'nesir_bilgisi', 'bakis_acisi', 'bakis-acisi',
            f'"{t}" tanımı aşağıdaki bakış açılarından hangisine aittir?',
            k, cel, f"<strong>{k}</strong> → {t}",
            "İPUCU: \"Ben\" varsa kahraman. \"Ahmet biliyordu/düşündü\" varsa hâkim. \"Ahmet ayağa kalktı, çıktı\" (içi bilinmiyor) gözlemci.",
            '105, 123', 'orta'))
    # Düz yazı türleri ayrımı
    duzyazi = [
        ('Deneme', 'Yazarın KİŞİSEL düşüncelerini, kanıt aramadan, sohbet havasında. Nurullah Ataç ustası',
            ['Eleştiri', 'Makale', 'Fıkra', 'Sohbet (Söyleşi)']),
        ('Eleştiri', 'Bir eseri/sanatçıyı/durumu DEĞERLENDİRME. Olumlu/olumsuz analiz, ölçütleri var. Hüseyin Cahit Yalçın, Cemil Meriç',
            ['Deneme', 'Makale', 'Fıkra', 'Sohbet']),
        ('Makale', 'Belli bir konuda görüş + KANIT + bilimsel-mantıksal yöntem. İlk makale: Şinasi (Tercüman-ı Ahvâl Mukaddimesi)',
            ['Deneme', 'Eleştiri', 'Fıkra', 'Sohbet']),
        ('Anı (Hatırat)', 'Yazarın YAŞADIKLARINI SONRADAN hatırlayıp anlatması. Falih Rıfkı - Çankaya, Yakup Kadri - Politikada 45 Yıl',
            ['Gezi', 'Günlük', 'Biyografi', 'Otobiyografi']),
        ('Gezi (Seyahatname)', 'Görülen yer/ülkelerin betimlemesi. Falih Rıfkı - Zeytindağı, Evliya Çelebi - Seyahatname',
            ['Anı', 'Günlük', 'Biyografi', 'Roman']),
        ('Günlük', 'GÜN GÜNÜNE yazılan kişisel notlar. Ataç\'ın Günleri',
            ['Anı', 'Mektup', 'Sohbet', 'Biyografi']),
    ]
    for k, t, cel in duzyazi:
        id_ = f"nb_{len(cards):04d}"
        cards.append(card(id_, 'nesir_bilgisi', 'duzyazi_turu', 'duzyazi-tur',
            f'"{t}" tanımı aşağıdaki düz yazı türlerinden hangisine aittir?',
            k, cel, f"<strong>{k}</strong> → {t}",
            "Deneme=kişisel düşünce, Makale=KANIT, Eleştiri=eser değerlendirme, Anı=sonradan, Günlük=günü gününe, Gezi=mekan.",
            '172-183', 'orta'))
    return cards


def gen_geleneksel_tiyatro_cards():
    cards = []
    tiyatro = [
        ('Karagöz', 'GÖLGE OYUNU. Beyaz perde önünde deve derisi tasvirlerle oynanır. HACİVAT (akıllı, kibirli) + KARAGÖZ (cahil, sade)',
            ['Orta Oyunu', 'Meddah', 'Köy Seyirlik Oyunu', 'Karagöz dramı']),
        ('Orta Oyunu', 'Sahne YOK, halka şeklinde dizilmiş seyircilerin ORTASINDA. PİŞEKAR (akıllı) + KAVUKLU (saf). YENİ DÜNYA + DÜKKAN aksesuarları',
            ['Karagöz', 'Meddah', 'Köy Seyirlik', 'Modern tiyatro']),
        ('Meddah', 'TEK KİŞİLİK tiyatro. Anlatıcı tüm rolleri tek başına oynar. MENDİL + SOPA aksesuarları, kahvehanede',
            ['Karagöz', 'Orta Oyunu', 'Köy Seyirlik', 'Komedi']),
        ('Köy Seyirlik Oyunları', 'Köylerde mevsim geçişlerinde, özellikle KIŞ aylarında oynanan amatör oyunlar. Bereket ritüeli',
            ['Karagöz', 'Orta Oyunu', 'Meddah', 'Halk konseri']),
    ]
    for k, t, cel in tiyatro:
        id_ = f"gt_{len(cards):04d}"
        cards.append(card(id_, 'geleneksel_tiyatro', k.lower().replace(' ','_'), 'tiyatro-tur',
            f'"{t}" özelliği aşağıdaki geleneksel Türk tiyatrosu türlerinden hangisine aittir?',
            k, cel, f"<strong>{k}</strong> → {t}",
            "Karagöz vs Orta Oyunu: KARAGÖZ perde+gölge, ORTA OYUNU meydan+halka. Karakterler: Hacivat-Karagöz vs Pişekar-Kavuklu.",
            '149-152', 'orta'))
    # Karakter eşleştirme
    karakter = [
        ('Hacivat ve Karagöz', 'Karagöz', ['Orta Oyunu', 'Meddah', 'Köy Seyirlik', 'Şehir tiyatrosu']),
        ('Pişekar ve Kavuklu', 'Orta Oyunu', ['Karagöz', 'Meddah', 'Köy Seyirlik', 'Modern tiyatro']),
    ]
    for sor, dogru, cel in karakter:
        id_ = f"gt_{len(cards):04d}"
        cards.append(card(id_, 'geleneksel_tiyatro', 'karakter', 'tiyatro-karakter',
            f'<strong>{sor}</strong> karakterleri aşağıdaki geleneksel tiyatro türlerinden hangisine aittir?',
            dogru, cel, f"<strong>{sor}</strong> → <strong>{dogru}</strong>'nun başkarakterleri.",
            "Karıştırma! Hacivat-Karagöz = KARAGÖZ. Pişekar-Kavuklu = ORTA OYUNU. İkisinde de akıllı+halk karakter ikilisi var.",
            '149-150', 'kolay'))
    # Bölümler
    id_ = f"gt_{len(cards):04d}"
    cards.append(card(id_, 'geleneksel_tiyatro', 'bolumler', 'tiyatro-bolum',
        "Karagöz ve Orta Oyunu'nun bölümleri aşağıdakilerden hangisinde doğru sırada verilmiştir?",
        'Mukaddime → Muhavere → Fasıl → Bitiş',
        ['Mukaddime → Fasıl → Muhavere → Sonuç', 'Giriş → Gelişme → Sonuç → Bitiş', 'Tanıtım → Olay → Çatışma → Çözüm', 'Açılış → Diyalog → Asıl oyun → Kapanış'],
        "Hem Karagöz hem Orta Oyunu'nda 4 bölüm: MUKADDİME (giriş), MUHAVERE (Karagöz-Hacivat diyalogu / Pişekar-Kavuklu), FASIL (asıl oyun), BİTİŞ.",
        "Karagöz ve Orta Oyunu BÖLÜMLERİ aynıdır. Bölüm adlarını karıştırma.",
        '151', 'orta'))
    return cards


def gen_masal_destan_cards():
    cards = []
    # Masal bölümleri
    masal = [
        ('Döşeme / Tekerleme', '"Bir varmış bir yokmuş, evvel zaman içinde..." gibi giriş tekerlemesi',
            ['Serim', 'Düğüm', 'Çözüm', 'Dilek']),
        ('Serim', 'Karakter ve mekan tanıtımı',
            ['Döşeme', 'Düğüm', 'Çözüm', 'Dilek']),
        ('Düğüm', 'Olayın karmaşıklaşması, çatışma',
            ['Döşeme', 'Serim', 'Çözüm', 'Dilek']),
        ('Çözüm', 'Olay sonuçlanır',
            ['Döşeme', 'Serim', 'Düğüm', 'Dilek']),
        ('Dilek / Dua', '"Onlar ermiş muradına biz çıkalım kerevetine..." gibi bitiş tekerlemesi',
            ['Döşeme', 'Serim', 'Düğüm', 'Çözüm']),
    ]
    for k, t, cel in masal:
        id_ = f"md_{len(cards):04d}"
        cards.append(card(id_, 'masal_fabl_destan', 'masal_bolumleri', 'masal-bolum',
            f'"{t}" aşağıdaki masal bölümlerinden hangisidir?',
            k, cel, f"<strong>{k}</strong> → {t}",
            "Masal 5 bölümlüdür: Döşeme (giriş tekerleme) → Serim → Düğüm → Çözüm → Dilek (bitiş tekerleme).",
            '166', 'orta'))
    # Fabl yazarları
    fabl = [
        ('Ezop (Aisopos)', 'Antik Yunan, fablın babası. M.Ö. 6. yy', ['La Fontaine', 'Beydeba', 'Şeyhi', 'Nasrettin Hoca']),
        ('La Fontaine', 'Fransa, 17. yy. Klasisizm temsilcisi. Fabllar kitabı', ['Ezop', 'Beydeba', 'Andersen', 'Grimm Kardeşler']),
        ('Beydeba', 'Hindistan. KELİLE VE DİMNE (yöneticilere ahlak öğreten)', ['Ezop', 'La Fontaine', 'Şeyhi', 'Firdevsi']),
    ]
    for k, t, cel in fabl:
        id_ = f"md_{len(cards):04d}"
        cards.append(card(id_, 'masal_fabl_destan', 'fabl', 'fabl-yazar',
            f'"{t}" aşağıdaki fabl yazarlarından hangisidir?',
            k, cel, f"<strong>{k}</strong> → {t}",
            "Fablın 3 büyük ismi: Ezop (Yunan, kurucu), La Fontaine (Fransız, klasisizm), Beydeba (Hint, Kelile ve Dimne).",
            '167', 'orta'))
    # Destan oluşum aşamaları
    id_ = f"md_{len(cards):04d}"
    cards.append(card(id_, 'masal_fabl_destan', 'destan_olusum', 'destan-olusum',
        "Doğal destanların oluşum aşamaları aşağıdakilerden hangisinde DOĞRU sırada verilmiştir?",
        'Çekirdek dönem → Yayılma dönemi → Derleme dönemi',
        ['Yayılma → Çekirdek → Derleme', 'Çekirdek → Derleme → Yayılma', 'Mitoloji → Tarih → Yazı', 'Sözlü → Yazılı → Basılı'],
        "Destan 3 aşamadan geçer: 1) ÇEKİRDEK (tarihte gerçek olay), 2) YAYILMA (halk ağzında mitolojik öge eklenir), 3) DERLEME (yazar toplar).",
        "ÖSYM sık sorduğu konu. 'Çekirdek' ile başlar, 'Derleme' ile biter.",
        '169-170', 'orta'))
    # Destan türleri
    id_ = f"md_{len(cards):04d}"
    cards.append(card(id_, 'masal_fabl_destan', 'destan_turu', 'destan-tur',
        "Çanakkale Şehitlerine (Mehmet Akif), Kuvâyi Milliye Destanı (Nazım Hikmet), Üç Şehitler Destanı (Fazıl Hüsnü Dağlarca) hangi destan türüne örnektir?",
        'Yapma destan',
        ['Doğal destan', 'Halk hikayesi', 'Mitolojik destan', 'Tarihi roman'],
        "<strong>Yapma destan</strong> = bir yazar tarafından bilinçli olarak yaratılmış destan. Doğal destan ise (Oğuz Kağan, Manas) anonim halk ürünüdür.",
        "Yapma destan ↔ Doğal destan. Çanakkale Şehitlerine YAPMA (Mehmet Akif yazdı). Oğuz Kağan DOĞAL (anonim).",
        '170', 'orta'))
    # Halk hikayesi
    hh = [
        ('Kerem ile Aslı', 'aşk hikayesi', ['Köroğlu', 'Battal Gazi', 'Manas Destanı', 'Dede Korkut']),
        ('Köroğlu', 'kahramanlık hikayesi', ['Kerem ile Aslı', 'Battal Gazi', 'Manas', 'Tahir ile Zühre']),
    ]
    for k, t, cel in hh:
        id_ = f"md_{len(cards):04d}"
        cards.append(card(id_, 'masal_fabl_destan', 'halk_hikayesi', 'halk-hikaye',
            f'<strong>{k}</strong> türü olarak hangi halk anlatımı türüne aittir?',
            ('Aşk hikayesi' if t == 'aşk hikayesi' else 'Kahramanlık hikayesi'),
            (['Kahramanlık hikayesi', 'Masal', 'Fabl', 'Destan'] if t == 'aşk hikayesi'
             else ['Aşk hikayesi', 'Masal', 'Fabl', 'Mitoloji']),
            f"<strong>{k}</strong> → {t}.",
            "Halk hikayeleri 2 ana türde: AŞK (Kerem ile Aslı, Ferhad ile Şirin, Tahir ile Zühre) + KAHRAMANLIK (Köroğlu, Battal Gazi).",
            '107-108', 'orta'))
    return cards


def gen_ilkler_cards():
    cards = []
    for ilk, (eser, yazar) in ILK_LER.items():
        # Eser sorusu
        celdiriciler_eser = [v[0] for k, v in ILK_LER.items() if k != ilk]
        celdiriciler_eser = shuffle_seed(celdiriciler_eser, ilk + 'e')[:4]
        id_ = f"il_{len(cards):04d}"
        c1 = card(
            id_=id_,
            konu='tanzimat',
            alt='ilkler',
            tip='ilkler-eser',
            soru=f"Türk edebiyatında <strong>{ilk.lower()}</strong> aşağıdakilerden hangisidir?",
            dogru_text=eser,
            celdiriciler=celdiriciler_eser,
            aciklama=f"<strong>{ilk}</strong> = <strong>{eser}</strong> ({yazar}).",
            tuzak="Tanzimat 'ilk'leri sürekli karıştırılır. İlk roman ↔ İlk edebi roman ↔ İlk tarihi roman → ayrı eserler.",
            mebi_sayfa='128',
            zorluk='orta',
        )
        cards.append(c1)
    return cards


# =====================================================
# Ana üretim
# =====================================================

def main():
    print("=== KARTLAR ÜRETİLİYOR ===")
    all_cards = []
    all_cards += gen_eser_yazar_cards()
    print(f"  eser-yazar: {len([c for c in all_cards if c['tip']=='eser-yazar'])}")
    all_cards += gen_yazar_eser_cards()
    print(f"  yazar-eser: {len([c for c in all_cards if c['tip']=='yazar-eser'])}")
    all_cards += gen_akim_temsilci_cards()
    print(f"  akim-temsilci: {len([c for c in all_cards if c['tip']=='akim-temsilci'])}")
    all_cards += gen_akim_tanim_cards()
    print(f"  akim-tanim: {len([c for c in all_cards if c['tip']=='akim-tanim'])}")
    all_cards += gen_donem_yazar_cards()
    print(f"  donem-yazar: {len([c for c in all_cards if c['tip']=='donem-yazar'])}")
    all_cards += gen_nazim_bicim_cards()
    print(f"  nazim-bicim: {len([c for c in all_cards if c['tip']=='nazim-bicim'])}")
    all_cards += gen_kosma_turleri_cards()
    print(f"  kosma-tur+sair: {len([c for c in all_cards if c['tip'] in ('kosma-tur','kosma-sair')])}")
    all_cards += gen_soz_sanati_cards()
    print(f"  soz-sanati: {len([c for c in all_cards if c['tip']=='soz-sanati-tanim'])}")
    all_cards += gen_siir_bilgisi_cards()
    print(f"  siir-bilgisi: {len([c for c in all_cards if c['konu']=='siir_bilgisi'])}")
    all_cards += gen_nesir_bilgisi_cards()
    print(f"  nesir-bilgisi: {len([c for c in all_cards if c['konu']=='nesir_bilgisi'])}")
    all_cards += gen_geleneksel_tiyatro_cards()
    print(f"  geleneksel-tiyatro: {len([c for c in all_cards if c['konu']=='geleneksel_tiyatro'])}")
    all_cards += gen_masal_destan_cards()
    print(f"  masal-fabl-destan: {len([c for c in all_cards if c['konu']=='masal_fabl_destan'])}")
    all_cards += gen_ilkler_cards()
    print(f"  ilkler: {len([c for c in all_cards if c['tip']=='ilkler-eser'])}")

    print(f"TOPLAM: {len(all_cards)} kart")
    with open(SITE / 'cards-auto.json', 'w', encoding='utf-8') as f:
        json.dump(all_cards, f, ensure_ascii=False, indent=1)
    print(f"  → {SITE / 'cards-auto.json'}")

    # ====== TOPICS INDEX ======
    print("\n=== TOPICS INDEX ===")
    topics_meta = [
        ('divan_edebiyati', 'divan_edebiyati', 'Divan Edebiyatı', 29, 10, 'ÇOK YÜKSEK', 'En yoğun konu. 13-19. yy klasik şiir geleneği. Fuzuli, Baki, Nedim, Nef\'i, Nabi, Şeyh Galip; gazel-kaside-mesnevi.'),
        ('cumhuriyet', 'cumhuriyet', 'Cumhuriyet Dönemi', 25, 10, 'ÇOK YÜKSEK', '1923-günümüz. 8 şiir akımı + roman/hikaye/tiyatro. En karmaşık dönem.'),
        ('siir_bilgisi', 'siir_bilgisi', 'Şiir Bilgisi', 17, 4, 'YÜKSEK', 'Nazım birimi, ölçü (hece/aruz/serbest), kafiye türleri, redif, şiir türleri.'),
        ('nesir_bilgisi', 'nesir_bilgisi', 'Nesir Bilgisi', 14, 4, 'YÜKSEK', 'Roman türleri, hikaye türleri, anlatıcı/bakış açısı, deneme/eleştiri/makale, anı/gezi/biyografi.'),
        ('tanzimat', 'tanzimat', 'Tanzimat', 10, 2, 'YÜKSEK', '1860-1896 Batı ile tanışma. "İlk"ler garantili. I. dönem (toplumcu) + II. dönem (bireyci).'),
        ('soz_sanatlari', 'soz_sanatlari', 'Söz Sanatları', 10, 6, 'YÜKSEK', 'Benzetme, istiare, mecaz-ı mürsel, teşhis, tezat, tenasüp, tevriye, telmih, hüsn-i talil.'),
        ('servet_i_funun_fecr_i_ati', 'servet-i-funun', 'Servet-i Fünun / Fecr-i Âti', 9, 3, 'YÜKSEK', '1896-1912. Halit Ziya (roman), Tevfik Fikret/Cenap Şahabettin (şiir), Ahmet Haşim (Fecr-i Âti).'),
        ('masal_fabl_destan', 'masal-fabl-destan', 'Masal / Fabl / Destan / Halk Hikâyesi', 8, 4, 'ORTA', 'Destan oluşum aşamaları (sürekli sorulan), Masal bölümleri, Fabl (Ezop, La Fontaine), Halk hikayesi.'),
        ('edebi_akimlar', 'edebi_akimlar', 'Edebi Akımlar', 8, 4, 'KESİN (her yıl 1)', '9 ana akım: klasisizm, romantizm, realizm, natüralizm, parnasizm, sembolizm, fütürizm, dadaizm, sürrealizm.'),
        ('halk_edebiyati', 'halk_edebiyati', 'Halk Edebiyatı', 6, 3, 'YÜKSEK (2025 boş)', 'Anonim + Aşık (koşma türleri: güzelleme/koçaklama/taşlama/ağıt) + Tekke (Yunus, Pir Sultan, Kaygusuz). 2026 için güçlü aday.'),
        ('milli_edebiyat', 'milli_edebiyat', 'Milli Edebiyat', 5, 3, 'ORTA', '1911-1923. Ömer Seyfettin (hikaye), Yakup Kadri/Reşat Nuri/Halide Edip (roman), Genç Kalemler.'),
        ('islamiyet_oncesi_gecis', 'islamiyet-oncesi-gecis', 'İslamiyet Öncesi / Geçiş Dönemi', 4, 3, 'YÜKSEK (yükselişte)', 'Sözlü dönem (koşuk/sagu/sav) + Geçiş 4 büyük eser (Kutadgu Bilig, Divânü Lügat, Atabet, Divan-ı Hikmet).'),
        ('geleneksel_tiyatro', 'geleneksel-tiyatro', 'Geleneksel Türk Tiyatrosu', 4, 4, 'DÜŞÜK (2025 geldi)', 'Karagöz (gölge oyunu), Orta Oyunu (Pişekar-Kavuklu), Meddah, Köy Seyirlik.'),
    ]
    topics_index = []
    for code, slug, title, toplam, alt_n, oncelik, kisa in topics_meta:
        topics_index.append({
            'code': code, 'slug': slug, 'title': title,
            'toplam': toplam, 'alt_basliklar': alt_n, 'oncelik': oncelik,
            'kisa_aciklama': kisa,
            'mebi_pages': MEBI_TOPIC.get(code, {}).get('pages', '—'),
        })
    with open(SITE / 'topics-index.json', 'w', encoding='utf-8') as f:
        json.dump(topics_index, f, ensure_ascii=False, indent=1)
    print(f"  → topics-index.json ({len(topics_index)} konu)")

    # ====== AUTHORS ======
    print("\n=== AUTHORS ===")
    author_freq = ANNOTATED.get('author_frequency', {})
    authors_list = []
    for name, info in author_freq.items():
        donem = YAZAR_DONEM.get(name, '')
        eserler = YAZAR_ESERLERI.get(name, [])
        konular = sorted({o['topic'] for o in info['occurrences'] if o.get('topic')})
        authors_list.append({
            'name': name,
            'soru_sayisi': info['count'],
            'yillar': sorted([y for y in info['years'] if y]),
            'konular': konular,
            'mebi_sayfa': MEBI_AUTHOR.get(name, ''),
            'diger_eserler': ', '.join(eserler[:5]) if eserler else '',
            'occurrences': info['occurrences'],
        })
    authors_list.sort(key=lambda a: (-a['soru_sayisi'], a['name']))
    with open(SITE / 'authors.json', 'w', encoding='utf-8') as f:
        json.dump(authors_list, f, ensure_ascii=False, indent=1)
    print(f"  → authors.json ({len(authors_list)} yazar)")

    # ====== PREDICTIONS ======
    print("\n=== PREDICTIONS ===")
    predictions = {
        'konular': [
            {'ad': 'Sözcükte Anlam', 'frekans_8yil': '8/8 yıl 1 soru', 'tahmin': '1', 'guven': 'KESİN'},
            {'ad': 'Cümlede Anlam', 'frekans_8yil': '8/8 yıl 1 soru', 'tahmin': '1', 'guven': 'KESİN'},
            {'ad': 'Paragrafta Anlam', 'frekans_8yil': '2020+ 4 sabit', 'tahmin': '4', 'guven': 'KESİN'},
            {'ad': 'Şiir Bilgisi', 'frekans_8yil': 'Yılda 1-3, ort 2.1', 'tahmin': '2', 'guven': 'YÜKSEK'},
            {'ad': 'Söz Sanatları', 'frekans_8yil': 'Yılda 1-2', 'tahmin': '1-2', 'guven': 'YÜKSEK'},
            {'ad': 'Nesir Bilgisi', 'frekans_8yil': 'Yılda 1-3', 'tahmin': '2', 'guven': 'YÜKSEK'},
            {'ad': 'İslamiyet Öncesi/Geçiş', 'frekans_8yil': 'Son 3 yıl 1\'er', 'tahmin': '1', 'guven': 'YÜKSEK (artan trend)'},
            {'ad': 'Halk Edebiyatı', 'frekans_8yil': '6 toplam, 2025 BOŞ', 'tahmin': '1-2', 'guven': 'ÇOK YÜKSEK (boşluk telafisi)'},
            {'ad': 'Divan Edebiyatı', 'frekans_8yil': 'Yılda 2-5, ort 3.6', 'tahmin': '3-4', 'guven': 'KESİN'},
            {'ad': 'Tanzimat', 'frekans_8yil': '8/8 yıl 1-2', 'tahmin': '1', 'guven': 'KESİN'},
            {'ad': 'Servet-i Fünun / Fecr-i Âti', 'frekans_8yil': 'Yılda 1-2, ort 1.1', 'tahmin': '1-2', 'guven': 'YÜKSEK'},
            {'ad': 'Milli Edebiyat', 'frekans_8yil': '5 toplam, 2025 geldi', 'tahmin': '0-1', 'guven': 'ORTA-DÜŞÜK'},
            {'ad': 'Cumhuriyet Dönemi', 'frekans_8yil': 'Yılda 2-5, ort 3.1', 'tahmin': '3', 'guven': 'KESİN'},
            {'ad': 'Geleneksel Tiyatro', 'frekans_8yil': '4 toplam, 2025 geldi', 'tahmin': '0', 'guven': 'DÜŞÜK'},
            {'ad': 'Masal/Fabl/Destan', 'frekans_8yil': '8 toplam, yılaşırı', 'tahmin': '1', 'guven': 'YÜKSEK'},
            {'ad': 'Edebi Akımlar', 'frekans_8yil': '8/8 yıl 1 soru', 'tahmin': '1', 'guven': 'KESİN'},
        ],
        'yazarlar_cok_yuksek': [
            {'ad': 'Halit Ziya Uşaklıgil', 'not_': '2023\'te geldi, 2024-25 boş — SF romanı klasiği'},
            {'ad': 'Necip Fazıl Kısakürek', 'not_': 'son 3 yıl boş — saf şiir mistik'},
            {'ad': 'Peyami Safa', 'not_': 'son 2 yıl boş — bireyin iç dünyası'},
            {'ad': 'Sait Faik Abasıyanık', 'not_': 'son 2 yıl boş — durum hikayesi'},
            {'ad': 'Şinasi', 'not_': 'son 2 yıl boş — Tanzimat öncüsü, ilkler'},
            {'ad': 'Yahya Kemal Beyatlı', 'not_': 'son 2 yıl boş — saf şiir'},
            {'ad': 'Ömer Seyfettin', 'not_': 'son 5 yıl boş — hikaye klasiği'},
            {'ad': 'Baki', 'not_': 'son 3 yıl boş — divan ikinci zirvesi'},
        ],
        'yazarlar_orta': [
            'Ahmet Hamdi Tanpınar, Tarık Buğra, Yakup Kadri',
            'Nef\'i, Şeyh Galip, Süleyman Çelebi, Yunus Emre',
        ],
        'bosluk_adaylari': [
            {'ad': 'Yedi Meşaleciler', 'not_': 'Cevdet Kudret, Ziya Osman Saba, Sabri Esat, Yaşar Nabi (1928, MEBİ s.76)'},
            {'ad': 'Hisarcılar', 'not_': 'Munis Faik Ozansoy, Mehmet Çınarlı (MEBİ s.83)'},
            {'ad': 'Maviciler / Attila İlhan', 'not_': '8 yılda 0 (MEBİ s.81)'},
            {'ad': 'Mustafa Kutlu, Bilge Karasu, İhsan Oktay Anar', 'not_': 'Modernist/postmodernist az sorulanlar'},
            {'ad': 'Behçet Necatigil, Asaf Halet Çelebi, A.M. Dıranas', 'not_': 'Saf şiir az sorulanlar'},
        ],
        'bosluk_haritasi': [
            {'konu': 'DİVAN', 'alt_basliklar': 'Müstezat, Terkib-i Bend, Terci-i Bend, Tezkire', 'guc': 'YÜKSEK'},
            {'konu': 'NESİR BİLGİSİ', 'alt_basliklar': 'Mektup, Günlük, Fıkra, Sohbet türleri', 'guc': 'YÜKSEK'},
            {'konu': 'SF/FECR-İ ÂTİ', 'alt_basliklar': 'Cenap Şahabettin Elhan-ı Şita dışı eserler, Mehmet Rauf hikayeler', 'guc': 'YÜKSEK'},
            {'konu': 'MİLLİ EDEBİYAT', 'alt_basliklar': 'Ziya Gökalp teorisi, Genç Kalemler manifestoları, Mehmet Emin Yurdakul', 'guc': 'YÜKSEK'},
            {'konu': 'CUMHURİYET', 'alt_basliklar': 'Yedi Meşaleciler, Hisarcılar, Maviciler, postmodernler', 'guc': 'ÇOK YÜKSEK'},
            {'konu': 'HALK EDEBİYATI', 'alt_basliklar': 'Varsağı türü, Erzurumlu Emrah, Gevheri', 'guc': 'YÜKSEK'},
            {'konu': 'İSL.ÖNCESİ', 'alt_basliklar': 'Divan-ı Hikmet detayları, Orhun yazıtları (Bilge Kağan vs Kül Tigin)', 'guc': 'YÜKSEK'},
            {'konu': 'EDEBİ AKIMLAR', 'alt_basliklar': 'Ekspresyonizm (Kafka), Empresyonizm', 'guc': 'YÜKSEK'},
        ],
    }
    with open(SITE / 'predictions.json', 'w', encoding='utf-8') as f:
        json.dump(predictions, f, ensure_ascii=False, indent=1)
    print("  → predictions.json")

    # ====== PROGRAM ======
    print("\n=== PROGRAM ===")
    program = {
        'haftalar': [
            {
                'baslik': 'Yüksek Frekans Temel — 14 Net Potansiyeli',
                'gunler': [
                    {'gun':'Pzt','konu':'Divan: Nazım biçimleri (gazel, kaside, mesnevi)','rehber':'Bölüm 3.1 §A-§C ilk 5 alt başlık','mebi':'MEBİ s.44-52','sorular':'PDF 95-110 / 10 soru'},
                    {'gun':'Sal','konu':'Divan: 16-18. yy şairler (Fuzuli, Baki, Nef\'i, Nabi, Nedim, Şeyh Galip)','rehber':'Bölüm 3.1 §C son 4 alt başlık','mebi':'MEBİ s.53-59','sorular':'PDF 111-123 / 10 soru'},
                    {'gun':'Çar','konu':'Cumhuriyet ŞİİR akımları (8 akım)','rehber':'Bölüm 3.2 §C alt 1-5','mebi':'MEBİ s.75-91','sorular':'PDF 148-172 şiir soruları'},
                    {'gun':'Per','konu':'Cumhuriyet ROMAN/HİKAYE (toplumcu + bireyin iç d.)','rehber':'Bölüm 3.2 §C alt 6-7','mebi':'MEBİ s.114-118 + 137-142','sorular':'PDF 148-172 roman/hikaye'},
                    {'gun':'Cum','konu':'Cumhuriyet: modernist + Sait Faik + tiyatro','rehber':'Bölüm 3.2 §C alt 8-10','mebi':'MEBİ s.115-120 + 158-164','sorular':'Önceki atlanmış sorular'},
                    {'gun':'Cmt','konu':'Şiir Bilgisi + Söz Sanatları','rehber':'Bölüm 3.3 + 3.4 tümü','mebi':'MEBİ s.13-21 + 22-25','sorular':'PDF 44-70 (tüm)'},
                    {'gun':'Paz','konu':'TEKRAR — ezber paketleri','rehber':'3.1, 3.2, 3.3, 3.4 yeşil kutular','mebi':'Hızlı geç','sorular':'Yanlışları tekrar çöz'},
                ],
            },
            {
                'baslik': 'Dönem Edebiyatları — +4 Net (Toplam 18)',
                'gunler': [
                    {'gun':'Pzt','konu':'Tanzimat — "İlk"ler + I. dönem','rehber':'Bölüm 3.6 §A-§B','mebi':'MEBİ s.60-62 + 127-130','sorular':'PDF 124-133 (10 soru)'},
                    {'gun':'Sal','konu':'Tanzimat II. dönem (Recaizade rekortmen)','rehber':'Bölüm 3.6 II.dönem alt','mebi':'MEBİ s.63-64 + 153-157','sorular':'Aynı 124-133'},
                    {'gun':'Çar','konu':'Servet-i Fünun + Fecr-i Âti','rehber':'Bölüm 3.7 (Halit Ziya 8 eser + Tevfik Fikret + Ahmet Haşim)','mebi':'MEBİ s.65-69 + 131-133','sorular':'PDF 134-142 (9 soru)'},
                    {'gun':'Per','konu':'Milli Edebiyat','rehber':'Bölüm 3.8','mebi':'MEBİ s.70-74 + 112-113 + 134-136','sorular':'PDF 143-147 (5 soru)'},
                    {'gun':'Cum','konu':'Halk Edebiyatı','rehber':'Bölüm 3.9 tümü','mebi':'MEBİ s.30-43','sorular':'PDF 89-94 (6 soru)'},
                    {'gun':'Cmt','konu':'İsl.Öncesi/Geçiş + Geleneksel Tiyatro + Masal','rehber':'Bölüm 3.10 + 3.11 + 3.12','mebi':'MEBİ s.26-29 + 149-152 + 165-171','sorular':'PDF 85-88 + 173-184'},
                    {'gun':'Paz','konu':'TEKRAR — Hafta 2 ezber paketleri','rehber':'3.6-3.12 yeşil kutular','mebi':'Hızlı geç','sorular':'Yanlışları tekrar'},
                ],
            },
            {
                'baslik': 'Edebi Akımlar + Yazar Matrisi — +2 Net (Toplam 20)',
                'gunler': [
                    {'gun':'Pzt','konu':'Edebi Akımlar I (Klas-Romantik-Real-Natüralist)','rehber':'Bölüm 3.13 §A + ilk 2 alt','mebi':'MEBİ s.186-188','sorular':'PDF 185-192'},
                    {'gun':'Sal','konu':'Edebi Akımlar II (Parnasizm-Sembolizm + 20.yy)','rehber':'Bölüm 3.13 §B son 2 alt','mebi':'MEBİ s.189-190','sorular':'Aynı 185-192 devamı'},
                    {'gun':'Çar','konu':'Nesir Bilgisi','rehber':'Bölüm 3.5 tümü','mebi':'MEBİ s.102-126 + 172-185','sorular':'PDF 71-84 (14 soru)'},
                    {'gun':'Per','konu':'Yazar Matrisi — Tablo A (50 tekrar yazar)','rehber':'Bölüm 4 Tablo A','mebi':'MEBİ s. sütunundan her yazara git','sorular':'Zayıf yazarlardan ekstra'},
                    {'gun':'Cum','konu':'Tablo B göz atma + 2026 Tahminleri','rehber':'Bölüm 4 Tablo B + Bölüm 5','mebi':'Boşluk konuları: s.76, 83','sorular':'Analiz günü'},
                    {'gun':'Cmt','konu':'Boşluk Adayları (Y.Meşale, Hisarcılar, Maviciler, postmodern)','rehber':'Bölüm 5.3','mebi':'MEBİ s.76, 83, 81, 117-120, 142','sorular':'Bu konulara değen sorular'},
                    {'gun':'Paz','konu':'TEKRAR — Hafta 3 + Mini Sözlük','rehber':'Bölüm 3.5, 3.13 + Bölüm 7','mebi':'Tarama yok','sorular':'Hafta 3 yanlışları'},
                ],
            },
            {
                'baslik': 'Konsolidasyon ve Deneme',
                'gunler': [
                    {'gun':'Pzt','konu':'Hızlı tekrar — Bölüm 3.1-3.6','rehber':'Sadece EZBER PAKETLERİ','mebi':'MEBİ s.13-67 göz gezdir','sorular':'Zayıf hissedilen 10 soru'},
                    {'gun':'Sal','konu':'Hızlı tekrar — Bölüm 3.7-3.13','rehber':'Sadece EZBER PAKETLERİ','mebi':'MEBİ s.68-190 göz gezdir','sorular':'Zayıf hissedilen 10 soru'},
                    {'gun':'Çar','konu':'Yazar Tabloları + Mini Sözlük','rehber':'Bölüm 4 + Bölüm 7 tümü','mebi':'Spot kontroller','sorular':'Yazar-eser eşleştirme'},
                    {'gun':'Per','konu':'1. DENEME (örn. 2024 sınavı)','rehber':'Yok','mebi':'Yok','sorular':'Geçmiş 1 yılın TÜMÜ — zaman tutarak'},
                    {'gun':'Cum','konu':'Deneme analizi + eksiklere dönüş','rehber':'Yanlış konunun Bölüm 3.x','mebi':'Yanlış konunun MEBİ sayfaları','sorular':'Hatalı 5-10 soru tekrar'},
                    {'gun':'Cmt','konu':'2. DENEME (örn. 2025)','rehber':'Yok','mebi':'Yok','sorular':'Başka 1 yılın TÜMÜ'},
                    {'gun':'Paz','konu':'Boşluk adayları + son ezber','rehber':'Bölüm 5.3 + Bölüm 7','mebi':'MEBİ s.76 + 83 + 81 + 117-120','sorular':'Boşluk konularına özgü'},
                ],
            },
        ],
    }
    with open(SITE / 'program.json', 'w', encoding='utf-8') as f:
        json.dump(program, f, ensure_ascii=False, indent=1)
    print("  → program.json (4 hafta × 7 gün)")

    # ====== GLOSSARY ======
    print("\n=== GLOSSARY ===")
    glossary = {
        'bolumler': [
            {
                'baslik': '9 Edebi Akım — Tek Bakışta',
                'basliklar': ['Akım', 'Dönem/Yer', 'Esas', 'Temsilciler'],
                'satirlar': [
                    ['Klasisizm', '17. yy Fransa', 'Akıl, antik, 3 birlik', 'Molière, Racine, Corneille, La Fontaine, Boileau'],
                    ['Romantizm', '19. yy başı Fransa', 'Duygu, hayal, halk', 'V. Hugo, Lamartine, Goethe, Schiller, Byron'],
                    ['Realizm', '19. yy ortası', 'Gözlem, gerçeklik', 'Balzac, Stendhal, Flaubert, Dostoyevski, Tolstoy'],
                    ['Natüralizm', '19. yy sonu', 'Bilimsel determinizm', 'Émile Zola, Maupassant, Goncourt'],
                    ['Parnasizm', '19. yy ortası', 'Şiir+biçim+objektif', 'Gautier, Leconte de Lisle, Heredia'],
                    ['Sembolizm', '19. yy sonu', 'Sembol+sezgi+müzik', 'Baudelaire, Verlaine, Rimbaud, Mallarmé'],
                    ['Fütürizm', '1909 İtalya', 'Hız+makine+gelecek', 'Marinetti'],
                    ['Dadaizm', '1916 İsviçre', 'Sanat karşıtı, anlamsız', 'Tristan Tzara, Hans Arp'],
                    ['Sürrealizm', '1924 Fransa', 'Bilinçaltı+rüya+Freud', 'André Breton, Aragon, Éluard, Dali'],
                    ['Egzistansiyalizm', '20. yy', 'Varoluş özden önce', 'Sartre, Camus, Heidegger, Kierkegaard'],
                    ['Ekspresyonizm', '20. yy Almanya', 'İç dünya dışa vurma', 'Kafka, Strindberg, Trakl'],
                ],
            },
            {
                'baslik': 'Türk Edebiyatı Dönemleri',
                'basliklar': ['Dönem', 'Yıllar', 'Önemli Sanatçılar', 'Tipik Eserler'],
                'satirlar': [
                    ['Sözlü Dönem', 'M.Ö.-10. yy', 'Anonim ozanlar', 'Koşuk, sagu, sav, destanlar'],
                    ['Geçiş Dön. (Karahanlı)', '10-13. yy', 'Yusuf Has Hacip, Kaşgarlı, Yesevi', 'Kutadgu Bilig, Divânü Lügat, Atabet, Divan-ı Hikmet'],
                    ['Divan Edebiyatı', '13-19. yy', "Fuzuli, Baki, Nedim, Nef'i, Şeyh Galip", 'Leyla vü Mecnun, Su Kasidesi, Hüsn ü Aşk'],
                    ['Halk Edebiyatı', '13. yy-günümüz', 'Yunus, Pir Sultan, Karacaoğlan', 'Koşma, semai, ilahi, nefes'],
                    ['Tanzimat I.', '1860-1876', 'Şinasi, N. Kemal, Z. Paşa, A. Mithat', 'Şair Evlenmesi, İntibah, Felâtun Bey'],
                    ['Tanzimat II.', '1876-1896', 'Recaizade, A. Hamit, Nabizade', 'Araba Sevdası, Makber, Karabibik'],
                    ['Servet-i Fünun', '1896-1901', 'Halit Ziya, T. Fikret, C. Şahabettin', 'Aşk-ı Memnu, Rübab-ı Şikeste, Elhan-ı Şita'],
                    ['Fecr-i Âti', '1909-1912', 'Ahmet Haşim', 'Piyale, Göl Saatleri'],
                    ['Milli Edebiyat', '1911-1923', 'Ömer Seyfettin, Y. Kadri, R. Nuri, H. Edip', 'Bomba, Yaban, Çalıkuşu, Sinekli Bakkal'],
                    ['Cumhuriyet', '1923-günümüz', 'Yahya Kemal, N. Hikmet, S. Faik, O. Atay', 'Çile, Tutunamayanlar, İnce Memed, Huzur'],
                ],
            },
            {
                'baslik': 'Tanzimat "İlk"leri',
                'basliklar': ['İlk', 'Eser', 'Yazar', 'Yıl'],
                'satirlar': [
                    ['İlk yerli roman', 'Taaşşuk-ı Talat ve Fitnat', 'Şemsettin Sami', '1872'],
                    ['İlk roman çevirisi', 'Telemak', 'Yusuf Kamil Paşa', '1859'],
                    ['İlk edebi roman', 'İntibah', 'Namık Kemal', '1876'],
                    ['İlk tarihi roman', 'Cezmi', 'Namık Kemal', '1880'],
                    ['İlk realist roman', 'Araba Sevdası', 'Recaizade Mahmut Ekrem', '1898'],
                    ['İlk köy romanı', 'Karabibik', 'Nabizade Nazım', '1891'],
                    ['İlk psikolojik roman denemesi', 'Zehra', 'Nabizade Nazım', '1896'],
                    ['İlk psikolojik roman', 'Eylül', 'Mehmet Rauf', '1901'],
                    ['İlk tiyatro (sahnelenen)', 'Şair Evlenmesi', 'Şinasi', '1860'],
                    ['İlk makale', 'Tercüman-ı Ahvâl Mukaddimesi', 'Şinasi', '1860'],
                    ['İlk özel Türk gazetesi', 'Tercüman-ı Ahvâl', 'Şinasi + Agah Efendi', '1860'],
                    ['İlk pastoral şiir', 'Sahra', 'Abdülhak Hamit', '1879'],
                    ['İlk büyük Türk-İslam mesnevisi', 'Kutadgu Bilig', 'Yusuf Has Hacip', '1069'],
                ],
            },
            {
                'baslik': 'Söz Sanatları — Tek Satır Özet',
                'basliklar': ['Sanat', 'Tanım', 'Örnek/Not'],
                'satirlar': [[s, t.split('.')[0], t.split('.', 1)[1] if '.' in t else ''] for s, t in SOZ_SANATI_TANIM.items()],
            },
            {
                'baslik': 'Halk vs Divan Nazım Biçimleri',
                'basliklar': ['Özellik', 'Halk', 'Divan'],
                'satirlar': [
                    ['Vezin', 'HECE', 'ARUZ'],
                    ['Nazım birimi', 'DÖRTLÜK', 'BEYİT'],
                    ['Dil', 'Sade Türkçe', 'Arapça-Farsça karışık'],
                    ['Konu', 'Aşk, doğa, halk', 'Aşk (mistik), şarap, padişah'],
                    ['Biçimler', 'Mani, koşma, semai, varsağı, destan', "Gazel, kaside, mesnevi, rubai, müstezat, şarkı"],
                    ['Şairler', 'Karacaoğlan, Köroğlu, Yunus, Pir Sultan', "Fuzuli, Baki, Nedim, Nef'i, Şeyh Galip"],
                ],
            },
        ],
    }
    with open(SITE / 'glossary.json', 'w', encoding='utf-8') as f:
        json.dump(glossary, f, ensure_ascii=False, indent=1)
    print("  → glossary.json")

    print("\n=== ÖZET ===")
    print(f"  Toplam kart: {len(all_cards)}")
    print(f"  Topic: {len(topics_index)}")
    print(f"  Yazar: {len(authors_list)}")
    print("\nTüm JSON dosyaları üretildi.")


if __name__ == '__main__':
    main()
