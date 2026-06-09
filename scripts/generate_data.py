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
from sections_authors_predictions import EXTRA_WORKS_BY_AUTHOR as EXTRA_WORKS

BASE = Path(__file__).parent.parent.parent  # Edebiyat Analiz/
# REV17: site data.js subject-aware path → ./data/edebiyat/. Bu yüzden output dir 'edebiyat' alt klasörü.
SITE = Path(__file__).parent.parent / 'public' / 'data' / 'edebiyat'
SITE.mkdir(parents=True, exist_ok=True)
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
    'Ömer Seyfettin': ['Bomba', 'Pembe İncili Kaftan', 'Falaka', 'Kaşağı', 'Diyet', 'Yüksek Ökçeler', 'Forsa', 'Başını Vermeyen Şehit', 'Yalnız Efe', 'Beyaz Lale', 'Kızıl Elma Neresi', 'Efruz Bey'],
    'Ziya Gökalp': ['Türkçülüğün Esasları', 'Kızılelma', 'Yeni Hayat', 'Altın Işık', 'Türkleşmek İslamlaşmak Muasırlaşmak', 'Türk Medeniyeti Tarihi', 'Malta Mektupları'],
    'Ali Canip Yöntem': ['Geçtiğim Yol', 'Milli Edebiyat Meselesi ve Cenab Bey\'le Münakaşalarım'],
    'Mehmet Emin Yurdakul': ['Türk Sazı', 'Cenge Giderken', 'Ey Türk Uyan', 'Tan Sesleri', 'Ordunun Destanı'],
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
    # ====== REV17 — Eksik çıkmış yazarlar ======
    # Divan eksikleri
    'Taşlıcalı Yahya': ['Şah u Geda', 'Gencîne-i Râz', 'Gülşen-i Envâr', 'Yusuf u Züleyha', 'Kitab-ı Usul', 'Şehzade Mustafa Mersiyesi'],
    'Aşık Paşa': ['Garibname', 'Fakrname', 'Vasf-ı Hâl', 'Hikâye'],
    'Ahmet Paşa': ['Divan', 'Kerem Kasidesi'],
    'Sehi Bey': ['Heşt Bihişt'],
    'Şeyhülislam Yahya': ['Divan'],
    'Hamdullah Hamdi': ['Yusuf u Züleyha', 'Leyla vü Mecnun', "Tuhfetü'l-Uşşak", 'Kıyafetname', 'Ahmediyye'],
    'Zati': ['Şem ü Pervane', 'Divan', 'Edirne Şehrengizi'],
    'Neşati': ['Divan', 'Şitaiyye'],
    # Tanzimat eksikleri (REV4'ten Direktör Ali Bey zaten EXTRA_WORKS'ta)
    'Hüseyin Rahmi Gürpınar': ['Mürebbiye', 'Şıpsevdi', 'Şık', 'Kuyruklu Yıldız Altında Bir İzdivaç', 'Gulyabani', 'Cadı', 'Ben Deli miyim?'],
    # Cumhuriyet eksikleri
    'Sevgi Soysal': ["Yenişehir'de Bir Öğle Vakti", 'Tante Rosa', 'Tutkulu Perçem', 'Yürümek', 'Şafak'],
    'İsmet Özel': ['Erbain', 'Of Not Being a Jew', 'Şair Erbain', 'Bir Yusuf Masalı'],
    'Cevat Fehmi Başkut': ['Buzlar Çözülmeden', 'Paydos', 'Küçük Şehir', 'Hacı Kaptan', 'Sana Rey Veriyorum'],
    # Edebi akımlar (kuramsal/yabancı)
    'Aristoteles': ['Poetika', 'Retorik', "Nikomakhos'a Etik"],
    # REV19e — MEBİ denemede sık geçen, eseri eksik yazarlar
    'Bağdatlı Ruhi': ['Terkib-i Bend', 'Divan'],
    'Füruzan': ['Parasız Yatılı', 'Kuşatma', 'Benim Sinemalarım', 'Gül Mevsimidir', 'Gecenin Öteki Yüzü'],
    'Hilmi Yavuz': ['Bakış Kuşu', 'Doğu Şiirleri', 'Gizemli Şiirler', 'Yara Şiirleri', 'Çöl Şiirleri'],
    'Recep Bilginer': ['Sarı Naciye', 'İsyancılar', 'Gazeteciden Dost', 'Ben Devletim', 'Karaağaç'],
    'Selim İleri': ['Her Gece Bodrum', 'Cehennem Kraliçesi', 'Ölüm İlişkileri', 'Mavi Kanatlarınla Yalnız Benim Olsaydın', 'Yarın Yapayalnız'],
    'Hacı Bektaş Veli': ['Makalat', 'Vilayetname', 'Şathiyye'],
    'Dertli': ['Dertli Divanı', 'Şiirleri'],
    'İlhan Geçer': ['Belki', 'Vurgun', 'Bir Bulut Geçti', 'Yıllar ve İzler'],
    # REV19g — 0 kartlı yazarlara spesifik eser (sadece generic/eser-yok olanlar)
    'Necati Bey': ['Necati Divanı', 'Gül-i Sad-berg'],
    'Hayali Bey': ['Hayali Divanı'],
    'Naili': ['Naili Divanı'],
    'Hoca Dehhani': ['Selçuklu Şehnamesi'],
    'Hacı Bayram Veli': ['Hacı Bayram Veli Nutukları'],
    'Pir Sultan Abdal': ['Pir Sultan Abdal Deyişleri'],
    'Direktör Ali Bey': ['Kokona Yatıyor', 'Misafiri İstiskal', "Lehçetü'l-Hakayık", 'Seyahat Jurnali'],
    'Aka Gündüz': ['Dikmen Yıldızı', 'Bir Şoförün Gizli Defteri', 'Çapkın Kız', 'Onların Romanı'],
    'Adalet Ağaoğlu': ['Ölmeye Yatmak', 'Bir Düğün Gecesi', 'Fikrimin İnce Gülü', 'Yüksek Gerilim', 'Dar Zamanlar'],
    'Pınar Kür': ['Yarın Yarın', 'Asılacak Kadın', 'Bir Cinayet Romanı', 'Küçük Oyuncu'],
    'Ahmet Muhip Dıranas': ['Gölgeler', 'Fahriye Abla', 'Olvido', 'Şiirler'],
    # Yabancı (edebi akım / paragraf bağlamı)
    'Shakespeare': ['Hamlet', 'Othello', 'Romeo ve Juliet', 'Macbeth', 'Kral Lear'],
    'Molière': ['Cimri', 'Tartuffe', 'Kibarlık Budalası', 'Hastalık Hastası'],
    'Mary Shelley': ['Frankenstein'],
    'Freud': ['Rüyaların Yorumu', 'Psikanalize Giriş', 'Totem ve Tabu'],
    'Brancusi': ['Öpüşme', 'Sonsuz Sütun', 'Uçan Kuş'],
    'Tesla': ["Buluşlarım", "Tesla'nın Otobiyografisi"],
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
    **{y: 'milli' for y in ['Ömer Seyfettin','Ziya Gökalp','Ali Canip Yöntem','Mehmet Emin Yurdakul','Yakup Kadri Karaosmanoğlu','Halide Edip Adıvar','Reşat Nuri Güntekin','Refik Halit Karay','Memduh Şevket Esendal','Mithat Cemal Kuntay','Ahmet Hikmet Müftüoğlu','Faruk Nafiz Çamlıbel','Halit Fahri Ozansoy','Enis Behiç Koryürek','Yusuf Ziya Ortaç','Orhan Seyfi Orhon']},
    # Cumhuriyet
    **{y: 'cumhuriyet' for y in ['Cevdet Kudret','Ziya Osman Saba','Sabri Esat Siyavuşgil','Yaşar Nabi Nayır','Vasfi Mahir Kocatürk','Kenan Hulusi Koray','Yahya Kemal Beyatlı','Mehmet Akif Ersoy','Cahit Sıtkı Tarancı','Ahmet Hamdi Tanpınar','Ahmet Muhip Dıranas','Necip Fazıl Kısakürek','Asaf Halet Çelebi','Behçet Necatigil','Fazıl Hüsnü Dağlarca','Arif Nihat Asya','Ahmet Kutsi Tecer','Bedri Rahmi Eyüboğlu','Cahit Külebi','Orhan Veli Kanık','Oktay Rifat','Melih Cevdet Anday','Cemal Süreya','Edip Cansever','Turgut Uyar','İlhan Berk','Sezai Karakoç','Ece Ayhan','Nazım Hikmet','Rıfat Ilgaz','Ahmed Arif','Ataol Behramoğlu','Munis Faik Ozansoy','Mehmet Çınarlı','Attila İlhan','Sabahattin Ali','Yaşar Kemal','Orhan Kemal','Kemal Tahir','Fakir Baykurt','Talip Apaydın','Mahmut Makal','Peyami Safa','Tarık Buğra','Mustafa Kutlu','Samiha Ayverdi','Oğuz Atay','Yusuf Atılgan','Bilge Karasu','Orhan Pamuk','İhsan Oktay Anar','Latife Tekin','Hasan Ali Toptaş','Sait Faik Abasıyanık','Halikarnas Balıkçısı','Haldun Taner','Turgut Özakman','Necati Cumalı','Güngör Dilmen','Turan Oflazoğlu','Nurullah Ataç','Suut Kemal Yetkin','Falih Rıfkı Atay']},
    # Geçiş
    **{y: 'gecis' for y in ['Yusuf Has Hacip','Kaşgarlı Mahmut','Edip Ahmet Yükneki','Ahmet Yesevi']},
    # REV17 eksikleri
    **{y: 'divan' for y in ['Taşlıcalı Yahya','Aşık Paşa','Ahmet Paşa','Sehi Bey','Şeyhülislam Yahya','Hamdullah Hamdi','Zati','Neşati']},
    **{y: 'tanzimat' for y in ['Hüseyin Rahmi Gürpınar']},  # Tanzimat-Milli geçişi
    **{y: 'cumhuriyet' for y in ['Sevgi Soysal','İsmet Özel','Cevat Fehmi Başkut']},
    **{y: 'edebi_akim' for y in ['Aristoteles']},  # yabancı akım teorisyeni
    # REV19e — MEBİ-only yazarların dönemleri (eseri yeni eklenenler)
    **{y: 'divan' for y in ['Bağdatlı Ruhi', 'Naili']},
    **{y: 'halk' for y in ['Dertli', 'Hacı Bektaş Veli', 'Hacı Bayram Veli']},
    **{y: 'cumhuriyet' for y in ['Füruzan', 'Hilmi Yavuz', 'Recep Bilginer', 'Selim İleri', 'İlhan Geçer', 'Aka Gündüz', 'Adalet Ağaoğlu', 'Pınar Kür']},
    **{y: 'tanzimat' for y in ['Direktör Ali Bey']},
    # Yabancı (edebi akım / paragraf bağlamı) — konu: edebi_akimlar
    **{y: 'edebi_akim' for y in ['Shakespeare', 'Molière', 'Mary Shelley', 'Freud', 'Brancusi', 'Tesla']},
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
    'edebi_akim': 'edebi_akimlar',
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

# Söz sanatları + gerçek beyit/cümle örnekleri (REVİZYON 4)
SOZ_SANATI_TANIM = {
    'Benzetme (Teşbih)': 'Bir varlığı başka varlığa benzetme. 4 unsur: benzeyen, kendisine benzetilen, yön, edat. Örnek: "Aslan gibi cesur bir delikanlı" (delikanlı=benzeyen, aslan=k.b., cesur=yön, gibi=edat).',
    'İstiare (Açık)': 'Sadece KENDİSİNE BENZETİLEN söylenir. Örnek: "Bir hilal uğruna ya Rab ne güneşler batıyor" (Mehmet Akif) — güneşler = şehit askerler.',
    'İstiare (Kapalı)': 'BENZEYEN söylenir + kendisine benzetilenin özelliği verilir. Örnek: "Gül açıldı saçları dağıldı" — gül = sevgili (saç insan özelliği).',
    'Mecaz-ı Mürsel': 'Benzetme amacı OLMADAN ilgi yoluyla aktarma. Örnek: "Sobayı yaktım" (içindeki yakıtı), "Bu akşam Yahya Kemal okudum" (eserlerini).',
    'Teşhis-İntak': 'Cansıza canlı özellikleri (teşhis) / konuşturma (intak). Örnek: "Ağaçlar el sallıyor" (Cahit Sıtkı). Fabllarda hayvanları konuşturma = intak.',
    'Tezat': 'Karşıt anlamlı sözcükler bir arada. Örnek: "Aşk derdiyle hoşem el çek ilacımdan tabip" (Fuzuli) — dert + hoş (mutluluk).',
    'Tenasüp': 'Anlamca İLGİLİ sözcükler bir arada. Örnek: "Bende Mecnun\'dan füzun aşıklık istidadı var / Aşık-ı sadık benim Mecnun\'un ancak adı var" (Fuzuli) — Mecnun + aşık + sevgi.',
    'Telmih': 'Tarihi/dini bir olaya gönderme. Örnek: "Süzme çeşmin gelmesin müjgan müjgan üstüne" (Şeyh Galip) — Mecnun-Leyla aşkına atıf.',
    'Hüsn-i Talil': 'Gerçek bir olaya hayali güzel bir sebep yakıştırma. Örnek: "Güller açmış çünkü bahar gelmiş" (gerçek) → "Güller açmış çünkü sevgilim geldi" (hüsn-i talil).',
    'Tevriye': 'Sözcüğün YAKIN ve UZAK iki anlamından UZAK olanını kastetme (Divan). Örnek: "Bana Tahir Efendi kelp demiş / İltifatı bu sözde zahirdir" (Nef\'i) — "tahir" hem kişi adı hem "temiz" anlamında.',
    'Mübalağa': 'Aşırı abartma. Örnek: "Sözleriyle dağları söker, denizleri kurutur" (klasik abartı).',
    'Kinaye': 'Açık ve gizli iki anlam, gizli anlam kastedilir. Örnek: "Elinin hamuruyla erkek işine karışma" (deyim, gerçek anlamda hamur değil).',
    'Tariz': 'İğneleme, tersini söyleme. Örnek: Tembele "Senin gibi çalışkanı bulamadım" demek.',
    'Nida': 'Ünlem. Örnek: "Ey Türk istikbalinin evladı!" (Atatürk - Gençliğe Hitabe).',
    'Tecahül-i Ârif': 'Bilineni bilmiyormuş gibi sorma. Örnek: "Şakaklarıma kar mı yağdı ne var?" (Cahit Sıtkı) — yaşlandığını bildiği halde sorma.',
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


def card(id_, konu, alt, tip, soru, dogru_text, celdiriciler, aciklama, tuzak='',
         mebi_sayfa='', zorluk='orta', osym_stratejisi='', dersini_ogren=''):
    """Bir kart oluştur (REV18b: osym_stratejisi + dersini_ogren alanları eklendi)."""
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
        # REV18b — Pedagojik derinlik
        'osym_stratejisi': osym_stratejisi,
        'dersini_ogren': dersini_ogren,
    }


# REV18b — Authors meta lookup (zengin template'ler için)
_AUTHORS_META_CACHE = None
def get_author_meta(yazar):
    """authors.json'dan donem/pozisyon/anekdot/klasik_tuzak/rakipleri çek."""
    global _AUTHORS_META_CACHE
    if _AUTHORS_META_CACHE is None:
        try:
            ap = SITE / 'authors.json'
            if ap.exists():
                data = json.loads(ap.read_text(encoding='utf-8'))
                _AUTHORS_META_CACHE = {a['name']: a for a in data}
            else:
                _AUTHORS_META_CACHE = {}
        except Exception:
            _AUTHORS_META_CACHE = {}
    return _AUTHORS_META_CACHE.get(yazar, {})


# REV18b — Works meta lookup (eser → tür/yıl/akım)
_WORKS_META_CACHE = None
def get_eser_meta(eser_title):
    """works.json'dan tur/yil/cikmis çek (eser adı bazlı)."""
    global _WORKS_META_CACHE
    if _WORKS_META_CACHE is None:
        try:
            wp = SITE / 'works.json'
            if wp.exists():
                data = json.loads(wp.read_text(encoding='utf-8'))
                _WORKS_META_CACHE = {}
                for w in data:
                    key = w['title'].lower().strip()
                    if key not in _WORKS_META_CACHE:
                        _WORKS_META_CACHE[key] = w
            else:
                _WORKS_META_CACHE = {}
        except Exception:
            _WORKS_META_CACHE = {}
    return _WORKS_META_CACHE.get(eser_title.lower().strip(), {})


def build_celdirici_analizi(celdiriciler, dogru_yazar):
    """Çeldiricileri tek tek analiz et — her birinin dönemi + neden cazip."""
    parts = []
    for c in celdiriciler[:3]:  # ilk 3 çeldirici
        m = get_author_meta(c)
        if not m:
            continue
        donem = m.get('donem', '')
        anekdot = (m.get('anekdot') or '')[:80]
        parts.append(f"<strong>{c}</strong> ({donem.replace('_', ' ')}) — {anekdot}...")
    return ' | '.join(parts) if parts else ''


# REV18b — Tip-spesifik pedagojik default'lar (kalan 9 fonksiyon için)
_TIP_OSYM_STRATEJI = {
    'kosma-tur': "ÖSYM koşma türünde KONU AYRIMI test eder: aşk→güzelleme, kahramanlık→koçaklama, yergi→taşlama, ölüm→ağıt. Stratejisi: Soru-paragrafındaki his/tema kelimesini yakala.",
    'kosma-sair': "Aşıkları türleriyle eşleştir: Karacaoğlan=güzelleme (aşk), Köroğlu/Dadaloğlu=koçaklama (kahramanlık), Seyrani=taşlama (yergi), Aşık Veysel=memleket. Strateji: aşık adı + dönem + tema üçlüsünü ezberle.",
    'soz-sanati-tanim': "ÖSYM söz sanatlarında BENZETME-İSTİARE-MECAZ-I MÜRSEL ayrımını test eder. Strateji: 'Benzeyen + benzetilen' var → benzetme; tek unsur var → istiare; benzetme yok ama parça-bütün ilişkisi → mecaz-ı mürsel; ses uyumu → tevriye/cinas.",
    'kafiye': "ÖSYM kafiye türünde SES SAYISINI test eder. Strateji: ses-ses say (yarım=1, tam=2, zengin=3+). Cinas/tunç ise ek anlam katmanı bak.",
    'olcu': "Hece sayısı + duraklar = hece ölçüsü; uzun-kısa hece kalıpları = aruz. Strateji: önce kalıbı çıkar (mef'ûlü/mefâ'îlü vb.); yoksa hece say.",
    'redif': "Kafiye SONRASI tekrarlanan aynı ek/sözcük = redif. Strateji: önce kafiyeyi bul, sonrası varsa redif.",
    'nazim-birimi': "Mısra=tek satır; beyit=2 mısra; dörtlük=4 mısra; bent=4+ mısra topluluğu. Strateji: kaç mısra bir grup oluşturuyor say.",
    'siir-turu': "Lirik=duygu; epik=kahramanlık; didaktik=öğretici; pastoral=doğa/köy; satirik=hiciv. Strateji: paragrafta hâkim duygu/tema → tür.",
    'kavram-tanim': "ÖSYM kavram-tanım sorusunda EDEBİYAT TERMİNOLOJİSİNİ test eder. Strateji: terimi parçala (mahallileşme = yerelleşme; sebk-i hindi = Hint tarzı), kök anlamını yakala.",
    'soylenemez': "Negatif eleme: 4 doğru + 1 YANLIŞ. Strateji: önce doğru olduğuna emin olduğun şıkları ele, kalan = yanlış cevap. Her şık için tek tek mini-doğrulama yap.",
    'negatif-eleme': "Aynı tipte negatif eleme. Strateji: 'değildir/yoktur' kelimesine dikkat. Genel-özel ilişkisini kontrol et.",
    'masal-yapisi': "Masal bölümleri: döşeme (giriş tekerlemesi) → serim → düğüm → çözüm → dilek tekerlemesi. Strateji: bölüm sırası + işlevi ezberle.",
    'destan-tur': "Doğal destan = anonim, sözlü gelenek (Manas, Oğuz Kağan); Yapma destan = belli yazar (Üç Şehitler, Çakır'ın Destanı). Strateji: yazar belli mi/değil mi.",
    'fabl': "Fabl = hayvan kahramanlı + ders veren = Ezop, La Fontaine, Beydeba (Kelile ve Dimne). Strateji: hayvan + ahlak dersi → fabl.",
    'paragraf-yazar-tani': "Paragrafta ipucu kelimeler → yazar. Strateji: dönem+tarz+anahtar eser/kavram. Çoğu zaman 'mahlas, mizah, sade dil, memleket' gibi tek kelime ipucu eserin yazarına götürür.",
    'dortluk-analiz': "Dörtlükten sanat/biçim çıkar. Strateji: kafiye düzeni + nazım birimi + içerikten tür+yazar tahmini.",
    'ilkler-eser': "Tanzimat 'İlk'leri: İlk roman=Taaşşuk-ı Talat ve Fitnat (Şemsettin Sami), İlk yerli roman=İntibah (Namık Kemal), İlk realist=Araba Sevdası (Recaizade), İlk tiyatro=Şair Evlenmesi (Şinasi), İlk köy=Karabibik (Nabizade). Strateji: 'ilk' + tür + dönem üçlüsünü ezberle.",
}

def enrich_kart_default(c):
    """Kart c'ye varsayılan pedagojik alanlar ekle (eğer boşsa).
    REV18b — kalan fonksiyonlar için hızlı pedagojik enrichment."""
    if not c.get('osym_stratejisi'):
        c['osym_stratejisi'] = _TIP_OSYM_STRATEJI.get(c.get('tip',''), '')
    if not c.get('dersini_ogren'):
        # Doğru cevap text'i + kısa özet
        dogru_text = ''
        for opt in c.get('secenekler', []):
            if opt.get('id') == c.get('dogru'):
                dogru_text = opt.get('text', '')
                break
        if dogru_text:
            c['dersini_ogren'] = f"Doğru cevap: {dogru_text}. ({c.get('tip','')} tipi soru)"
    return c


def get_donem_yazarlar(donem):
    return [y for y, d in YAZAR_DONEM.items() if d == donem]


# REV19c — Gerçek ÖSYM çeldiri birliktelikleri (çıkmış sorulardan)
_REAL_DISTRACTORS_CACHE = None
def get_real_distractors():
    global _REAL_DISTRACTORS_CACHE
    if _REAL_DISTRACTORS_CACHE is None:
        try:
            rp = BASE / 'data' / 'real_distractors.json'
            _REAL_DISTRACTORS_CACHE = json.loads(rp.read_text(encoding='utf-8')) if rp.exists() else {}
        except Exception:
            _REAL_DISTRACTORS_CACHE = {}
    return _REAL_DISTRACTORS_CACHE


def celdirici_yazar_ayni_donem(dogru_yazar, n=3):
    """REV19c: önce ÖSYM'nin GERÇEKTE birlikte sorduğu yazarlar (otantik tuzak),
    sonra aynı dönem yazarlarıyla doldur."""
    donem = YAZAR_DONEM.get(dogru_yazar, 'cumhuriyet')
    same_period = shuffle_seed(
        [y for y in get_donem_yazarlar(donem) if y != dogru_yazar],
        dogru_yazar + '-celdirici')
    real = [y for y in get_real_distractors().get(dogru_yazar, [])
            if y in YAZAR_DONEM and y != dogru_yazar]
    ordered = []
    for y in real + same_period:
        if y not in ordered:
            ordered.append(y)
    return ordered[:n]


def celdirici_eser_ayni_yazar_donem(dogru_eser, n=3, exclude_yazar=None):
    """Eser çeldiricisi: REV19c — önce ÖSYM'nin gerçek çeldiri-yazarlarının eserleri,
    sonra doğru eserin yazarının dönemindeki başka eserler.
    exclude_yazar verilirse o yazarın TÜM eserleri çeldiriden kesin çıkar (çift-doğru önleme)."""
    dogru_yazar = exclude_yazar or ESER_YAZAR.get(dogru_eser, '')
    donem = YAZAR_DONEM.get(dogru_yazar, 'cumhuriyet')
    _own_works = set(YAZAR_ESERLERI.get(dogru_yazar, []))
    # REV19c — gerçek çeldiri-yazarların ilk eseri (otantik)
    real_pool = []
    for y in get_real_distractors().get(dogru_yazar, []):
        if y == dogru_yazar:
            continue
        for e in YAZAR_ESERLERI.get(y, [])[:2]:
            if e != dogru_eser:
                real_pool.append(e)
    # Aynı dönem eserleri (fallback/doldurma)
    period_pool = []
    for y, eserler in YAZAR_ESERLERI.items():
        if YAZAR_DONEM.get(y) == donem and y != dogru_yazar:
            period_pool.extend(eserler)
    if len(real_pool) + len(period_pool) < n:
        for y, eserler in YAZAR_ESERLERI.items():
            if y != dogru_yazar and eserler:
                period_pool.append(eserler[0])
    period_pool = shuffle_seed(period_pool, dogru_eser + '-celdirici')
    ordered = []
    for e in real_pool + period_pool:
        # Çift-doğru önleme: doğru yazarın hiçbir eseri çeldiri olamaz
        if e == dogru_eser or e in _own_works or ESER_YAZAR.get(e) == dogru_yazar:
            continue
        if e not in ordered:
            ordered.append(e)
    return ordered[:n]


# =====================================================
# Kart üretim fonksiyonları
# =====================================================

def gen_eser_yazar_cards():
    cards = []
    # Genel/muğlak eser adlarını eleme (birden çok yazara ait olabilir)
    GENERIC = {'Divan', 'Şiirleri', 'Şiirler', 'Şarkıları', 'Nefesler'}
    for yazar, eserler in YAZAR_ESERLERI.items():
        if not eserler: continue
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

            # REV18b — Pedagojik zengin meta
            auth_m = get_author_meta(yazar)
            eser_m = get_eser_meta(eser)
            pozisyon = auth_m.get('pozisyon', '')
            anekdot = (auth_m.get('anekdot') or '')[:300]
            klasik_tuzak = auth_m.get('klasik_tuzak', '')
            eser_tur = eser_m.get('tur', '')
            eser_yil = eser_m.get('yil', '')
            eser_cikmis = eser_m.get('cikmis', False)
            diger = auth_m.get('diger_eserler', '')
            diger_top3 = ', '.join([e.strip() for e in diger.split(',')[:4] if e.strip() and e.strip() != eser])[:140]

            # Zengin açıklama
            eser_meta_str = f"{eser_tur}" if eser_tur and eser_tur != '—' else ''
            if eser_yil: eser_meta_str += f", {eser_yil}" if eser_meta_str else eser_yil
            cikmis_badge = " <span style='color:#f59e0b'>⭐ ÖSYM çıkmış</span>" if eser_cikmis else ""

            aciklama = (
                f"<strong>📖 Eser:</strong> «{eser}»"
                + (f" ({eser_meta_str})" if eser_meta_str else "")
                + f"{cikmis_badge}<br>"
                + f"<strong>✍ Yazar:</strong> {yazar}"
                + (f" — {pozisyon}, {TOPIC_LABEL.get(konu, donem)}" if pozisyon else f" — {TOPIC_LABEL.get(konu, donem)}")
                + "<br><br>"
                + (f"<strong>🎯 Bağlam:</strong> {anekdot}{'...' if len(auth_m.get('anekdot','')) > 300 else ''}<br><br>" if anekdot else "")
                + (f"<strong>📚 Yazarın diğer eserleri:</strong> {diger_top3}" if diger_top3 else "")
            )

            # Zengin tuzak — gerçek klasik tuzak metni + çeldirici analizi
            celdirici_analiz = build_celdirici_analizi(celdiriciler, yazar)
            tuzak = (
                (f"<strong>⚠ KLASİK ÖSYM TUZAĞI:</strong> {klasik_tuzak}<br><br>" if klasik_tuzak else "")
                + (f"<strong>🔍 Şıklardaki çeldiriciler:</strong> {celdirici_analiz}<br><br>" if celdirici_analiz else "")
                + f"<strong>✓ Ayrım anahtarı:</strong> Bu eser doğrudan {yazar}'ın imzasıdır — {pozisyon.lower() if pozisyon else 'yazar'}lık tarzı + dönem özelliklerinden çıkarsanır."
            )

            # ÖSYM stratejisi (kart tipine özel)
            osym_stratejisi = (
                f"ÖSYM 'eser → yazar' sorusunda eserin ÖZEL ANLAMINI ve yazarın imzasını test eder. "
                f"Strateji: (1) Eser türü ({eser_tur or 'belirsiz'}) → yazar pozisyonu eşleşmeli "
                + (f"({pozisyon} ✓)" if pozisyon else "")
                + ". (2) Eser yılı/akımı → yazarın aktif dönemi. (3) Aynı dönemden çeldiriciler — yazarın benzersiz eserlerini öğrenin."
            )

            dersini_ogren = (
                f"«{eser}» = {yazar}'ın imzası"
                + (f" (çünkü {pozisyon.lower()} olarak en bilinen)" if pozisyon else "")
                + "."
            )

            c = card(
                id_=id_,
                konu=konu,
                alt=yazar.lower().replace(' ', '_'),
                tip='eser-yazar',
                soru=f"<strong>«{eser}»</strong> adlı eserin yazarı aşağıdakilerden hangisidir?",
                dogru_text=yazar,
                celdiriciler=celdiriciler,
                aciklama=aciklama,
                tuzak=tuzak,
                mebi_sayfa=mebi if mebi != '—' else '',
                zorluk='orta',
                osym_stratejisi=osym_stratejisi,
                dersini_ogren=dersini_ogren,
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
        spesifik = [e for e in eserler if e.split(' (')[0].strip() not in GENERIC]
        if not spesifik: continue
        dogru_eser = spesifik[0]
        if dogru_eser in seen: continue
        seen.add(dogru_eser)
        celdiriciler = celdirici_eser_ayni_yazar_donem(dogru_eser, 4, exclude_yazar=yazar)
        if len(celdiriciler) < 3: continue
        mebi = MEBI_AUTHOR.get(yazar, '—')
        id_ = f"ye_{len(cards):04d}"

        # REV18b — Pedagojik meta
        auth_m = get_author_meta(yazar)
        eser_m = get_eser_meta(dogru_eser)
        pozisyon = auth_m.get('pozisyon', '')
        anekdot = (auth_m.get('anekdot') or '')[:300]
        klasik_tuzak = auth_m.get('klasik_tuzak', '')
        eser_tur = eser_m.get('tur', '')
        eser_yil = eser_m.get('yil', '')
        cikmis = eser_m.get('cikmis', False)
        diger = auth_m.get('diger_eserler', '')
        diger_top = [e.strip() for e in diger.split(',')[:5] if e.strip() and e.strip() != dogru_eser][:4]

        meta_str = eser_tur if eser_tur and eser_tur != '—' else ''
        if eser_yil: meta_str += f", {eser_yil}" if meta_str else eser_yil
        cikmis_badge = " <span style='color:#f59e0b'>⭐ ÖSYM çıkmış</span>" if cikmis else ""

        aciklama = (
            f"<strong>✍ Yazar:</strong> {yazar}"
            + (f" — {pozisyon}, {TOPIC_LABEL.get(konu, donem)}" if pozisyon else "") + "<br>"
            + f"<strong>📖 Doğru eser:</strong> «{dogru_eser}»"
            + (f" ({meta_str})" if meta_str else "")
            + f"{cikmis_badge}<br><br>"
            + (f"<strong>🎯 Bağlam:</strong> {anekdot}{'...' if len(auth_m.get('anekdot','')) > 300 else ''}<br><br>" if anekdot else "")
            + (f"<strong>📚 Yazarın diğer eserleri:</strong> {', '.join(diger_top)}" if diger_top else "")
        )

        # Çeldirici eserlerin yazarlarını çıkar (ESER_YAZAR ile)
        cel_owners = []
        for ce in celdiriciler[:3]:
            owner = ESER_YAZAR.get(ce, '?')
            cel_owners.append(f"«{ce}» → <strong>{owner}</strong>")
        cel_str = ' | '.join(cel_owners)

        tuzak = (
            (f"<strong>⚠ KLASİK ÖSYM TUZAĞI:</strong> {klasik_tuzak}<br><br>" if klasik_tuzak else "")
            + (f"<strong>🔍 Çeldirici eserlerin gerçek sahipleri:</strong> {cel_str}<br><br>" if cel_str else "")
            + f"<strong>✓ Ayrım anahtarı:</strong> {yazar}'ın repertuarında «{dogru_eser}» var; diğer şıklar aynı dönem ama farklı yazarlardan."
        )

        osym_stratejisi = (
            f"ÖSYM 'yazar → eser' sorusunda yazarın ESER REPERTUARINI test eder. "
            f"Strateji: (1) Yazarın {pozisyon.lower() if pozisyon else 'sanatçı'} olarak en ünlü eserini hatırla. "
            f"(2) Aynı dönem yazarlarının eserlerini birbirinden ayırt et. "
            f"(3) Yıl/akım eşleştirmesi → tarihsel sıra önemli."
        )

        dersini_ogren = f"{yazar} → «{dogru_eser}»"
        if diger_top:
            dersini_ogren += f" (ayrıca {', '.join(diger_top[:2])})."

        c = card(
            id_=id_,
            konu=konu,
            alt=yazar.lower().replace(' ', '_'),
            tip='yazar-eser',
            soru=f"<strong>{yazar}</strong>'a ait olan eser aşağıdakilerden hangisidir?",
            dogru_text=dogru_eser,
            celdiriciler=celdiriciler,
            aciklama=aciklama,
            tuzak=tuzak,
            mebi_sayfa=mebi if mebi != '—' else '',
            zorluk='orta',
            osym_stratejisi=osym_stratejisi,
            dersini_ogren=dersini_ogren,
        )
        cards.append(c)
    return cards


# =====================================================
# REV19 — Yazar odaklı YENİ soru tipleri (içerik→başka eser, çağdaş)
# Kullanıcının istediği: a) yazar→eser b) eser→yazar (mevcut)
#   c) içeriği ver, BAŞKA eserini sor  d) çağdaşının eseri/çağdaşı kim
# =====================================================

_WORK_CONTENT_CACHE = None
def get_work_content():
    """data/work_content.json — eser → {yazar, donem, icerik (ad geçmez)}."""
    global _WORK_CONTENT_CACHE
    if _WORK_CONTENT_CACHE is None:
        try:
            wp = BASE / 'data' / 'work_content.json'
            _WORK_CONTENT_CACHE = json.loads(wp.read_text(encoding='utf-8')) if wp.exists() else {}
        except Exception:
            _WORK_CONTENT_CACHE = {}
    return _WORK_CONTENT_CACHE


_GENERIC_ESER = {'Divan', 'Şiirleri', 'Şiirler', 'Şarkıları', 'Nefesler'}
def _first_specific_work(yazar):
    for e in YAZAR_ESERLERI.get(yazar, []):
        if e.split(' (')[0].strip() not in _GENERIC_ESER:
            return e
    return None


def _baska_eser_for(yazar, haric_eser):
    """Yazarın haric_eser dışındaki spesifik bir eseri (varsa)."""
    for e in YAZAR_ESERLERI.get(yazar, []):
        if e.split(' (')[0].strip() in _GENERIC_ESER:
            continue
        if e != haric_eser:
            return e
    return None


def gen_icerik_baska_eser_cards():
    """Tip c: İçerik verilir (yazar/eser adı YOK) → aynı yazarın BAŞKA eseri sorulur."""
    cards = []
    wc = get_work_content()
    for eser, info in wc.items():
        yazar = info['yazar']
        baska = _baska_eser_for(yazar, eser)
        if not baska:
            continue
        celd = celdirici_eser_ayni_yazar_donem(baska, 6, exclude_yazar=yazar)
        celd = [c for c in celd if c not in (eser, baska)][:4]
        if len(celd) < 3:
            continue
        konu = info['donem']
        mebi = MEBI_AUTHOR.get(yazar, '—')
        auth_m = get_author_meta(yazar)
        pozisyon = auth_m.get('pozisyon', '')
        diger = auth_m.get('diger_eserler', '')
        diger_top = ', '.join([e.strip() for e in diger.split(',')[:5]
                               if e.strip() and e.strip() not in (eser, baska)][:4])
        id_ = f"ibe_{len(cards):04d}"
        aciklama = (
            f"<strong>📖 İçeriği verilen eser:</strong> «{eser}» — {yazar}.<br>"
            f"<strong>✓ Doğru cevap:</strong> «{baska}» de aynı yazarın eseridir.<br><br>"
            + (f"<strong>📚 Yazarın diğer eserleri:</strong> {diger_top}" if diger_top else "")
        )
        tuzak = (
            "<strong>⚠ TUZAK:</strong> İçerikteki eserle KARIŞTIRMA — soru o eseri değil, "
            f"aynı yazarın BAŞKA eserini istiyor. Şıklardaki diğer eserler aynı dönemden ama farklı yazarlardan.<br><br>"
            f"<strong>✓ Ayrım anahtarı:</strong> Önce içerikten yazarı bul ({yazar}), sonra o yazarın repertuarındaki başka eseri seç."
        )
        osym_str = (
            "ÖSYM 'içerik → başka eser' kalıbında YAZAR REPERTUARINI dolaylı test eder: "
            "eserin temasından yazarı tanı, sonra o yazarın diğer eserini hatırla. "
            "İki katmanlı: tema→yazar→başka eser."
        )
        ders = f"İçerikteki eser {yazar}'a ait; aynı yazarın başka eseri «{baska}»."
        c = card(
            id_=id_, konu=konu, alt=yazar.lower().replace(' ', '_'),
            tip='icerik-baska-eser',
            soru=("Aşağıda <strong>içeriği</strong> verilen eserle <strong>aynı yazara ait BAŞKA</strong> "
                  f"bir eser hangisidir?<br><br><em>«{info['icerik']}»</em>"),
            dogru_text=baska, celdiriciler=celd, aciklama=aciklama, tuzak=tuzak,
            mebi_sayfa=mebi if mebi != '—' else '', zorluk='zor',
            osym_stratejisi=osym_str, dersini_ogren=ders,
        )
        cards.append(c)
    return cards


def gen_icerik_yazar_cards():
    """Tip c2: İçerik verilir (ad YOK) → eserin YAZARI sorulur."""
    cards = []
    wc = get_work_content()
    for eser, info in wc.items():
        yazar = info['yazar']
        celd = celdirici_yazar_ayni_donem(yazar, 5)
        celd = [c for c in celd if c != yazar][:4]
        if len(celd) < 3:
            continue
        konu = info['donem']
        mebi = MEBI_AUTHOR.get(yazar, '—')
        auth_m = get_author_meta(yazar)
        pozisyon = auth_m.get('pozisyon', '')
        klasik_tuzak = auth_m.get('klasik_tuzak', '')
        id_ = f"iy_{len(cards):04d}"
        aciklama = (
            f"<strong>📖 Eser:</strong> «{eser}»<br>"
            f"<strong>✍ Yazar:</strong> {yazar}"
            + (f" — {pozisyon}" if pozisyon else "") + "<br><br>"
            f"<strong>🎯 İçerikten yazara:</strong> Verilen tema/konu doğrudan {yazar}'ın imzasıdır."
        )
        tuzak = (
            (f"<strong>⚠ KLASİK ÖSYM TUZAĞI:</strong> {klasik_tuzak}<br><br>" if klasik_tuzak else "")
            + "<strong>✓ Ayrım anahtarı:</strong> İçerikteki anahtar motifleri (dönem + tema + kahraman) yakala; "
              "şıklardaki diğer adlar aynı dönemden çeldiricilerdir."
        )
        osym_str = (
            "ÖSYM 'içerik/paragraf → yazar' kalıbında eserin temasından yazarı tanımayı test eder. "
            "Strateji: dönem + tema + tip/kahraman üçlüsünü anahtar kabul et; ezbere değil bağlamdan çıkar."
        )
        ders = f"Bu içerik/tema = {yazar}'ın «{eser}» eseri."
        c = card(
            id_=id_, konu=konu, alt=yazar.lower().replace(' ', '_'),
            tip='icerik-yazar',
            soru=("Aşağıda <strong>içeriği</strong> verilen eser hangi yazara aittir?"
                  f"<br><br><em>«{info['icerik']}»</em>"),
            dogru_text=yazar, celdiriciler=celd, aciklama=aciklama, tuzak=tuzak,
            mebi_sayfa=mebi if mebi != '—' else '', zorluk='orta',
            osym_stratejisi=osym_str, dersini_ogren=ders,
        )
        cards.append(c)
    return cards


def gen_cagdas_eser_cards():
    """Tip d: 'X ile aynı dönemde (çağdaşı) yaşamış bir sanatçının eseri?'"""
    cards = []
    focus = sorted(set(info['yazar'] for info in get_work_content().values()))
    for yazar in focus:
        sd = YAZAR_DONEM.get(yazar)
        if not sd:
            continue
        cagdaslar = [y for y in get_donem_yazarlar(sd) if y != yazar and _first_specific_work(y)]
        if not cagdaslar:
            continue
        cagdas = shuffle_seed(cagdaslar, yazar + '-cagdas')[0]
        dogru = _first_specific_work(cagdas)
        # Çeldirici: BAŞKA dönemlerden eserler
        diger = []
        for y, eserler in YAZAR_ESERLERI.items():
            yd = YAZAR_DONEM.get(y)
            if yd and yd != sd:
                w = _first_specific_work(y)
                if w:
                    diger.append(w)
        celd = shuffle_seed(list(dict.fromkeys(diger)), dogru + '-celd')[:4]
        if len(celd) < 3:
            continue
        konu = DONEM_TOPIC.get(sd, 'cumhuriyet')
        id_ = f"cge_{len(cards):04d}"
        donem_lbl = TOPIC_LABEL.get(konu, sd)
        aciklama = (
            f"<strong>✓ Doğru cevap:</strong> «{dogru}» → {cagdas}, {yazar} ile aynı dönemde ({donem_lbl}).<br><br>"
            f"<strong>🎯 Dönem ağı:</strong> {yazar} = {donem_lbl}. Bu dönemin diğer sanatçılarını birlikte öğren."
        )
        tuzak = (
            "<strong>⚠ TUZAK:</strong> Şıklardaki diğer eserler BAŞKA dönemlerden — kulağa tanıdık gelse de "
            f"{yazar}'ın çağdaşı değiller.<br><br>"
            "<strong>✓ Ayrım anahtarı:</strong> Her eseri yazarının dönemine yerleştir; sadece aynı dönemdeki doğrudur."
        )
        osym_str = (
            "ÖSYM 'çağdaş/dönemdeş' kalıbında sanatçıları DÖNEME yerleştirmeyi test eder. "
            "Strateji: her şıkkı yazar→dönem olarak etiketle; sorulan yazarla aynı dönemi seç."
        )
        ders = f"{yazar} ile {cagdas} aynı dönemde ({donem_lbl}); «{dogru}» o döneme ait."
        c = card(
            id_=id_, konu=konu, alt=yazar.lower().replace(' ', '_'),
            tip='cagdas-eser',
            soru=(f"<strong>{yazar}</strong> ile aynı dönemde (çağdaşı) yaşamış bir sanatçının eseri "
                  "aşağıdakilerden hangisidir?"),
            dogru_text=dogru, celdiriciler=celd, aciklama=aciklama, tuzak=tuzak,
            mebi_sayfa='', zorluk='zor',
            osym_stratejisi=osym_str, dersini_ogren=ders,
        )
        cards.append(c)
    return cards


def gen_cagdas_yazar_cards():
    """Tip d2: 'Aşağıdakilerden hangisi X ile aynı dönemdedir (çağdaşı)?'"""
    cards = []
    focus = sorted(set(info['yazar'] for info in get_work_content().values()))
    for yazar in focus:
        sd = YAZAR_DONEM.get(yazar)
        if not sd:
            continue
        cagdaslar = [y for y in get_donem_yazarlar(sd) if y != yazar]
        if not cagdaslar:
            continue
        dogru = shuffle_seed(cagdaslar, yazar + '-cagdasy')[0]
        diger_donem = [y for y in YAZAR_DONEM if YAZAR_DONEM.get(y) != sd and y != yazar]
        celd = shuffle_seed(list(dict.fromkeys(diger_donem)), yazar + '-celdy')[:4]
        if len(celd) < 3:
            continue
        konu = DONEM_TOPIC.get(sd, 'cumhuriyet')
        id_ = f"cgy_{len(cards):04d}"
        donem_lbl = TOPIC_LABEL.get(konu, sd)
        aciklama = (
            f"<strong>✓ Doğru cevap:</strong> {dogru} → {yazar} ile aynı dönem ({donem_lbl}).<br><br>"
            f"<strong>🎯 Dönem ağı:</strong> {donem_lbl} sanatçılarını bir grup olarak ezberle."
        )
        tuzak = (
            "<strong>⚠ TUZAK:</strong> Diğer şıklar başka dönem sanatçıları — tanıdık adlar olabilir "
            "ama dönemleri farklı.<br><br>"
            "<strong>✓ Ayrım anahtarı:</strong> Her adı dönemine yaz; sorulan yazarla eşleşeni seç."
        )
        osym_str = (
            "ÖSYM 'dönemdeş yazar' kalıbında sanatçı-dönem eşleştirmesini test eder. "
            "Strateji: dönem listelerini (Tanzimat, SF, Milli, Cumhuriyet...) gruplar hâlinde ezberle."
        )
        ders = f"{yazar} ile {dogru} aynı dönemde ({donem_lbl})."
        c = card(
            id_=id_, konu=konu, alt=yazar.lower().replace(' ', '_'),
            tip='cagdas-yazar',
            soru=f"Aşağıdaki sanatçılardan hangisi <strong>{yazar}</strong> ile aynı dönemde (çağdaşı) yer alır?",
            dogru_text=dogru, celdiriciler=celd, aciklama=aciklama, tuzak=tuzak,
            mebi_sayfa='', zorluk='orta',
            osym_stratejisi=osym_str, dersini_ogren=ders,
        )
        cards.append(c)
    return cards


def gen_akim_temsilci_cards():
    cards = []
    # Çeldirici akımı belirle (her doğru akım için karşıt çeldirici)
    AKIM_KARSIT = {
        'Klasisizm': 'Romantizm', 'Romantizm': 'Klasisizm',
        'Realizm': 'Romantizm', 'Natüralizm': 'Realizm',
        'Parnasizm': 'Romantizm', 'Sembolizm': 'Parnasizm',
        'Fütürizm': 'Klasisizm', 'Dadaizm': 'Sürrealizm',
        'Sürrealizm': 'Dadaizm', 'Egzistansiyalizm': 'Klasisizm',
        'Ekspresyonizm': 'Realizm',
    }
    for akim, temsilciler in AKIM_TEMSILCI.items():
        if not temsilciler: continue
        dogru = temsilciler[0]
        celdiriciler = []
        for ak2, ts2 in AKIM_TEMSILCI.items():
            if ak2 != akim and ts2:
                celdiriciler.append(ts2[0])
        celdiriciler = shuffle_seed(celdiriciler, akim + '-c')[:4]
        id_ = f"at_{len(cards):04d}"

        ozellik = AKIM_OZELLIK.get(akim, '')
        diger_temsilciler = ', '.join(temsilciler[1:5]) if len(temsilciler) > 1 else ''
        karsit = AKIM_KARSIT.get(akim, '')
        karsit_ozellik = AKIM_OZELLIK.get(karsit, '')

        aciklama = (
            f"<strong>🎨 Akım:</strong> {akim}<br>"
            f"<strong>👑 Öncü temsilci:</strong> {dogru}<br><br>"
            f"<strong>📋 Akımın temel özellikleri:</strong> {ozellik}<br><br>"
            + (f"<strong>👥 Diğer temsilcileri:</strong> {diger_temsilciler}" if diger_temsilciler else "")
        )

        cel_anal = []
        for ce in celdiriciler[:3]:
            # Çeldirici hangi akımdan?
            for ak2, ts2 in AKIM_TEMSILCI.items():
                if ce in ts2 and ak2 != akim:
                    cel_anal.append(f"<strong>{ce}</strong> ({ak2})")
                    break
        cel_str = ' | '.join(cel_anal)

        tuzak = (
            (f"<strong>⚠ KLASİK ÖSYM TUZAĞI:</strong> {akim} {karsit} ile sıkça karıştırılır. "
             f"{akim} = {ozellik[:80]}...; {karsit} = {karsit_ozellik[:80]}...<br><br>"
             if karsit else "")
            + (f"<strong>🔍 Çeldirici temsilciler farklı akımlardan:</strong> {cel_str}<br><br>" if cel_str else "")
            + f"<strong>✓ Ayrım anahtarı:</strong> {akim}'in temel sloganı/felsefesi → {dogru}'in yapıtlarında somutlaşır."
        )

        osym_stratejisi = (
            f"ÖSYM 'akım → temsilci' sorusunda akımın FELSEFİ KÖKEN ve sloganlarını test eder. "
            f"Strateji: (1) Akımın temel ilkesini hatırla ({ozellik[:60]}). "
            f"(2) Karşıt akımla zıtlık ilişkisini ezberle. "
            f"(3) Öncü temsilci genelde manifestoyu yazan veya akımı başlatandır."
        )

        dersini_ogren = f"{akim} → {dogru} (önce). Karşıtı: {karsit}." if karsit else f"{akim} → {dogru}."

        c = card(
            id_=id_,
            konu='edebi_akimlar',
            alt=akim.lower(),
            tip='akim-temsilci',
            soru=f"<strong>{akim}</strong> akımının önde gelen temsilcisi aşağıdakilerden hangisidir?",
            dogru_text=dogru,
            celdiriciler=celdiriciler,
            aciklama=aciklama,
            tuzak=tuzak,
            mebi_sayfa='186-190',
            zorluk='orta',
            osym_stratejisi=osym_stratejisi,
            dersini_ogren=dersini_ogren,
        )
        cards.append(c)
    return cards


def gen_akim_tanim_cards():
    cards = []
    AKIM_KARSIT = {
        'Klasisizm': 'Romantizm', 'Romantizm': 'Klasisizm',
        'Realizm': 'Natüralizm', 'Natüralizm': 'Realizm',
        'Parnasizm': 'Sembolizm', 'Sembolizm': 'Parnasizm',
        'Fütürizm': 'Klasisizm', 'Dadaizm': 'Sürrealizm',
        'Sürrealizm': 'Dadaizm', 'Egzistansiyalizm': 'Klasisizm',
        'Ekspresyonizm': 'Realizm',
    }
    for akim, ozellik in AKIM_OZELLIK.items():
        celdiriciler = [a for a in AKIM_OZELLIK.keys() if a != akim]
        celdiriciler = shuffle_seed(celdiriciler, akim + '-tanim')[:4]
        id_ = f"akt_{len(cards):04d}"
        temsilciler = AKIM_TEMSILCI.get(akim, [])[:4]
        karsit = AKIM_KARSIT.get(akim, '')
        karsit_ozellik = AKIM_OZELLIK.get(karsit, '')
        anahtar = ozellik.split(',')[0] if ',' in ozellik else ozellik[:30]

        aciklama = (
            f"<strong>🎨 Akım:</strong> {akim}<br>"
            f"<strong>📋 Temel özellikler:</strong> {ozellik}<br><br>"
            + (f"<strong>👥 Temsilcileri:</strong> {', '.join(temsilciler)}<br><br>" if temsilciler else "")
            + f"<strong>🔑 Anahtar kelime:</strong> {anahtar}"
        )

        tuzak = (
            (f"<strong>⚠ KLASİK ÖSYM TUZAĞI:</strong> {akim} ve {karsit} sıkça karıştırılır. "
             f"{akim} = {ozellik[:80]}; {karsit} = {karsit_ozellik[:80]}.<br><br>"
             if karsit else "")
            + f"<strong>🔍 Şıklardaki yakın akımlar:</strong> Realizm-Natüralizm, Romantizm-Sembolizm, Klasisizm-Parnasizm grupları sıkça karıştırılır. Her birinin tek farklı bir özelliği var (örn. Natüralizm = bilimsel determinizm; Realizm = sade gözlem).<br><br>"
            + f"<strong>✓ Ayrım anahtarı:</strong> Akım sloganı/temel ilkesi → {ozellik[:60]} — bu cümleyi yakala."
        )

        osym_stratejisi = (
            f"ÖSYM 'özellik → akım' sorusunda akımın FELSEFİ SLOGANINI test eder. "
            f"Strateji: (1) Soruyu anlam-haritalı oku: hangi kavram (akıl/duygu/biçim/imge) öne çıkıyor. "
            f"(2) Yakın akımları zıt çiftler halinde ezberle (Klasisizm↔Romantizm, Realizm↔Natüralizm). "
            f"(3) Akımın 'reddediği' karşıtını sor — genelde önceki akımı reddeder."
        )

        dersini_ogren = f"{akim}: «{anahtar}»" + (f", karşıt {karsit}." if karsit else ".")

        c = card(
            id_=id_,
            konu='edebi_akimlar',
            alt=akim.lower(),
            tip='akim-tanim',
            soru=f"\"{ozellik}\" özellikleri aşağıdaki akımlardan hangisine aittir?",
            dogru_text=akim,
            celdiriciler=celdiriciler,
            aciklama=aciklama,
            tuzak=tuzak,
            mebi_sayfa='186-190',
            zorluk='orta',
            osym_stratejisi=osym_stratejisi,
            dersini_ogren=dersini_ogren,
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
        auth_m = get_author_meta(yazar)
        pozisyon = auth_m.get('pozisyon', '')
        anekdot = (auth_m.get('anekdot') or '')[:250]
        klasik_tuzak = auth_m.get('klasik_tuzak', '')
        diger = auth_m.get('diger_eserler', '')
        diger_top = ', '.join(e.strip() for e in diger.split(',')[:3] if e.strip())[:100]

        aciklama = (
            f"<strong>✍ Yazar:</strong> {yazar}"
            + (f" — {pozisyon}" if pozisyon else "") + "<br>"
            f"<strong>📅 Dönem:</strong> {dogru}<br><br>"
            + (f"<strong>🎯 Bağlam:</strong> {anekdot}...<br><br>" if anekdot else "")
            + (f"<strong>📚 Bilinen eserleri:</strong> {diger_top}" if diger_top else "")
        )

        tuzak = (
            (f"<strong>⚠ KLASİK ÖSYM TUZAĞI:</strong> {klasik_tuzak}<br><br>" if klasik_tuzak else "")
            + f"<strong>🔍 Dönem karışıklıkları:</strong> Sıkça karıştırılan dönemler: "
              "(1) Tanzimat II ↔ Servet-i Fünun (1896 sınırı), "
              "(2) Servet-i Fünun ↔ Fecr-i Âti ↔ Milli Edebiyat (1908-1911 geçişi), "
              "(3) Milli Edebiyat ↔ Cumhuriyet (1923 sınırı, yazar geçişi).<br><br>"
            + f"<strong>✓ Ayrım anahtarı:</strong> {yazar}'ın {dogru} olmasının nedeni — etkin olduğu yıl + dergi/grup üyeliği + tema."
        )

        osym_stratejisi = (
            f"ÖSYM 'yazar → dönem' sorusunda yazarın AKTİF YILI + DERGİ/GRUP üyeliğini test eder. "
            f"Strateji: (1) Yazarın doğum-ölüm yılları → ana dönem. "
            f"(2) Bağlı olduğu dergi (Servet-i Fünun, Genç Kalemler, Yedi Meşale, Garip vb.). "
            f"(3) İlk önemli eserin yayım yılı → dönem sınırı."
        )

        dersini_ogren = f"{yazar} → {dogru}" + (f" ({pozisyon})" if pozisyon else "") + "."

        c = card(
            id_=id_,
            konu=konu,
            alt=yazar.lower().replace(' ', '_'),
            tip='donem-yazar',
            soru=f"<strong>{yazar}</strong> aşağıdaki edebi dönemlerden hangisine aittir?",
            dogru_text=dogru,
            celdiriciler=celdiriciler,
            aciklama=aciklama,
            tuzak=tuzak,
            mebi_sayfa=MEBI_AUTHOR.get(yazar, '') if MEBI_AUTHOR.get(yazar, '—') != '—' else '',
            zorluk='kolay',
            osym_stratejisi=osym_stratejisi,
            dersini_ogren=dersini_ogren,
        )
        cards.append(c)
    return cards


def gen_nazim_bicim_cards():
    cards = []
    # Karıştırılan çift haritası
    NAZIM_KARSIT = {
        'Gazel': ('Kaside', 'İkisi de aa-ba-ca kafiye. GAZEL: 5-15 beyit, AŞK; KASİDE: 33-99 beyit, METHİYE/MERSİYE.'),
        'Kaside': ('Gazel', 'İkisi de aa-ba-ca kafiye. KASİDE: uzun, methiye; GAZEL: kısa, aşk.'),
        'Mesnevi': ('Kaside', 'MESNEVİ: her beyit kendi içinde kafiyeli (aa-bb-cc); KASİDE: tek kafiye (aa-ba-ca).'),
        'Rubai': ('Tuyuğ', 'İkisi de 4 mısra. RUBAİ: aruz vezniyle, FELSEFİ; TUYUĞ: aruz, TÜRK-İSLAM aforizma.'),
        'Tuyuğ': ('Rubai', 'TUYUĞ: Türklere özgü 4 mısra; RUBAİ: İran/Fars kökenli felsefi.'),
        'Koşma': ('Semai', 'KOŞMA: 11 heceli; SEMAİ: 8 heceli. İkisi de halk şiiri 4 dörtlük.'),
        'Mani': ('Türkü', 'MANİ: 7 heceli 4 mısra, aaxa; TÜRKÜ: değişken hece, ezgi öne çıkar.'),
    }
    for bicim, tanim in NAZIM_BICIMI.items():
        celdiriciler = [b for b in NAZIM_BICIMI.keys() if b != bicim]
        celdiriciler = shuffle_seed(celdiriciler, bicim)[:4]
        konu = 'divan_edebiyati' if bicim in ('Gazel','Kaside','Mesnevi','Rubai','Tuyuğ','Şarkı','Terkib-i Bend','Terci-i Bend') else 'halk_edebiyati'
        id_ = f"nb_{len(cards):04d}"
        karsit, karsit_aciklama = NAZIM_KARSIT.get(bicim, ('', ''))

        aciklama = (
            f"<strong>📝 Nazım biçimi:</strong> {bicim}<br>"
            f"<strong>📋 Tanım:</strong> {tanim}<br><br>"
            f"<strong>📚 Konum:</strong> {'Divan Edebiyatı klasik biçim' if konu == 'divan_edebiyati' else 'Halk şiiri geleneği'}."
        )

        tuzak = (
            (f"<strong>⚠ KLASİK ÖSYM TUZAĞI:</strong> {bicim} ↔ {karsit}: {karsit_aciklama}<br><br>" if karsit else "")
            + f"<strong>🔍 Çeldirici biçimlerin temel farkı:</strong> Her biçimin imzası: nazım birimi (beyit/dörtlük) + kafiye düzeni + konu sınıfı.<br><br>"
            + f"<strong>✓ Ayrım anahtarı:</strong> {bicim}'in benzersiz özelliği — kafiye düzeni + birim sayısı."
        )

        osym_stratejisi = (
            f"ÖSYM 'tanım → nazım biçimi' sorusunda KAFİYE DÜZENİ + NAZIM BİRİMİ + KONU üçlüsünü test eder. "
            f"Strateji: (1) Kafiye düzenini ezberle (aa-ba-ca = gazel/kaside; aa-bb-cc = mesnevi; abab = koşma). "
            f"(2) Birim sayısı: kaç beyit/dörtlük? "
            f"(3) Konu: aşk → gazel; methiye → kaside; uzun anlatı → mesnevi."
        )

        dersini_ogren = f"{bicim}: {tanim[:50]}..." + (f" Karıştırma: {karsit}." if karsit else "")

        c = card(
            id_=id_,
            konu=konu,
            alt=bicim.lower(),
            tip='nazim-bicim',
            soru=f"\"{tanim}\" özellikleri aşağıdaki nazım biçimlerinden hangisine aittir?",
            dogru_text=bicim,
            celdiriciler=celdiriciler,
            aciklama=aciklama,
            tuzak=tuzak,
            mebi_sayfa='47-52' if konu == 'divan_edebiyati' else '36-37',
            zorluk='orta',
            osym_stratejisi=osym_stratejisi,
            dersini_ogren=dersini_ogren,
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


def gen_soylenmez_cards():
    """ÖSYM'nin EN SIK kalıbı: 'Aşağıdakilerden hangisi söylenemez/değildir?'"""
    cards = []

    # Yazar negatif eleme (Fuzuli için söylenemez vb.)
    yazar_negatif = [
        ('Fuzuli', 'divan_edebiyati', '56-57',
         ['16. yüzyıl Divan şairidir', 'Bağdat çevresinde yaşamıştır', 'Türkçe, Arapça, Farsça divanı vardır', 'Leyla vü Mecnun mesnevisini yazmıştır'],
         'Mesnevi türünden ÖRNEK vermemiştir'),
        ('Şeyh Galip', 'divan_edebiyati', '58-59',
         ['18. yüzyılın son büyük Divan şairidir', 'Mevlevi tarikatına mensuptur', 'Hüsn ü Aşk adlı alegorik mesneviyi yazmıştır', 'Sebk-i Hindi üslubunu benimsemiştir'],
         'Lale Devri\'nde mahallileşme akımının kurucusudur'),  # Bu Nedim — söylenemez
        ('Halit Ziya Uşaklıgil', 'servet_i_funun_fecr_i_ati', '131',
         ['Servet-i Fünun romanının en güçlü ismidir', 'Mai ve Siyah, Aşk-ı Memnu, Kırık Hayatlar romanlarını yazmıştır', 'Türk romanını Batılı standarda taşımıştır', 'Realizm-natüralizm etkisindedir'],
         'Türk edebiyatında ilk psikolojik roman olan Eylül\'ün yazarıdır'),  # Eylül Mehmet Rauf
        ('Nazım Hikmet', 'cumhuriyet', '79, 82',
         ['Serbest nazımın Türk edebiyatındaki öncüsüdür', 'Toplumcu gerçekçi şiir akımının önemli ismidir', 'Memleketimden İnsan Manzaraları adlı uzun şiiri vardır', 'Kuvâyi Milliye Destanı\'nı yazmıştır'],
         'Garip akımının kurucularındandır'),  # Garip Orhan Veli
        ('Yahya Kemal Beyatlı', 'cumhuriyet', '77',
         ['Saf şiir geleneğinin önemli temsilcisidir', 'Aruz ölçüsünü Türkçeyle ustaca uyumlu kullanmıştır', 'Kendi Gök Kubbemiz adlı şiir kitabı vardır', 'Aziz İstanbul adlı nesir eseri vardır'],
         'Garip akımının üyelerindendir'),
        ('Sait Faik Abasıyanık', 'cumhuriyet', '115',
         ['Burgazada balıkçılarını, küçük insanları anlattı', 'Çehov tarzı durum hikayesinin Türk edebiyatındaki en güçlü temsilcisi sayılır', 'Semaver, Sarnıç, Lüzumsuz Adam adlı kitapları vardır', 'Hikayelerinde şiirsel bir dil kullanmıştır'],
         'Toplumcu gerçekçi roman akımının kurucusudur'),
        ('Yakup Kadri Karaosmanoğlu', 'milli_edebiyat', '134-135',
         ['Türk romanının dört kuşağını yazmıştır', 'Yaban, Kiralık Konak, Nur Baba, Hüküm Gecesi gibi eserleri vardır', 'Sosyo-tarihsel roman geleneğinin önemli temsilcisidir', 'Önce Fecr-i Âti\'ye sonra Milli Edebiyat\'a katılmıştır'],
         'İlk psikolojik roman olan Eylül\'ün yazarıdır'),
        ('Tevfik Fikret', 'servet_i_funun_fecr_i_ati', '66',
         ['Servet-i Fünun şiirinin en güçlü ismidir', 'Rübab-ı Şikeste ve Halûk\'un Defteri kitapları vardır', 'Sis ve Hân-ı Yağma şiirleri toplumsal eleştiri içerir', 'Şermin adlı çocuk şiirlerini heceyle yazmıştır'],
         'Mistik şiirin Türk edebiyatındaki en güçlü temsilcisidir'),  # Bu Necip Fazıl
        ('Namık Kemal', 'tanzimat', '62, 154',
         ['Tanzimat I. dönemin en önemli yazarlarındandır', 'İntibah (ilk edebi roman) ve Cezmi (ilk tarihi roman) kitaplarını yazmıştır', 'Vatan yahut Silistre tiyatrosu ünlüdür', 'Hürriyet kasidesini yazmıştır'],
         'Türk romanını Batılı standarda taşıyan ilk yazardır'),  # Halit Ziya
        ('Ömer Seyfettin', 'milli_edebiyat', '113',
         ['Türk hikayeciliğinin en önemli isimlerindendir', 'Genç Kalemler dergisinin kurucularındandır', 'Bomba, Pembe İncili Kaftan, Falaka, Kaşağı gibi hikayeleri vardır', 'Sade dil hareketinin pratik öncülerindendir'],
         'İlk romanı Çalıkuşu\'dur'),  # Çalıkuşu Reşat Nuri
    ]
    for yazar, konu, mebi, dogru_secenekler, yanlis in yazar_negatif:
        cel = dogru_secenekler[:4]  # 4 doğru özellik çeldirici olur
        id_ = f"sn_{len(cards):04d}"
        cards.append(card(id_, konu, yazar.lower().replace(' ', '_'), 'soylenemez-yazar',
            f"<strong>{yazar}</strong> ile ilgili aşağıdakilerden hangisi <strong>SÖYLENEMEZ</strong>?",
            yanlis, cel,
            f"<strong>{yazar}</strong> için söylenebilenler: " + '; '.join(dogru_secenekler[:3]) + ". Soruda istenen YANLIŞ ifade '" + yanlis + "' idi.",
            "Negatif eleme sorularında YANLIŞ bilgi DOĞRU CEVAP olur. Tüm şıkları kontrol et, biri kesin yanlış olmalı.",
            mebi, 'orta'))

    # Akım negatif eleme
    akim_negatif = [
        ('Realizm', 'edebi_akimlar', '188',
         ['Gözlem ve gerçeklik esastır', 'Sıradan insan ve günlük yaşam konu edilir', 'Balzac, Stendhal, Flaubert, Tolstoy temsilcileridir', 'Romantizme tepki olarak ortaya çıkmıştır'],
         'Şiirde objektif anlatımı amaçlayan ve antik konuları işleyen akımdır'),  # Parnasizm
        ('Sembolizm', 'edebi_akimlar', '190',
         ['Şiirde müzikalite ve sezgi esastır', 'Baudelaire, Verlaine, Rimbaud, Mallarmé temsilcileridir', 'Anlam kapalı, simgesel bir anlatım benimser', 'Ahmet Haşim Türk edebiyatında en güçlü temsilcisidir'],
         'Bilinçaltını ve rüyayı sanatın merkezine alır'),  # Sürrealizm
        ('Klasisizm', 'edebi_akimlar', '187',
         ['17. yüzyılda Fransa\'da doğmuştur', 'Akıl ve sağduyu esastır', 'Üç birlik kuralı (zaman-mekan-eylem) tiyatroda uygulanır', 'Molière, Racine, Corneille temsilcileridir'],
         'Halk hayatı ve doğa övgüsü merkezdedir'),  # Romantizm
        ('Romantizm', 'edebi_akimlar', '188',
         ['19. yüzyılın başlarında Fransa\'da doğdu', 'Klasisizme tepki olarak ortaya çıktı', 'Duygu, hayal ve doğa öne çıkar', 'Victor Hugo, Lamartine, Goethe temsilcileridir'],
         'Bilimsel determinizm ve çevre-genetik tutsağı insan tasviri yapılır'),  # Natüralizm
        ('Natüralizm', 'edebi_akimlar', '188',
         ['Realizmin aşırı halidir', 'Bilimsel determinizm benimser', 'İnsanın çevre ve genetik tutsağı olduğunu savunur', 'Émile Zola en güçlü temsilcisidir'],
         'Antik konuları işler ve biçim mükemmelliğini hedefler'),  # Parnasizm
        ('Sürrealizm', 'edebi_akimlar', '190',
         ['1924\'te André Breton manifestosuyla başladı', 'Bilinçaltı, rüya ve otomatik yazım önemlidir', 'Freud\'un psikanalizinden etkilenmiştir', 'Dadaizmin devamı niteliğindedir'],
         'Geçmişin reddi, hız ve makine övgüsü esastır'),  # Fütürizm
    ]
    for akim, konu, mebi, dogru_secenekler, yanlis in akim_negatif:
        cel = dogru_secenekler[:4]
        id_ = f"sn_{len(cards):04d}"
        cards.append(card(id_, konu, akim.lower(), 'soylenemez-akim',
            f"<strong>{akim}</strong> akımı ile ilgili aşağıdakilerden hangisi <strong>SÖYLENEMEZ</strong>?",
            yanlis, cel,
            f"<strong>{akim}</strong> akımının temel özellikleri: " + '; '.join(dogru_secenekler[:3]) + ". Yanlış ifade '" + yanlis + "' başka akıma aittir.",
            "Akım özellikleri sürekli karıştırılır. Hangi özellik hangi akıma ait olduğunu ezberlemek lazım.",
            mebi, 'zor'))

    # Eser negatif eleme
    eser_negatif = [
        ('Hüsn ü Aşk', 'divan_edebiyati', '58-59',
         ['Şeyh Galip tarafından yazılmıştır', 'Mesnevi nazım biçiminde kaleme alınmıştır', 'Alegorik tasavvufi bir eserdir', 'Son büyük Divan mesnevisi sayılır'],
         'Halk hikayesi geleneğinin önemli ürünlerindendir'),
        ('Çalıkuşu', 'milli_edebiyat', '135',
         ['Reşat Nuri Güntekin\'in en bilinen romanıdır', 'Anadolu öğretmeni Feride\'nin hikayesini anlatır', 'Milli Edebiyat döneminin önemli eseridir', 'Halk diline yakın sade Türkçeyle yazılmıştır'],
         'Toplumcu gerçekçi akımın ilk örneklerindendir'),
        ('Tutunamayanlar', 'cumhuriyet', '120, 142',
         ['Oğuz Atay\'ın romanıdır', 'Türk postmodernizminin başlangıcı sayılır', 'Anti-roman özellikleri taşır', 'İroni ve parçalanmış anlatım kullanır'],
         'Toplumcu gerçekçi akımın temel eserlerindendir'),
        ('Kutadgu Bilig', 'islamiyet_oncesi_gecis', '28-29',
         ['Yusuf Has Hacip tarafından 1069\'da yazılmıştır', 'Allegorik bir mesnevidir', 'Devlet yönetimi ve mutluluk üzerinedir', 'İlk büyük Türk-İslam mesnevisi sayılır'],
         'Halk şiiri geleneğinin temel eseridir'),
    ]
    for eser, konu, mebi, dogru_secenekler, yanlis in eser_negatif:
        cel = dogru_secenekler[:4]
        id_ = f"sn_{len(cards):04d}"
        cards.append(card(id_, konu, eser.lower().replace(' ', '_'), 'soylenemez-eser',
            f"<strong>«{eser}»</strong> adlı eser için aşağıdakilerden hangisi <strong>SÖYLENEMEZ</strong>?",
            yanlis, cel,
            f"<strong>{eser}</strong> için söylenebilecekler: " + '; '.join(dogru_secenekler[:3]) + ". '" + yanlis + "' yanlıştır.",
            "Eser hakkındaki yanlış iddia, başka bir akım/tür/yazara ait olabilir.",
            mebi, 'zor'))

    # Dönem/akım negatif
    donem_negatif = [
        ('Servet-i Fünun', 'servet_i_funun_fecr_i_ati', '65-69',
         ['1896-1901 yıllarını kapsar', 'Sanat sanat içindir anlayışı benimsenir', 'Aruz ölçüsü ve sembolizm-parnasizm etkisi vardır', 'Halit Ziya, Tevfik Fikret, Cenap Şahabettin önde gelen isimlerdir'],
         'Sade Türkçe ve milli tema öne çıkarılır'),
        ('Milli Edebiyat', 'milli_edebiyat', '70-74',
         ['1911-1923 dönemini kapsar', 'Sade Türkçe + hece vezni + milli tema üç ilkesidir', 'Genç Kalemler dergisi etrafında başlamıştır', 'Ömer Seyfettin, Ziya Gökalp, Ali Canip kurucudur'],
         'Sanat sanat içindir anlayışı ile aruz ölçüsü kullanılır'),  # SF
        ('Garip akımı', 'cumhuriyet', '79-80',
         ['1941\'de Orhan Veli, Oktay Rifat, Melih Cevdet kurmuştur', 'Şiire ait her şeyi reddeder (ölçü, kafiye, söz sanatı)', 'Gündelik konuşma dili kullanılır', 'Küçük insan ve günlük yaşam konu edilir'],
         'Kapalı imge ve müzikalite ile soyutlama esastır'),  # II. Yeni
    ]
    for donem, konu, mebi, dogru_secenekler, yanlis in donem_negatif:
        cel = dogru_secenekler[:4]
        id_ = f"sn_{len(cards):04d}"
        cards.append(card(id_, konu, donem.lower().replace(' ', '_').replace('-',''), 'soylenemez-donem',
            f"<strong>{donem}</strong> dönemi/akımı ile ilgili aşağıdakilerden hangisi <strong>SÖYLENEMEZ</strong>?",
            yanlis, cel,
            f"<strong>{donem}</strong> özellikleri: " + '; '.join(dogru_secenekler[:3]) + ".",
            "Dönem özellikleri yakın dönemlerle karıştırılır. Bilinen özelliğin yokluğu = farklı dönem.",
            mebi, 'orta'))

    return cards


def gen_paragraf_tani_cards():
    """ÖSYM klasiği: yazarın tarzı/dönemi/eseri uzun paragrafla → yazar bul"""
    cards = []

    # Format: (yazar_dogru, konu, mebi, paragraf, çeldirici_yazarlar)
    paragraf_yazar = [
        ('Yunus Emre', 'halk_edebiyati', '34, 42',
         "Anadolu Türkçesini edebi bir dile dönüştürdüğü kabul edilen şair, 13-14. yüzyılda yaşamış mistik tasavvuf şairidir. Sade dilde yazdığı ilahileri ve şiirleri Türk tasavvuf şiirinin en sevilen ürünleri arasındadır. \"Bir ben vardır bende benden içeri\" gibi dizeleriyle evrensel insan sevgisini ifade etmiştir. Risaletü'n-Nushiyye adlı mesnevisi vardır.",
         ['Mevlana', 'Pir Sultan Abdal', 'Kaygusuz Abdal', 'Hacı Bektaş Veli']),
        ('Fuzuli', 'divan_edebiyati', '57',
         "16. yüzyılda Bağdat çevresinde yaşamış, Divan şiirinin en güçlü AŞK şairi olarak kabul edilir. Türkçe, Arapça ve Farsça üç dilde divanı vardır. Leyla vü Mecnun adlı mesnevisi, Su Kasidesi adlı naatı ve Şikayetname adlı mensur mektubu ünlüdür. \"Aşk derdiyle hoşem el çek ilacımdan tabip\" beyiti onun derinliğini özetler.",
         ['Baki', 'Şeyh Galip', "Nef'i", 'Nedim']),
        ('Halit Ziya Uşaklıgil', 'servet_i_funun_fecr_i_ati', '131',
         "Servet-i Fünun romanının zirvesi olan yazar, Türk romanını Batılı tekniğe ulaştırmıştır. Mai ve Siyah'ta bir sanatçının dramını, Aşk-ı Memnu'da İstanbul üst sınıfının yasak aşkını işler. Romanlarında karakterlerin iç dünyasını ayrıntılı betimler. Anılarını Kırk Yıl adlı eserinde toplamıştır.",
         ['Mehmet Rauf', 'Tevfik Fikret', 'Hüseyin Cahit Yalçın', 'Yakup Kadri Karaosmanoğlu']),
        ('Yakup Kadri Karaosmanoğlu', 'milli_edebiyat', '134-135',
         "Türk romanının dört kuşak panoramasını veren yazar, önce Fecr-i Âti'ye sonra Milli Edebiyat'a katılmıştır. Yaban romanında aydının köy gerçekliğiyle yüzleşmesini, Kiralık Konak'ta üç kuşak çatışmasını, Nur Baba'da Bektaşilik eleştirisini, Sodom ve Gomore'de işgal İstanbul'unun ahlak çöküntüsünü işler.",
         ['Halide Edip Adıvar', 'Reşat Nuri Güntekin', 'Refik Halit Karay', 'Peyami Safa']),
        ('Sait Faik Abasıyanık', 'cumhuriyet', '115',
         "Burgazada balıkçılarının, küçük insanların, yalnızların hayatını anlatan hikayeci. Çehov tarzı DURUM hikayesinin Türk edebiyatındaki en güçlü temsilcisi sayılır. Semaver, Sarnıç, Lüzumsuz Adam, Son Kuşlar, Alemdağ'da Var Bir Yılan adlı kitapları vardır. Hikayelerinde olay yerine an ve izlenim öne çıkar; dili şiirseldir.",
         ['Memduh Şevket Esendal', 'Refik Halit Karay', 'Ömer Seyfettin', 'Tarık Buğra']),
        ('Oğuz Atay', 'cumhuriyet', '120, 142',
         "Türk romanında postmodernizmin başlangıcı sayılan yazar, anti-roman geleneğini Türk edebiyatına taşıdı. Tutunamayanlar adlı eserinde mühendis Turgut Özben'in intihar eden arkadaşı Selim'i araştırmasını ironi ve parçalanmış anlatımla anlatır. Tehlikeli Oyunlar adlı romanı ve Korkuyu Beklerken adlı hikaye kitabı vardır.",
         ['Yusuf Atılgan', 'Bilge Karasu', 'Orhan Pamuk', 'Ahmet Hamdi Tanpınar']),
        ('Necip Fazıl Kısakürek', 'cumhuriyet', '78',
         "Cumhuriyet dönemi şiirinde mistik ve metafizik çizginin en güçlü temsilcisi. Şiirlerini Çile adlı kitabında topladı. Kaldırımlar, Sakarya Türküsü gibi şiirleri ünlüdür. Bir Adam Yaratmak adlı tiyatro eseri vardır. Mistik yönelimi, doğu-batı çatışması ve manevi arayış temalarını işler.",
         ['Yahya Kemal Beyatlı', 'Ahmet Hamdi Tanpınar', 'Cahit Sıtkı Tarancı', 'Fazıl Hüsnü Dağlarca']),
        ('Tarık Buğra', 'cumhuriyet', '138',
         "Milli ve tarihsel temaları bireyin perspektifinden işleyen romancı. Küçük Ağa adlı romanında Milli Mücadele sürecinde bir İstanbul hocasının Anadolu'ya açılışını ve değişimini anlatır. Osmancık adlı romanında Osmanlı'nın kuruluşunu, Dönemeçte'de Türk modernleşmesini ele alır.",
         ['Kemal Tahir', 'Yakup Kadri Karaosmanoğlu', 'Mustafa Kutlu', 'Ahmet Hamdi Tanpınar']),
        ('Şeyh Galip', 'divan_edebiyati', '58-59',
         "18. yüzyılın son büyük Divan şairi. Mevlevi tarikatına mensuptu. En önemli eseri Hüsn ü Aşk adlı alegorik tasavvuf mesnevisi olup, Güzellik ile Aşk'ın yolculuğunu anlatır. Sebk-i Hindi (Hint üslubu) üslubunu benimsemiş, soyut imgeler ve dolambaçlı söyleyiş kullanmıştır. Mevlana'nın Mesnevî'sine şerh yazmıştır.",
         ['Nedim', 'Fuzuli', "Nef'i", 'Nabi']),
        ('Ömer Seyfettin', 'milli_edebiyat', '113',
         "Türk hikayeciliğinin babası sayılan yazar, sade Türkçe hareketinin pratik öncüsüdür. Genç Kalemler dergisinin kurucularındandır. Klasik OLAY hikayesi (Maupassant tarzı) tekniğini kullandı. Bomba, Pembe İncili Kaftan, Falaka, Kaşağı, Forsa, Diyet gibi tek tek mükemmel hikayeleri vardır. 1920'de erken yaşta öldü.",
         ['Sait Faik Abasıyanık', 'Refik Halit Karay', 'Memduh Şevket Esendal', 'Halide Edip Adıvar']),
        ('Mehmet Akif Ersoy', 'cumhuriyet', '74',
         "Türk milli marşının söz yazarı, İslamcı-toplumcu çizginin en güçlü şairi. Tüm şiirlerini Safahat adlı 7 kitaplık eserinde toplamıştır. Manzum hikaye tekniğini kullanmış; Süleymaniye Kürsüsünde, Asım, Hatıralar gibi bölümleri vardır. Çanakkale Şehitlerine adlı yapma destanı yazmıştır.",
         ['Yahya Kemal Beyatlı', 'Tevfik Fikret', 'Necip Fazıl Kısakürek', 'Ahmet Haşim']),
        ('Ahmet Hamdi Tanpınar', 'cumhuriyet', '78, 137-139',
         "Hem şair hem romancı hem denemeci olan çok yönlü yazar. Şiirde saf şiir geleneğini, romanda zaman-medeniyet temasını işler. Huzur ve Saatleri Ayarlama Enstitüsü romanlarıyla, Beş Şehir adlı denemesiyle ünlüdür. 19. Asır Türk Edebiyatı Tarihi adlı edebiyat tarihi kaynağı vardır. \"Bursa'da Zaman\" şiiri klasiktir.",
         ['Yahya Kemal Beyatlı', 'Oğuz Atay', 'Peyami Safa', 'Necip Fazıl Kısakürek']),
        ('Peyami Safa', 'cumhuriyet', '137-139',
         "Bireyin iç dünyasını ve özellikle DOĞU-BATI çatışmasını romanlarının merkezine alan yazar. 9. Hariciye Koğuşu adlı romanı bir hastane gözlemidir. Fatih Harbiye'de iki dünya arasında kalan bir kızı, Matmazel Noraliya'nın Koltuğu'nda psikolojik derinliği, Yalnızız'da varoluşsal sorunları işler.",
         ['Ahmet Hamdi Tanpınar', 'Tarık Buğra', 'Yakup Kadri Karaosmanoğlu', 'Mustafa Kutlu']),
        ('Şinasi', 'tanzimat', '61',
         "Tanzimat edebiyatının öncüsü. Türk edebiyatına BATILI yenilikleri ilk getiren isimdir: ilk özel Türk gazetesi (Tercüman-ı Ahvâl, Agah Efendi ile), ilk makale (Tercüman-ı Ahvâl Mukaddimesi), ilk sahnelenen tiyatro (Şair Evlenmesi). Müntehabat-ı Eş'ar adlı şiir derlemesi ve Durub-ı Emsal-i Osmaniye adlı atasözü derlemesi vardır.",
         ['Namık Kemal', 'Ziya Paşa', 'Ahmet Mithat Efendi', 'Recaizade Mahmut Ekrem']),
        ('Recaizade Mahmut Ekrem', 'tanzimat', '63-64, 128',
         "Tanzimat II. döneminin önde gelen ismi. Türk edebiyatında ilk REALİST roman olan Araba Sevdası'nı yazdı (yanlış batılılaşma eleştirisi). Talim-i Edebiyat adlı edebiyat eleştirisi kitabı vardır. Eski-yeni tartışmasında Muallim Naci'ye karşı yenilikçi tarafı temsil etti. Servet-i Fünuncuları yetiştirdi.",
         ['Abdülhak Hamit Tarhan', 'Şinasi', 'Namık Kemal', 'Muallim Naci']),
        ('Ahmet Haşim', 'servet_i_funun_fecr_i_ati', '68-69',
         "AKŞAM ŞAİRİ olarak bilinen, sembolizmin Türk edebiyatındaki en güçlü temsilcisi. Fecr-i Âti'nin de önde gelen ismi. Piyale ve Göl Saatleri adlı şiir kitapları, Bize Göre adlı deneme kitabı vardır. Merdiven, O Belde, Bir Günün Sonunda Arzu gibi şiirleri sembolist üslubun klasik örnekleridir. Şiir hakkındaki görüşlerini Mukaddime'de açıkladı.",
         ['Yahya Kemal Beyatlı', 'Cenap Şahabettin', 'Tevfik Fikret', 'Cahit Sıtkı Tarancı']),
        ('Sabahattin Ali', 'cumhuriyet', '114, 116',
         "Toplumcu gerçekçi roman ve hikayenin önemli isimlerinden. Kuyucaklı Yusuf adlı romanı bir Anadolu kasabasında otoriteye karşı bir bireyin hikayesidir. Kürk Mantolu Madonna'da Berlin-Ankara arasında iç dünya çatışması işlenir. İçimizdeki Şeytan adlı romanı vardır. Değirmen, Ses, Yeni Dünya adlı hikaye kitapları vardır.",
         ['Yaşar Kemal', 'Orhan Kemal', 'Kemal Tahir', 'Fakir Baykurt']),
        ('Yaşar Kemal', 'cumhuriyet', '140',
         "Çukurova merkezli toplumcu gerçekçi romancı. İnce Memed dört ciltlik destansı romanında Çukurova eşkıyalığını ve toprak ağalığını işler. Ortadirek, Yer Demir Gök Bakır, Demirciler Çarşısı Cinayeti gibi romanları vardır. Geniş betimleme + halk söyleyişi + destansı üslupla tanınır.",
         ['Sabahattin Ali', 'Orhan Kemal', 'Kemal Tahir', 'Fakir Baykurt']),
        ('Refik Halit Karay', 'milli_edebiyat', '136',
         "Önce Fecr-i Âti'de, sonra Milli Edebiyat'ta, sürgün sonrası Cumhuriyet'te yazmış üç dönemli yazar. Memleket Hikayeleri'nde Anadolu sürgününde gözlemlediği taşra hayatını, Gurbet Hikayeleri'nde yurt dışı sürgününü anlatır. Halk-Anadolu-sürgün temaları onun imzasıdır.",
         ['Yakup Kadri Karaosmanoğlu', 'Memduh Şevket Esendal', 'Reşat Nuri Güntekin', 'Halide Edip Adıvar']),
        ('Halide Edip Adıvar', 'milli_edebiyat', '135-136',
         "Milli Mücadele kadınının romandaki sesi. Sinekli Bakkal adlı romanı en bilinen eseridir. Ateşten Gömlek, Vurun Kahpeye gibi Kurtuluş Savaşı romanları vardır. Handan adlı psikolojik romanı, Mor Salkımlı Ev adlı anısı vardır. İngilizce eğitim almış, Anadolu'da öğretmenlik yapmıştır.",
         ['Yakup Kadri Karaosmanoğlu', 'Reşat Nuri Güntekin', 'Refik Halit Karay', 'Adalet Ağaoğlu']),
    ]
    for yazar, konu, mebi, paragraf, celdiriciler in paragraf_yazar:
        id_ = f"pt_{len(cards):04d}"
        cards.append(card(id_, konu, yazar.lower().replace(' ', '_'), 'paragraf-yazar-tani',
            paragraf + "<br><br><strong>Bu paragrafta tanıtılan yazar aşağıdakilerden hangisidir?</strong>",
            yazar, celdiriciler,
            f"Paragrafta verilen ipuçları (eser adları, tema, dönem) yazarın özelliklerini özetler: <strong>{yazar}</strong>.",
            "Paragraf-yazar tanı sorularında ESER ADLARI, DÖNEM, TEMA en güçlü ipucudur. Eserin adı geçiyorsa o yazardır.",
            mebi, 'orta'))
    return cards


def gen_dortluk_analiz_cards():
    """Gerçek beyit/dörtlük + söz sanatı/nazım biçimi/kafiye sorusu"""
    cards = []

    # Beyit + nazım biçimi/söz sanatı
    beyitler = [
        # (beyit/dörtlük, soru_tipi, dogru, celdiriciler, aciklama, konu, mebi)
        (
            "<em>Aşk derdiyle hoşem el çek ilacımdan tabip<br>Kılma derman kim helakim zehri dermanındadır</em><br><br>"
            "<strong>Yukarıdaki beyit hangi söz sanatına örnektir? (Aşıkın derdinden zevk alması ve ilacı reddetmesi)</strong>",
            'beyit-sanat', 'Tezat',
            ['Tenasüp', 'Hüsn-i talil', 'Telmih', 'Mübalağa'],
            "Beyitteki TEZAT: derdiyle hoşem (acı + mutluluk) + ilaç reddedişi (derman = ölüm). Fuzuli'ye ait.",
            'soz_sanatlari', '24'
        ),
        (
            "<em>\"Bir safa bahşedelim gel şu dil-i nâ-şâda<br>Gidelim serv-i revanım yürü Sa'dâbâd'a\"</em><br><br>"
            "<strong>Yukarıdaki beyit hangi Divan şairine aittir? (Lale Devri, mahallileşme, İstanbul)</strong>",
            'beyit-sair', 'Nedim',
            ['Nef\'i', 'Fuzuli', 'Baki', 'Şeyh Galip'],
            "Sa'dâbâd, Lale Devri, mahallileşme = NEDİM'in imzaları. \"Serv-i revan\" (yürüyen servi = sevgili) ifadesi.",
            'divan_edebiyati', '58-59'
        ),
        (
            "<em>\"Tahir Efendi bana kelp demiş<br>İltifatı bu sözde zahirdir<br>Maliki mezhebim benim zira<br>İtibarımca kelp tahirdir\"</em><br><br>"
            "<strong>Yukarıdaki şiir parçası hangi Divan şairine ait ve hangi nazım türündendir?</strong>",
            'sair-tur', "Nef'i — Hicviye",
            ['Fuzuli — Gazel', 'Baki — Mersiye', 'Nabi — Hikemi', 'Nedim — Şarkı'],
            "NEF'İ'nin meşhur hicvi. Tahir Efendi'nin \"kelp\" (köpek) demesine karşı kelime oyunuyla cevap (kelp tahirdir = köpek temizdir). Maliki mezhebine göndermeli.",
            'divan_edebiyati', '57-58'
        ),
        (
            "<em>\"Ağır ağır çıkacaksın bu merdivenlerden<br>Eteklerinde güneş rengi bir yığın yaprak<br>Ve bir zaman bakacaksın semaya ağlayarak\"</em><br><br>"
            "<strong>Yukarıdaki şiir hangi şaire aittir?</strong>",
            'siir-sair', 'Ahmet Haşim',
            ['Yahya Kemal Beyatlı', 'Cahit Sıtkı Tarancı', 'Necip Fazıl Kısakürek', 'Cenap Şahabettin'],
            "AHMET HAŞİM'in \"Merdiven\" şiirinin açılışı. Akşam + sembolizm + kapalılık imzaları onun.",
            'cumhuriyet', '68-69'
        ),
        (
            "<em>\"Otuz beş yaş, yolun yarısı eder<br>Dante gibi ortasındayız ömrün\"</em><br><br>"
            "<strong>Yukarıdaki şiir hangi şaire aittir? (Otuz Beş Yaş şiiri, ölüm korkusu)</strong>",
            'siir-sair', 'Cahit Sıtkı Tarancı',
            ['Necip Fazıl Kısakürek', 'Ahmet Hamdi Tanpınar', 'Yahya Kemal Beyatlı', 'Asaf Halet Çelebi'],
            "CAHİT SITKI TARANCI'nın \"Otuz Beş Yaş\" şiiri. Ölüm korkusu ve varoluşsal sorgu temalı.",
            'cumhuriyet', '77'
        ),
        (
            "<em>\"Anlatamıyorum derdimi anlatamıyorum<br>Bilmem ki nasıl anlatsam<br>Sizin diliniz başka benim dilim başka\"</em><br><br>"
            "<strong>Yukarıdaki şiir hangi akıma aittir? (serbest nazım, gündelik dil, doğrudan ifade)</strong>",
            'siir-akim', 'Garip (I. Yeni)',
            ['Saf şiir', 'İkinci Yeni', 'Toplumcu gerçekçi', 'Sembolizm'],
            "GARİP akımının tipik özellikleri: ölçü-kafiye yok, gündelik dil, doğrudan ifade. Orhan Veli üslubu.",
            'cumhuriyet', '79-80'
        ),
        (
            "<em>\"Bir ben vardır bende benden içeri\"</em><br><br>"
            "<strong>Yukarıdaki dize hangi şaire aittir? (Anadolu Türkçesi, mistik tasavvuf)</strong>",
            'dize-sair', 'Yunus Emre',
            ['Mevlana', 'Pir Sultan Abdal', 'Kaygusuz Abdal', 'Hacı Bektaş Veli'],
            "YUNUS EMRE'nin meşhur dizesi. Tasavvufi tema + Türkçe + içe dönük arayış.",
            'halk_edebiyati', '34, 42'
        ),
        (
            "<em>\"Şu dağlar olmasaydı<br>Çiçeği solmasaydı<br>Ölüm Allah'ın emri<br>Ayrılık olmasaydı\"</em><br><br>"
            "<strong>Yukarıdaki dörtlük hangi halk şiiri biçimine aittir?</strong>",
            'dortluk-bicim', 'Mani',
            ['Koşma', 'Semai', 'Varsağı', 'Ağıt'],
            "MANİ: 7 heceli, 4 mısra, aaxa kafiye, son 2 dize asıl mesaj. İlk 2 dize doldurma (dağlar/çiçek).",
            'halk_edebiyati', '31'
        ),
        (
            "<em>\"Ferman padişahın, dağlar bizimdir\"</em><br><br>"
            "<strong>Yukarıdaki dize hangi aşığa aittir?</strong>",
            'dize-asik', 'Dadaloğlu',
            ['Karacaoğlan', 'Köroğlu', 'Seyrani', 'Pir Sultan Abdal'],
            "DADALOĞLU'nun ünlü dizesi. AVŞAR Türkmen aşığı, Osmanlı'nın iskâna zorlamasına karşı direniş.",
            'halk_edebiyati', '36-37'
        ),
        (
            "<em>\"Vergisinden alacağı bile var<br>Sevdiğim ahırına bağlı tomar tomar<br>Senin tarlanda kullanılır onlar\"</em><br><br>"
            "<strong>Yukarıdaki şiirde işlenen konu, hangi koşma türüne işaret eder?</strong>",
            'kosma-tur', 'Taşlama',
            ['Güzelleme', 'Koçaklama', 'Ağıt', 'Methiye'],
            "TAŞLAMA: toplumsal eleştiri, yergi, hiciv. Vergi-toprak-iktidar eleştirisi taşlamanın klasiği.",
            'halk_edebiyati', '36-37'
        ),
        (
            "<em>\"Su ki kayalardan inerken çağıldar<br>Çağıldarken ürküntü saçar gönüllere\"</em><br><br>"
            "<strong>Yukarıdaki iki dizede hangi söz sanatı belirgindir? (Su kişileştirilmiş, korku yayıyor)</strong>",
            'beyit-sanat', 'Teşhis (Kişileştirme)',
            ['Mecaz-ı mürsel', 'Tezat', 'Hüsn-i talil', 'Telmih'],
            "Suya 'ürküntü saçar' (insan duygusu) atfedilmiş = TEŞHİS. Cansıza canlı/insan özelliği verme.",
            'soz_sanatlari', '24'
        ),
        (
            "<em>\"Şu Boğaz harbi nedir? Var mı ki dünyada eşi?<br>En kesif orduların yükleniyor dördü beşi\"</em><br><br>"
            "<strong>Yukarıdaki şiir hangi şaire ait ve hangi yapma destana aittir?</strong>",
            'sair-eser', 'Mehmet Akif Ersoy — Çanakkale Şehitlerine',
            ['Nazım Hikmet — Kuvâyi Milliye Destanı', 'Fazıl Hüsnü Dağlarca — Üç Şehitler Destanı', 'Mehmet Akif — Süleymaniye Kürsüsünde', 'Yahya Kemal — Süleymaniye\'de Bayram Sabahı'],
            "MEHMET AKİF'in \"Çanakkale Şehitlerine\" yapma destanı. Safahat'ın 6. kitabında yer alır.",
            'cumhuriyet', '74'
        ),
        (
            "<em>\"Bu dünyadan göçüp gitmek istemiyorum biliyorum\"</em><br><br>"
            "<strong>Yukarıdaki dize hangi şaire ve hangi şiire aittir? (varoluşsal kaygı, ölüm)</strong>",
            'dize-eser', 'Cahit Sıtkı Tarancı — Otuz Beş Yaş',
            ['Necip Fazıl — Sakarya Türküsü', 'Yahya Kemal — Kendi Gök Kubbemiz', 'Ahmet Haşim — Merdiven', 'Tanpınar — Bursa\'da Zaman'],
            "CAHİT SITKI TARANCI'nın \"Otuz Beş Yaş\" şiirinin sondan dizelerinden. Ölüm korkusunun en açık ifadesi.",
            'cumhuriyet', '77'
        ),
        (
            "<em>\"Sevda yıllar geçtikçe artıyor<br>Karda gül gibi kalbim sızıyor\"</em><br><br>"
            "<strong>Yukarıdaki beyit hangi nazım birimine örnektir?</strong>",
            'birim', 'Beyit',
            ['Mısra', 'Dörtlük', 'Bent', 'Müsavi mısra'],
            "BEYİT = 2 mısra (yani 2 dize) bir araya gelmiş yapı. Divan şiirinin temel birimi.",
            'siir_bilgisi', '14'
        ),
    ]
    for paragraf_soru, tip, dogru, celdiriciler, aciklama, konu, mebi in beyitler:
        id_ = f"da_{len(cards):04d}"
        cards.append(card(id_, konu, 'dortluk_analiz', tip,
            paragraf_soru,
            dogru, celdiriciler,
            aciklama,
            "Gerçek beyit/dörtlük sorularında: önce şairin imzasını ara (mahlas, üslup), sonra konu/teme bakarak yazara/akıma git.",
            mebi, 'zor'))
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
    # REV19 — yeni yazar-odaklı tipler (içerik→başka eser, içerik→yazar, çağdaş eser/yazar)
    all_cards += gen_icerik_baska_eser_cards()
    print(f"  icerik-baska-eser: {len([c for c in all_cards if c['tip']=='icerik-baska-eser'])}")
    all_cards += gen_icerik_yazar_cards()
    print(f"  icerik-yazar: {len([c for c in all_cards if c['tip']=='icerik-yazar'])}")
    all_cards += gen_cagdas_eser_cards()
    print(f"  cagdas-eser: {len([c for c in all_cards if c['tip']=='cagdas-eser'])}")
    all_cards += gen_cagdas_yazar_cards()
    print(f"  cagdas-yazar: {len([c for c in all_cards if c['tip']=='cagdas-yazar'])}")
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
    all_cards += gen_soylenmez_cards()
    print(f"  soylenemez: {len([c for c in all_cards if 'soylenemez' in c.get('tip','')])}")
    all_cards += gen_paragraf_tani_cards()
    print(f"  paragraf-tani: {len([c for c in all_cards if c.get('tip')=='paragraf-yazar-tani'])}")
    all_cards += gen_dortluk_analiz_cards()
    print(f"  dortluk-analiz: {len([c for c in all_cards if c.get('alt_konu')=='dortluk_analiz'])}")
    all_cards += gen_ilkler_cards()
    print(f"  ilkler: {len([c for c in all_cards if c['tip']=='ilkler-eser'])}")

    print(f"TOPLAM: {len(all_cards)} kart")

    # REV18b — Pedagojik default enrichment (osym_stratejisi + dersini_ogren tip bazlı)
    enriched_count = 0
    for c in all_cards:
        before_osym = c.get('osym_stratejisi', '')
        before_ders = c.get('dersini_ogren', '')
        enrich_kart_default(c)
        if c.get('osym_stratejisi') and not before_osym:
            enriched_count += 1
    print(f"  REV18b: {enriched_count} kart pedagojik default ile zenginleştirildi (tip-spesifik strateji)")

    # REV17 — Pattern skorlarını kartlara enjekte (konu bazlı)
    _pa_path = BASE / 'data' / 'pattern_analysis.json'
    if _pa_path.exists():
        try:
            _pa = json.loads(_pa_path.read_text(encoding='utf-8'))
            _pa_konu = {k['kod']: k for k in _pa.get('konular', [])}
            score_count = 0
            for c in all_cards:
                kp = _pa_konu.get(c.get('konu', ''), {})
                c['due_score_2026'] = kp.get('due_score', 0)
                c['priority_2026'] = kp.get('priority', 'İHMAL')
                if kp:
                    score_count += 1
            print(f"  REV17: {score_count}/{len(all_cards)} kart 2026 skorlandı")
        except Exception as e:
            print(f"⚠ Kart pattern skoru: {e}")

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

    # Alias dedupe: aynı kişi farklı isimle geçtiyse birleştir
    ALIAS = {
        'Cevat Şakir': 'Halikarnas Balıkçısı',
        'Faruk Nafiz': 'Faruk Nafiz Çamlıbel',
        'Halit Ziya': 'Halit Ziya Uşaklıgil',
        'Yakup Kadri': 'Yakup Kadri Karaosmanoğlu',
        'Halide Edip': 'Halide Edip Adıvar',
        'Reşat Nuri': 'Reşat Nuri Güntekin',
        'Refik Halit': 'Refik Halit Karay',
        'Memduh Şevket': 'Memduh Şevket Esendal',
        'Orhan Veli': 'Orhan Veli Kanık',
        'Melih Cevdet': 'Melih Cevdet Anday',
        'Yahya Kemal': 'Yahya Kemal Beyatlı',
        'Mehmet Akif': 'Mehmet Akif Ersoy',
        'Cahit Sıtkı': 'Cahit Sıtkı Tarancı',
        'Necip Fazıl': 'Necip Fazıl Kısakürek',
        'Sait Faik': 'Sait Faik Abasıyanık',
        'Ahmet Mithat': 'Ahmet Mithat Efendi',
        'Nâzım Hikmet': 'Nazım Hikmet',
        'Recaizade': 'Recaizade Mahmut Ekrem',
        'Sami Paşazade Sezai': 'Samipaşazade Sezai',
        'Fuzûlî': 'Fuzuli',
        'Bâkî': 'Baki',
        'Nâbî': 'Nabi',
        'Nâilî': 'Naili',
        'Hayâlî': 'Hayali Bey',
        'Mevlânâ': 'Mevlana',
        'Cenap Şehabettin': 'Cenap Şahabettin',
        'Abdülhak Hamit': 'Abdülhak Hamit Tarhan',
        'Şeyh Gâlip': 'Şeyh Galip',
        'Nef’i': "Nef'i",
        'Necati': 'Necati Bey',
        'Nikola Tesla': 'Tesla',
    }

    # Önce alias'ları birleştir
    merged = {}
    for name, info in author_freq.items():
        canonical = ALIAS.get(name, name)
        if canonical not in merged:
            merged[canonical] = {'count': 0, 'years': set(), 'occurrences': []}
        merged[canonical]['count'] += info['count']
        merged[canonical]['years'].update(info['years'])
        merged[canonical]['occurrences'].extend(info['occurrences'])

    # REV17 — M1.a all_authors_in_questions.json'dan eksik yazarları çek
    # (şıklarda geçen ama mentioned_authors'a girmemiş yazarlar — örn. Taşlıcalı Yahya)
    extra_path = BASE / 'data' / 'all_authors_in_questions.json'
    if extra_path.exists():
        try:
            extra = json.loads(extra_path.read_text(encoding='utf-8'))
            added_authors = 0
            added_occs = 0
            for name, info in extra.items():
                canonical = ALIAS.get(name, name)
                if canonical not in merged:
                    merged[canonical] = {'count': 0, 'years': set(), 'occurrences': []}
                    added_authors += 1
                existing_qnos = {(o.get('year'), o.get('qno')) for o in merged[canonical]['occurrences']}
                for occ in info.get('occurrences', []):
                    key = (occ['year'], occ['qno'])
                    if key not in existing_qnos:
                        merged[canonical]['occurrences'].append({
                            'year': occ['year'],
                            'qno': occ['qno'],
                            'topic': occ.get('topic', ''),
                        })
                        merged[canonical]['years'].add(occ['year'])
                        merged[canonical]['count'] += 1
                        existing_qnos.add(key)
                        added_occs += 1
            print(f"  REV17: +{added_authors} yeni yazar, +{added_occs} ek occurrence (şık yazarları)")
        except Exception as e:
            print(f"⚠ all_authors_in_questions.json okunamadı: {e}")

    # REV17 — pattern_analysis.json'dan yazar bazlı due_score yükle
    pattern_yazar_map = {}
    pattern_konu_map = {}
    pattern_path = BASE / 'data' / 'pattern_analysis.json'
    if pattern_path.exists():
        try:
            pa = json.loads(pattern_path.read_text(encoding='utf-8'))
            for y in pa.get('yazarlar', []):
                key = ALIAS.get(y['name'], y['name'])
                # En yüksek skoru tut (alias birden çok kayıt dönerse)
                if key not in pattern_yazar_map or y['due_score'] > pattern_yazar_map[key]['due_score']:
                    pattern_yazar_map[key] = y
            for k in pa.get('konular', []):
                pattern_konu_map[k['kod']] = k
            print(f"  REV17: pattern_analysis yüklendi ({len(pattern_yazar_map)} yazar, {len(pattern_konu_map)} konu)")
        except Exception as e:
            print(f"⚠ pattern_analysis okunamadı: {e}")

    # REV19e/f — pattern'daki (çıkmış + MEBİ-only + müfredat klasiği) tüm yazarları
    # profile dönüştür: çıkmışta yok ama veri olan yazarlar da sayfa + kart alsın.
    inj = 0
    for pname in pattern_yazar_map:
        canonical = ALIAS.get(pname, pname)
        if canonical in merged:
            continue
        if canonical not in YAZAR_DONEM:   # kart üretilebilir olmalı (dönem + eser)
            continue
        merged[canonical] = {'count': 0, 'years': set(), 'occurrences': []}
        inj += 1
    print(f"  REV19e/f: +{inj} yazar enjekte (MEBİ-only + müfredat klasikleri)")

    authors_list = []
    for name, info in merged.items():
        donem = YAZAR_DONEM.get(name, '')
        eserler = YAZAR_ESERLERI.get(name, [])
        konular = sorted({o['topic'] for o in info['occurrences'] if o.get('topic')})
        diger_eserler = ', '.join(eserler[:5]) if eserler else EXTRA_WORKS.get(name, '')
        if not diger_eserler:
            diger_eserler = ''
        # REV17 — Pattern lookup
        p = pattern_yazar_map.get(name, {})
        authors_list.append({
            'name': name,
            'soru_sayisi': info['count'],
            'yillar': sorted([y for y in info['years'] if y]),
            'konular': konular,
            # REV19e — dönem (YAZAR_DONEM'den; enjekte yazarların konular'ı boş olduğu için)
            'donem': DONEM_TOPIC.get(YAZAR_DONEM.get(name, ''), ''),
            'mebi_sayfa': MEBI_AUTHOR.get(name, ''),
            'diger_eserler': diger_eserler,
            'occurrences': info['occurrences'],
            # REV17 — 2026 öncelik bilgisi (matematiksel pattern engine'den)
            'due_score_2026': p.get('due_score', 0),
            'priority_2026': p.get('priority', 'İHMAL'),
            'son_yil': p.get('last_year'),
            'current_gap': p.get('current_gap'),
            'rationale_2026': p.get('rationale', ''),
            # REV19 — MEBİ deneme sinyali + 2026 anma yılı
            'mebi_deneme_count': p.get('mebi_deneme_count', 0),
            'anma_yili_2026': p.get('anma_yili_2026', False),
            'anma_yili_dalga': p.get('anma_yili_dalga', False),
        })
    authors_list.sort(key=lambda a: (-a['soru_sayisi'], a['name']))
    with open(SITE / 'authors.json', 'w', encoding='utf-8') as f:
        json.dump(authors_list, f, ensure_ascii=False, indent=1)
    print(f"  → authors.json ({len(authors_list)} yazar, dedupe sonrası)")

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
        'periyodik_desen': [
            {'konu': 'Halk Edebiyatı', 'periyot': '2-3 yıl boş, sonra 2 yıl üst üste', 'son_geldigi': '2024 (2 soru)', 'tahmin': '2026 — YÜKSEK (boşluk telafisi)'},
            {'konu': 'İslamiyet Öncesi/Geçiş', 'periyot': '2018-2019 yok, 2020+ üst üste', 'son_geldigi': '2025 (1 soru)', 'tahmin': '2026 — YÜKSEK (artan trend, 6 yıl üst üste)'},
            {'konu': 'Milli Edebiyat', 'periyot': '2-yılda-bir aralıklı', 'son_geldigi': '2025 (1 soru)', 'tahmin': '2026 — DÜŞÜK (geldikten sonra düşer)'},
            {'konu': 'Geleneksel Tiyatro', 'periyot': '2-yılda-bir', 'son_geldigi': '2025 (1 soru)', 'tahmin': '2026 — DÜŞÜK (geçen yıl geldi)'},
            {'konu': 'Masal/Fabl/Destan', 'periyot': '~yıl aşırı', 'son_geldigi': '2024 (1 soru), 2025 (1 soru)', 'tahmin': '2026 — ORTA'},
            {'konu': 'Servet-i Fünun', 'periyot': '2021 hariç her yıl', 'son_geldigi': '2023, 2024 (2şer soru)', 'tahmin': '2026 — YÜKSEK (1-2 garanti)'},
        ],
        'yazar_son_yil_haritasi': [
            {'yazar': 'Halit Ziya Uşaklıgil', 'son_geldigi': '2023', 'bos_yil': 2, 'oncelik': 'ÇOK YÜKSEK'},
            {'yazar': 'Şinasi', 'son_geldigi': '2023', 'bos_yil': 2, 'oncelik': 'YÜKSEK'},
            {'yazar': 'Tarık Buğra', 'son_geldigi': '2025', 'bos_yil': 0, 'oncelik': 'DÜŞÜK (geldi)'},
            {'yazar': 'Sait Faik Abasıyanık', 'son_geldigi': '2023', 'bos_yil': 2, 'oncelik': 'ÇOK YÜKSEK'},
            {'yazar': 'Necip Fazıl Kısakürek', 'son_geldigi': '—', 'bos_yil': 8, 'oncelik': 'ÇOK YÜKSEK (hiç çıkmadı)'},
            {'yazar': 'Yahya Kemal Beyatlı', 'son_geldigi': '2024', 'bos_yil': 1, 'oncelik': 'ORTA'},
            {'yazar': 'Peyami Safa', 'son_geldigi': '—', 'bos_yil': 8, 'oncelik': 'ÇOK YÜKSEK'},
            {'yazar': 'Ömer Seyfettin', 'son_geldigi': '2020', 'bos_yil': 5, 'oncelik': 'ÇOK YÜKSEK'},
            {'yazar': 'Baki', 'son_geldigi': '2022', 'bos_yil': 3, 'oncelik': 'YÜKSEK'},
            {'yazar': 'Nedim', 'son_geldigi': '2024', 'bos_yil': 1, 'oncelik': 'ORTA'},
            {'yazar': 'Fuzuli', 'son_geldigi': '2025', 'bos_yil': 0, 'oncelik': 'DÜŞÜK (geldi)'},
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
    # REV17 — pattern_analysis.json'dan otomatik Top 20 + konu skorlarını enjekte
    pa_path = BASE / 'data' / 'pattern_analysis.json'
    if pa_path.exists():
        try:
            pa = json.loads(pa_path.read_text(encoding='utf-8'))
            # Pattern engine output'u site'a da kopyala (/sistem sayfası fetch eder)
            (SITE / 'pattern_analysis.json').write_text(
                json.dumps(pa, ensure_ascii=False, indent=1),
                encoding='utf-8'
            )
            # Top 20 yazar (due_score azalan, alias dedupe)
            seen_yazar = set()
            top20 = []
            for y in pa.get('yazarlar', []):
                canonical = ALIAS.get(y['name'], y['name'])
                if canonical in seen_yazar:
                    continue
                seen_yazar.add(canonical)
                top20.append({
                    'ad': canonical,
                    'due_score': y['due_score'],
                    'priority': y['priority'],
                    'freq': y['freq_8yil'],
                    'son_yil': y.get('last_year'),
                    'current_gap': y.get('current_gap'),
                    'rationale': y.get('rationale', ''),
                })
                if len(top20) >= 20:
                    break
            predictions['top_20_yazar_2026'] = top20
            # Konu skorları (skor azalan)
            predictions['pattern_konu_skorlari'] = [
                {
                    'kod': k['kod'],
                    'ad': TOPIC_LABEL.get(k['kod'], k['kod']),
                    'due_score': k['due_score'],
                    'priority': k['priority'],
                    'freq': k.get('freq_8yil', 0),
                    'raw_count': k.get('raw_count', 0),
                    'last_year': k.get('last_year'),
                    'current_gap': k.get('current_gap'),
                    'rationale': k.get('rationale', ''),
                }
                for k in sorted(pa.get('konular', []), key=lambda x: -x['due_score'])
            ]
            print(f"  REV17: Top 20 yazar + {len(predictions['pattern_konu_skorlari'])} konu skoru enjekte")
        except Exception as e:
            print(f"⚠ predictions pattern enjekte: {e}")

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
    # Dönem etiket helper'ı (sözlükte kullanılacak)
    def donem_label(d):
        return {
            'divan': 'Divan', 'halk': 'Halk',
            'tanzimat': 'Tanzimat', 'sf_fecr': 'SF/Fecr-i Âti',
            'milli': 'Milli Ed.', 'cumhuriyet': 'Cumhuriyet', 'gecis': 'Geçiş'
        }.get(d, '—')

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
            {
                'baslik': 'Alfabetik Yazar-Eser Envanteri (~70 yazar)',
                'basliklar': ['Yazar', 'Dönem', 'Öne Çıkan Eserleri'],
                'satirlar': sorted([
                    [y, donem_label(YAZAR_DONEM.get(y, '')), ', '.join(YAZAR_ESERLERI[y][:4])]
                    for y in YAZAR_ESERLERI.keys() if YAZAR_ESERLERI[y]
                ], key=lambda r: r[0].lower()),
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
