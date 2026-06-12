"""
REV21 — Yazar Hafıza Kodlama (Görsel/İşitsel Mnemonic) kaynağı.

Her yazar için bir kodlama objesi:
  ad_cagrisimi : sesçil isim kancası (name hook)
  sahne        : 1-3 cümle canlı/absürt imge — QUIZ PROMPT'u olur.
                 ⚠ Yazar adını VE eser adını DÜZ METİN olarak İÇERMEZ
                   (semboller/homofonlar üzerinden kodlanır → spoiler guard).
  cozum        : sahnedeki sembolleri gerçek eser/kahraman/döneme eşler
                 (yalnız cevaptan SONRA gösterilir).
  tip          : "hikaye" | "gorsel" | "ses"
  emoji        : tek emoji

Kaynak: yalnız authors.json.diger_eserler + mevcut anekdot/klasik_tuzak +
ÖSYM kanonu. Yeni biyografik/olgusal iddia YOK, uydurma eser YOK.

İki tüketici (decoupled, REV20 build_terimler.py paterni):
  - generate_data.py  gen_kodlama_cards()  → quiz kartları
  - enrich_authors.py                       → authors.json'a kodlama enjekte

Çıktı: data/kodlama_kaynak.json  ({ "Yazar Adı": {kodlama} })
"""
import json, sys, io, unicodedata
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# DATA_ROOT, generate_data.py ile AYNI yere yazmalı (Edebiyat Analiz/data/)
SITE_ROOT = Path(__file__).parent.parent            # .../edebiyat-site
DATA_ROOT = Path(__file__).parent.parent.parent     # .../Edebiyat Analiz
OUT = DATA_ROOT / 'data' / 'kodlama_kaynak.json'
AUTHORS_PATH = SITE_ROOT / 'public' / 'data' / 'edebiyat' / 'authors.json'

# =====================================================================
# REV21a — ÇOK YÜKSEK (17) + YÜKSEK (17) = 34 yazar
# =====================================================================
KODLAMA = {
    # ---------- ÇOK YÜKSEK ----------
    "Nabi": {
        "ad_cagrisimi": "Nabi → 'na-bi' = öğüt veren bilge",
        "sahne": "Bilge bir baba oğlunun kulağını çeker, sayfalarca öğüt verir; sonra deveye binip iki kutsal beldeyi hac niyetine gezer, dönüşte gördüğü bir düğün alayının şenliğini satır satır anlatır.",
        "cozum": "Oğula öğüt (hikemî/didaktik) → Hayriye · iki kutsal belde hac → Tuhfetü'l-Haremeyn · düğün şenliği → Surname · aşk mesnevisi → Hayrabad. Nabi = ÖĞÜT/hikmet şiirinin öncüsü (17. yy).",
        "tip": "hikaye", "emoji": "📿",
    },
    "Refik Halit Karay": {
        "ad_cagrisimi": "Refik → 'refakat/uzak yoldaş', Karay → kara yollar",
        "sahne": "Muhalif kalemi yüzünden iki kez yurdundan kovulan bir yazar; bir deftere doğduğu kasabanın insanlarını, öbür deftere uzak diyarlardaki özlemi yazar. Eski bir konak beyi yeni düzene ayak uydurmaya çalışır.",
        "cozum": "Yurttan kovulma → Sürgün · doğduğu kasaba insanları → Memleket Hikayeleri · uzak diyar/özlem → Gurbet Hikayeleri · yeni düzene uyan eski bey → Bugünün Saraylısı · doğu/inanç → Yezidin Kızı. İki kez sürgün → gurbet/memleket teması.",
        "tip": "hikaye", "emoji": "🧳",
    },
    "Ahmet Hamdi Tanpınar": {
        "ad_cagrisimi": "Tanpınar → 'tam-ayar pınarı', saat/zaman takıntısı",
        "sahne": "Bütün ülkenin kol saatlerini tek bir dakikaya çekmek için koca bir resmî kurum kuran adam; iç dünyası dinginleşsin ister, yurdun dört bir yanından beş durağı dolaşır, kulağında küflü bir Osmanlı makamı, ama hep perdenin gerisinde kalır.",
        "cozum": "Saatleri tek dakikaya çeken kurum → Saatleri Ayarlama Enstitüsü · iç dinginlik → Huzur · beş durak/şehir → Beş Şehir · eski Osmanlı makamı → Mahur Beste · perde gerisi → Sahnenin Dışındakiler. Zaman + Doğu-Batı medeniyeti teması.",
        "tip": "hikaye", "emoji": "⏰",
    },
    "Âşık Paşa": {
        "ad_cagrisimi": "Âşık Paşa → Anadolu'da garip bir derviş, öğüt + Türkçe sevdası",
        "sahne": "Anadolu'da garip bir derviş; halk Arapça-Farsça okurken 'kendi dilimiz hor görülmesin' diye on binlerce beyitlik bir öğüt kitabı yazar; gurbeti, ölümü, dünyanın geçiciliğini anlatır.",
        "cozum": "Garip derviş + Türkçe savunusu + öğüt → Garib-name (Garipname; 14. yy, Türkçenin değerini savunan didaktik mesnevi). Âşık Paşa = Anadolu'da Türkçe bilincinin erken sesi.",
        "tip": "hikaye", "emoji": "🧎",
    },
    "Baki": {
        "ad_cagrisimi": "Baki → 'baki/ölümsüz', Sultanü'ş-Şuara (şairler sultanı)",
        "sahne": "Saray çevresinde zarif, dünyevi bir şair; koca bir padişah ölünce arkasından görkemli bir ağıt düzer, 'her şey gelip geçer' der ama şöhreti kalıcı olur.",
        "cozum": "Padişah (Kanuni) ölümüne görkemli ağıt → Kanuni Mersiyesi · dinî eser → Mealimü'l-Yakin. Zarif/dünyevi gazel, 'şairler sultanı' (16. yy). Tuzak: Fuzuli ACILI/tasavvufi ↔ Baki ZARİF/dünyevi.",
        "tip": "hikaye", "emoji": "👑",
    },
    "Ahmedi": {
        "ad_cagrisimi": "Ahmedi → büyük cihangirin destancısı (14. yy)",
        "sahne": "14. yüzyıl şairi; dünyayı fetheden efsanevi bir cihangirin maceralarını ve çağın bütün ilmini koca bir mesneviye sığdırır; ayrıca güneş ile yıldız adlı iki sevgilinin aşkını yazar.",
        "cozum": "Dünya fatihi cihangir (İskender) destanı → İskendername (ilk büyük Türkçe İskender mesnevisi, ansiklopedik) · güneş+yıldız aşkı → Cemşid ü Hurşid. Ahmedi = 14. yy mesnevi.",
        "tip": "hikaye", "emoji": "⚔️",
    },
    "Mehmet Akif Ersoy": {
        "ad_cagrisimi": "Mehmet Akif → 'âkif/sebatkâr', İstiklal Marşı şairi",
        "sahne": "Halkın içinden, manzum hikâyelerle yoksul mahalleleri anlatan dindar bir şair; bir caminin kürsüsünden vaaz verir, milletin istiklalini haykırır; bütün şiirlerini tek bir 'safhalar/aşamalar' kitabında toplar.",
        "cozum": "Safhalar/aşamalar (hayat sahneleri) → Safahat (7 kitap, manzum gerçekçilik) · cami kürsüsünden vaaz → Süleymaniye Kürsüsünde. İstiklal Marşı şairi (Safahat'a koymadı). Milli Edebiyat + İslamcı çizgi.",
        "tip": "hikaye", "emoji": "🕌",
    },
    "Nedim": {
        "ad_cagrisimi": "Nedim → 'nedime/eğlence dostu', Lale Devri zevki",
        "sahne": "Lale Devri'nin neşeli şairi; İstanbul'un mesire yerlerini, içkiyi, güzelleri ezgi ezgi anlatır; ağır tasavvufu bırakıp 'mahalleye iner', günlük zevki över.",
        "cozum": "Şarkı nazım biçimini zirveye taşıdı → Şarkıları · toplu şiirleri → Divan-ı Nedim. Mahallileşme + Lale Devri + dünyevi zevk (18. yy). Tuzak: tasavvuf değil, hayatın neşesi.",
        "tip": "hikaye", "emoji": "🌷",
    },
    "Orhan Veli Kanık": {
        "ad_cagrisimi": "Orhan Veli → 'garip veli', ölçü-kafiyeyi çöpe atan üçlünün başı",
        "sahne": "Üç arkadaş ölçüyü, kafiyeyi, süslü mecazı çöpe atar; sokaktaki sıradan insanı, bedava yaşamayı, küçük şeyleri esprili bir dille yazar; 'şiir herkesin' derler.",
        "cozum": "Akımın adı + ilk kitap → Garip (1941; Melih Cevdet + Oktay Rifat ile). Diğerleri: Vazgeçemediğim, Yenisi, Karşı. Ölçüsüz-kafiyesiz serbest, gündelik hayat. Tuzak: I. Yeni = Garip.",
        "tip": "hikaye", "emoji": "🗑️",
    },
    "Şeyh Galip": {
        "ad_cagrisimi": "Şeyh Galip → 'galip gelen aşk', Mevlevi + Hint tarzı (sebk-i hindi)",
        "sahne": "Mevlevi tekkesinin son büyük şairi; 'Güzellik' ile 'Sevgi' adlı iki kahramanın diyar diyar geçtikleri imtihanlarla buluştuğu alegorik bir mesnevi yazar; dili girift, hayalleri uçuk.",
        "cozum": "Güzellik (Hüsn) + Sevgi (Aşk) alegorisi → Hüsn ü Aşk (son büyük mesnevi, sebk-i hindi) · mesnevi şerhi → Şerh-i Cezîre-i Mesnevî. 18. yy Mevlevi. Tuzak: Fuzuli'nin Leyla vü Mecnun'u ile karıştırma.",
        "tip": "hikaye", "emoji": "🌹",
    },
    "Şinasi": {
        "ad_cagrisimi": "Şinasi → 'ışın/öncü', Tanzimat'ın ilkçisi",
        "sahne": "Batı'yı ilk tanıtan öncü; görücü usulü evliliği eleştiren ilk yerli sahne oyununu yazar; ilk özel gazeteyi çıkarıp önsözünde 'halk için' der; bir de atasözlerini derler.",
        "cozum": "İlk yerli tiyatro (görücü usulü eleştirisi) → Şair Evlenmesi · ilk özel gazete önsözü → Tercüman-ı Ahvâl Mukaddimesi · atasözü derlemesi → Durub-ı Emsal-i Osmaniye · şiir seçkisi → Müntehabat-ı Eş'ar. Tanzimat 'ilk'lerinin adamı.",
        "tip": "hikaye", "emoji": "📰",
    },
    "Mithat Cemal Kuntay": {
        "ad_cagrisimi": "Mithat Cemal → üç devir, tek roman",
        "sahne": "Tek büyük romanıyla anılan yazar; Abdülhamit, Meşrutiyet ve Mütareke olmak üzere üç ayrı çağın başkentini, çürüyen bir nesil üzerinden anlatır.",
        "cozum": "Üç çağın İstanbul'u (Abdülhamit/Meşrutiyet/Mütareke) → Üç İstanbul. Mithat Cemal = tek romanla kalıcı.",
        "tip": "hikaye", "emoji": "🏙️",
    },
    "Ziya Gökalp": {
        "ad_cagrisimi": "Ziya Gökalp → 'gök-alp', Türkçülüğün babası · ⭐ 2026 Anma Yılı",
        "sahne": "Milletin fikir babası; 'kültür ayrı, medeniyet ayrı' der; ulaşılmaz bir ülküyü kızıl bir elmaya benzetir; halk masallarını manzum yazar; üç ilkeyi (Türk olmak, Müslüman olmak, çağdaşlaşmak) tek kitapta birleştirir.",
        "cozum": "Türkçülük teorisi → Türkçülüğün Esasları · ülkü = kızıl elma → Kızılelma · üç ilke → Türkleşmek İslamlaşmak Muasırlaşmak · yeni ülkü şiirleri → Yeni Hayat · çocuk/masal manzumeleri → Altın Işık. ⭐ 2026 Ziya Gökalp Anma Yılı (150. doğum). Tuzak: teorisyen Gökalp ≠ hikâyeci Ömer Seyfettin.",
        "tip": "hikaye", "emoji": "🍎",
    },
    "Yahya Kemal Beyatlı": {
        "ad_cagrisimi": "Yahya Kemal → 'kemal/olgun İstanbul aşığı', sağlığında kitap bastırmadı",
        "sahne": "Eski Osmanlı zarafetine ve İstanbul'a vurgun şair; aruzu modern Türkçeyle diriltir; 'ölüm bile güzeldir bu şehirde' der; sağlığında tek şiir kitabı bile bastırmaz.",
        "cozum": "Bizim semamız/kültürümüz → Kendi Gök Kubbemiz · eski şiiri diriltmek → Eski Şiirin Rüzgârıyle · İstanbul denemeleri → Aziz İstanbul. Neoklasik, aruz + saf Türkçe. Tuzak: Ahmet Haşim (imge) ≠ Yahya Kemal (musiki + İstanbul).",
        "tip": "hikaye", "emoji": "🌉",
    },
    "Faruk Nafiz Çamlıbel": {
        "ad_cagrisimi": "Faruk Nafiz → 'far/yol lambası', Anadolu yolcusu · Beş Hececiler",
        "sahne": "İstanbullu bir öğretmen at arabasıyla Anadolu'ya gider; bir kervansarayın duvarlarına kazınmış dizeleri okur; memleket sevgisini, çobanı, pınarı hece vezniyle yazar; 'yabancı ilham değil, kendi toprağımız' der.",
        "cozum": "Kervansaray/han duvarındaki dizeler → Han Duvarları (Anadolu'ya açılan memleketçi şiir) · çoban + pınar → Çoban Çeşmesi · yerli sanat manifestosu → Sanat ('Başka sanat bilmeyiz...'). Beş Hececiler, memleket edebiyatı.",
        "tip": "hikaye", "emoji": "🐎",
    },
    "Fuzuli": {
        "ad_cagrisimi": "Fuzuli → 'fasulye sulu' / 'fuzulî = boşuna seven'",
        "sahne": "Çölde aklını yitirmiş bir âşık, kavuşamadığı sevgili için yanar; susuzluktan suya yalvararak peygambere methiye düzer; bir de devlet kapısına 'bahşişimi vermediler' diye sitem mektubu yazar.",
        "cozum": "Çölde âşık (Mecnun) + sevgili (Leyla) → Leyla vü Mecnun · suya methiye / peygamber sevgisi → Su Kasidesi · maaş sitemi mektubu → Şikayetname · Kerbela mersiyesi → Hadîkatü's-Suedâ · afyon-şarap münazarası → Beng ü Bâde. ACILI/tasavvufi (16. yy). Tuzak: Baki zarif/dünyevi.",
        "tip": "hikaye", "emoji": "💧",
    },
    "Memduh Şevket Esendal": {
        "ad_cagrisimi": "Memduh Şevket → 'mendil', durum (Çehov tarzı) hikâyesi",
        "sahne": "Olaysız, sıradan günleri 'hiçbir şey olmadan' anlatan hikâyeci; bir apartmanda başkente yeni gelen kiracıların küçük dünyasını çizer; bedavacı bir tipi, bir el oyununu konu eder.",
        "cozum": "Apartman + Ankaralı kiracılar → Ayaşlı ve Kiracıları (tek romanı) · bedavacı tip → Otlakçı · gizli el → Mendil Altında · eşkıya → Çakıcının İlk Kurşunu. Maupassant/Çehov tarzı DURUM (kesit) hikâyesi. Tuzak: Ömer Seyfettin OLAY ≠ Esendal DURUM.",
        "tip": "hikaye", "emoji": "🧣",
    },
    # ---------- YÜKSEK ----------
    "Köroğlu": {
        "ad_cagrisimi": "Köroğlu → 'kör baba + at Kırat', dağdaki yiğit",
        "sahne": "Babasının gözüne mil çekilince dağa çıkan yiğit; atına atlayıp zalim beye kafa tutar; mertlik, savaş, kahramanlık coşkusuyla türküler söyler ('Benden selam olsun Bolu Beyi'ne').",
        "cozum": "Kahramanlık/savaş coşkusu türküleri → koçaklamaları · etrafında oluşan destansı anlatı → Köroğlu Halk Hikâyesi. 16. yy âşık. Tuzak: aşk=güzelleme (Karacaoğlan), kahramanlık=koçaklama (Köroğlu/Dadaloğlu).",
        "tip": "hikaye", "emoji": "🐎",
    },
    "Nef'i": {
        "ad_cagrisimi": "Nef'i → 'nefret okları', övgüde ve sövgüde zirve",
        "sahne": "Keskin dilli şair; kasidede göklere çıkarır (abartılı övgü), hicivde yerin dibine sokar; 'kaza okları' adlı zehirli yergilerinden sonra bu dili yüzünden boğdurulur.",
        "cozum": "Zehirli hiciv okları → Siham-ı Kaza ('kaza okları' — bu yüzden idam edildi) · aşk/övgü → Tuhfetü'l-Uşşak. 17. yy: abartılı kaside (fahriye) + hiciv ustası. Tuzak: methiye+fahriye Nef'i; hikemî Nabi.",
        "tip": "hikaye", "emoji": "🏹",
    },
    "Namık Kemal": {
        "ad_cagrisimi": "Namık Kemal → 'vatan + hürriyet şairi', Tanzimat I. dönem",
        "sahne": "'Vatan, hürriyet, millet' diye gürleyen heyecanlı bir Tanzimatçı; bir vatan müdafaası oyunu sahnelenince halk sokağa dökülür (sürgüne yollanır); ilk edebî romanda baştan çıkan bir gencin uyanışını, ilk tarihî romanda kahraman bir Türk'ü yazar.",
        "cozum": "Vatan savunması oyunu → Vatan yahut Silistre (halkı coşturdu, sürgün sebebi) · ilk edebî roman (uyanış) → İntibah · ilk tarihî roman → Cezmi · oyunlar → Gülnihal, Akif Bey. Tanzimat I. dönem (toplum için sanat, vatan-hürriyet).",
        "tip": "hikaye", "emoji": "🇹🇷",
    },
    "Ahmet Haşim": {
        "ad_cagrisimi": "Ahmet Haşim → 'haşmetli akşam', saf şiir/imge",
        "sahne": "Akşamı, kızıl gurubu, durgun gölleri saplantı gibi yazan şair; 'şiir anlaşılmak için değil, hissedilmek içindir' der; bir içki kadehinden gün batımı seyreder; gündelik denemeler ve bir de Almanya gezi notları bırakır.",
        "cozum": "İçki kadehi (gün batımı) → Piyale (içinde 'Merdiven', 'O Belde') · durgun göller/akşam → Göl Saatleri · denemeler → Bize Göre · gezi → Frankfurt Seyahatnamesi. Saf şiir + imge, Fecr-i Âti. Tuzak: Cenap Şahabettin (Servet-i Fünun) ile karıştırma.",
        "tip": "hikaye", "emoji": "🌅",
    },
    "Ahmet Mithat Efendi": {
        "ad_cagrisimi": "Ahmet Mithat → 'hâce-i evvel (ilk hoca)', yazı makinesi · halk için",
        "sahne": "Halkı eğitmek için durmadan yazan 'ilk hoca'; alafranga bir züppe ile çalışkan yerli genci karşılaştırır (Doğu-Batı dersi); macera-deniz romanları ve sayısız küçük hikâye anlatır; 'okur kaçmasın' diye araya girip açıklar.",
        "cozum": "Alafranga züppe (Felatun) ↔ çalışkan yerli (Rakım) → Felâtun Bey ile Râkım Efendi (yanlış Batılılaşma) · hikâye dizisi → Letaif-i Rivayet · deniz/macera → Hasan Mellah. Tanzimat, halkçı/didaktik. Tuzak: züppe tipi sonra Bihruz (Recaizade).",
        "tip": "hikaye", "emoji": "👨‍🏫",
    },
    "Şeyhi": {
        "ad_cagrisimi": "Şeyhi → 'şifacı hekim', eşek hikâyesi",
        "sahne": "Hem hekim hem şair; padişahtan aldığı köyü zorbalar elinden alınca, semiz öküzlere özenip boynuz isterken kulakları kesilen zavallı bir eşeğin hikâyesiyle mizahî/alegorik sitem yazar; bir de hükümdar-güzel aşkını anlatır.",
        "cozum": "Boynuz isterken kulağından olan eşek (mizahî hiciv) → Harname · hükümdar Hüsrev + güzel Şirin aşkı → Hüsrev ü Şirin. 15. yy, ilk büyük mizah/fabl-mesnevi. Tuzak: Harname = Şeyhi (hekim-şair).",
        "tip": "hikaye", "emoji": "🫏",
    },
    "Yakup Kadri Karaosmanoğlu": {
        "ad_cagrisimi": "Yakup Kadri → 'yaban/yabancı aydın', Kadro dergisi · dönem romancısı",
        "sahne": "Her romanında bir devri kesen yazar; köye giden aydının köylüyle uçurumunu, bir konağın üç kuşakta çöküşünü, bir tekkenin yozlaşmasını, Meşrutiyet'in kanlı gecesini, yeni başkentin kuruluş heyecanını anlatır.",
        "cozum": "Köy-aydın uçurumu → Yaban · üç kuşakta çöken konak → Kiralık Konak · yozlaşan Bektaşi tekkesi → Nur Baba · Meşrutiyet/İttihat çatışması → Hüküm Gecesi · yeni başkent → Ankara. Milli Edebiyat → Kadro, 'dönem panoraması' romancısı.",
        "tip": "hikaye", "emoji": "🌾",
    },
    "Recaizade Mahmut Ekrem": {
        "ad_cagrisimi": "Recaizade → 'üstad', fayton züppesi Bihruz · Muallim Naci kavgası",
        "sahne": "Tanzimat II. dönemin 'üstadı'; faytonuyla hava atan, Fransızca özentisi alafranga bir züppenin trajikomik aşkını yazar; 'her güzel şey şiirdir' diyerek eski kafalı bir hocayla kıyasıya tartışır ('Zemzeme'-'Demdeme' atışması).",
        "cozum": "Fayton meraklısı züppe (Bihruz) → Araba Sevdası (ilk realist romanlardan) · yeni şiir bildirisi → Zemzeme (Muallim Naci'nin Demdeme'sine karşı) · edebiyat ders kitabı → Talim-i Edebiyat. Tuzak: Recaizade YENİ/Batı ↔ Muallim Naci ESKİ/Doğu.",
        "tip": "hikaye", "emoji": "🛞",
    },
    "Şeyhülislam Yahya": {
        "ad_cagrisimi": "Şeyhülislam Yahya → din başı ama rind gazel ustası (ironi)",
        "sahne": "Devletin en yüksek din makamında oturan biri; buna rağmen en güzel, en rind (dünyevi, şarap-aşk temalı) gazelleri yazar; 17. yüzyılın usta gazel şairi sayılır.",
        "cozum": "Toplu gazelleri → Divan. Şeyhülislam (din makamı) + rind gazel ustası ironisi (17. yy). Tuzak: makamı din, şiiri dünyevi/aşk.",
        "tip": "hikaye", "emoji": "☪️",
    },
    "Orhan Kemal": {
        "ad_cagrisimi": "Orhan Kemal → 'orhan + emek', Çukurova işçisi · toplumcu gerçekçi",
        "sahne": "Çukurova'ya iş için göçen üç köylünün fabrikada ve tarlada ezilişini yazar; görev sarhoşu bir bekçiyi, çiftlikte ağa düzenini, yoksul mahalle insanlarını anlatır; emeği ve sınıfı konu eder.",
        "cozum": "Çukurova'ya göçen üç işçi → Bereketli Topraklar Üzerinde · görev delisi bekçi → Murtaza · ağa/çiftlik → Hanımın Çiftliği · eskici aile → Eskici ve Oğulları · genç kız → Cemile. Toplumcu gerçekçi (işçi/köylü).",
        "tip": "hikaye", "emoji": "🏭",
    },
    "Necip Fazıl Kısakürek": {
        "ad_cagrisimi": "Necip Fazıl → 'çileli üstad', Büyük Doğu · kaldırımlar şairi",
        "sahne": "Gece kaldırımlarda yürüyen, iç buhran ve metafizik ıstırap çeken 'üstad'; ruhunun ıstırabını haykırır; bir nehre seslenerek milletin derdini anlatır; sahnede kendi trajedisini kuran bir adamı yazar.",
        "cozum": "İç ıstırap/metafizik acı (toplu şiir) → Çile · gece + yalnızlık → Kaldırımlar · Sakarya nehrine sesleniş → Sakarya Türküsü · tiyatro → Bir Adam Yaratmak. Büyük Doğu, mistik/İslamcı çizgi.",
        "tip": "hikaye", "emoji": "🌃",
    },
    "Halide Edip Adıvar": {
        "ad_cagrisimi": "Halide Edip → Kurtuluş Savaşı'nın kadın sesi · güçlü kadın kahramanlar",
        "sahne": "Milli Mücadele'de kürsüden halkı coşturan, cepheye koşan bir kadın yazar; İstanbul'un dar bir mahallesinde Doğu-Batı sentezini, işgale karşı yanan bir gömleği, bir öğretmen kıza atılan iftirayı anlatır; güçlü kadın kahramanlar kurar.",
        "cozum": "İstanbul'un dar mahallesi (Doğu-Batı sentezi) → Sinekli Bakkal (en ünlü) · işgal/Milli Mücadele ateşi → Ateşten Gömlek · öğretmene iftira → Vurun Kahpeye · güçlü kadın → Handan. Milli Edebiyat, kadın kahraman + Kurtuluş Savaşı. Tuzak: Reşat Nuri (Çalıkuşu) ile karıştırma.",
        "tip": "hikaye", "emoji": "🔥",
    },
    "Fakir Baykurt": {
        "ad_cagrisimi": "Fakir Baykurt → fakir köyün öğretmeni · Köy Enstitüsü",
        "sahne": "Köy Enstitüsü çıkışlı öğretmen-yazar; bir Anadolu köyünde, bir ailenin evi ve toprağı için muhtarla, ağa düzeniyle verdiği amansız kavgayı, köy husumetleri (yılanları) üzerinden anlatır.",
        "cozum": "Köydeki ev/toprak kavgası + husumet → Yılanların Öcü (Kemal Tahir önsözüyle ünlü). Köy Enstitüsü kuşağı, toplumcu köy romanı. Tuzak: Mahmut Makal / Talip Apaydın ile aynı damar.",
        "tip": "hikaye", "emoji": "🐍",
    },
    "Mehmet Rauf": {
        "ad_cagrisimi": "Mehmet Rauf → 'rauf/içli', ilk psikolojik roman",
        "sahne": "Servet-i Fünun'un içli romancısı; bir yalıda, evli bir kadına âşık olan kuzenin yasak ve bastırılmış duygularını, sonbaharın hüznüyle iç içe anlatır — Türkçede ilk büyük 'iç çözümleme' romanı.",
        "cozum": "Yalıda yasak aşk + sonbahar hüznü → Eylül (ilk psikolojik roman). Tuzak: Halit Ziya'nın Aşk-ı Memnu'su ile karıştırma — ikisi de Servet-i Fünun + yasak aşk; ama Eylül = Mehmet Rauf.",
        "tip": "hikaye", "emoji": "🍂",
    },
    "Reşat Nuri Güntekin": {
        "ad_cagrisimi": "Reşat Nuri → 'reçel nur', Anadolu öğretmeni Feride",
        "sahne": "İstanbul'dan Anadolu'ya öğretmen olarak giden cıvıl cıvıl, kuş gibi genç bir kadın; bir ailenin yaprak yaprak dökülüp dağılışını, taassuba karşı bir öğretmenin mücadelesini, dudakta başlayıp kalbe inen bir aşkı anlatır.",
        "cozum": "Anadolu'ya giden cıvıl cıvıl öğretmen (kuş) → Çalıkuşu (Feride) · dağılan aile → Yaprak Dökümü · taassuba karşı öğretmen → Yeşil Gece · dudakta başlayan aşk → Dudaktan Kalbe · sertlik/merhamet → Acımak. Anadolu + öğretmen teması. Tuzak: Halide Edib ile karıştırma.",
        "tip": "hikaye", "emoji": "🐦",
    },
    "Sehi Bey": {
        "ad_cagrisimi": "Sehi Bey → 'sekiz cennet', ilk şair tezkiresi",
        "sahne": "Şairlerin hayat ve eserlerini ilk kez derli toplu kaydeden adam; topladığı şair biyografilerini 'sekiz cennet' adlı bir kitapta sekiz bölüme ayırır — Anadolu sahasının ilk şuara tezkiresi.",
        "cozum": "Sekiz cennet / sekiz bölüm şair biyografileri → Heşt Bihişt (Anadolu'da ilk şair tezkiresi, 16. yy). Sehi Bey = ilk tezkireci. Tuzak: tezkire = şair biyografileri sözlüğü.",
        "tip": "hikaye", "emoji": "📚",
    },
    "Süleyman Çelebi": {
        "ad_cagrisimi": "Süleyman Çelebi → mevlit yazarı, peygamberin doğumu",
        "sahne": "Bursa Ulu Cami imamı; Hz. Peygamber'in doğumunu ve miracını coşkulu beyitlerle anlatan, asırlardır kandillerde okunan o meşhur manzumeyi yazar — adı 'kurtuluş vesilesi' demektir.",
        "cozum": "Peygamberin doğumu (mevlit) → Vesîletü'n-Necât (halk arasında 'Mevlid'). 15. yy, türünün ilk ve en ünlüsü. Tuzak: Mevlid = Süleyman Çelebi.",
        "tip": "hikaye", "emoji": "🌙",
    },
    # =====================================================================
    # REV21b — ORTA (30 yazar), öncelikten aza
    # =====================================================================
    "Ahmet Kutsi Tecer": {
        "ad_cagrisimi": "Kutsi → 'köşe kutusu' · Aşık Veysel'i keşfeden",
        "sahne": "Halk kültürünü derleyen şair-öğretmen; Anadolu'yu dolaşıp saz şairlerini (bir köy âşığını) gün yüzüne çıkarır; bir mahalle köşesini sahneye taşıyan oyun ve bir klasik müzik faslı yazar.",
        "cozum": "Mahalle köşesi oyunu → Köşebaşı · klasik müzik faslı → Şehnaz Faslı. Aşık Veysel'i edebiyata kazandıran, halk kültürü derleyicisi (Cumhuriyet).",
        "tip": "hikaye", "emoji": "🎼",
    },
    "Necati Cumalı": {
        "ad_cagrisimi": "Cumalı → 'cuma sıcağı, kurak'",
        "sahne": "Ege kasabasında iki kardeşin su yüzünden kavgası, kavurucu bir mevsimin bunaltısı; taşra kadınının bastırılmış arzusunu anlatan öyküler.",
        "cozum": "Su kavgası / kurak mevsim → Susuz Yaz (Berlin Altın Ayı'lı filme uyarlandı) · taşra kadını → Mine. Cumhuriyet, Ege/taşra gerçekçiliği.",
        "tip": "hikaye", "emoji": "🌵",
    },
    "Tevfik Fikret": {
        "ad_cagrisimi": "Tevfik Fikret → 'fikir + kırık saz' · Servet-i Fünun lideri, Aşiyan",
        "sahne": "Servet-i Fünun'un öfkeli şairi; istibdat İstanbul'unu kara bir pusa gömüp lanetler; oğluna umut bağlayıp 'sen Batı'da adam ol' der; geçmişin zorbalığına isyan eder; çocuklar için de şiir yazar.",
        "cozum": "Kırık saz (umutsuzluk) → Rübab-ı Şikeste · İstanbul'a lanet (pus) → Sis · oğul Haluk → Halûk'un Defteri · geçmiş zorbalığa isyan → Tarih-i Kadim · çocuk şiirleri → Şermin. Servet-i Fünun lideri. Tuzak: ateşli/toplumcu Fikret ↔ sembolist Cenap.",
        "tip": "hikaye", "emoji": "🌫️",
    },
    "Aka Gündüz": {
        "ad_cagrisimi": "Aka Gündüz → 'ağabey gündüz' · popüler Milli Mücadele romancısı",
        "sahne": "Milli Mücadele duygusunu popüler aşk romanlarına döken yazar; Ankara'da bir yıldız-kız, bir sürücünün gizli güncesi, hovarda bir genç kızın hikâyesi.",
        "cozum": "Ankara/yıldız kız → Dikmen Yıldızı · sürücü güncesi → Bir Şoförün Gizli Defteri · hovarda kız → Çapkın Kız · halkın romanı → Onların Romanı. Milli Edebiyat, popüler roman.",
        "tip": "hikaye", "emoji": "🌟",
    },
    "Cenap Şahabettin": {
        "ad_cagrisimi": "Cenap Şahabettin → 'şahane şita (kış)' · sembolist doktor",
        "sahne": "Servet-i Fünun'un sembolist şairi (aslında doktor); karların yağışını musiki gibi tasvir eder; ağır, sanatlı bir dille hac yolculuğunu yazar; 'sanat şahsî ve muhteremdir' der.",
        "cozum": "Karların musikisi (kış nağmeleri) → Elhan-ı Şita · hac gezi notları → Hac Yolunda · şiirleri → Tâmâtî. Servet-i Fünun sembolizm. Tuzak: Ahmet Haşim ile karıştırma — Cenap SERVET-İ FÜNUN, Haşim FECR-İ ÂTİ.",
        "tip": "hikaye", "emoji": "❄️",
    },
    "Hüseyin Cahit Yalçın": {
        "ad_cagrisimi": "Hüseyin Cahit → 'cahit/kavgacı' · SF'yi kapattıran kalem",
        "sahne": "Servet-i Fünun'un kavgacı kalemi; çevirip yayımladığı bir makale ('Edebiyat ve Hukuk') yüzünden dergi kapatılır; yıllar sonra o edebiyat kavgalarını hatıra olarak yazar.",
        "cozum": "Edebiyat kavgalarının hatıraları → Edebî Hatıralarım. Servet-i Fünun'u kapattıran 'Edebiyat ve Hukuk' makalesinin sahibi; eleştirmen/polemikçi.",
        "tip": "hikaye", "emoji": "🖋️",
    },
    "Necati Bey": {
        "ad_cagrisimi": "Necati Bey → 'neşeli, atasözlü' · 15. yy mahallileşme",
        "sahne": "15. yüzyıl şairi; şiirine halk deyimlerini ve atasözlerini ustaca yerleştirir (sade, yerli söyleyiş); 'yüz yapraklı gül' adlı bir derlemesi vardır.",
        "cozum": "Toplu şiirleri → Necati Divanı · 'yüz yapraklı gül' → Gül-i Sad-berg. 15. yy, şiirde atasözü/deyim ustası; mahallileşmenin erken örneği.",
        "tip": "hikaye", "emoji": "🌹",
    },
    "Ahmet Muhip Dıranas": {
        "ad_cagrisimi": "Dıranas → 'duran nas' · saf şiir",
        "sahne": "Saf şiirin usta ismi; mahallenin güzel ablasına çocukça hayranlığı, geçmişin unutuluşunu (İspanyolca bir başlıkla) ve karaltıları lirik bir dille yazar.",
        "cozum": "Mahallenin güzel ablası → Fahriye Abla · unutuş (İspanyolca) → Olvido · karaltılar → Gölgeler. Cumhuriyet saf şiir (Necip Fazıl/Tanpınar çizgisi).",
        "tip": "hikaye", "emoji": "🌆",
    },
    "Bağdatlı Ruhi": {
        "ad_cagrisimi": "Bağdatlı Ruhi → 'ruh + Bağdat' · toplumsal eleştirel bentler",
        "sahne": "16. yüzyıl Bağdat şairi; devrin haksızlığını, ikiyüzlülüğünü bentler hâlinde eleştiren ünlü bir manzume yazar (Ziya Paşa ona nazire döşeyecektir).",
        "cozum": "Toplumsal eleştirel bentli manzume → Terkib-i Bend (Ziya Paşa'nın naziresiyle ünlü) · toplu şiirleri → Divan. 16. yy, sosyal hiciv.",
        "tip": "hikaye", "emoji": "🪶",
    },
    "Edip Cansever": {
        "ad_cagrisimi": "Edip Cansever → 'can + sever' · İkinci Yeni, eşya/masa şiiri",
        "sahne": "İkinci Yeni'nin imgeci şairi; bir masayı, bir karanfili ağırlıklarıyla şiire sokar; insanın trajedilerini uzun, dramatik şiirlerde anlatır ('Masa da masaymış ha').",
        "cozum": "Ağırlığıyla karanfil → Yerçekimli Karanfil · insanın trajedileri → Tragedyalar. İkinci Yeni (lidersiz 6'lı). Tuzak: Turgut Uyar/Cemal Süreya ile aynı grup.",
        "tip": "hikaye", "emoji": "🌸",
    },
    "Turgut Uyar": {
        "ad_cagrisimi": "Turgut Uyar → 'uyarı, kasvet' · İkinci Yeni",
        "sahne": "İkinci Yeni'nin şairi; modern kentte bunalan, huzursuz bireyin kasvetli/nemli dünyasını yazar; eski klasik biçimleri (bir 'divan') modern, ironik içerikle yeniden kurar.",
        "cozum": "Nemli/kasvetli kent → Tütünler Islak · modern-ironik klasik biçim → Divan (Turgut Uyar'ın). İkinci Yeni. Tuzak: Edip Cansever/Cemal Süreya ile aynı grup.",
        "tip": "hikaye", "emoji": "🚬",
    },
    "Ziya Osman Saba": {
        "ad_cagrisimi": "Ziya Osman Saba → 'sabah · saba makamı' · Yedi Meşaleci",
        "sahne": "Yedi Meşale'nin en hassas şairi; çocukluğa, eski güzel günlere, küçük mutluluklara ve ölüme dair içli şiirler yazar; bir avlu çeşmesi ve kanat çırpan kuşlar imgesiyle anılır.",
        "cozum": "Çeşme (sebil) + güvercinler → Sebil ve Güvercinler · geçmiş zaman özlemi → Geçen Zaman. Yedi Meşaleciler (1928).",
        "tip": "hikaye", "emoji": "🕊️",
    },
    "Şemsettin Sami": {
        "ad_cagrisimi": "Şemsettin Sami → 'şems/güneş sözlükçü' · ilk roman + ilk sözlük",
        "sahne": "İlk Türk romanını yazan dilci; iki gencin trajik aşkını anlatır; ardından Türkçenin ilk büyük sözlüğünü ve bir ansiklopedi/coğrafya sözlüğünü hazırlar.",
        "cozum": "İlk Türk romanı (iki gencin aşkı) → Taaşşuk-ı Talat ve Fitnat · ilk büyük Türkçe sözlük → Kamus-ı Türki · ansiklopedik sözlük → Kamus-ı Alâm. Tanzimat, dilci.",
        "tip": "hikaye", "emoji": "📖",
    },
    "Orhan Seyfi Orhon": {
        "ad_cagrisimi": "Orhan Seyfi → 'seyf/kılıç' · Beş Hececi",
        "sahne": "Beş Hececiler'den; hece vezniyle sade, lirik şiirler yazar; bir peri kızıyla çobanın masalsı manzum hikâyesini ve fırtınalı kar tablolarını anlatır.",
        "cozum": "Peri kızı + çoban masalı → Peri Kızı ile Çoban Hikayesi · fırtına/kar → Fırtına ve Kar. Beş Hececiler (hece + sade). Tuzak: Faruk Nafiz/Yusuf Ziya ile aynı beşli.",
        "tip": "hikaye", "emoji": "🌨️",
    },
    "Ömer Seyfettin": {
        "ad_cagrisimi": "Ömer Seyfettin → 'ömrü kısa hikâyeci' · Yeni Lisan, OLAY hikâyesi",
        "sahne": "Genç yaşta ölen, sade Türkçenin (Yeni Lisan) öncüsü hikâyeci; tarihten ve çocukluk anılarından çarpıcı sonlu olay hikâyeleri yazar: bir komitacının patlayıcısı, gururlu bir vezirin incili kaftanı, okul dayağı, bir at tarağı, namus borcu.",
        "cozum": "Komitacının patlayıcısı → Bomba · gururlu vezirin kaftanı → Pembe İncili Kaftan · okul dayağı → Falaka · at tarağı → Kaşağı · namus borcu → Diyet. Milli Edebiyat, Yeni Lisan, OLAY hikâyesi (Maupassant). Tuzak: Esendal DURUM ≠ Ömer Seyfettin OLAY; teorisyen Gökalp ≠ hikâyeci Ö. Seyfettin.",
        "tip": "hikaye", "emoji": "🖋️",
    },
    "Haldun Taner": {
        "ad_cagrisimi": "Haldun Taner → epik (Brecht) tiyatro + kabare",
        "sahne": "Türk epik tiyatrosunun ustası; gecekondu kabadayısının destanını, gözünü kapayıp vazifesini savan ikiyüzlü memuru, bir eşeğin gölgesi yüzünden çıkan davayı sahneye taşır; usta bir hikâyeci de.",
        "cozum": "Gecekondu kabadayısı destanı → Keşanlı Ali Destanı · ikiyüzlü memur → Gözlerimi Kaparım Vazifemi Yaparım · eşeğin gölgesi davası → Eşeğin Gölgesi · diğer: Sersem Kocanın Kurnaz Karısı, On İkiye Bir Var. Epik/kabare tiyatro + hikâye (Cumhuriyet).",
        "tip": "hikaye", "emoji": "🎭",
    },
    "Halit Fahri Ozansoy": {
        "ad_cagrisimi": "Halit Fahri → 'fahri/şeref' · Beş Hececi, 'Aruza Veda'",
        "sahne": "Beş Hececiler'den; aruzu bırakıp heceye geçişi 'eski kalıba veda' şiiriyle ilan eder; savaş/cenk coşkusunu, uğursuz bir gece kuşunu (manzum oyun) ve içe dönük dizeleri yazar.",
        "cozum": "Cenk/savaş coşkusu → Cenk Duyguları · uğursuz gece kuşu (manzum oyun) → Baykuş · içe dönüş → Sulara Doğru. Beş Hececiler; 'Aruza Veda' şiiriyle ünlü.",
        "tip": "hikaye", "emoji": "🦉",
    },
    "Taşlıcalı Yahya": {
        "ad_cagrisimi": "Taşlıcalı Yahya → asker-şair, mersiyeci (16. yy)",
        "sahne": "16. yüzyıl asker-şair; haksızca boğdurulan bir şehzadenin (Mustafa) ardından cesur bir mersiye yazar; sultan ile dilenci aşkını, bir sır hazinesini, bir ışık bahçesini ve peygamber kıssasını mesnevilere döker.",
        "cozum": "Sultan + dilenci aşkı → Şah u Geda · sır hazinesi → Gencîne-i Râz · ışık bahçesi → Gülşen-i Envâr · peygamber kıssası → Yusuf u Züleyha · diğer: Kitab-ı Usul. 16. yy; Şehzade Mustafa Mersiyesi'yle ünlü (ÖSYM'de sık çeldirici).",
        "tip": "hikaye", "emoji": "⚔️",
    },
    "Yusuf Ziya Ortaç": {
        "ad_cagrisimi": "Yusuf Ziya → 'ziya/ışık' · Beş Hececi + Akbaba mizah",
        "sahne": "Beş Hececiler'den; akıncı coşkusunu hece vezniyle yazar; sonra mizaha yönelip ünlü bir mizah dergisi (Akbaba) çıkarır.",
        "cozum": "Akıncı/cenk coşkusu → Akından Akına. Beş Hececiler + Akbaba mizah dergisi sahibi. Tuzak: Faruk Nafiz/Orhan Seyfi ile aynı beşli.",
        "tip": "hikaye", "emoji": "🪶",
    },
    "Asaf Halet Çelebi": {
        "ad_cagrisimi": "Asaf Halet → 'acayip harfler' · sıradışı/mistik",
        "sahne": "Bambaşka, mistik bir şair; şiir kitaplarına tek bir Arap harfi ya da iki harfin birleşimini ad verir; Hint, Mısır ve tasavvuf imgeleriyle dolu egzotik dizeler yazar.",
        "cozum": "İki harf (lâm-elif) → Lamelif · tek harf → He. Cumhuriyet, sıradışı/mistik-egzotik şiir. Tuzak: hiçbir gruba tam girmez, kendine özgü.",
        "tip": "hikaye", "emoji": "🕉️",
    },
    "Edip Ahmet Yükneki": {
        "ad_cagrisimi": "Edip Ahmet → edep/ahlak öğreten kör şair (Geçiş dönemi)",
        "sahne": "Doğuştan kör, 12. yüzyıl geçiş dönemi şairi; bilgiyi, cömertliği, doğruluğu öven; 'hakikatlerin eşiği' anlamına gelen didaktik bir öğüt kitabı yazar (aruz; dörtlük + beyit).",
        "cozum": "Hakikatlerin eşiği → Atabetü'l Hakayık (Geçiş dönemi, didaktik/ahlaki). Tuzak: Kutadgu Bilig (Yusuf Has Hacib) ile karıştırma — o 'siyasetname', bu 'ahlak öğüdü'.",
        "tip": "hikaye", "emoji": "📿",
    },
    "Füruzan": {
        "ad_cagrisimi": "Füruzan → 'firuze' · yoksul/kadın hikâyeleri",
        "sahne": "Yoksulların, taşradan göçenlerin ve kadınların dünyasını anlatan hikâyeci; yatılı okulda burslu okuyan yoksul bir kız çocuğunun yoksunluğunu, kuşatılmış hayatları yazar.",
        "cozum": "Yatılı okulda burslu yoksul kız → Parasız Yatılı · kuşatılmış hayatlar → Kuşatma · diğer: Benim Sinemalarım, Gül Mevsimidir, Gecenin Öteki Yüzü. Cumhuriyet, toplumcu, kadın/yoksul gerçekçiliği.",
        "tip": "hikaye", "emoji": "🎒",
    },
    "Rıfat Ilgaz": {
        "ad_cagrisimi": "Rıfat Ilgaz → 'Ilgaz dağı + haylaz sınıf'",
        "sahne": "Toplumcu ama mizahçı yazar; tembel, haylaz, kopya ustası bir lise sınıfının güldürürken düşündüren maceralarını yazar (filme/dizilere uyarlandı).",
        "cozum": "Haylaz lise sınıfı → Hababam Sınıfı. Cumhuriyet, toplumcu + mizah.",
        "tip": "hikaye", "emoji": "🏫",
    },
    "Sait Faik Abasıyanık": {
        "ad_cagrisimi": "Sait Faik → 'sahil + faik' · Burgazada, DURUM hikâyesi",
        "sahne": "Adada, deniz kıyısında, balıkçılar ve sıradan insanlar arasında dolaşan içli hikâyeci; olaysız, şiirsel kesitler yazar; bir işçi ailesinin sabah çayı demliğini, toplumdan kopuk 'gereksiz' bir adamı anlatır.",
        "cozum": "Sabah çayı demliği (işçi ailesi) → Semaver · toplumdan kopuk adam → Lüzumsuz Adam · diğer: Sarnıç, Şahmerdan, Mahalle Kahvesi. Cumhuriyet, DURUM (kesit) hikâyesi, insan sevgisi (Sait Faik Hikâye Armağanı). Tuzak: Ömer Seyfettin OLAY ≠ Sait Faik DURUM.",
        "tip": "hikaye", "emoji": "☕",
    },
    "Turan Oflazoğlu": {
        "ad_cagrisimi": "Turan Oflazoğlu → tarihî tiyatro · padişah trajedileri",
        "sahne": "Osmanlı tarihinden trajediler kuran oyun yazarı; içkiyle ve öfkeyle boğuşan otoriter bir padişahı, bir de yeniçeriye kurban giden genç bir hükümdarı sahneye taşır.",
        "cozum": "Otoriter/öfkeli padişah → IV. Murat · yeniçeriye kurban genç hükümdar → Genç Osman. Cumhuriyet, tarihsel trajedi.",
        "tip": "hikaye", "emoji": "🎭",
    },
    "Yunus Emre": {
        "ad_cagrisimi": "Yunus Emre → tasavvuf/ilahi babası · sade Türkçe",
        "sahne": "13-14. yüzyıl Anadolu'sunun gönül şairi; 'sevelim sevilelim' diyen ilahileriyle halkın diline yerleşir; bir de öğüt/nasihat mesnevisi yazar; tasavvufu en sade Türkçeyle anlatır.",
        "cozum": "İlahileri/şiirleri → Divan · öğüt mesnevisi → Risaletü'n-Nushiyye. Tekke/tasavvuf, sade Türkçe, ilahi. Tuzak: Yunus DERVİŞ/sevgi; Kaygusuz şathiye/mizah.",
        "tip": "hikaye", "emoji": "🕊️",
    },
    "Abdülhak Hamit Tarhan": {
        "ad_cagrisimi": "Abdülhak Hamit → 'azametli' · Şair-i Azam (Tanzimat II)",
        "sahne": "Tanzimat II. dönemin 'en büyük şair'i sayılan kuralsız romantik; eşinin ölümü üzerine metafizik bir feryat/ağıt yazar; kırı şehre yeğleyen şiirler ve tarihî kahraman oyunları (bir komutan, bir hükümdar) kaleme alır.",
        "cozum": "Eş ölümüne metafizik feryat → Makber · kır/doğa övgüsü → Sahra · şehir → Belde · tarihî oyunlar → Tarık, Eşber. Tanzimat II, 'Şair-i Azam', romantizm + kuralsızlık. Tuzak: Recaizade 'üstad', Hamit 'azam'.",
        "tip": "hikaye", "emoji": "⚰️",
    },
    "Neşati": {
        "ad_cagrisimi": "Neşati → 'neşe + şita (kış)' · 17. yy sebk-i hindi",
        "sahne": "17. yüzyıl Mevlevi şairi; girift, ince hayalli (Hint tarzı) gazeller yazar; karlı kış manzarasını anlatan ünlü bir kasidesiyle ('gitdün ammâ...') anılır.",
        "cozum": "Kış kasidesi → Şitaiyye · toplu şiirleri → Divan. 17. yy, sebk-i hindi (Hint tarzı), Mevlevi. Tuzak: Nef'i/Nabi ile aynı yüzyıl; ama Neşati girift/ince hayal.",
        "tip": "hikaye", "emoji": "❄️",
    },
    "Ahmet Hikmet Müftüoğlu": {
        "ad_cagrisimi": "Ahmet Hikmet → 'hikmet + çağlayan' · Milli Ed. Türkçü hikâye",
        "sahne": "Milli Edebiyat'ın Türkçü hikâyecisi; coşkun, milli duygulu hikâyeler (çağlayan gibi taşan) yazar; Orta Asya Türklüğüne özlem duyan bir romanı (bir hanımın adıyla) bırakır.",
        "cozum": "Coşkun milli hikâyeler → Çağlayanlar · Türkçü roman → Gönül Hanım. Milli Edebiyat, Türkçülük.",
        "tip": "hikaye", "emoji": "🌊",
    },
    "Peyami Safa": {
        "ad_cagrisimi": "Peyami Safa → psikolojik roman, Doğu-Batı (Server Bedi)",
        "sahne": "İç dünyayı kazan psikolojik romancı; bir hastane koğuşunda hasta bir gencin ızdırabını; iki semt üzerinden Doğu-Batı/alaturka-alafranga çatışmasını; bunalımdan maneviyata kaçışı anlatır.",
        "cozum": "Hastane koğuşu (hasta genç) → 9. Hariciye Koğuşu · iki semt = Doğu-Batı → Fatih Harbiye · maneviyata kaçış → Matmazel Noraliya'nın Koltuğu · diğer: Yalnızız. Cumhuriyet, psikolojik roman + Doğu-Batı. (Server Bedi takma adıyla popüler romanlar.)",
        "tip": "hikaye", "emoji": "🏥",
    },
}


# ---------------------------------------------------------------------
def _norm(s):
    s = unicodedata.normalize('NFD', s or '')
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return (s.lower().replace('ı', 'i').replace('ş', 's').replace('ç', 'c')
            .replace('ğ', 'g').replace('ö', 'o').replace('ü', 'u'))


def main():
    # Inline KODLAMA + opsiyonel data/kodlama_extra_*.json dosyalarını birleştir
    # (REV21c gibi toplu üretimler ayrı JSON'dan gelir).
    merged = dict(KODLAMA)
    extra_n = 0
    for ef in sorted((DATA_ROOT / 'data').glob('kodlama_extra_*.json')):
        try:
            ed = json.loads(ef.read_text(encoding='utf-8'))
            for name, k in ed.items():
                if name not in merged:
                    merged[name] = k
                    extra_n += 1
        except Exception as e:
            print(f"⚠ {ef.name} okunamadı: {e}")
    if extra_n:
        print(f"  + {extra_n} ek kodlama (kodlama_extra_*.json)")

    # Spoiler check: sahne yazar adının token'larını (>=4 harf) içermemeli.
    authors = {}
    if AUTHORS_PATH.exists():
        authors = {a['name']: a for a in json.loads(AUTHORS_PATH.read_text(encoding='utf-8'))}
    warn = 0
    for name, k in merged.items():
        sahne_n = _norm(k['sahne'])
        # yazar adı token kontrolü
        for tok in name.split():
            if len(tok) >= 4 and _norm(tok) in sahne_n:
                print(f"⚠ SPOILER (ad): '{name}' → sahnede '{tok}' geçiyor")
                warn += 1
        # ilk eser kontrolü (kodlama-eser kartı spoiler'ı; generic eserler kart üretmez → atla)
        GENERIC = {'Divan', 'Şiirleri', 'Şiirler', 'Şarkıları', 'Nefesler', 'Halk Hikayesi'}
        diger = (authors.get(name, {}).get('diger_eserler') or '')
        works = [w.strip() for w in diger.split(',')
                 if w.strip() and w.split(' (')[0].strip() not in GENERIC]
        for w in works[:1]:
            core = w.split(' (')[0].strip()
            if len(core) >= 5 and _norm(core) in sahne_n:
                print(f"⚠ SPOILER (eser): '{name}' → sahnede ilk eser '{core}' geçiyor (kodlama-eser kartı atlanacak)")
                warn += 1
        # zorunlu alanlar
        for f in ('ad_cagrisimi', 'sahne', 'cozum', 'tip', 'emoji'):
            if not k.get(f):
                print(f"⚠ EKSİK ALAN: '{name}' → {f}")
                warn += 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"✓ {len(merged)} yazar kodlaması → {OUT}")
    print(f"  Spoiler/eksik uyarısı: {warn}")


if __name__ == '__main__':
    main()
