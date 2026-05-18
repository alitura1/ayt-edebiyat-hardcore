"""
REV5 — authors.json'a 5 yeni field (donem, pozisyon, anekdot, klasik_tuzak, rakipleri) ekler.
"Futbolcu kartı" tonu: kuru biyografi YOK, akılda kalan/somut/anekdotal detay + sınava bridge.
"""
import json, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = Path(__file__).parent.parent
AUTHORS_PATH = BASE / 'public' / 'data' / 'authors.json'

# Yazar adı -> 5 field enrichment
# anekdot: 1-3 cümle, somut/anekdotal/akılda kalan + bir sınava bridge cümlesi
# klasik_tuzak: ÖSYM'nin bu yazarda kurduğu spesifik karışıklık (yazar↔yazar veya eser↔eser)
# rakipleri: sık karıştırılan yazarların orijinal authors.name'leri (slugify runtime'da yapılır)
ENRICHMENT = {
    "Ahmet Haşim": {
        "donem": "servet_i_funun_fecr_i_ati",
        "pozisyon": "Şair",
        "anekdot": "Saf şiirin Türkçedeki manifestosu Piyale'yi yazan adam. 'Şiir nesre çevrilemeyen nazımdır' diye Fecr-i Âti'nin sanat ilkesini cebine koydu. Akşam'ı 'O Belde'yi 'Merdiven'i okuyanlar imgenin ne olduğunu öğrenir — ezberlemeden tanırsın.",
        "klasik_tuzak": "Cenap Şahabettin ile karıştırma. İkisi de saf şiir + sembolizm yakını. Ama Haşim FECR-İ ÂTİ + sonrası bağımsız; Cenap saf SERVET-İ FÜNUN. 'Piyale, Göl Saatleri' Haşim; 'Elhân-ı Şitâ' Cenap.",
        "rakipleri": ["Cenap Şahabettin", "Yahya Kemal Beyatlı", "Tevfik Fikret"]
    },
    "Fuzuli": {
        "donem": "divan_edebiyati",
        "pozisyon": "Şair",
        "anekdot": "Türk şiirinin acı sultanı. 'Aşk derdiyle hoşem' diyen, sevdiğine kavuşamayan Leyla vü Mecnun'un en güzel Türkçe versiyonunu yazan 16. yy şairi. Su Kasidesi'ni okumadan tasavvufu anlayamazsın — Hz. Muhammed'e methiye + sevgi + acı bir bütün.",
        "klasik_tuzak": "Baki ile karıştırma. İkisi de 16. yy + gazel ustası. Ama Fuzuli ACILI/tasavvufi/içsel; Baki ZARİF/dünyevi/saray şairi. 'Aşk derdi' Fuzuli; 'Kanunî Mersiyesi' Baki.",
        "rakipleri": ["Baki", "Şeyh Galip", "Nedim"]
    },
    "Namık Kemal": {
        "donem": "tanzimat",
        "pozisyon": "Çok yönlü",
        "anekdot": "Tanzimat'ın isyan eden adamı. 'Vatan yahut Silistre' oyunu sahnelenince halk sokağa döküldü, sürgün edildi. İlk edebi roman İntibah, ilk tarihi roman Cezmi. Şinasi'nin başlattığı Batılılaşmaya 'hürriyet ve vatan' temasını ekleyen kişi.",
        "klasik_tuzak": "Şinasi ile karıştırma. Şinasi İLK'lerin BABASI (ilk şiir çevirisi, ilk tiyatro, ilk gazete), Namık Kemal SİYASAL/HEYECANLI içeriği getiren. 'Vatan' Namık Kemal'in markası.",
        "rakipleri": ["Şinasi", "Ziya Paşa", "Ahmet Mithat Efendi"]
    },
    "Recaizade Mahmut Ekrem": {
        "donem": "tanzimat",
        "pozisyon": "Çok yönlü",
        "anekdot": "Tanzimat II. dönem'in 'üstad'ı. Muallim Naci ile 'eski-yeni' kavgasının yeni cephesini temsil etti. Araba Sevdası ilk realist Türk romanlarından — alafranga züppe Bihruz Bey'in trajikomik aşkı. 'Zemzeme' kitabıyla yeni şiir anlayışını ilan etti.",
        "klasik_tuzak": "Muallim Naci ile karıştırma — ikisi tam zıt kutuplar: Recaizade YENİ/Batı/realist, Muallim Naci ESKİ/Doğu/divan tarzı. 'Zemzeme' Recaizade; 'Demdeme' Muallim Naci'nin cevabı.",
        "rakipleri": ["Muallim Naci", "Abdülhak Hamit Tarhan", "Samipaşazade Sezai"]
    },
    "Refik Halit Karay": {
        "donem": "milli_edebiyat",
        "pozisyon": "Hikayeci",
        "anekdot": "Anadolu insanını GERÇEK haliyle hikayeleyen ilk yazar. 'Memleket Hikayeleri' ve sürgündeyken yazdığı 'Gurbet Hikayeleri' Türk hikayeciliğinin iki ayağı. Sürgünlerden dolayı 'memleket' kelimesi onun için ayrı bir tat.",
        "klasik_tuzak": "Ömer Seyfettin ile karıştırma — ikisi de Milli Edebiyat hikayeciliği zirvesi. Ömer Seyfettin DİL SADELEŞMESİ + tarih/mizah, Refik Halit MEMLEKET GERÇEKÇİLİĞİ + sürgün. 'Falaka' Ömer Seyfettin; 'Memleket Hikayeleri' Refik Halit.",
        "rakipleri": ["Ömer Seyfettin", "Reşat Nuri Güntekin", "Yakup Kadri Karaosmanoğlu"]
    },
    "Ahmet Mithat Efendi": {
        "donem": "tanzimat",
        "pozisyon": "Çok yönlü",
        "anekdot": "Tanzimat'ın 'yazı makinesi'. 200'den fazla eser yazdı, kendi matbaası vardı, halkı OKUR yapmayı dert edindi. 'Felatun Bey ile Rakım Efendi' Doğu-Batı çatışmasının ilk tipik temsili. Edebiyat değil, halk için yazdı — bu yüzden 'halk yazarı' lakabı.",
        "klasik_tuzak": "Şemsettin Sami ile karıştırma. İkisi de Tanzimat I. dönem popüler nesir. Ama Ahmet Mithat ROMAN + halk eğitimi, Şemsettin Sami SÖZLÜK (Kamus-ı Türki) + ansiklopedi (Kamusu'l-Alam). 'Taaşşuk-ı Talat ve Fitnat' Şemsettin Sami'nin ilk romanı.",
        "rakipleri": ["Şemsettin Sami", "Namık Kemal", "Şinasi"]
    },
    "Nabi": {
        "donem": "divan_edebiyati",
        "pozisyon": "Şair",
        "anekdot": "17. yy hikemî (didaktik) şiirin lideri. 'Hayriyye' adlı eserini oğluna nasihat olarak yazdı — divan şiirinde dünyevi öğüt çok rastlanmaz. Onun şiirinde aşk yerine 'akıl, ahlak, hayat dersi' var. Sebk-i hindi akımının Türkçedeki büyük ismi.",
        "klasik_tuzak": "Sebk-i hindi denince Nef'i veya Şeyh Galip akla gelir, ama hikemî tarz NABİ'nin işi. Nef'i HİCİV, Şeyh Galip ALİSEL TASAVVUF, Nabi NASİHAT/DÜŞÜNCE.",
        "rakipleri": ["Nef'i", "Şeyh Galip", "Naili"]
    },
    "Necati Bey": {
        "donem": "divan_edebiyati",
        "pozisyon": "Şair",
        "anekdot": "15. yy'ın 'Türki-i Basit' (sade Türkçe) öncüsü. Atasözleri ve halk deyimlerini divan şiirinin estetiğine çevirdi — bu çok cesur bir hareketti. 'Necati' lakaplı şair çoktur, ama 'Necati Bey' denince DİVAN'da bu adam akla gelmeli.",
        "klasik_tuzak": "Necati Cumalı (Cumhuriyet dönemi şair/oyun) ile karıştırma. Necati BEY 15. yy DİVAN; Necati CUMALI 20. yy CUMHURİYET. Aynı isim, 500 yıl arası.",
        "rakipleri": ["Necati Cumalı", "Şeyhi", "Ahmedi"]
    },
    "Abdülhak Hamit Tarhan": {
        "donem": "tanzimat",
        "pozisyon": "Çok yönlü",
        "anekdot": "Türk şiirinin BATI'ya AÇILAN kapısı, 'Şair-i Azam'. Karısı Fatma Hanım ölünce yazdığı 'Makber' Türk şiirinde ilk büyük romantik feryat. Eserlerinin çoğu okunamayacak kadar uzun ya da sahnelenemez (Eşber, Tezer, Sardanapal) ama EDEBİYAT TARİHİ için anıttır.",
        "klasik_tuzak": "Tanzimat II. dönem'de iki büyük şair var: Hamit ve Recaizade. Hamit ROMANTİZM + ÖLÜM/AŞK, Recaizade ELEŞTİRİ + 'üstad'lık. 'Makber' Hamit, 'Pejmürde' Recaizade.",
        "rakipleri": ["Recaizade Mahmut Ekrem", "Tevfik Fikret", "Muallim Naci"]
    },
    "Şeyhi": {
        "donem": "divan_edebiyati",
        "pozisyon": "Şair",
        "anekdot": "15. yy'ın Hüsrev ü Şirin ve Harname'siyle nam yapmış şairi. Harname'de bir eşeğin başına gelenleri mizahi alegori ile anlatır — divan şiirinde MİZAH bulmak nadirdir, Şeyhi bu yüzden hatırlanır. Hekim aynı zamandaydı.",
        "klasik_tuzak": "Şeyh GALİP (18. yy, Hüsn ü Aşk) ile karıştırma. İsim benzer ama Şeyhi 15. yy + alegorik mizah, Şeyh Galip 18. yy + tasavvufi sembolizm. Harname Şeyhi, Hüsn ü Aşk Şeyh Galip.",
        "rakipleri": ["Şeyh Galip", "Ahmedi", "Necati Bey"]
    },
    "Cenap Şahabettin": {
        "donem": "servet_i_funun_fecr_i_ati",
        "pozisyon": "Şair",
        "anekdot": "Servet-i Fünun'un en lirik şairi. 'Elhân-ı Şitâ' (Kış İlahileri) onun marka şiiridir — kar'ı şiirde böyle anlatan başka biri yok. Tıp doktoruydu, şiirini bir bilim adamının hassasiyetiyle örerdi. Sembolizmin Türkçedeki ilk büyük örnekleri.",
        "klasik_tuzak": "Ahmet Haşim ile karıştırma. İkisi de saf şiir yakını. Cenap SERVET-İ FÜNUN dönemi (Tevfik Fikret arkadaşı), Haşim sonraki FECR-İ ÂTİ. 'Elhân-ı Şitâ' Cenap; 'O Belde' Haşim.",
        "rakipleri": ["Ahmet Haşim", "Tevfik Fikret", "Süleyman Nazif"]
    },
    "Faruk Nafiz Çamlıbel": {
        "donem": "cumhuriyet",
        "pozisyon": "Şair",
        "anekdot": "Beş Hececiler'in en ünlüsü. 'Han Duvarları' Anadolu'yu bir şiirde özetleyen anıt eser. 'Sanat' şiirinde 'Yeniden vatan duygusunu uyandıralım' der — memleket edebiyatının manifestosu. Heceyi serbest şiire alternatif olarak savundu.",
        "klasik_tuzak": "Beş Hececiler beşlisi sıkça karıştırılır: Faruk Nafiz, Yusuf Ziya Ortaç, Orhan Seyfi Orhon, Enis Behiç Koryürek, Halit Fahri Ozansoy. 'Han Duvarları' = Faruk Nafiz; diğer adlar başka şiirler için.",
        "rakipleri": ["Yusuf Ziya Ortaç", "Orhan Seyfi Orhon", "Ahmet Kutsi Tecer"]
    },
    "Memduh Şevket Esendal": {
        "donem": "cumhuriyet",
        "pozisyon": "Hikayeci",
        "anekdot": "Türk hikayesine 'olay değil durum' anlayışını sokan adam. Çehov tarzı — büyük olay yoktur, küçük insan/küçük an vardır. 'Ayaşlı ile Kiracıları' romanı pansiyon hayatından kesitlerle Cumhuriyet'in ilk dönem İstanbul'unu çizer. Diplomat ve siyasetçi kimliği de var.",
        "klasik_tuzak": "Sait Faik ile karıştırma — ikisi de 'durum hikayesi' (Çehov tarzı) ustası. Memduh Şevket büyük ölçekte BÜROKRAT/MEMUR hayatı, Sait Faik İSTANBUL/AYDOĞDU/balıkçı evreni.",
        "rakipleri": ["Sabahattin Ali", "Orhan Kemal", "Refik Halit Karay"]
    },
    "Orhan Veli Kanık": {
        "donem": "cumhuriyet",
        "pozisyon": "Şair",
        "anekdot": "Garip akımının kurucusu — şiirden vezin, kafiye, mecaz, yüksek üslup ATILDI. 'Anlatamıyorum' ve 'Bedava' gibi şiirleri gündelik dilin şiirleşmesi. 36 yaşında öldü ama Türk şiirini ikiye böldü: ondan önce/sonra.",
        "klasik_tuzak": "Garip ÜÇLÜSÜ: Orhan Veli + Oktay Rifat + Melih Cevdet Anday. Orhan Veli lider. 'İstanbul'u Dinliyorum' Orhan Veli; 'Karga ile Tilki' Melih Cevdet'in çevirileri.",
        "rakipleri": ["Melih Cevdet Anday", "Cahit Külebi", "Ece Ayhan"]
    },
    "Sabahattin Ali": {
        "donem": "cumhuriyet",
        "pozisyon": "Romancı",
        "anekdot": "Türk edebiyatının HAYALET roman olan 'Kürk Mantolu Madonna'sını yazan adam. 1948'de Bulgar sınırında öldürüldü — toplumcu yazar olduğu için. 'Kuyucaklı Yusuf' köy gerçeğini, 'İçimizdeki Şeytan' Cumhuriyet aydınını anlatır. Genç olarak ölmesi onu efsane yaptı.",
        "klasik_tuzak": "Orhan Kemal ile karıştırma — ikisi de toplumcu/halkçı. Sabahattin Ali ROMANTİK/MELANKOLİ + 'Madonna', Orhan Kemal İŞÇİ/EKMEK + Çukurova. 'Kürk Mantolu Madonna' Sabahattin Ali markası.",
        "rakipleri": ["Orhan Kemal", "Yaşar Kemal", "Kemal Tahir"]
    },
    "Tevfik Fikret": {
        "donem": "servet_i_funun_fecr_i_ati",
        "pozisyon": "Şair",
        "anekdot": "Servet-i Fünun'un BAŞ ŞAİRİ ama oğlu Haluk'a 'Müslüman olma, oku, ışık ol' diye vasiyet etti — Türk şiirinde böyle keskin bir laik manifest yok. 'Sis' İstanbul'a yazılmış en güçlü hicviye. 'Tarih-i Kadim' Türk şiirinde dinle hesaplaşmanın zirvesi.",
        "klasik_tuzak": "Cenap Şahabettin ile karıştırma. İkisi de SF, ama Fikret TOPLUMCU/ÖFKELİ/laik, Cenap LİRİK/sembolist/lirizm. 'Sis' Fikret; 'Elhân-ı Şitâ' Cenap.",
        "rakipleri": ["Cenap Şahabettin", "Mehmet Akif Ersoy", "Yahya Kemal Beyatlı"]
    },
    "Yahya Kemal Beyatlı": {
        "donem": "cumhuriyet",
        "pozisyon": "Şair",
        "anekdot": "Şiirini hayatta yayımlamadı — ölümünden sonra 'Kendi Gök Kubbemiz' çıktı. 'Sessiz Gemi' bilinen en güzel Türk şiirlerinden. Osmanlı'nın estetik mirasını Cumhuriyet'e taşıyan adam: 'Eski şiirin rüzgarıyla / Yeni şiir' formülü.",
        "klasik_tuzak": "Ahmet Haşim ile karıştırma. İkisi de saf şiir, ikisi de o devrin büyük isimleri. Haşim FECR-İ ÂTİ + sembolizm + akşam imgesi; Yahya Kemal CUMHURİYET + neo-klasik + İstanbul/tarih.",
        "rakipleri": ["Ahmet Haşim", "Ahmet Hamdi Tanpınar", "Necip Fazıl Kısakürek"]
    },
    "Yakup Kadri Karaosmanoğlu": {
        "donem": "milli_edebiyat",
        "pozisyon": "Romancı",
        "anekdot": "Türk romanının panoramik kalemi. 'Yaban' Kurtuluş Savaşı'nda Anadolu köylüsünü aydının gözünden, 'Kiralık Konak' kuşak çatışmasını, 'Kadro' onun dergisi. Cumhuriyet'in temel romanlarını yazan beşli içinde belki en derini.",
        "klasik_tuzak": "Yakup Kadri'nin her romanı FARKLI bir devri/temayı anlatır. 'Yaban' = Kurtuluş, 'Kiralık Konak' = kuşak çatışması, 'Sodom ve Gomore' = mütareke, 'Nur Baba' = Bektaşi tekke. Karıştırılmamalı.",
        "rakipleri": ["Reşat Nuri Güntekin", "Halide Edip Adıvar", "Refik Halit Karay"]
    },
    "Ahmedi": {
        "donem": "divan_edebiyati",
        "pozisyon": "Şair",
        "anekdot": "14. yy'ın divan şiiri kurucularından. 'İskendername' adlı 8000+ beyitlik mesnevisi tarih + macera + bilgi karışımı bir ansiklopedi. 'Cemşid ü Hurşid' de mesnevi. Anadolu'da Türkçe divan şiirinin ilk gerçek eseri sayılır.",
        "klasik_tuzak": "Şeyhi (Harname, 15. yy) ile karıştırma. İkisi de erken divan + mesnevi. Ahmedi 14. yy + İskendername (tarih), Şeyhi 15. yy + Harname (mizah).",
        "rakipleri": ["Şeyhi", "Süleyman Çelebi", "Hacı Bayram Veli"]
    },
    "Ahmet Hamdi Tanpınar": {
        "donem": "cumhuriyet",
        "pozisyon": "Çok yönlü",
        "anekdot": "Yahya Kemal'in öğrencisi, Türk edebiyatı tarihçisi + romancı + şair + denemeci. 'Huzur' Türk modernist romanının başyapıtı, 'Saatleri Ayarlama Enstitüsü' Cumhuriyet bürokrasisinin tek satırlık özeti. 'Beş Şehir' deneme türünün anıtı.",
        "klasik_tuzak": "Oğuz Atay ile karıştırma — ikisi de Türk modernist roman. Tanpınar İRONİK + TARİHSEL FELSEFE + estetik, Atay MİZAH + KARA KOMEDİ + Tutunamayanlar. 'Huzur' Tanpınar, 'Tutunamayanlar' Atay.",
        "rakipleri": ["Oğuz Atay", "Peyami Safa", "Yahya Kemal Beyatlı"]
    },
    "Ahmet Kutsi Tecer": {
        "donem": "cumhuriyet",
        "pozisyon": "Çok yönlü",
        "anekdot": "Memleket edebiyatının manifestosunu yazan adam. Halk şiirini Cumhuriyet aydını arasında 'aşk' haline getirdi. Aşık Veysel'i ilk keşfedip İstanbul'a getiren odur. 'Köşebaşı' oyunu Türk modern tiyatrosunun erken örneği. 'Orda Bir Köy Var Uzakta' onun mısraıdır.",
        "klasik_tuzak": "Faruk Nafiz Çamlıbel ile karıştırma — ikisi de memleket edebiyatı. Faruk Nafiz BEŞ HECECİLER + 'Han Duvarları', Tecer HALK ŞİİRİ ARAŞTIRMACILIĞI + Aşık Veysel.",
        "rakipleri": ["Faruk Nafiz Çamlıbel", "Cahit Külebi", "Bedri Rahmi Eyüboğlu"]
    },
    "Haldun Taner": {
        "donem": "cumhuriyet",
        "pozisyon": "Tiyatrocu",
        "anekdot": "Türk tiyatrosunda Brechtyen EPİK tiyatronun kurucusu. 'Keşanlı Ali Destanı' destan-tiyatro karışımı, Türk halk tiyatrosu + Batı modernist tekniği birleşimi. Hikayeleri de var ama tiyatrosuyla anılır.",
        "klasik_tuzak": "Turgut Özakman ile karıştırma — ikisi de Cumhuriyet tiyatrosunun büyük adları. Haldun Taner BRECHT/EPİK + 'Keşanlı Ali Destanı', Özakman MİLLİ TEMA + 'Şu Çılgın Türkler'.",
        "rakipleri": ["Necip Fazıl Kısakürek", "Cevat Fehmi Başkut", "Aziz Nesin"]
    },
    "Halide Edip Adıvar": {
        "donem": "milli_edebiyat",
        "pozisyon": "Romancı",
        "anekdot": "Sultanahmet Meydanı'ndaki Kurtuluş Savaşı mitingini ateşli konuşmasıyla yöneten adam aslında kadındır — 'Halide Onbaşı' lakabı oradan. 'Sinekli Bakkal' Türk romanının halk + İstanbul + Doğu-Batı bireşimi. 'Vurun Kahpeye' Anadolu öğretmenini efsane yaptı.",
        "klasik_tuzak": "Reşat Nuri Güntekin ile karıştırma — ikisi de Anadolu öğretmen romanı. Halide Edip MİLLİ MÜCADELE + güçlü kadın + İstanbul-Anadolu köprüsü, Reşat Nuri ÇALIKUŞU/Feride + romantik.",
        "rakipleri": ["Reşat Nuri Güntekin", "Yakup Kadri Karaosmanoğlu", "Refik Halit Karay"]
    },
    "Köroğlu": {
        "donem": "halk_edebiyati",
        "pozisyon": "Şair",
        "anekdot": "Halk hikayesi + saz şairi kimliği iç içe. Babasının gözlerini çıkartan beye karşı isyan edip dağa çıkan ve halkın iyiliği için çalışan haydut/şair. 'Benden selam olsun Bolu Beyi'ne' onun marka mısraı. Aşık edebiyatının en mitolojik figürü.",
        "klasik_tuzak": "Köroğlu HEM bir HALK HİKAYESİ kahramanı HEM bir ŞAİR. Halk hikayesini başkaları anlattı, şiirleri ona ait. Karacaoğlan veya Dadaloğlu gibi kıyaslanır ama Köroğlu 16-17. yy efsaneleşmiş figür.",
        "rakipleri": ["Karacaoğlan", "Dadaloğlu", "Aşık Veysel"]
    },
    "Orhan Kemal": {
        "donem": "cumhuriyet",
        "pozisyon": "Romancı",
        "anekdot": "Çukurova işçilerinin ve göçmenlerinin yazarı. Nazım Hikmet'in hapishane öğrencisi — orada yazmayı öğrendi. 'Bereketli Topraklar Üzerinde', 'Cemile', 'Murtaza' toplumcu gerçekçiliğin Türkçedeki adresi. Yoksulluğu romantize etmeden anlatan az yazardandır.",
        "klasik_tuzak": "Yaşar Kemal ile karıştırma — ikisi de Çukurova ve toplumcu gerçekçi. Orhan Kemal İŞÇİ/FABRİKA/şehir kenarı, Yaşar Kemal KÖY/AĞA/dağ + epik üslup. 'İnce Memed' Yaşar Kemal markası.",
        "rakipleri": ["Yaşar Kemal", "Kemal Tahir", "Sabahattin Ali"]
    },
    "Reşat Nuri Güntekin": {
        "donem": "milli_edebiyat",
        "pozisyon": "Romancı",
        "anekdot": "'Çalıkuşu' Feride'yi yazarak Türk romanına en sevilen kadın kahramanı kazandırdı. Anadolu öğretmeninin destanı bu kitap. 'Yaprak Dökümü', 'Yeşil Gece', 'Acımak' — hepsi Anadolu insanını sevecen bir gözle anlatır.",
        "klasik_tuzak": "Halide Edip ile karıştırma. Reşat Nuri ROMANTİK/DUYGUSAL + halkın gönlünde Feride, Halide Edip POLİTİK/Kurtuluş Savaşı + güçlü tipler. 'Çalıkuşu' Reşat Nuri; 'Sinekli Bakkal' Halide Edip.",
        "rakipleri": ["Halide Edip Adıvar", "Yakup Kadri Karaosmanoğlu", "Refik Halit Karay"]
    },
    "Şeyh Galip": {
        "donem": "divan_edebiyati",
        "pozisyon": "Şair",
        "anekdot": "18. yy'ın son büyük divan şairi. 26 yaşında 'Hüsn ü Aşk' alegorik mesnevisini yazdı — tasavvufun şiir biçiminde özeti. Mevlevi şeyhiydi, Mevlana'nın torunlarından. Sebk-i hindi'nin Türkçedeki zirvesi.",
        "klasik_tuzak": "Şeyhi (15. yy, Harname) ile karıştırma. İsim benzer ama 300 yıl arası. Şeyh GALİP tasavvufi alegori, Şeyhi mizahi mesnevi.",
        "rakipleri": ["Nedim", "Nef'i", "Naili"]
    },
    "Şinasi": {
        "donem": "tanzimat",
        "pozisyon": "Çok yönlü",
        "anekdot": "Türk edebiyatının 'İLK'lerinin BABASI. İlk Batı tarzı şiir çevirisi (Tercüman-ı Manzume), ilk Batı tarzı tiyatro (Şair Evlenmesi), ilk özel gazete (Tasvir-i Efkar), ilk noktalama işareti kullanımı. Tanzimat'ın yenilik kapısı.",
        "klasik_tuzak": "Namık Kemal ile karıştırma — Şinasi YENİLİKLERİN KURUCUSU/sade üslup, Namık Kemal HEYECANLI/vatan/hürriyet temaları + tiyatro/roman. 'Tercüman-ı Ahval' (gazete) Şinasi.",
        "rakipleri": ["Namık Kemal", "Ziya Paşa", "Ahmet Mithat Efendi"]
    },
    "Aka Gündüz": {
        "donem": "milli_edebiyat",
        "pozisyon": "Çok yönlü",
        "anekdot": "Milli Edebiyat'ın popüler romancı/hikayecisi. 'Dikmen Yıldızı' Ankara'yı romanlaştıran ilk eserlerden. Genellikle ikinci sıra anılır ama 'milli tema' işleyen önemli isimlerden.",
        "klasik_tuzak": "Mehmet Emin Yurdakul, Ömer Seyfettin gibi 'milli' isimlerle karıştırılabilir. Aka Gündüz daha çok POPÜLER ROMAN + Ankara odaklı, diğerleri ideolojik/dil sadeleşmesi öncüsü.",
        "rakipleri": ["Mehmet Emin Yurdakul", "Ahmet Hikmet Müftüoğlu", "Ömer Seyfettin"]
    },
    "Baki": {
        "donem": "divan_edebiyati",
        "pozisyon": "Şair",
        "anekdot": "16. yy'ın 'Sultanü'ş-Şuara'sı (şairlerin sultanı). Kanunî'nin gözdesi. 'Kanunî Mersiyesi' Türk şiirinin en görkemli ağıtlarından. Aşk yerine 'rint/zarif' dünyevi yaşam, lirik betimlemeler. Fuzuli'nin tam karşıt kutbu.",
        "klasik_tuzak": "Fuzuli (içsel acı) vs Baki (dünyevi zarafet) — 16. yy'ın iki kutbu. 'Kanunî Mersiyesi' Baki imzası; 'Su Kasidesi' Fuzuli.",
        "rakipleri": ["Fuzuli", "Nedim", "Nef'i"]
    },
    "Halit Fahri Ozansoy": {
        "donem": "cumhuriyet",
        "pozisyon": "Şair",
        "anekdot": "Beş Hececiler'in beşinden biri. Yusuf Ziya'nın çıkardığı Akbaba mizah dergisinde de yazdı. 'Cenk Duyguları' şiir kitabı. Tiyatro oyunları da yazdı (Baykuş, On Yılın Destanı).",
        "klasik_tuzak": "Beş Hececiler arasında en az hatırlananı. Diğer dördü: Faruk Nafiz, Yusuf Ziya, Orhan Seyfi, Enis Behiç. Hepsi HECE VEZNİ + MİLLİ TEMA.",
        "rakipleri": ["Faruk Nafiz Çamlıbel", "Yusuf Ziya Ortaç", "Orhan Seyfi Orhon"]
    },
    "Hayali Bey": {
        "donem": "divan_edebiyati",
        "pozisyon": "Şair",
        "anekdot": "16. yy'ın özgün lirik şairi. Aşk şiirinde Fuzuli/Baki'den farklı bir hayal dünyası kurar — 'hayali' lakabı bundandır. Kanunî döneminde itibarı yüksek, ama Baki'nin gölgesinde kalmış.",
        "klasik_tuzak": "Baki ile aynı dönem + aynı saray çevresi → karıştırma riski. Baki SULTANÜ'Ş-ŞUARA, Hayali İKİNCİ SIRADA + lirik özgünlük.",
        "rakipleri": ["Baki", "Fuzuli", "Nedim"]
    },
    "Hüseyin Cahit Yalçın": {
        "donem": "servet_i_funun_fecr_i_ati",
        "pozisyon": "Çok yönlü",
        "anekdot": "Servet-i Fünun'un romancı + eleştirmen + gazetecisi. 'Edebiyat ve Hukuk' makalesi Servet-i Fünun'un dağılma sebebi sayılır (II. Abdülhamit kapattı). 'Hayal İçinde' romanı + 'Kavgalarım' eleştiri.",
        "klasik_tuzak": "Halit Ziya Uşaklıgil ile karıştırma — ikisi de SF roman. Halit Ziya BÜYÜK ROMAN + Aşk-ı Memnu, Hüseyin Cahit ROMANTİK + ELEŞTİRMEN-GAZETECİ kimliği baskın.",
        "rakipleri": ["Halit Ziya Uşaklıgil", "Tevfik Fikret", "Mehmet Rauf"]
    },
    "Kemal Tahir": {
        "donem": "cumhuriyet",
        "pozisyon": "Romancı",
        "anekdot": "Toplumcu gerçekçilik içinde tezli/düşünceli romancı. 'Devlet Ana' Osmanlı'nın kuruluşunu, 'Esir Şehrin İnsanları' Mütareke İstanbul'unu, 'Yorgun Savaşçı' Kurtuluş Savaşı'nı anlatır. Nazım Hikmet ile hapis arkadaşı.",
        "klasik_tuzak": "Orhan Kemal, Yaşar Kemal ile karıştırma — üç 'Kemal' soyadlı toplumcu yazar. Kemal Tahir TARİHSEL TEZ + Anadolu/Osmanlı düşünsel, Orhan Kemal İŞÇİ, Yaşar Kemal KÖY EPİĞİ.",
        "rakipleri": ["Orhan Kemal", "Yaşar Kemal", "Sabahattin Ali"]
    },
    "Mehmet Akif Ersoy": {
        "donem": "milli_edebiyat",
        "pozisyon": "Şair",
        "anekdot": "İstiklal Marşı'nın şairi. 'Safahat' 7 kitaplık devasa şiir külliyatı — toplumun her kesimini sokak diliyle anlatır. Veteriner hekim, milletvekili, sürgün. Türkçe'nin yaşayan halini şiirde gösteren adam.",
        "klasik_tuzak": "Tevfik Fikret ile karıştırma — ikisi tam karşıt kutuplar. Fikret LAİK/öfkeli/'Müslüman olma', Akif İSLAMCI/uyandırıcı/'İstiklal Marşı'. İkisi de SF dönemini geçirdi, Akif sonra Milli Edebiyat'a evrildi.",
        "rakipleri": ["Tevfik Fikret", "Yahya Kemal Beyatlı", "Necip Fazıl Kısakürek"]
    },
    "Mithat Cemal Kuntay": {
        "donem": "cumhuriyet",
        "pozisyon": "Romancı",
        "anekdot": "'Üç İstanbul' romanı: II. Abdülhamit, II. Meşrutiyet, Mütareke dönemlerini bir İstanbul üzerinden anlatır. Aslında şair ve hukukçu, ama bu tek romanı ile edebiyat tarihine girer.",
        "klasik_tuzak": "Bu yazar tek roman ile tanınır: ÜÇ İSTANBUL. Karıştırılma riski düşük ama 'kim?' diye sorulduğunda 'Üç İstanbul' = Mithat Cemal.",
        "rakipleri": ["Yakup Kadri Karaosmanoğlu", "Ahmet Hamdi Tanpınar", "Peyami Safa"]
    },
    "Muallim Naci": {
        "donem": "tanzimat",
        "pozisyon": "Şair",
        "anekdot": "Tanzimat II. dönem'in ESKİ ŞİİR savunucusu. Recaizade'nin yeni şiir manifestosu 'Zemzeme'ye cevap olarak 'Demdeme' yazdı — Türk edebiyatının en ünlü polemiklerinden. Aruzun ustası, Batılılaşmaya direnen kanat.",
        "klasik_tuzak": "Recaizade Mahmut Ekrem ile karıştırma (TAM ZIT). Recaizade YENİ, Naci ESKİ. 'Zemzeme' Recaizade; 'Demdeme' Naci.",
        "rakipleri": ["Recaizade Mahmut Ekrem", "Abdülhak Hamit Tarhan", "Ziya Paşa"]
    },
    "Necati Cumalı": {
        "donem": "cumhuriyet",
        "pozisyon": "Çok yönlü",
        "anekdot": "Şair + hikayeci + oyun yazarı. 'Susuz Yaz' oyunu Karlovy Vary'de ödül aldı, Türk tiyatrosunu dünyaya açtı. Egeli, Aydınlı; köy hayatını ve insanını duygulu bir dille yazdı.",
        "klasik_tuzak": "Necati BEY (15. yy divan şairi) ile karıştırma. 'Cumalı' = 20. yy Cumhuriyet, 'Bey' = 15. yy Divan.",
        "rakipleri": ["Necati Bey", "Yaşar Kemal", "Haldun Taner"]
    },
    "Necip Fazıl Kısakürek": {
        "donem": "cumhuriyet",
        "pozisyon": "Çok yönlü",
        "anekdot": "Türk şiirine mistik/dini boyutu modern üslupla getiren adam. 'Çile' şiir kitabı, 'Bir Adam Yaratmak' oyunu, 'Büyük Doğu' dergisi. Bohem hayatla mistik arayışın çelişkili dehası.",
        "klasik_tuzak": "Sezai Karakoç ile karıştırma — ikisi de mistik şiir. Necip Fazıl ÖNCÜ + dramatik üslup, Sezai Karakoç DİRİLİŞ ekolü + sembolist.",
        "rakipleri": ["Sezai Karakoç", "Yahya Kemal Beyatlı", "Arif Nihat Asya"]
    },
    "Nedim": {
        "donem": "divan_edebiyati",
        "pozisyon": "Şair",
        "anekdot": "18. yy Lale Devri'nin şairi. Şiire İstanbul'u, Sadabad eğlencelerini, dünyevi zevki soktu — divan şiirinde böylesi 'yaşam sevinci' nadirdir. 'Mahallileşme' akımının zirvesi: şiirde halk sözcükleri, deyimler.",
        "klasik_tuzak": "Mahallileşme = Nedim. Sebk-i hindi = Nabi/Şeyh Galip. Karıştırma. 'Sadabad' Nedim'in markası.",
        "rakipleri": ["Şeyh Galip", "Nabi", "Nef'i"]
    },
    "Nef'i": {
        "donem": "divan_edebiyati",
        "pozisyon": "Şair",
        "anekdot": "17. yy'ın HİCİV şairi. Padişaha bile kafa tuttu, sonunda boğdurulup denize atıldı. 'Siham-ı Kaza' hicivlerinin kitabı. Methiye/kaside ustası ama hiciviyle hatırlanır.",
        "klasik_tuzak": "Hiciv = Nef'i. 'Tahir Efendi bana kelp demiş' beyiti onun. Diğer 17. yy divan şairi Nabi DİDAKTİK, Nef'i KEÇİBOYNUZU.",
        "rakipleri": ["Nabi", "Naili", "Şeyhülislam Yahya"]
    },
    "Orhan Seyfi Orhon": {
        "donem": "cumhuriyet",
        "pozisyon": "Şair",
        "anekdot": "Beş Hececiler'den. 'Anadolu Toprağı' Anadolu sevdasını işleyen şiir. Akbaba mizah dergisinde Yusuf Ziya ile çalıştı. Aşk-millet-vatan üçlemesinde gezindi.",
        "klasik_tuzak": "Yusuf Ziya Ortaç ile sıkça karıştırılır — ikisi de Beş Hececiler + Akbaba. Şiir isimleri farklı; 'Anadolu Toprağı' = Orhan Seyfi.",
        "rakipleri": ["Yusuf Ziya Ortaç", "Faruk Nafiz Çamlıbel", "Enis Behiç Koryürek"]
    },
    "Samipaşazade Sezai": {
        "donem": "tanzimat",
        "pozisyon": "Romancı",
        "anekdot": "Tanzimat II. dönem'in realist romanının ilk gerçek temsilcisi. 'Sergüzeşt' romanı bir cariyenin hayatını ve özgürlük arayışını anlatır — Türk romanında 'fakir kız' arketipinin başlangıcı.",
        "klasik_tuzak": "Nabizade Nazım (Karabibik) ile karıştırma — ikisi de Tanzimat II. dönem realist roman öncüsü. 'Sergüzeşt' Sezai; 'Karabibik' (ilk köy romanı) Nabizade.",
        "rakipleri": ["Nabizade Nazım", "Recaizade Mahmut Ekrem", "Ahmet Mithat Efendi"]
    },
    "Süleyman Çelebi": {
        "donem": "divan_edebiyati",
        "pozisyon": "Şair",
        "anekdot": "15. yy'ın 'Mevlid' (Vesiletü'n-Necat) yazarı. Hz. Muhammed'in doğumunu/yaşamını Türkçe mesnevi olarak anlattı, halkın camide okuduğu eser. Türk-İslam edebiyatının en yaygın metinlerinden.",
        "klasik_tuzak": "Mevlana ile karıştırma. Mevlana 13. yy + Farsça Mesnevi; Süleyman Çelebi 15. yy + Türkçe Mevlid. İkisi de mesnevi yazdı ama dil/dönem farkı.",
        "rakipleri": ["Mevlana", "Ahmet Yesevi", "Hacı Bayram Veli"]
    },
    "Tarık Buğra": {
        "donem": "cumhuriyet",
        "pozisyon": "Romancı",
        "anekdot": "Cumhuriyet'in ikinci kuşak büyük romancılarından. 'Küçük Ağa' Kurtuluş Savaşı'nın Anadolu'daki sosyal/dini boyutunu, 'Osmancık' Osmanlı'nın kuruluşunu anlatır. Tarihi roman + psikolojik derinlik.",
        "klasik_tuzak": "Kemal Tahir 'Devlet Ana' ile yine Osmanlı kuruluşunu işledi. Tarık Buğra 'Osmancık' farklı bir okumayla. İkisini karıştırmamak için: Devlet Ana = Kemal Tahir, Osmancık = Tarık Buğra.",
        "rakipleri": ["Kemal Tahir", "Ahmet Hamdi Tanpınar", "Mustafa Necati Sepetçioğlu"]
    },
    "Yaşar Kemal": {
        "donem": "cumhuriyet",
        "pozisyon": "Romancı",
        "anekdot": "Türk romanının Nobel adayı. 'İnce Memed' Çukurova'nın eşkıya destanı — 4 ciltlik dağ romanı. Toplumcu gerçekçi ama anlatımı epik/destansı. Halk kültürünü modern romana taşımanın en başarılı örneği.",
        "klasik_tuzak": "Orhan Kemal, Kemal Tahir 'Kemal'leri ile karıştırma. Yaşar Kemal EPİK + Çukurova + İnce Memed.",
        "rakipleri": ["Orhan Kemal", "Kemal Tahir", "Sabahattin Ali"]
    },
    "Yunus Emre": {
        "donem": "halk_edebiyati",
        "pozisyon": "Şair",
        "anekdot": "13-14. yy geçiş dönemi tasavvuf şairi. Türkçeyi gerçek bir SANAT dili haline getiren adam — Arapça/Farsça yerine sade Türkçeyle ilahi yazdı. 'Mevlana, Yunus'tan önce Türkçeyi şiir dili olarak kullanmamıştır' diyenler var.",
        "klasik_tuzak": "Mevlana ile karıştırma — ikisi de tasavvuf, ikisi de 13. yy. Mevlana FARSÇA + saray çevresi, Yunus TÜRKÇE + halk dili. Yunus dili 'sade', Mevlana 'gösterişli'.",
        "rakipleri": ["Mevlana", "Hacı Bayram Veli", "Ahmet Yesevi"]
    },
    "Yusuf Ziya Ortaç": {
        "donem": "cumhuriyet",
        "pozisyon": "Çok yönlü",
        "anekdot": "Beş Hececiler'den. Akbaba mizah dergisinin sahibi — Türk mizah basını tarihinde anıt isim. Şiirleri kadar siyasi hicivleri ve nükteleri bilinir.",
        "klasik_tuzak": "Orhan Seyfi Orhon ile karıştırma — ikisi de Beş Hececiler + Akbaba. Yusuf Ziya AKBABA SAHİBİ, Orhan Seyfi yazar/şair.",
        "rakipleri": ["Orhan Seyfi Orhon", "Faruk Nafiz Çamlıbel", "Halit Fahri Ozansoy"]
    },
    "Ziya Paşa": {
        "donem": "tanzimat",
        "pozisyon": "Şair",
        "anekdot": "Tanzimat I. dönem'in 'Terkib-i Bend' ve 'Terci-i Bend' şairi. 'Bu cihan dârül-hicrana benzer, kim ki anladıysa zindana' onun. Geleneksel divan kalıbıyla yenilikçi içerik yazdı — geçiş döneminin tipik figürü.",
        "klasik_tuzak": "Namık Kemal ile karıştırma — ikisi de Tanzimat I. dönem. Ziya Paşa GELENEKSEL KALIPLA YENİ İÇERİK + 'Şiir ve İnşa' makalesi; Namık Kemal TİYATRO/ROMAN + heyecanlı üslup.",
        "rakipleri": ["Namık Kemal", "Şinasi", "Ahmet Mithat Efendi"]
    },
    "Şemsettin Sami": {
        "donem": "tanzimat",
        "pozisyon": "Çok yönlü",
        "anekdot": "Türk SÖZLÜK biliminin babası. 'Kamus-ı Türki' (Türk Sözlüğü) ve 'Kamusu'l-Alam' (Ansiklopedi). 'Taaşşuk-ı Talat ve Fitnat' Türk edebiyatının İLK ROMAN'ı kabul edilir.",
        "klasik_tuzak": "Ahmet Mithat ile karıştırma — ikisi de Tanzimat I. dönem popüler. Şemsettin Sami SÖZLÜK + İLK ROMAN, Ahmet Mithat ÇOK ROMAN + halk eğitimi.",
        "rakipleri": ["Ahmet Mithat Efendi", "Namık Kemal", "Direktör Ali Bey"]
    },
    "Adalet Ağaoğlu": {
        "donem": "cumhuriyet",
        "pozisyon": "Romancı",
        "anekdot": "Cumhuriyet kuşağının kadın yazarlarından. 'Ölmeye Yatmak' kuşak/kimlik romanı, 'Bir Düğün Gecesi' politik dönüşüm anı. Bilinç akışı tekniğini Türkçeye sokanlardan.",
        "klasik_tuzak": "Latife Tekin, Pınar Kür gibi diğer Cumhuriyet kadın yazarları ile karıştırma. Adalet Ağaoğlu BİLİNÇ AKIŞI + politik kuşak romanı.",
        "rakipleri": ["Latife Tekin", "Pınar Kür", "Sevgi Soysal"]
    },
    "Ahmet Hikmet Müftüoğlu": {
        "donem": "milli_edebiyat",
        "pozisyon": "Hikayeci",
        "anekdot": "Milli Edebiyat'ın 'Çağlayanlar' adlı hikaye kitabıyla bilinen yazarı. Turancı çizgide, Türk mitolojisi ve folkloru hikayelere taşıdı.",
        "klasik_tuzak": "Ömer Seyfettin ile karıştırma — ikisi de Milli Edebiyat hikayeciliği. Ahmet Hikmet TURANCI + mitolojik, Ömer Seyfettin SADE DİL + sosyal mesaj/mizah.",
        "rakipleri": ["Ömer Seyfettin", "Refik Halit Karay", "Aka Gündüz"]
    },
    "Ahmet Vefik Paşa": {
        "donem": "tanzimat",
        "pozisyon": "Çok yönlü",
        "anekdot": "Türk tiyatrosuna Molière çevirileriyle yön veren adam. Bursa valisi iken yerel tiyatroyu destekledi. 'Lehçe-i Osmani' sözlüğü ve 'Şecere-i Türki' çevirisi de var.",
        "klasik_tuzak": "Molière çevirmeni = Ahmet Vefik Paşa. Tiyatroyla anılır ama VALİ + ÇEVİRMEN profili daha belirgin.",
        "rakipleri": ["Molière", "Direktör Ali Bey", "Şinasi"]
    },
    "Ahmet Yesevi": {
        "donem": "islamiyet_oncesi_gecis",
        "pozisyon": "Şair",
        "anekdot": "Geçiş Dönemi'nin (12. yy) tasavvuf şairi. 'Divan-ı Hikmet' Türklerin İslamiyet'i kabulünden sonraki ilk büyük tasavvufi eserdir. Yunus Emre'nin atası sayılır.",
        "klasik_tuzak": "Yunus Emre ile karıştırma. Yesevi 12. yy ORTA ASYA + Divan-ı Hikmet, Yunus 13-14. yy ANADOLU + sade Türkçe. Yesevi öncül, Yunus zirve.",
        "rakipleri": ["Yunus Emre", "Hacı Bayram Veli", "Mevlana"]
    },
    "Arif Nihat Asya": {
        "donem": "cumhuriyet",
        "pozisyon": "Şair",
        "anekdot": "'Bayrak Şairi'. 'Ey mavi göklerin beyaz ve kızıl süsü' onun mısraı. Milli ve manevi temaları işledi. 'Naat' eseri Hz. Muhammed'e methiye geleneğini Cumhuriyet'e taşıdı.",
        "klasik_tuzak": "Necip Fazıl ile karıştırma — ikisi de manevi/milli şiir. Arif Nihat BAYRAK + naat + sade, Necip Fazıl ÇİLE + mistik dramatik.",
        "rakipleri": ["Necip Fazıl Kısakürek", "Sezai Karakoç", "Mehmet Akif Ersoy"]
    },
    "Bedri Rahmi Eyüboğlu": {
        "donem": "cumhuriyet",
        "pozisyon": "Şair",
        "anekdot": "Hem ressam hem şair. 'Karadut' onun marka şiiri. Halk şiirini modern üslupla buluşturdu — folklor unsurlarını şiirine taşıdı.",
        "klasik_tuzak": "Bedri Rahmi RESSAM-ŞAİR kombinasyonu özel; folklor temalı diğer şairlerle (Cahit Külebi, Ahmet Kutsi Tecer) karıştırılabilir.",
        "rakipleri": ["Cahit Külebi", "Ahmet Kutsi Tecer", "Fazıl Hüsnü Dağlarca"]
    },
    "Brancusi": {
        "donem": "edebi_akimlar",
        "pozisyon": "Çok yönlü",
        "anekdot": "Romanyalı modern heykeltıraş — Türk edebiyatı yazarı değil. AYT'de paragraf sorularında 'sanat' örneği olarak geçer. 'Bilim insanı veya sanatçı' tarzı paragraflarda dikkat.",
        "klasik_tuzak": "Bu bir edebiyat sorusu değil, paragraf wisdom. Cevap kişisi olarak değil, paragraftaki bilgiyle anlam çıkarma.",
        "rakipleri": []
    },
    "Cahit Külebi": {
        "donem": "cumhuriyet",
        "pozisyon": "Şair",
        "anekdot": "Memleket şiirinin ikinci kuşak temsilcisi. Sivaslı, Anadolu'yu sıcak, gündelik bir dille şiirleştirdi. 'Hikaye' ve 'Sivas Yollarında' bilinen şiirleri.",
        "klasik_tuzak": "Ahmet Kutsi Tecer ile karıştırma — ikisi de memleket şiiri. Tecer halk şiir araştırması + 'Orda Bir Köy Var Uzakta', Külebi LİRİK + Sivas/Anadolu sıcaklığı.",
        "rakipleri": ["Ahmet Kutsi Tecer", "Bedri Rahmi Eyüboğlu", "Faruk Nafiz Çamlıbel"]
    },
    "Direktör Ali Bey": {
        "donem": "tanzimat",
        "pozisyon": "Tiyatrocu",
        "anekdot": "Tanzimat tiyatrosunun erken figürü. 'Kokona Yatıyor', 'Geveze Berber' kısa komedileri ile bilinir. Tiyatroyu Osmanlı sosyetesine sevdiren isimlerden.",
        "klasik_tuzak": "Şinasi'nin 'Şair Evlenmesi' (ilk Batı tarzı oyun) sonrası Türk komedisini devam ettiren isim Direktör Ali Bey. Karıştırılma şansı düşük ama unutulmasın.",
        "rakipleri": ["Şinasi", "Ahmet Vefik Paşa", "Namık Kemal"]
    },
    "Ece Ayhan": {
        "donem": "cumhuriyet",
        "pozisyon": "Şair",
        "anekdot": "İkinci Yeni'nin en SIRADIŞI şairi. 'Bakışsız Bir Kedi Kara' şiirinde anlam katmanlarını alt üst etti. 'Sivil şiir' anlayışı — sıradan/marjinal kahramanlar.",
        "klasik_tuzak": "İkinci Yeni'nin dörtlüsü: Turgut Uyar, Edip Cansever, Cemal Süreya, Ece Ayhan. Ece Ayhan EN UÇTAKİ + sivil şiir; Cemal Süreya AŞK; Cansever EŞYA; Uyar ARABESK MUTLULUK.",
        "rakipleri": ["Cemal Süreya", "Edip Cansever", "Turgut Uyar"]
    },
    "Enis Behiç Koryürek": {
        "donem": "cumhuriyet",
        "pozisyon": "Şair",
        "anekdot": "Beş Hececiler'den. 'Gemiciler' şiiri ile denizci/uzak yolculuk temaları getirdi — milli edebiyat şiirinde sıra dışı bir kanal. Sonradan tasavvufi şiire yöneldi.",
        "klasik_tuzak": "Beş Hececiler içinde DENİZ teması = Enis Behiç. Diğerleri Anadolu odaklı.",
        "rakipleri": ["Faruk Nafiz Çamlıbel", "Halit Fahri Ozansoy", "Yusuf Ziya Ortaç"]
    },
    "Falih Rıfkı Atay": {
        "donem": "cumhuriyet",
        "pozisyon": "Çok yönlü",
        "anekdot": "Cumhuriyet'in gezi yazarı ve gazetecisi. 'Zeytindağı' Birinci Dünya Savaşı Filistin cephesi anısı, 'Çankaya' Atatürk'ün biyografik portresi. Cumhuriyet'in ilk kuşak fikir adamlarından.",
        "klasik_tuzak": "Reşat Nuri'nin 'Anadolu Notları' gezisiyle karıştırılabilir. Falih Rıfkı SAVAŞ-DÖNEM ANI + Atatürk biyografisi.",
        "rakipleri": ["Reşat Nuri Güntekin", "Ahmet Haşim", "Yakup Kadri Karaosmanoğlu"]
    },
    "Fazıl Hüsnü Dağlarca": {
        "donem": "cumhuriyet",
        "pozisyon": "Şair",
        "anekdot": "Cumhuriyet'in en üretken şairi — 80+ kitap. 'Çocuk ve Allah', 'Üç Şehitler Destanı' biliniyor. Her tür temayı işledi: çocuk, savaş, milli, mistik.",
        "klasik_tuzak": "Belli bir akıma sokmak zor; Garip/İkinci Yeni dışı bağımsız büyük şair. Necip Fazıl, Yahya Kemal düzeyinde 'bağımsız' grubunda.",
        "rakipleri": ["Necip Fazıl Kısakürek", "Yahya Kemal Beyatlı", "Arif Nihat Asya"]
    },
    "Freud": {
        "donem": "edebi_akimlar",
        "pozisyon": "Çok yönlü",
        "anekdot": "Avusturyalı psikanalist, edebiyat değil bilim. AYT'de paragraf-anlam veya akım sorusunda 'bilinçaltı/psikanaliz' bağlamında geçer. Sürrealizm akımının kuramsal arka planı.",
        "klasik_tuzak": "Türk yazarı değil, paragraf wisdom için kullanılır. Sürrealizm akımıyla ilişkilendirildiğinde anlam kazanır.",
        "rakipleri": []
    },
    "Hacı Bayram Veli": {
        "donem": "divan_edebiyati",
        "pozisyon": "Şair",
        "anekdot": "14-15. yy tekke şairi. Bayramiye tarikatının kurucusu. Az şiir yazdı ama Türk-İslam tasavvufunda derin iz bıraktı. Türkçe ilahileri Anadolu halk söyleyişinin temelinde.",
        "klasik_tuzak": "Yunus Emre, Yesevi, Mevlana, Süleyman Çelebi gibi diğer tasavvuf şairleriyle karıştırma. Hacı Bayram BAYRAMİYE TARİKATI kurucusu = ayırt edici.",
        "rakipleri": ["Yunus Emre", "Mevlana", "Ahmet Yesevi"]
    },
    "Halikarnas Balıkçısı": {
        "donem": "cumhuriyet",
        "pozisyon": "Romancı",
        "anekdot": "Asıl adı Cevat Şakir Kabaağaçlı. Bodrum'a sürgün, oradan deniz/Ege yazarı doğdu. 'Aganta Burina Burinata', 'Mavi Sürgün' deniz edebiyatının zirvesi. 'Mavi Anadoluculuk' fikir akımının baş ismi.",
        "klasik_tuzak": "İsim aldatıcı — 'Halikarnas Balıkçısı' bir mahlas, gerçek adı Cevat Şakir. Aynı yazar.",
        "rakipleri": ["Sait Faik Abasıyanık", "Yaşar Kemal", "Memduh Şevket Esendal"]
    },
    "Halit Ziya Uşaklıgil": {
        "donem": "servet_i_funun_fecr_i_ati",
        "pozisyon": "Romancı",
        "anekdot": "Türk romanına Batılı tekniği getiren ilk büyük yazar. 'Aşk-ı Memnu' (1900) Türkçedeki ilk gerçek psikolojik roman/yasak aşk anlatımı. Servet-i Fünun'un romancı zirvesi.",
        "klasik_tuzak": "Mehmet Rauf'un 'Eylül'üyle karıştırılır — ikisi de SF + ilk psikolojik roman tartışmasında. AŞK-I MEMNU = HALİT ZİYA; EYLÜL = MEHMET RAUF.",
        "rakipleri": ["Hüseyin Cahit Yalçın", "Mehmet Rauf", "Tevfik Fikret"]
    },
    "Latife Tekin": {
        "donem": "cumhuriyet",
        "pozisyon": "Romancı",
        "anekdot": "1980 sonrası kuşağın belki en özgün ismi. 'Sevgili Arsız Ölüm' büyülü gerçekçilik + köy göçü, 'Berci Kristin Çöp Masalları' kenar mahalle insanını mitolojik dille anlattı.",
        "klasik_tuzak": "Adalet Ağaoğlu, Pınar Kür ile karıştırma — Cumhuriyet kadın yazarları. Latife Tekin BÜYÜLÜ GERÇEKÇİLİK + kenar mahalle.",
        "rakipleri": ["Adalet Ağaoğlu", "Pınar Kür", "Sevgi Soysal"]
    },
    "Mary Shelley": {
        "donem": "edebi_akimlar",
        "pozisyon": "Romancı",
        "anekdot": "İngiliz yazar, 'Frankenstein' (1818) romanının yaratıcısı. AYT'de Romantizm + Gotik roman + bilim-kurgu başlangıcı bağlamında geçer.",
        "klasik_tuzak": "Türk yazarı değil. Romantizm/Gotik akımlar sorulduğunda referans isim.",
        "rakipleri": []
    },
    "Mehmet Emin Yurdakul": {
        "donem": "milli_edebiyat",
        "pozisyon": "Şair",
        "anekdot": "Milli Edebiyat şiirinin öncüsü. 'Cenge Giderken' / 'Ben bir Türk'üm, dinim cinsim uludur' Türk milliyetçi şiirinin manifestosu. Hece + sade Türkçe + millet teması üçgenini kuran şair.",
        "klasik_tuzak": "Beş Hececiler ile karıştırma — onlar daha sonraki kuşak. Mehmet Emin ÖNCÜ + 'Cenge Giderken'; Beş Hececiler ardıllar.",
        "rakipleri": ["Ziya Gökalp", "Faruk Nafiz Çamlıbel", "Ahmet Hikmet Müftüoğlu"]
    },
    "Melih Cevdet Anday": {
        "donem": "cumhuriyet",
        "pozisyon": "Şair",
        "anekdot": "Garip Üçlüsü'nün üçüncüsü. Orhan Veli + Oktay Rifat ile birlikte vezin-kafiyeyi şiirden attılar. Sonrasında özgün bir bilgelik şiirine yöneldi.",
        "klasik_tuzak": "Garip Üçlüsü: Orhan Veli (lider) + Melih Cevdet + Oktay Rifat. Üçü birlikte 'Garip' antolojisini çıkardılar (1941).",
        "rakipleri": ["Orhan Veli Kanık", "Oktay Rifat Horozcu", "Cahit Külebi"]
    },
    "Mevlana": {
        "donem": "divan_edebiyati",
        "pozisyon": "Şair",
        "anekdot": "13. yy'ın evrensel sufisi. 'Mesnevi' 25 bin beyitlik tasavvuf ansiklopedisi. FARSÇA yazdı — bu yüzden 'Türk edebiyatı şairi' demek tartışmalı, ama Anadolu kültürünün taşıyıcısı kabul edilir.",
        "klasik_tuzak": "Yunus Emre ile karıştırma. Mevlana FARSÇA + saray çevresi + Mesnevi, Yunus TÜRKÇE + halk + sade ilahi. Aynı yüzyıl ama dil/seyirci farkı.",
        "rakipleri": ["Yunus Emre", "Ahmet Yesevi", "Hacı Bayram Veli"]
    },
    "Molière": {
        "donem": "edebi_akimlar",
        "pozisyon": "Tiyatrocu",
        "anekdot": "17. yy Fransız komedi yazarı, KLASİSİZM akımının büyük adı. AYT'de tek başına az sorulur ama 'Ahmet Vefik Paşa'nın çevirdiği Molière' bağlantısı önemli.",
        "klasik_tuzak": "Türk yazarı değil ama Tanzimat tiyatrosuna direkt etki etti (Ahmet Vefik Paşa çevirileri). 'Cimri', 'Tartuffe' karakterleri Türk komedisinin atası.",
        "rakipleri": ["Ahmet Vefik Paşa", "Shakespeare", "Direktör Ali Bey"]
    },
    "Nabizade Nazım": {
        "donem": "tanzimat",
        "pozisyon": "Romancı",
        "anekdot": "Türk edebiyatının ilk KÖY romanı 'Karabibik'in yazarı. Tanzimat II. dönem realizmin/natüralizmin Türkçedeki ilk denemesi. 'Zehra' psikolojik roman denemesi.",
        "klasik_tuzak": "Samipaşazade Sezai (Sergüzeşt) ile karıştırma — ikisi de Tanzimat II. dönem realist roman öncüsü. 'Karabibik' = Nabizade Nazım; 'Sergüzeşt' = Samipaşazade Sezai.",
        "rakipleri": ["Samipaşazade Sezai", "Recaizade Mahmut Ekrem", "Abdülhak Hamit Tarhan"]
    },
    "Naili": {
        "donem": "divan_edebiyati",
        "pozisyon": "Şair",
        "anekdot": "17. yy SEBK-İ HİNDİ akımının Türkçedeki ilk büyük temsilcisi. İnce, sembolik, hayal yüklü gazelleri ile bilinir. Çağdaşı Nef'i'nin hicvi kadar gürültülü değildi.",
        "klasik_tuzak": "Sebk-i hindi denince ilk akla Şeyh Galip gelir ama o 18. yy. 17. yy'da SEBK-İ HİNDİ = NAİLİ. Nef'i (hiciv) ve Nabi (didaktik) çağdaşı.",
        "rakipleri": ["Nef'i", "Nabi", "Şeyh Galip"]
    },
    "Nazım Hikmet": {
        "donem": "cumhuriyet",
        "pozisyon": "Şair",
        "anekdot": "Türk şiirinin TOPLUMCU GERÇEKÇİ devrimcisi. Hapiste yatarken yazdığı 'Memleketimden İnsan Manzaraları' Türk şiirinin destansı eseri. Serbest nazmı + Marksist içeriği birleştirdi. Sürgünde Moskova'da öldü.",
        "klasik_tuzak": "Serbest nazım = Nazım Hikmet (Garip değil). Garip de vezni attı ama 'gündelik dil' odaklı; Nazım 'destansı serbest nazım' + politik tema.",
        "rakipleri": ["Orhan Veli Kanık", "Necip Fazıl Kısakürek", "Yahya Kemal Beyatlı"]
    },
    "Oğuz Atay": {
        "donem": "cumhuriyet",
        "pozisyon": "Romancı",
        "anekdot": "'Tutunamayanlar' (1971-72) Türk modernist romanının zirvesi. Joyce'tan etkilenmiş, bilinç akışı + ironi + parodi. Hayattayken anlaşılmadı, sonradan kült oldu. 'Tehlikeli Oyunlar' diğer büyük romanı.",
        "klasik_tuzak": "Ahmet Hamdi Tanpınar ile karıştırma — ikisi de Türk modernist. Tanpınar TARİHSEL DERİN + 'Huzur'; Atay İRONİK PARODİ + 'Tutunamayanlar'.",
        "rakipleri": ["Ahmet Hamdi Tanpınar", "Yusuf Atılgan", "Peyami Safa"]
    },
    "Peyami Safa": {
        "donem": "cumhuriyet",
        "pozisyon": "Romancı",
        "anekdot": "Türk PSİKOLOJİK romanının büyük adı. 'Dokuzuncu Hariciye Koğuşu' bir hasta çocuğun bilinciyle hastane romanı, 'Matmazel Noraliya'nın Koltuğu' mistik psikoloji. 'Server Bedi' takma adıyla popüler roman da yazdı.",
        "klasik_tuzak": "Mehmet Rauf 'Eylül' ile ilk psikolojik roman; Peyami Safa Cumhuriyet'in psikolojik roman zirvesi. Farklı dönemler, aynı tür.",
        "rakipleri": ["Mehmet Rauf", "Ahmet Hamdi Tanpınar", "Halit Ziya Uşaklıgil"]
    },
    "Pınar Kür": {
        "donem": "cumhuriyet",
        "pozisyon": "Romancı",
        "anekdot": "'Asılacak Kadın' romanı kadın bakış açısı + ölüm cezası teması. 1970'ler sonrası kuşağın güçlü kalemlerinden. Polisiye-toplumsal roman karışımı.",
        "klasik_tuzak": "Adalet Ağaoğlu, Latife Tekin, Sevgi Soysal ile karıştırma. Pınar Kür POLİSİYE + KADIN BAKIŞI.",
        "rakipleri": ["Adalet Ağaoğlu", "Latife Tekin", "Sevgi Soysal"]
    },
    "Sezai Karakoç": {
        "donem": "cumhuriyet",
        "pozisyon": "Şair",
        "anekdot": "DİRİLİŞ ekolünün kurucusu, mistik şiirin Cumhuriyet'teki büyük adlarından. 'Mona Roza', 'Sürgün Ülkeden Başkentler Başkentine' marka şiirleri. İslamcı düşünür kimliği de var.",
        "klasik_tuzak": "Necip Fazıl ile karıştırma — ikisi de mistik şiir. Necip Fazıl ÇİLE + Büyük Doğu; Sezai Karakoç DİRİLİŞ + Mona Roza.",
        "rakipleri": ["Necip Fazıl Kısakürek", "Arif Nihat Asya", "Cahit Zarifoğlu"]
    },
    "Shakespeare": {
        "donem": "edebi_akimlar",
        "pozisyon": "Tiyatrocu",
        "anekdot": "İngiliz tiyatrosunun zirvesi. AYT'de paragraf-anlam veya akım sorusunda evrensel insan teması bağlamında geçer. Rönesans dönemi.",
        "klasik_tuzak": "Türk yazarı değil. Hamlet/Macbeth gibi karakterler 'evrensel insan' örneği olarak paragraflarda geçer.",
        "rakipleri": []
    },
    "Süleyman Nazif": {
        "donem": "servet_i_funun_fecr_i_ati",
        "pozisyon": "Çok yönlü",
        "anekdot": "Servet-i Fünun'un gazetecisi/şairi. 'Firak-ı Irak' Bağdat'ın İngilizlerce işgali üzerine yazılmış ünlü makale. Kardeşi Faik Ali de şair.",
        "klasik_tuzak": "Cenap Şahabettin, Tevfik Fikret çevresinde anılır. SF içinde şiirden çok GAZETECİLİK + MAKALE alanında öne çıkar.",
        "rakipleri": ["Cenap Şahabettin", "Hüseyin Cahit Yalçın", "Tevfik Fikret"]
    },
    "Tesla": {
        "donem": "edebi_akimlar",
        "pozisyon": "Çok yönlü",
        "anekdot": "Sırp-Amerikan mucit-mühendis. Türk edebiyatı yazarı DEĞİL. AYT'de paragraf-anlam sorularında 'bilim insanı/yenilik' örneği olarak geçer.",
        "klasik_tuzak": "Bu paragraf wisdom için. Cevap kişiye değil, paragraftaki bilgiye odaklan.",
        "rakipleri": []
    },
    "Ziya Gökalp": {
        "donem": "milli_edebiyat",
        "pozisyon": "Çok yönlü",
        "anekdot": "Milli Edebiyat'ın İDEOLOĞU/sosyoloğu. 'Türkçülüğün Esasları' fikir kitabı, 'Kızıl Elma' şiir destanı. Türk milliyetçiliğinin kuramsal mimarı. 'Türkleşmek, İslamlaşmak, Muasırlaşmak' formülü.",
        "klasik_tuzak": "Mehmet Emin Yurdakul ile karıştırma — Yurdakul ŞAİR/şiirsel manifesto, Gökalp DÜŞÜNÜR/sosyolog + fikri sistematik.",
        "rakipleri": ["Mehmet Emin Yurdakul", "Ömer Seyfettin", "Yusuf Akçura"]
    },
    "Ömer Seyfettin": {
        "donem": "milli_edebiyat",
        "pozisyon": "Hikayeci",
        "anekdot": "Türk hikayeciliğinin BABASI. 'Genç Kalemler' dergisinde dil sadeleşmesinin manifestosunu yazdı. 'Bomba', 'Pembe İncili Kaftan', 'Falaka', 'Kaşağı' — okumayan kalmadı bu hikayeleri. 36'da hapishanede öldü.",
        "klasik_tuzak": "Refik Halit ile karıştırma — ikisi de Milli Edebiyat hikayeciliği. Ömer Seyfettin DİL SADELEŞMESİ + tarih/mizah + 'Genç Kalemler', Refik Halit MEMLEKET GERÇEKÇİLİĞİ.",
        "rakipleri": ["Refik Halit Karay", "Ahmet Hikmet Müftüoğlu", "Yakup Kadri Karaosmanoğlu"]
    },
}


def main():
    if not AUTHORS_PATH.exists():
        print(f"HATA: {AUTHORS_PATH} bulunamadı")
        return
    data = json.loads(AUTHORS_PATH.read_text(encoding='utf-8'))
    enriched = 0
    missing = []
    for entry in data:
        name = entry['name']
        if name in ENRICHMENT:
            patch = ENRICHMENT[name]
            for k, v in patch.items():
                entry[k] = v
            enriched += 1
        else:
            missing.append(name)
            # Fallback: konuya göre dönem ata, diğer alanlar boş
            primary = entry['konular'][0] if entry.get('konular') else 'cumhuriyet'
            entry.setdefault('donem', primary)
            entry.setdefault('pozisyon', 'Çok yönlü')
            entry.setdefault('anekdot', '')
            entry.setdefault('klasik_tuzak', '')
            entry.setdefault('rakipleri', [])

    AUTHORS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"✓ {enriched} yazar zenginleştirildi (toplam {len(data)})")
    if missing:
        print(f"⚠ Enrichment'ta olmayan {len(missing)} yazar:")
        for m in missing:
            print(f"  - {m}")


if __name__ == '__main__':
    main()
