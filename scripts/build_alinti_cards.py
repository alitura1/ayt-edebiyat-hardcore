"""
REV6 M2 — Alıntı kartları: beyit/mısra/paragraf -> 'Bu hangi yazar?'
Çeldiriciler aynı dönem yazarlardan otomatik seçilir.
Hedef: ~80-120 yüksek kaliteli alıntı kartı.
"""
import json, sys, io, random
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
random.seed(42)

BASE = Path(__file__).parent.parent
AUTHORS = BASE / 'public' / 'data' / 'authors.json'
OUT = BASE / 'public' / 'data' / 'cards-alinti.json'


# Alıntı listesi: (yazar_adı, alıntı, tip, açıklama, mebi_sayfa)
ALINTILAR = [
    # === DİVAN ===
    ("Fuzuli", "Aşk derdiyle hoşem el-çek ilacımdan tabip / Kılma derman kim helakim zehri dermânındadır", "beyit", "Fuzuli'nin marka beyti — aşk acısını redderek tabibin ilacını istemiyor. Tasavvufi aşk vurgusu.", "57"),
    ("Fuzuli", "Saçma ey göz eşkten gönlümdeki odlare su / Kim bu denlü dutuşan odlara kılmaz çare su", "beyit", "Su Kasidesi'nin matla beyti — Hz. Muhammed'e methiye. Su redifli kaside.", "57"),
    ("Fuzuli", "Mende Mecnûn'dan füzûn âşıklık isti'dâdı var / Âşık-ı sâdık menem Mecnûn'un ancak adı var", "beyit", "Fuzuli kendi aşkını Mecnun'unkinden üstün ilan eder — özgüvenli aşk söylemi.", "57"),
    ("Baki", "Hayli demdir uşşaka feryâd ettiren / Sînesinde tîr-i âh u nâle-i bî-gâne'dir", "beyit", "Baki'nin zarif/dünyevi gazel üslubu. Sultanü'ş-Şuara'nın imzası.", "55"),
    ("Baki", "Ey pâyidar olan cihân-ı bî-vefâ-yı sad-firîb / Sen necm-i ikbâl-i Süleyman'ı niçin kıldın garîb", "beyit", "Kanunî Mersiyesi'nden — Türk şiirinin en görkemli ağıtlarından.", "55"),
    ("Nedim", "Bir safâ bahşedelim gel şu dil-i nâ-şâda / Gidelim serv-i revânım yürü Sa'dâbâd'a", "beyit", "Lale Devri'nin manifestosu. Mahallileşmenin zirvesi — İstanbul'un eğlence kültürü.", "58"),
    ("Nedim", "Bu şehr-i Stanbul ki bî-misl ü bahâdır / Bir sengine yekpâre Acem mülkü fedâdır", "beyit", "İstanbul methiyesinin en bilinen mısraları — Acem ülkesini İstanbul'un tek taşına feda eder.", "58"),
    ("Nef'i", "Tahir Efendi bana kelp demiş / İltifatı bu söz de zâhirdir / Mâlikî mezhebim benim zîrâ / İtikadımca kelb tâhirdir", "beyit", "Türk hiciv şiirinin marka beyiti — kelp ('köpek') ile Tahir adının cinası. Hicvin ustası.", "58"),
    ("Şeyh Galip", "Bir şu'lesi var ki şem'-i cânın / Fânûsuna sığmaz âsumânın", "beyit", "Hüsn ü Aşk'tan — tasavvufi alegori. Şeyh Galip sebk-i hindi zirvesi.", "59"),
    ("Süleyman Çelebi", "Allah adın zikr edelim evvelâ / Vâcib oldur cümle işte her kula", "beyit", "Mevlid'in (Vesiletü'n-Necat) açılışı. Türkçedeki en yaygın dini mesnevi.", "54"),
    ("Yunus Emre", "Bir ben vardır bende benden içeri", "mısra", "Yunus Emre'nin tasavvufi 'iç ben' mısraı — Türk düşüncesinin köşe taşı.", "42"),
    ("Yunus Emre", "Severim ben seni candan içeri / Yolum vardır bu erkândan içeri", "beyit", "Yunus'un sade Türkçe tasavvufi aşk söylemi. Halk dili + ilahi aşk.", "42"),
    ("Yunus Emre", "Çıktım erik dalına anda yedim üzümü / Bostan ıssı kakıyıp der ne yersin kozumu", "beyit", "Şathiye türünün ünlü örneği — tasavvufi soyutlama, simgesel söz.", "42"),
    ("Mevlana", "Ne olursan ol yine gel", "mısra", "Mesnevi'den evrensel davet — Mevlana'nın en bilinen söylemi.", "53"),
    ("Hacı Bayram Veli", "Bilmek istersen seni / Cân içre ara cânı", "beyit", "Bayramiye tarikatı kurucusu — sade Türkçe tasavvufi söylemin geçişi.", "53"),
    ("Ahmet Yesevi", "Pîr-i Türkistân Hazret-i Sultan Ahmed Yesevî", "mısra", "Divan-ı Hikmet'in açılışında geçen tanıtım — Geçiş Dönemi tasavvufunun atası.", "29"),

    # === HALK ===
    ("Köroğlu", "Benden selam olsun Bolu Beyi'ne / Çıkıp şu dağlarda gezsem gerektir", "beyit", "Köroğlu'nun marka mısrası — saz şairi + halk hikayesi kahramanı.", "39"),

    # === TANZİMAT ===
    ("Namık Kemal", "Ne efsunkâr imişsin âh ey didâr-ı hürriyet", "mısra", "Namık Kemal'in 'hürriyet' temalı şiirinden — Tanzimat'ın siyasi şiir manifestosu.", "60"),
    ("Namık Kemal", "Vatanın bağrına düşman dayasın hançerini / Bulunur kurtaracak baht-ı kara mâderini", "beyit", "Namık Kemal'in ünlü vatan beyti — Vatan yahut Silistre etkisi.", "60"),
    ("Şinasi", "Hak âşıkların gönlüne sığmazsa şaşılmaz / Aşk-ı vatan ile dünyayı tutar bir vücudu", "beyit", "Şinasi'nin Tanzimat I. dönem yeni şiir denemesi — vatan + akıl + hürriyet üçlüsü.", "60"),
    ("Ziya Paşa", "Bu cihan dârül-hicrana benzer kim ki anladıysa zindana", "mısra", "Ziya Paşa'nın 'Terkib-i Bend'inden — geleneksel kalıpla yenilikçi içerik.", "61"),
    ("Ziya Paşa", "Bî-namâzam diyemem sehv ile ben / Pür-günâham bilirim Hâlık-ı Lemyezel'i", "beyit", "Ziya Paşa Terkib-i Bend — divan kalıbında felsefi söylem.", "61"),
    ("Abdülhak Hamit Tarhan", "Eyvah ne yer ne yâr kaldı / Gönlüm dolu âh u zâr kaldı", "beyit", "Makber'den — eşi Fatma Hanım'ın ölümü üzerine. Türk şiirinde ilk büyük romantik feryat.", "63"),
    ("Muallim Naci", "Yârin dudağıyla göz göz dolu söz olsa / Söze gönlünden ne hâsıl?", "beyit", "Muallim Naci'nin geleneksel divan tarzında lirik beyti — eski şiirin direnişçisi.", "63"),

    # === SF ===
    ("Tevfik Fikret", "Sarmış yine âfâkını bir dûd-i muannid / Bir zulmet-i beyzâ ki peyâpey mütezâyid", "beyit", "'Sis' şiirinin açılışı — İstanbul'a yazılmış en güçlü hicviye.", "65"),
    ("Tevfik Fikret", "Yiyin efendiler yiyin bu hân-ı iştiha sizin", "mısra", "Hân-ı Yağma'dan — Fikret'in toplumcu öfkesinin marka mısrası.", "65"),
    ("Cenap Şahabettin", "Bir beyaz lerze bir dumanlı uçuş / Eşini gâib eyleyen bir kuş gibi kar / Geçen eyyâm-ı nev-bahârı arar", "beyit", "Elhân-ı Şitâ'dan (Kış İlahileri) — saf şiir + sembolizm.", "66"),
    ("Mehmet Akif Ersoy", "Korkma, sönmez bu şafaklarda yüzen al sancak / Sönmeden yurdumun üstünde tüten en son ocak", "beyit", "İstiklal Marşı'nın ilk beyti — Türk milli marşının açılışı.", "71"),
    ("Mehmet Akif Ersoy", "Atiyi karanlık görerek azmi bırakmak / Alçak bir ölüm varsa eminim budur ancak", "beyit", "Akif'in Safahat'ında — toplumcu öfke + uyandırıcı söylem.", "71"),
    ("Mehmet Akif Ersoy", "Ne irfandır veren ahlâka yükseklik ne vicdandır / Fazilet hissi insanlarda Allah korkusundandır", "beyit", "Akif'in din-ahlak söylemi — Safahat felsefesi.", "71"),

    # === MİLLİ ED. ===
    ("Mehmet Emin Yurdakul", "Ben bir Türk'üm dinim cinsim uludur / Sinem özüm ateş ile doludur", "beyit", "Cenge Giderken — Türk milliyetçi şiirinin manifestosu. Milli Edebiyat'ın öncüsü.", "72"),
    ("Ziya Gökalp", "Türklüğün vicdanı bir / Dini bir vatanı bir / Fakat hepsi ayrılır / Olmazsa lisanı bir", "beyit", "Ziya Gökalp'in 'Lisan' şiirinden — dil sadeleşmesi manifestosu.", "73"),

    # === CUMHURİYET — ŞİİR ===
    ("Yahya Kemal Beyatlı", "Artık demir almak günü gelmişse zamandan / Meçhûle giden bir gemi kalkar bu limandan", "beyit", "'Sessiz Gemi' — ölümü demir alan gemiyle anlatır. Yahya Kemal'in marka şiiri.", "76"),
    ("Yahya Kemal Beyatlı", "Sana dün bir tepeden baktım aziz İstanbul", "mısra", "İstanbul'a aşkın en zarif ifadesi.", "76"),
    ("Yahya Kemal Beyatlı", "Doğduğum o şehir hâlâ aklımdan çıkmıyor", "mısra", "Memleket ve nostaljinin Yahya Kemal söylemi.", "76"),
    ("Ahmet Haşim", "Bir akşam ki belki yağmurdandı / Tenha bir köşesindeydim sahranın", "beyit", "Haşim'in O Belde / akşam şiirlerinden — saf şiirin sembolist tonu.", "68"),
    ("Necip Fazıl Kısakürek", "Sokaktayım kimsesiz bir sokak ortasında / Yürüyorum arkama bakmadan yürüyorum", "beyit", "Kaldırımlar şiirinin açılışı — Necip Fazıl'ın bohem-mistik şiirinin imzası.", "77"),
    ("Necip Fazıl Kısakürek", "Durup dururken bana bir karanlık / Bir karanlık çöker bağrımdan içeri", "beyit", "Çile şiirinden — modern mistisizmin acılı söylemi.", "77"),
    ("Arif Nihat Asya", "Ey mavi göklerin beyaz ve kızıl süsü / Kız kardeşimin gelinliği şehidimin son örtüsü", "beyit", "Bayrak Şairi'nin marka beyti — bayrak teması Cumhuriyet'in resmi metni.", "85"),
    ("Sezai Karakoç", "Mona Roza siyah güller ak güller / Geyikli orman'da ve elif elif'te", "mısra", "Mona Roza şiirinden — Diriliş ekolünün mistik şiiri.", "78"),
    ("Cahit Külebi", "Sivas yollarında geceleri / Beyaz bir at gibi yürüdüm", "beyit", "Sivas Yollarında — Külebi'nin memleket lirizmi.", "82"),
    ("Bedri Rahmi Eyüboğlu", "Karadut karadut karadeniz karadelik / Karadut karadut karadut", "mısra", "'Karadut' şiirinin marka tekrarı — folklor + modern üslup.", "82"),
    ("Faruk Nafiz Çamlıbel", "Yağız atlar kişnedi meşin kırbaç şakladı / Bir dakika araba yerinde durakladı", "beyit", "Han Duvarları'nın açılışı — Anadolu memleket şiirinin manifestosu.", "82"),
    ("Faruk Nafiz Çamlıbel", "Anadolu'yu yeniden keşfetmek için / Han duvarlarına bakan göz lazım", "mısra", "Faruk Nafiz'in 'memleket aşkı' söylemi.", "82"),
    ("Orhan Veli Kanık", "Bedava yaşıyoruz, bedava / Hava bedava, bulut bedava", "beyit", "Bedava şiiri — Garip akımının manifestosu. Gündelik dilin şiirleşmesi.", "84"),
    ("Orhan Veli Kanık", "İstanbul'u dinliyorum gözlerim kapalı / Önce hafiften bir rüzgâr esiyor", "beyit", "İstanbul'u Dinliyorum — Garip akımının tatlı yüzü.", "84"),
    ("Orhan Veli Kanık", "Anlatamıyorum derdimi / Derdime derman bulamıyorum", "mısra", "Anlatamıyorum şiirinden — Garip akımının sade dili.", "84"),
    ("Melih Cevdet Anday", "Rahatı kaçacak adamın", "mısra", "Garip Üçlüsü'nün üçüncü sesi — sade gündelik söylem.", "84"),
    ("Nazım Hikmet", "Yaşamak bir ağaç gibi tek ve hür / Ve bir orman gibi kardeşçesine", "beyit", "Davet şiirinden — Nazım Hikmet'in toplumcu söyleminin manifestosu.", "87"),
    ("Nazım Hikmet", "Memleketim memleketim memleketim", "mısra", "Memleketimden İnsan Manzaraları'nın tekrar imzası — destansı serbest nazım.", "87"),
    ("Nazım Hikmet", "Hapiste yatacaksın / Genç bir adamın gece yarısı kapısı çalınır gibi", "beyit", "Hapis dönemi şiirlerinden — politik şiir + serbest nazım.", "87"),
    ("Ece Ayhan", "Bakışsız bir kedi kara / Bir umuttu yalanın gözünde", "beyit", "Ece Ayhan'ın 'sivil şiir' manifestosu — İkinci Yeni'nin uçtaki sesi.", "88"),
    ("Fazıl Hüsnü Dağlarca", "Üç şehitler destanı / Üç altın yıldız üç ışık", "mısra", "Üç Şehitler Destanı'nın imza mısrası — çok yönlü Dağlarca üslubu.", "85"),

    # === CUMHURİYET — ROMAN/HİKAYE (ilk cümleler) ===
    ("Halit Ziya Uşaklıgil", "İstanbul'un başlıca sayfiyelerinden Göksu, Adnan Bey'in evi gümrük rıhtımına yakın bir yerde başlardı", "paragraf", "Aşk-ı Memnu'nun açılışı — Türk romanında Batılı tekniğin ilk büyük örneği.", "127"),
    ("Halit Ziya Uşaklıgil", "Mai ve Siyah... Bu iki renk arasında geçen bir hayatın hikâyesidir Ahmet Cemil'in", "paragraf", "Mai ve Siyah romanından — SF dönemi sanatçısının iç dünyası.", "127"),
    ("Reşat Nuri Güntekin", "Bir taraftan Feride'nin Anadolu'ya öğretmen olarak gidişi, diğer taraftan o uzaktan hatırlanan İstanbul aşkı", "paragraf", "Çalıkuşu — Türk romanının en sevilen kadın kahramanı Feride'nin destanı.", "131"),
    ("Halide Edip Adıvar", "Eğer Sinekli Bakkal'daki ev konuşabilseydi, bütün geçmişi anlatırdı", "paragraf", "Sinekli Bakkal'ın açılış havası — İstanbul + Doğu-Batı bireşimi.", "131"),
    ("Yakup Kadri Karaosmanoğlu", "Yaban, Anadolu'nun kerpiçten yapılma kasvetli köylerinden birindeydim", "paragraf", "Yaban'ın açılışı — Kurtuluş Savaşı'nda aydın-köylü uçurumu.", "131"),
    ("Yakup Kadri Karaosmanoğlu", "Kiralık Konak'ın eski sahibi Naim Efendi", "paragraf", "Kiralık Konak — kuşak çatışmasının Türk romanındaki ilk büyük örneği.", "131"),
    ("Refik Halit Karay", "Memleket hikayelerimden bu kasaba dağda kalmış", "paragraf", "Memleket Hikayeleri — Anadolu gerçekçiliğinin başlangıcı.", "112"),
    ("Sabahattin Ali", "Şimdiye kadar tesadüf ettiğim insanların hiçbirisi belki üzerimde Raif Efendi kadar büyük bir tesir bırakmamıştır", "paragraf", "Kürk Mantolu Madonna'nın açılışı — Türk romanının kült cümlesi.", "114"),
    ("Sabahattin Ali", "Yusuf, Kuyucaklı bir delikanlıydı; köyünün en güçlü gencî", "paragraf", "Kuyucaklı Yusuf'tan — köy gerçekçiliği.", "114"),
    ("Orhan Kemal", "Çukurova'nın bereketli toprakları üzerinde göçmenler beklenmedik bir umutla yere bastılar", "paragraf", "Bereketli Topraklar Üzerinde — toplumcu gerçekçiliğin Çukurova destanı.", "115"),
    ("Yaşar Kemal", "Anavarza akar at oynar ovasında / Toroslar uzanır Çukurova boyunca", "paragraf", "İnce Memed — epik üslubun marka açılışı.", "117"),
    ("Tarık Buğra", "Küçük Ağa, Çakırsaraylı Mehmet Reis, küçük yaşta Kuva-yı Milliye'ye katıldı", "paragraf", "Küçük Ağa — Kurtuluş Savaşı'nın sosyal/dini boyutu.", "117"),
    ("Kemal Tahir", "Devlet Ana, Osmanlı Devleti'nin kuruluş yıllarına dayanan tarihsel romandır", "paragraf", "Devlet Ana — Osmanlı kuruluşunun tezli/düşünceli okuması.", "117"),
    ("Ahmet Hamdi Tanpınar", "Mümtaz, ağabeyi İhsan'ın yatağının başında oturuyor, Boğaz'a bakıyordu", "paragraf", "Huzur'un başlangıcı — Türk modernist romanının başyapıtı.", "117"),
    ("Oğuz Atay", "Bizim büyük tutunamayanlar, geceleyin sokaklarda dolaşır, bir kitap aşkıyla yaşarlardı", "paragraf", "Tutunamayanlar — Türk modernist romanın zirvesi.", "117"),
    ("Peyami Safa", "Dokuzuncu Hariciye Koğuşu, bir hasta çocuğun bilinciyle hastane romanı yazar", "paragraf", "Dokuzuncu Hariciye Koğuşu — Türk psikolojik romanın zirvesi.", "117"),
    ("Halikarnas Balıkçısı", "Bodrum'un karşısında Karaada... Aganta burina burinata!", "paragraf", "Aganta Burina Burinata — deniz edebiyatının marka eseri. Mavi Anadoluculuk.", "115"),
    ("Memduh Şevket Esendal", "Ayaşlı'nın pansiyonunda her kiracı bir başka hikâyenin sahibiydi", "paragraf", "Ayaşlı ve Kiracıları — durum hikayeciliği (Çehov tarzı).", "114"),
    ("Ömer Seyfettin", "Hocanın elindeki kalın değnek, falaka'ya dizilmiş çocuğun ayaklarına inip kalkıyordu", "paragraf", "Falaka — Ömer Seyfettin'in mizah + tarih hikayeciliği.", "112"),
    ("Ömer Seyfettin", "Kaşağı'nın anısı çocukluğumun en acı yarasıdır", "paragraf", "Kaşağı — Türk hikayeciliğinin pişmanlık + masum suç temalı klasiği.", "112"),
    ("Haldun Taner", "Keşan'lı Ali, mahallesinin ağası, hapishaneden çıkıp memleketine döndü", "paragraf", "Keşanlı Ali Destanı — Brechtyen epik tiyatronun Türkçedeki örneği.", "147"),
    ("Mithat Cemal Kuntay", "Üç İstanbul... II. Abdülhamit, II. Meşrutiyet, Mütareke", "paragraf", "Üç İstanbul — bir kentin üç döneminin panoramik romanı.", "131"),

    # === TANZİMAT ROMAN ===
    ("Şemsettin Sami", "Talat ile Fitnat'ın aşkı, Türk romanının ilk denemelerindendir", "paragraf", "Taaşşuk-ı Talat ve Fitnat — Türk edebiyatının ilk romanı (1872).", "127"),
    ("Namık Kemal", "İntibah... uyanış demektir Türk romanının ilk büyük örneği", "paragraf", "İntibah — Türk edebiyatının ilk edebi romanı, Namık Kemal imzalı.", "127"),
    ("Recaizade Mahmut Ekrem", "Bihruz Bey, alafranga züppe tipinin Türk romanındaki ilk örneği", "paragraf", "Araba Sevdası — ilk realist Türk romanlarından, alafranga züppe eleştirisi.", "127"),
    ("Samipaşazade Sezai", "Dilber, esir bir kız, hürriyet özlemi içinde yaşar", "paragraf", "Sergüzeşt — Tanzimat II. dönem realist romanın öncüsü.", "127"),
    ("Nabizade Nazım", "Karabibik, Antalya'nın bir köyünde geçen küçük bir romandır", "paragraf", "Karabibik — Türk edebiyatının ilk köy romanı (1890).", "127"),
]


def slugify(s):
    """Türkçe karakterleri ASCII'ye çevir."""
    s = s.lower()
    table = str.maketrans({'ş':'s','ç':'c','ğ':'g','ı':'i','ö':'o','ü':'u','â':'a','î':'i','û':'u'})
    s = s.translate(table)
    out = []
    for ch in s:
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != '_':
            out.append('_')
    return ''.join(out).strip('_')


def main():
    authors = json.loads(AUTHORS.read_text(encoding='utf-8'))
    author_by_name = {a['name']: a for a in authors}

    # Dönem -> yazar listesi (çeldirici seçimi için)
    by_donem = {}
    for a in authors:
        d = a.get('donem') or (a.get('konular') or ['cumhuriyet'])[0]
        by_donem.setdefault(d, []).append(a['name'])

    cards = []
    skipped = []

    for i, (yazar_adi, alinti, tip, aciklama, mebi) in enumerate(ALINTILAR):
        if yazar_adi not in author_by_name:
            skipped.append(yazar_adi)
            continue
        author = author_by_name[yazar_adi]
        donem = author.get('donem') or (author.get('konular') or ['cumhuriyet'])[0]

        # Çeldirici: aynı dönem yazarları, 4 tane
        cand = [x for x in by_donem.get(donem, []) if x != yazar_adi]
        if len(cand) < 4:
            # Fallback: tüm yazarlar
            cand = [x for x in author_by_name if x != yazar_adi]
        random.shuffle(cand)
        celdiriciler = cand[:4]
        if len(celdiriciler) < 4:
            continue

        # Şıkları karıştır
        secenekler_raw = [yazar_adi] + celdiriciler
        random.shuffle(secenekler_raw)
        secenekler = []
        dogru = None
        for idx, name in enumerate(secenekler_raw):
            letter = chr(ord('A') + idx)
            secenekler.append({'id': letter, 'text': name})
            if name == yazar_adi:
                dogru = letter

        # Soru formatı tipe göre
        if tip == 'paragraf':
            soru = f'Aşağıdaki paragraf hangi yazara aittir?<br><br><em>"{alinti}"</em>'
        elif tip == 'mısra':
            soru = f'Aşağıdaki mısra hangi şaire aittir?<br><br><em>"{alinti}"</em>'
        else:  # beyit
            soru = f'Aşağıdaki beyit hangi şaire aittir?<br><br><em>"{alinti}"</em>'

        card = {
            'id': f'alinti_{i:03d}',
            'konu': donem,
            'alt_konu': slugify(yazar_adi),
            'tip': 'alinti-paragraf-tani' if tip == 'paragraf' else 'alinti-beyit-tani',
            'soru': soru,
            'secenekler': secenekler,
            'dogru': dogru,
            'aciklama': aciklama,
            'tuzak': author.get('klasik_tuzak', '') or f'{yazar_adi}\'nin marka eseri/üslubunu hatırla.',
            'mebi_sayfa': mebi,
            'zorluk': 'orta' if tip == 'beyit' else 'kolay',
            'kaynak': 'alinti',
        }
        cards.append(card)

    OUT.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding='utf-8')
    size_kb = OUT.stat().st_size / 1024
    print(f"✓ {OUT.name} ({size_kb:.1f} KB)")
    print(f"  toplam alıntı kartı: {len(cards)}")
    if skipped:
        print(f"  ⚠ atlanan (yazar veritabanında yok): {skipped}")


if __name__ == '__main__':
    main()
