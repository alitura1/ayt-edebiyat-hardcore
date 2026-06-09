# -*- coding: utf-8 -*-
"""
REV19 — M2 — Eser İçerik/Özet Veritabanı (tip c soruları için)

Kullanıcının istediği soru tipi:
  "Yazarı vermeden eserin İÇERİĞİNİ verip BAŞKA bir eserini sorabilir"

Bu, eserin TEMA/İÇERİK özetini gerektirir — yazar adı ve eserin tam adı GEÇMEZ
(spoiler önleme). İçerikler MEBİ özet PDF (ayt-tde.pdf) + çıkmış ÖSYM
paragraflarının dayandığı kanonik edebiyat bilgisine göre kürasyonla yazılmıştır.

Output: data/work_content.json
  { eser_adi: {"yazar":..., "donem":..., "icerik":"...(ad geçmez)", "kaynak":"mebi+cikmis"} }

Not: Yalnızca İÇERİĞİ tarif edilebilir (roman/hikaye/mesnevi/oyun) eserler.
Soyut divanlar için içerik sorusu üretilmez.
"""
import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent.parent          # Edebiyat Analiz/
SITE = ROOT / 'edebiyat-site' / 'public' / 'data' / 'edebiyat'
OUT = ROOT / 'data' / 'work_content.json'

# Kürasyon: (eser, yazar, donem, içerik). İçerik = yazar/eser adı GEÇMEYEN tema özeti.
WORK_CONTENT = [
    # ---- Servet-i Fünun / Tanzimat geçişi roman ----
    ("Aşk-ı Memnu", "Halit Ziya Uşaklıgil", "servet_i_funun_fecr_i_ati",
     "Boğaz'daki bir yalıda, genç bir kadının kocasının yeğeniyle yaşadığı yasak aşkı ve bu ilişkinin yıkıcı sonucunu işleyen, edebiyatımızın ilk büyük psikolojik romanı."),
    ("Mai ve Siyah", "Halit Ziya Uşaklıgil", "servet_i_funun_fecr_i_ati",
     "Şair olma hayalleri kuran, mavi düşleri siyah hüsranlara dönüşen idealist bir gencin trajedisi üzerinden Servet-i Fünun kuşağının ruh hâlini yansıtan roman."),
    ("Kırık Hayatlar", "Halit Ziya Uşaklıgil", "servet_i_funun_fecr_i_ati",
     "Bir doktorun aile hayatındaki sadakatsizlik ve çözülmeyi, dönemin İstanbul'unun gündelik gerçekçiliğiyle anlatan roman."),
    ("Eylül", "Mehmet Rauf", "servet_i_funun_fecr_i_ati",
     "İki yakın arkadaş ile birinin eşi arasında gelişen, eylemden çok iç dünyaya ve duygulara odaklanan, ilk psikolojik aşk romanı sayılan eser."),

    # ---- Milli Edebiyat / Cumhuriyet roman ----
    ("Çalıkuşu", "Reşat Nuri Güntekin", "milli_edebiyat",
     "İstanbul'da büyüyen genç bir kızın, nişanlısının ihanetiyle Anadolu'ya öğretmen olarak gidişini ve orada yaşadığı zorlukları anlatan roman."),
    ("Yeşil Gece", "Reşat Nuri Güntekin", "milli_edebiyat",
     "Bir Anadolu kasabasında idealist bir öğretmenin softalık ve cehaletle mücadelesini ele alan roman."),
    ("Yaban", "Yakup Kadri Karaosmanoğlu", "milli_edebiyat",
     "Birinci Dünya Savaşı gazisi bir aydının, işgal yıllarında sığındığı Orta Anadolu köyünde köylüyle yaşadığı derin yabancılaşmayı anlatan roman."),
    ("Kiralık Konak", "Yakup Kadri Karaosmanoğlu", "milli_edebiyat",
     "Bir konak çevresinde üç kuşağı izleyerek Tanzimat'tan Birinci Dünya Savaşı'na uzanan Batılılaşma ve değer çözülmesini işleyen roman."),
    ("Nur Baba", "Yakup Kadri Karaosmanoğlu", "milli_edebiyat",
     "Bir Bektaşi tekkesindeki yozlaşmayı ve bir şeyhin çevresindeki kadınlarla ilişkilerini eleştirel biçimde anlatan roman."),
    ("Sinekli Bakkal", "Halide Edip Adıvar", "milli_edebiyat",
     "İstanbul'un eski bir mahallesinde Doğu-Batı sentezini, halk kültürünü ve bir kadının yükselişini anlatan roman."),
    ("Ateşten Gömlek", "Halide Edip Adıvar", "milli_edebiyat",
     "Milli Mücadele günlerinde cepheye adanmışlığı, bireysel aşklarla vatan sevgisinin çatışmasını anlatan ilk Kurtuluş Savaşı romanlarından."),
    ("Handan", "Halide Edip Adıvar", "milli_edebiyat",
     "Aydın bir kadının iç dünyasını, aşklarını ve düşünsel çatışmalarını mektuplar aracılığıyla anlatan psikolojik roman."),

    # ---- Milli Ed. hikaye ----
    ("Memleket Hikayeleri", "Refik Halit Karay", "milli_edebiyat",
     "Anadolu insanını ve taşra hayatını gözleme dayalı gerçekçilikle anlatan, Anadolu'yu hikâyeye taşıyan ilk önemli kitap."),
    ("Gurbet Hikayeleri", "Refik Halit Karay", "milli_edebiyat",
     "Yazarın sürgün yıllarında, yurdundan uzak düşmüş insanların özlemini ve gurbet acısını işleyen hikâyeleri."),
    ("Bomba", "Ömer Seyfettin", "milli_edebiyat",
     "Balkanlar'da bir köyde yaşanan trajediyi sade bir dille anlatan, milli duyarlık taşıyan hikâye."),
    ("Kaşağı", "Ömer Seyfettin", "milli_edebiyat",
     "Bir çocuğun kardeşine yaptığı haksızlığın vicdan azabına dönüşmesini anlatan, çocukluk anısına dayalı hikâye."),
    ("Forsa", "Ömer Seyfettin", "milli_edebiyat",
     "Yıllarca esir kalan yaşlı bir Türk denizcisinin vatan özlemini ve kavuşma anını işleyen duygulu hikâye."),

    # ---- Cumhuriyet roman / hikaye ----
    ("Kürk Mantolu Madonna", "Sabahattin Ali", "cumhuriyet",
     "Almanya'da bir ressam kadına duyulan içe kapanık aşkın, yıllar sonra bir defter aracılığıyla anlatıldığı roman."),
    ("Kuyucaklı Yusuf", "Sabahattin Ali", "cumhuriyet",
     "Küçük bir kasabaya evlatlık alınan bir gencin, çevresindeki baskı ve adaletsizlikle çatışmasını anlatan toplumcu gerçekçi roman."),
    ("İçimizdeki Şeytan", "Sabahattin Ali", "cumhuriyet",
     "Cumhuriyet dönemi aydınının iradesizliğini ve bir aşk ilişkisi üzerinden ahlaki çözülmesini sorgulayan roman."),
    ("Dokuzuncu Hariciye Koğuşu", "Peyami Safa", "cumhuriyet",
     "Hasta bir gencin hastane koğuşundaki acılarını ve bir kıza duyduğu umutsuz sevgiyi iç çözümlemeyle anlatan otobiyografik roman."),
    ("Fatih-Harbiye", "Peyami Safa", "cumhuriyet",
     "İki semt üzerinden Doğu-Batı, alaturka-alafranga karşıtlığını bir genç kızın ikilemiyle anlatan roman."),
    ("Huzur", "Ahmet Hamdi Tanpınar", "cumhuriyet",
     "İstanbul, musiki ve aşk ekseninde, bir aydının iç dünyasını ve Doğu-Batı arasında huzur arayışını işleyen roman."),
    ("Saatleri Ayarlama Enstitüsü", "Ahmet Hamdi Tanpınar", "cumhuriyet",
     "Toplumun modernleşme çabasını, anlamsız bir kurum etrafında mizah ve ironiyle eleştiren roman."),
    ("Tutunamayanlar", "Oğuz Atay", "cumhuriyet",
     "Bir intiharın ardından, topluma tutunamayan bir aydının izini süren, modernist anlatım teknikleriyle örülü roman."),
    ("İnce Memed", "Yaşar Kemal", "cumhuriyet",
     "Çukurova'da ağa zulmüne başkaldıran bir köylünün eşkıyaya dönüşüp efsaneleşmesini destansı bir dille anlatan roman."),
    ("Devlet Ana", "Kemal Tahir", "cumhuriyet",
     "Osmanlı Devleti'nin kuruluş yıllarını halkın ve uç beylerinin gözünden anlatan tarihi roman."),
    ("Bereketli Topraklar Üzerinde", "Orhan Kemal", "cumhuriyet",
     "Çukurova'ya çalışmaya giden üç köylünün ağır işçilik koşullarında sömürülmesini anlatan toplumcu gerçekçi roman."),
    ("Küçük Ağa", "Tarık Buğra", "cumhuriyet",
     "Milli Mücadele yıllarında bir kasaba ve bir din adamının değişimini, kurtuluş savaşına bakışıyla anlatan roman."),
    ("Esir Şehrin İnsanları", "Kemal Tahir", "cumhuriyet",
     "İşgal altındaki İstanbul'da aydınların direniş ve teslimiyet arasındaki sınavını anlatan roman."),

    # ---- Tanzimat roman/tiyatro ----
    ("Araba Sevdası", "Recaizade Mahmut Ekrem", "tanzimat",
     "Alafrangalık özentisi bir gencin, bir kadına duyduğu gülünç tutkuyla düştüğü trajikomik durumu anlatan, ilk realist Türk romanlarından."),
    ("İntibah", "Namık Kemal", "tanzimat",
     "Saf bir gencin kötü bir kadının tuzağına düşüp mahvoluşunu anlatan, ilk edebî Türk romanı sayılan eser."),
    ("Cezmi", "Namık Kemal", "tanzimat",
     "Bir Osmanlı askerinin kahramanlığı üzerinden vatan ve hürriyet temalarını işleyen, ilk tarihi Türk romanı."),
    ("Felatun Bey ile Rakım Efendi", "Ahmet Mithat Efendi", "tanzimat",
     "Yanlış Batılılaşmış savurgan bir tip ile Doğu-Batı sentezini doğru kuran çalışkan bir tipi karşılaştıran roman."),
    ("Taaşşuk-ı Talat ve Fitnat", "Şemsettin Sami", "tanzimat",
     "Görücü usulü evliliği eleştiren, iki gencin trajik aşkını anlatan ilk yerli Türk romanı."),
    ("Sergüzeşt", "Samipaşazade Sezai", "tanzimat",
     "Köle olarak satılan bir kızın çektiği acılar üzerinden esaret kurumunu eleştiren roman."),
    ("Karabibik", "Nabizade Nazım", "tanzimat",
     "Bir Antalya köyünde köylü hayatını gerçekçi biçimde ele alan, ilk köy romanı sayılan eser."),
    ("Şair Evlenmesi", "Şinasi", "tanzimat",
     "Görücü usulü evlilik ve toplumsal yanlışları mizahla eleştiren, ilk yerli tiyatro eseri."),

    # ---- Divan mesnevi/eser (içerik tarif edilebilir) ----
    ("Leyla vü Mecnun", "Fuzuli", "divan_edebiyati",
     "Birbirine kavuşamayan iki âşığın hikâyesini ilahi aşka yükselten, tasavvufi boyutuyla bilinen mesnevi."),
    ("Hüsn ü Aşk", "Şeyh Galip", "divan_edebiyati",
     "Güzellik ile Aşk'ın alegorik yolculuğunu sembollerle anlatan, Sebk-i Hindî üslubunun zirvesi sayılan tasavvufi mesnevi."),
    ("Harname", "Şeyhi", "divan_edebiyati",
     "Boynuz istemeye giderken kulağından olan bir eşeğin başına gelenleri mizahi alegoriyle anlatan mesnevi."),
    ("Hayriyye", "Nabi", "divan_edebiyati",
     "Şairin oğluna ahlak, hayat ve toplum üzerine öğütler verdiği, hikemî (didaktik) tarzın örneği eser."),
    ("Hayrabad", "Nabi", "divan_edebiyati",
     "Didaktik ve hikemî üslupla işlenen, dönemin değerlerini öğütleyen mesnevi."),

    # ---- Servet-i Fünun / Milli şiir (içerik/temasıyla) ----
    ("Sis", "Tevfik Fikret", "servet_i_funun_fecr_i_ati",
     "İstanbul'u baskı döneminin sembolü olarak ele alıp ağır bir dille eleştiren, sosyal içerikli manzume."),
    ("Haluk'un Defteri", "Tevfik Fikret", "servet_i_funun_fecr_i_ati",
     "Şairin oğluna seslendiği, gelecek ve ilerleme inancını işleyen toplumcu şiirler bütünü."),
    ("Safahat", "Mehmet Akif Ersoy", "milli_edebiyat",
     "Toplumun dertlerini, yoksulluğu ve inanç değerlerini gerçekçi tablolarla anlatan, manzum hikâyeler içeren büyük şiir kitabı."),
    ("Cenge Giderken", "Mehmet Emin Yurdakul", "milli_edebiyat",
     "Sade dil ve hece ölçüsüyle yazılmış, milli duyguları öne çıkaran ilk örneklerden olan şiir."),

    # ---- Geçiş dönemi ----
    ("Risaletü'n-Nushiye", "Yunus Emre", "islamiyet_oncesi_gecis",
     "İnsan-ı kâmil olma yolunu, akıl ve nefis mücadelesini didaktik biçimde anlatan, mesneviyle başlayıp nesirle süren tasavvufi eser."),

    # ---- Ziya Gökalp (2026 anma yılı) ----
    ("Kızılelma", "Ziya Gökalp", "milli_edebiyat",
     "Türk milliyetçiliğinin ülküsünü destansı ve sembolik bir dille işleyen şiir kitabı."),
    ("Altın Işık", "Ziya Gökalp", "milli_edebiyat",
     "Halk masalları ve efsanelerinden yararlanılarak çocuklara milli değerleri aktarmayı amaçlayan eser."),
    ("Türkçülüğün Esasları", "Ziya Gökalp", "milli_edebiyat",
     "Türkçülük düşüncesini; hars-medeniyet ayrımı, dilde sadeleşme ve milli kültür ekseninde sistemleştiren fikir kitabı."),

    # ===================================================================
    # REV19c-2 — Yüksek öncelikli (ÇOK YÜKSEK / YÜKSEK) ama içeriksiz yazarlar
    # Kullanıcı: "sadece Ziya Gökalp değil, sürekli sorulan yüksek önemli
    # yazarlara da aynısını yap". Üslup/içerik temelli, spoiler-free.
    # ===================================================================
    # ---- Divan ----
    ("Garibname", "Âşık Paşa", "divan_edebiyati",
     "Farsçanın itibarlı olduğu bir çağda tamamı Türkçe kaleme alınan, on iki bini aşkın beyitten oluşan; Anadolu Türkçesine sahip çıkmayı savunan didaktik mesnevi."),
    ("Kanuni Mersiyesi", "Baki", "divan_edebiyati",
     "On altıncı yüzyılda, görkemli dönemin zarafetini ve dünyevi güzelliği kusursuz bir ahenkle işleyen; 'şairler sultanı' sayılan bir gazel ustasının üslubu."),
    ("İskendername", "Ahmedi", "divan_edebiyati",
     "Büyük İskender'in efsaneleşmiş seferlerini, dönemin tıp ve astronomi bilgileriyle birlikte anlatan; on dördüncü yüzyılın en hacimli Türkçe mesnevilerinden."),
    ("Divan-ı Nedim", "Nedim", "divan_edebiyati",
     "Bir eğlence çağının neşesini, şehrin gündelik hayatını ve aşkı zarif, içten ve yerli bir söyleyişle işleyen; divan şiirine canlılık getiren on sekizinci yüzyıl şairinin tarzı."),
    ("Siham-ı Kaza", "Nef'i", "divan_edebiyati",
     "Keskin diliyle devrin ileri gelenlerini yeren hicivlerin toplandığı; bu cesareti sonunda şairin canına mal olan on yedinci yüzyıl eseri."),
    ("Şeyhülislam Divanı", "Şeyhülislam Yahya", "divan_edebiyati",
     "On yedinci yüzyılda yüksek bir ilmiye makamı taşırken gazelleriyle de tanınan; rahat, zarif ve içten söyleyişli bir divan şairinin tarzı."),
    ("Heşt Bihişt", "Sehi Bey", "divan_edebiyati",
     "Anadolu sahasının ilk şair biyografileri derlemesi olan; dönemin şairlerini sekiz bölüm hâlinde tanıtan eser."),
    ("Vesîletü'n-Necât", "Süleyman Çelebi", "divan_edebiyati",
     "Hz. Muhammed'in doğumunu, hayatını ve faziletlerini anlatan; yüzyıllarca dinî törenlerde okunagelen ünlü manzum eser."),

    # ---- Servet-i Fünun / Fecr-i Âti ----
    ("Piyale", "Ahmet Haşim", "servet_i_funun_fecr_i_ati",
     "Akşamı, gurbeti ve hayalî bir 'belde'yi; anlamdan çok müziğe ve imgeye dayanan saf şiir anlayışıyla işleyen Fecr-i Âti şairinin kitabı."),

    # ---- Cumhuriyet şiir ----
    ("Kendi Gök Kubbemiz", "Yahya Kemal Beyatlı", "cumhuriyet",
     "Eski İstanbul'u, Osmanlı medeniyetini ve musikiyi; geçmiş şiirin sesini modern bir duyarlıkla birleştirerek işleyen büyük şairin kitabı."),
    ("Han Duvarları", "Faruk Nafiz Çamlıbel", "cumhuriyet",
     "Heceyle yazılan şiirlerde Anadolu'yu, memleket sevgisini ve halkı işleyen; Beş Hececiler'in en tanınmış isminin imzası."),
    ("Garip", "Orhan Veli Kanık", "cumhuriyet",
     "Şiirden ölçü, kafiye ve süslü söyleyişi atıp gündelik hayatı ve sıradan insanı yalın bir dille anlatan; bir akımın öncüsü olan şairin kitabı."),
    ("Çile", "Necip Fazıl Kısakürek", "cumhuriyet",
     "Korku, ürperti ve metafizik arayışı yoğun bir iç sesle işleyen; inanç-merkezli bir çizgide şiir ve tiyatro veren sanatçının kitabı."),
    ("Safahat", "Mehmet Akif Ersoy", "milli_edebiyat",
     "Toplumun dertlerini, yoksulluğu ve inanç değerlerini gerçekçi sokak tablolarıyla; manzum hikâyeler biçiminde anlatan büyük şiir kitabı."),

    # ---- Cumhuriyet roman/hikaye ----
    ("Üç İstanbul", "Mithat Cemal Kuntay", "cumhuriyet",
     "Abdülhamit, Meşrutiyet ve Mütareke dönemlerinin İstanbul'unu; çıkarcı bir neslin yükseliş ve çöküşü üzerinden anlatan büyük tarihî-toplumsal roman."),
    ("Ayaşlı ve Kiracıları", "Memduh Şevket Esendal", "cumhuriyet",
     "Bir Ankara apartmanındaki kiracıların hayatından kesitlerle erken Cumhuriyet toplumunu; olaydan çok 'durum'a odaklanan dingin bir anlatımla veren roman."),

    # ---- Halk edebiyatı ----
    ("Köroğlu Destanı", "Köroğlu", "halk_edebiyati",
     "Babasının gözlerine kıyılan bir yiğidin, bir beyden öç almak için dağa çıkıp halkın kahramanı oluşunu anlatan; coşkun koçaklamalarıyla ünlü halk hikâyesi/destanı."),

    # REV19e — MEBİ-only yüksek değerli yazarlar (zengin tip için)
    ("Semaver", "Sait Faik Abasıyanık", "cumhuriyet",
     "Büyük olaylar yerine sıradan insanların küçük anlarını, İstanbul'u ve emekçileri şiirsel bir dille anlatan; 'durum hikâyesi'nin örneği öykü kitabı."),
    ("Benim Adım Kırmızı", "Orhan Pamuk", "cumhuriyet",
     "Bir nakkaşın öldürülmesi etrafında, Doğu-Batı resim anlayışını ve kimliği farklı anlatıcıların ağzından kuran postmodern tarihî roman."),
    ("Anayurt Oteli", "Yusuf Atılgan", "cumhuriyet",
     "Taşra bir otelin kâtibinin, bir kadını bekleyişi etrafında giderek içine kapanışını ve yalnızlığını işleyen psikolojik roman."),
    ("Yılanların Öcü", "Fakir Baykurt", "cumhuriyet",
     "Bir Anadolu köyünde toprak, muhtar ve haksızlıkla mücadele eden köylülerin direnişini gerçekçi biçimde anlatan köy romanı."),
    ("Parasız Yatılı", "Füruzan", "cumhuriyet",
     "Yoksul kadınların, çocukların ve kenar mahalle insanlarının hayatından kesitleri duyarlı bir dille anlatan, ödüllü öykü kitabı."),
    ("Uzun Hikaye", "Mustafa Kutlu", "cumhuriyet",
     "Bir baba-oğulun kasaba kasaba dolaşan hayatını, sade ve tasavvufi bir duyarlıkla anlatan uzun öykü."),
    ("Aylak Adam", "Yusuf Atılgan", "cumhuriyet",
     "Topluma ve düzene yabancılaşmış, gerçek aşkı arayan başıboş bir adamın iç dünyasını izleyen modern roman."),
]


def slugify_tr(s):
    tr = str.maketrans('şŞçÇğĞıİöÖüÜâÂîÎûÛ', 'sScCgGiIoOuUaAiIuU')
    s = (s or '').translate(tr).lower()
    out = []
    for ch in s:
        if ch.isalnum():
            out.append(ch)
        elif ch in ' -_':
            out.append('-')
    slug = ''.join(out)
    while '--' in slug:
        slug = slug.replace('--', '-')
    return slug.strip('-')


def main():
    data = {}
    for eser, yazar, donem, icerik in WORK_CONTENT:
        data[eser] = {
            'yazar': yazar,
            'yazarSlug': slugify_tr(yazar),
            'donem': donem,
            'slug': slugify_tr(eser),
            'icerik': icerik,
            'kaynak': 'mebi+cikmis',
        }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'✓ work_content.json yazıldı: {len(data)} eser → {OUT}')
    # Yazar başına eser sayısı (tip c için ≥2 olan yazarlar)
    from collections import Counter
    c = Counter(v['yazar'] for v in data.values())
    coklu = [a for a, n in c.items() if n >= 2]
    print(f'  Tip-c uygun (≥2 içerikli eser) yazar: {len(coklu)} → {", ".join(coklu)}')


if __name__ == '__main__':
    main()
