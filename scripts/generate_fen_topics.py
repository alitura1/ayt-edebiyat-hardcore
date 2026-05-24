"""TYT Fen 24 ünite için HTML üret (REV2: TBD'siz, sıcak üniteler için "altın bilgiler" kutusu).

Input: public/data/fen/topics-index.json
Output: public/data/fen/topics/<slug>.html

Her HTML:
- Başlık + ders rozeti + öncelik
- Frekans tablosu (yıl × soru)
- 📘 MEBİ Konu Özet PDF Aç linki
- 🔬 İlgili PhET simülasyonlar (varsa)
- 🎯 Sıcak üniteler için "Altın Bilgiler" kutusu (ders-spesifik bilgi maddeleri)
- 🎴 Kart havuzu + Quiz / Atış başlat butonları
- TBD placeholder'ları KALDIRILDI (eksik hissi yaratmasın)
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CANDS = [
    r"C:\Users\Ali Tura Çetin\Documents\Edebiyat Analiz\edebiyat-site\public\data\fen",
    r"C:\Users\Ali Tura Cetin\Documents\Edebiyat Analiz\edebiyat-site\public\data\fen",
]
DATA_DIR = next((Path(p) for p in CANDS if Path(p).exists()), None)
assert DATA_DIR, "data/fen yok!"

TOPICS_IDX = DATA_DIR / "topics-index.json"
TOPICS_OUT = DATA_DIR / "topics"
SIMS_PATH = DATA_DIR / "simulations.json"

with open(TOPICS_IDX, encoding="utf-8") as f:
    topics = json.load(f)
with open(SIMS_PATH, encoding="utf-8") as f:
    sims = json.load(f)

DERS_PDF = {
    "fizik": "tyt-fizik-ozet-notu.pdf",
    "kimya": "tyt-kimya-ozet-notu.pdf",
    "biyoloji": "tyt-biyoloji-ozet-notu.pdf",
}
DERS_LABEL = {"fizik": "⚛ Fizik", "kimya": "🧪 Kimya", "biyoloji": "🧬 Biyoloji"}

# Sıcak üniteler için ders-spesifik "altın bilgiler" — ezberlenmesi gereken çekirdek
ALTIN_BILGILER = {
    "fizik_madde": [
        "<strong>Özkütle</strong> formülü: <em>ρ = m / V</em> · birimi g/cm³ (suyun ρ = 1).",
        "<strong>Yüzme/batma</strong>: cismin ρ &lt; sıvının ρ → yüzer; cismin ρ = sıvının ρ → askıda; ρ &gt; → batar.",
        "<strong>Yapışma (adhezyon)</strong> = farklı maddeler, <strong>kohezyon</strong> = aynı madde molekülleri arası çekim.",
        "ÖSYM kalıbı: özdeş hacimli sıvılarda kütle-hacim grafiği → özkütle karşılaştırma soruları çok klasiktir.",
    ],
    "fizik_hareket_kuvvet": [
        "<strong>Hız</strong> = yol / zaman · ortalama hız ile anlık hız ayrımına dikkat.",
        "<strong>Newton 1</strong>: eylemsizlik (kuvvet yoksa sabit hız veya durgun). <strong>Newton 2</strong>: <em>F = m · a</em>. <strong>Newton 3</strong>: her etkiye eşit ve zıt tepki.",
        "<strong>Sürtünme</strong>: yüzeye dik kuvvete (N) bağlıdır, hıza değil. Statik sürtünme &gt; kinetik sürtünme.",
        "Eğik atış: yatay hız sabit, düşey hız değişir; menzil 45°'de maksimum.",
    ],
    "fizik_isi_sicaklik": [
        "<strong>Sıcaklık</strong> = ortalama kinetik enerji (intensive); <strong>ısı</strong> = enerji transferi (extensive).",
        "<strong>Isı alış-veriş</strong>: <em>Q = m · c · ΔT</em>; karışım sıcaklığında ısı korunur.",
        "<strong>Hâl değişimi</strong> sırasında sıcaklık SABİT; Q = m · L (erime/buharlaşma ısısı).",
        "<strong>Genleşme</strong>: <em>ΔL = L · α · ΔT</em>; gazlarda hacimsel, sıvılarda hacimsel/yüzeysel, katılarda boyutsal/yüzeysel/hacimsel.",
    ],
    "fizik_elektrik_manyetizma": [
        "<strong>Ohm yasası</strong>: <em>V = I · R</em>. Birimler: Volt, Amper, Ohm.",
        "<strong>Seri</strong>: dirençler toplanır (R = R1+R2+...), akım her noktada eşit. <strong>Paralel</strong>: 1/R = 1/R1+1/R2+..., gerilim her kolda eşit.",
        "Ampul parlaklığı: P = V·I = V²/R = I²·R. Devre değişiminde direnç değişimi parlaklığı belirler.",
        "ÖSYM klasiği: anahtar açma/kapama sonrası hangi ampul ışık verir, hangileri eş parlaklıkta.",
    ],
    "fizik_basinc_kaldirma": [
        "<strong>Katı basınç</strong>: P = F / A · taban alanı artarsa basınç azalır.",
        "<strong>Sıvı basıncı</strong>: P = ρ · g · h · derinlik ve sıvı yoğunluğuna bağlıdır, kabın şekline bağlı değildir.",
        "<strong>Kaldırma kuvveti</strong>: Fkald = ρsıvı · g · Vbatık · Arşimet ilkesi.",
        "Yüzme/askıda/batma şartları özkütle karşılaştırmasıyla çözülür.",
    ],
    "fizik_dalgalar": [
        "<strong>Dalga denklemi</strong>: v = λ · f (hız = dalga boyu × frekans).",
        "Bir ortamdan başka ortama geçişte: <strong>frekans değişmez</strong>, dalga boyu ve hız değişir.",
        "Yay dalgalarında: gergin yayda hız artar (T artışı). Su dalgaları: derin sudan sığ suya geçince yavaşlar, λ azalır.",
        "Ses ortamda hızlı yayılır (katı &gt; sıvı &gt; gaz); ışık tam tersi (en hızlı vakumda).",
    ],
    "fizik_optik": [
        "<strong>Düzlem ayna</strong>: nesne-ayna mesafesi = görüntü-ayna mesafesi; görüntü sanal, düz, eşit boyutta.",
        "<strong>Çukur ayna (konkav)</strong>: merkez dışında nesne → gerçek + ters görüntü. <strong>Tümsek ayna (konveks)</strong>: hep sanal + düz + küçük.",
        "<strong>İnce kenarlı (yakınsak) mercek</strong>: ışığı toplar, görüntü gerçek/ters (cisim odak dışındaysa). <strong>Kalın kenarlı (ıraksak)</strong>: sanal/düz/küçük.",
        "<strong>Snell yasası</strong>: n1 · sinθ1 = n2 · sinθ2. Yoğun ortama geçişte ışın normale yaklaşır.",
    ],

    "kimya_bilim": [
        "Elementlerin sembolü periyodik tabloda — büyük harf + (varsa) küçük harf (örn. Na, Cl, Fe).",
        "Kimyasal değişim = yeni madde oluşur (yanma, paslanma). Fiziksel değişim = madde aynı kalır (erime, çözünme).",
        "Kimyada güvenlik: asit suyun üstüne dökülmez (suya asit eklenir — saçramayı önler).",
        "Sembolik dil: kimyasal formülde alt indis atom sayısını, katsayı molekül sayısını gösterir.",
    ],
    "kimya_atom_periyodik": [
        "<strong>Atom</strong> = proton + nötron (çekirdek) + elektron (etrafta). <strong>Atom numarası</strong> = proton sayısı.",
        "<strong>Kütle numarası</strong> = proton + nötron sayısı. <strong>İzotop</strong>: aynı atom no, farklı kütle no.",
        "<strong>Periyot</strong> (yatay sıra) = enerji katmanı sayısı. <strong>Grup</strong> (dikey) = değerlik elektronu (1A=1, 7A=7, 8A=8 hariç soygazlar 8).",
        "Metaller solda (1A-2A, geçiş), ametaller sağda (5A-7A), soygazlar 8A. Periyot soldan sağa atom yarıçapı azalır, iyonlaşma enerjisi artar.",
    ],
    "kimya_etkilesim": [
        "<strong>İyonik bağ</strong>: metal + ametal (elektron alış-veriş). NaCl, MgO. Kristalimsi, suda iyonlarına ayrışır.",
        "<strong>Kovalent bağ</strong>: ametal + ametal (paylaşım). H₂, O₂, CO₂. Polar/apolar molekül ayrımı elektronegatiflik farkıyla.",
        "<strong>Metalik bağ</strong>: metal + metal. Elektron denizi, iletkenlik ve şekillendirilebilirlik kaynağı.",
        "Zayıf etkileşimler: H bağı (DNA, su), dipol-dipol, London kuvvetleri (apolar moleküller).",
    ],
    "kimya_madde_halleri": [
        "<strong>Sıvılar</strong>: yüzey gerilimi (su damlasının yuvarlak şekli), viskozite (akma direnci), kılcallık (bitkilerde su taşıma).",
        "<strong>Gazlar</strong>: ideal gaz <em>PV = nRT</em>. P↑, V↓ (Boyle); T↑, V↑ (Charles); n↑, V↑ (Avogadro).",
        "Hâl değişimi: erime/donma sıcaklığında, kaynama/yoğuşma sıcaklığında sıcaklık SABİT (gizli ısı).",
        "Sıvı buhar basıncı: dış basınca eşit olunca kaynama olur — yükseklerde su daha düşük sıcaklıkta kaynar.",
    ],
    "kimya_temel_kanunlar": [
        "<strong>Mol</strong> = 6.022 × 10²³ tanecik (Avogadro sayısı).",
        "<strong>n = m / Mr</strong> (n: mol, m: kütle gram, Mr: molar kütle).",
        "<strong>Kütle korunumu</strong>: denklem dengelenmiş olmalı — her iki tarafta aynı atom sayısı.",
        "Kimyasal hesaplama: önce denklemi dengele, sonra mol oranlarından yola çık.",
    ],
    "kimya_karisimlar": [
        "<strong>Homojen karışım</strong>: tek faz görünür (çözeltiler, alaşımlar, hava). <strong>Heterojen</strong>: birden fazla faz (süspansiyon, emülsiyon).",
        "<strong>Çözelti</strong>: çözücü + çözünen. Çözünürlük sıcaklık ve basınçla değişir.",
        "Ayırma teknikleri: <strong>süzme</strong> (katı-sıvı), <strong>damıtma</strong> (sıvı-sıvı, kaynama noktası farkı), <strong>kromatografi</strong>, <strong>mıknatıs</strong>, <strong>elek</strong>.",
        "ÖSYM klasiği: bir karışımın hangi yöntemle ayrılabileceği soruları.",
    ],
    "kimya_asit_baz_tuz": [
        "<strong>Asit</strong> = H⁺ verir (HCl, H₂SO₄, HNO₃, CH₃COOH). <strong>Baz</strong> = OH⁻ verir (NaOH, KOH, NH₃ — bazlık).",
        "<strong>pH</strong>: 0-14 skalası. pH &lt; 7 asit, = 7 nötr, &gt; 7 baz. pH = -log[H⁺].",
        "<strong>Nötralleşme</strong>: asit + baz → tuz + su. HCl + NaOH → NaCl + H₂O.",
        "Asit + metal → tuz + H₂ gazı (aktif metaller). Asit + karbonat → tuz + su + CO₂.",
    ],

    "bio_yasam_bilimi": [
        "<strong>Canlıların ortak özellikleri</strong>: hücresel yapı, metabolizma, üreme, büyüme, uyum (homeostazi), tepki, kalıtım.",
        "<strong>İnorganik bileşikler</strong>: su (canlı kütlesinin %70-90), mineral, gaz, asit-baz.",
        "<strong>Organik bileşikler</strong>: karbonhidrat (enerji), lipit (depo + zar), protein (enzim, yapı), nükleik asit (DNA/RNA).",
        "<strong>Enzimler</strong>: protein yapılı, substrata özgü, optimum sıcaklık + pH'ta çalışır. Aktivasyon enerjisini DÜŞÜRÜR.",
    ],
    "bio_hucre": [
        "<strong>Çekirdek</strong>: DNA + kontrol merkezi. <strong>Mitokondri</strong>: ATP üretimi (solunum). <strong>Ribozom</strong>: protein sentezi. <strong>Kloroplast</strong>: fotosentez (sadece bitki).",
        "Bitki hücresinde EKSTRA: hücre çeperi (selüloz), büyük koful, kloroplast. Hayvan hücresinde EKSTRA: sentrozom, lizozom.",
        "<strong>Pasif taşıma</strong> (ATP YOK): difüzyon, osmoz, kolaylaştırılmış difüzyon. Yoğun ortamdan az yoğuna.",
        "<strong>Aktif taşıma</strong> (ATP HARCANIR): az yoğundan yoğun ortama (sodyum-potasyum pompası). <strong>Endositoz / ekzositoz</strong>: büyük moleküller.",
    ],
    "bio_canlilar": [
        "Linnaeus sınıflandırması: <strong>Âlem - Şube - Sınıf - Takım - Aile - Cins - Tür</strong>. Tür ikili adlandırma (binomial).",
        "5 âlem: <strong>Monera</strong> (bakteri, prokaryot), <strong>Protista</strong> (öglena, amip), <strong>Mantar</strong> (heterotrof), <strong>Bitki</strong> (ototrof), <strong>Hayvan</strong> (heterotrof).",
        "Ototrof = kendi besinini üretir (bitki, bazı bakteriler). Heterotrof = dışarıdan alır (hayvan, mantar, çoğu bakteri).",
        "Virüsler hücre değildir — canlılar dışında, konak hücreye ihtiyaç duyarlar.",
    ],
    "bio_bolunme": [
        "<strong>Mitoz</strong>: vücut hücreleri, 2n → 2n (DNA korunur), 2 özdeş hücre. Büyüme, onarım, eşeysiz üreme.",
        "<strong>Mayoz</strong>: üreme hücreleri, 2n → n (DNA yarıya iner), 4 farklı hücre. Çeşitlilik (crossing-over).",
        "<strong>Eşeysiz üreme</strong>: bölünme, tomurcuklanma, sporlanma, rejenerasyon, vejetatif (mitoz tabanlı, özdeş bireyler).",
        "<strong>Eşeyli üreme</strong>: gametler birleşir (mayoz + döllenme), zigot oluşur, çeşitlilik artar.",
    ],
    "bio_kalitim": [
        "<strong>Gen</strong> = kalıtsal özelliği taşıyan DNA parçası. <strong>Alel</strong> = aynı genin farklı versiyonu.",
        "<strong>Genotip</strong>: AA homozigot baskın, Aa heterozigot, aa homozigot çekinik. <strong>Fenotip</strong>: gözle görülen özellik.",
        "<strong>Mendel ilkeleri</strong>: ayrılma + bağımsız dağılım. Punnett karesi ile olasılık hesabı.",
        "<strong>X'e bağlı kalıtım</strong>: hemofili, renk körlüğü erkeklerde daha sık (tek X). Annede taşıyıcılık (XᴬXᵃ).",
    ],
    "bio_ekosistem": [
        "<strong>Besin zinciri</strong>: üretici (bitki) → birincil tüketici (otçul) → ikincil tüketici (etçil) → üçüncül tüketici.",
        "Trofik düzey yukarı çıktıkça <strong>enerji azalır</strong> (~%10'u aktarılır). Üretici en altta en fazla biyokütle.",
        "<strong>Biyolojik birikim</strong>: zehirli madde (DDT, ağır metal) besin zincirinde en üst basamakta yoğunlaşır.",
        "Biyolojik çeşitlilik: tür, genetik, ekosistem çeşitliliği. Endemik türler korunmalı.",
    ],
}


def render_topic_html(t):
    slug = t["slug"]
    title = t["title"]
    ders = t["ders"]
    toplam = t["toplam"]
    ortalama = t["ortalama"]
    oncelik = t["oncelik"]
    mebi = t["mebi_pages"]
    yillar = t["yillar"]
    kart_say = t["kart_say"]
    aciklama = t["kisa_aciklama"]

    pdf_file = DERS_PDF.get(ders, "")
    first_page = mebi.split("-")[0].strip() if mebi else "1"

    # Frekans tablosu
    yillar_sorted = sorted(yillar.items())
    freq_row1 = "".join(f"<th>{y}</th>" for y, _ in yillar_sorted)
    freq_row2 = "".join(f"<td style='text-align:center'>{v if v else '—'}</td>" for _, v in yillar_sorted)

    # Öncelik rozeti
    if oncelik == "sicak":
        onc_html = '<span class="oncelik-sicak">🔥 SICAK ALAN</span>'
    elif oncelik == "orta":
        onc_html = '<span class="oncelik-orta">🟡 ORTA</span>'
    else:
        onc_html = '<span class="oncelik-dusuk">⚪ DÜŞÜK</span>'

    # İlgili PhET simülasyonlar
    unit_sims = [s for s in sims if s.get("konu") == slug]
    sim_section = ""
    if unit_sims:
        sim_section = (
            '<h3>🔬 Bu Üniteye Ait İnteraktif Simülasyonlar</h3>'
            '<p style="margin-bottom:0.5rem;font-size:0.85rem">Konuyu canlı oynayarak kavra — Türkçe ya da yan menüden Türkçe seç:</p>'
            '<ul>'
            + "".join(
                f'<li><strong><a href="{s["url"]}" target="_blank" rel="noopener">{s["title"]}</a></strong> — {s["aciklama"]}</li>'
                for s in unit_sims
            )
            + '</ul>'
            '<p style="font-size:0.8rem;color:#64748b;margin-top:0.5rem">→ Daha fazlası: <a href="#/simulasyonlar">🔬 Simülasyonlar sayfası</a></p>'
        )

    # MEBİ Box: PDF Aç linki
    mebi_box = (
        f'<div class="mebi-box">'
        f'<strong>📘 MEBİ Konu Özeti</strong> → '
        f'<a href="./pdf/fen/{pdf_file}#page={first_page}" target="_blank" rel="noopener">PDF Aç (s.{mebi})</a> '
        f'· yan sekmede aç, oku gel'
        f'</div>'
    )

    # Sıcak ise extra vurgu
    sicak_vurgu = ""
    if oncelik == "sicak":
        sicak_vurgu = (
            f'<div class="tuzak-box">'
            f'<strong>🎯 BU ÜNİTEDEN HER YIL ~{round(ortalama)} SORU.</strong> '
            f'8 yılda toplam {toplam} soru çıkmış. Kart havuzundan en az {min(kart_say, 15)} soru çöz, hata defterini sıfırla.'
            f'</div>'
        )

    # Sıcak üniteler için altın bilgiler kutusu
    altin_section = ""
    altin_items = ALTIN_BILGILER.get(slug)
    if altin_items and oncelik == "sicak":
        altin_section = (
            '<h3>🎯 Bu Ünitenin Altın Bilgileri</h3>'
            '<div class="ezber-box">'
            '<strong>Sınava giderken bunları MUTLAKA bil:</strong>'
            '<ul style="margin-top:0.5rem;margin-left:1.2rem">'
            + "".join(f'<li style="margin-bottom:0.35rem">{item}</li>' for item in altin_items)
            + '</ul>'
            '</div>'
        )

    # Aksiyon: quiz + atış
    aksiyon = (
        f'<div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-top:1.5rem">'
        f'<a href="#/quiz/setup?konu={slug}" style="padding:0.6rem 1.2rem;background:#047857;color:white;border-radius:0.5rem;font-weight:600;text-decoration:none">🎯 Bu üniteden {min(kart_say, 10)} soru çöz</a>'
        f'<a href="#/atis?konu={slug}" style="padding:0.6rem 1.2rem;background:#1D4ED8;color:white;border-radius:0.5rem;font-weight:600;text-decoration:none">⚡ Atış modu</a>'
        f'</div>'
    )

    html = f"""<div class="topic-content">
<h2>{title}</h2>

<p style="font-size:0.95rem;color:#475569;margin-bottom:1rem">
<span style="margin-right:0.5rem">{DERS_LABEL[ders]}</span>
{onc_html}
<span style="margin-left:0.5rem">📅 {toplam} soru / 8 yıl · ortalama yılda {ortalama}</span>
</p>

<p>{aciklama}</p>

{sicak_vurgu}

{mebi_box}

<h3>📊 ÖSYM Yıl Yıl Frekans (2018-2025)</h3>
<table>
<thead><tr>{freq_row1}<th>Toplam</th></tr></thead>
<tbody><tr>{freq_row2}<td style="text-align:center;font-weight:bold;background:#FEE2E2;color:#991B1B">{toplam}</td></tr></tbody>
</table>

{altin_section}

<div class="ezber-box">
<strong>🎴 Kart Havuzu</strong> — Bu ünitede sitede <strong>{kart_say} ÖSYM sorusu</strong> hazır.
Cevap anahtarı PDF'te yer almıyor (manuel doldurulması beklenir); ama soru metnini ve şıkları öğrenmek refleks için zaten yeterli.
</div>

{sim_section}

{aksiyon}

<p style="margin-top:2rem;font-size:0.8rem;color:#64748b;text-align:center">
📘 Kaynak: MEB MEBİ TYT Konu Özetleri ({DERS_LABEL[ders]} s.{mebi}) + ÖSYM 2018-2025 çıkmış soru analizi
</p>
</div>
"""
    return html


# Generate all
for t in topics:
    slug = t["slug"]
    html = render_topic_html(t)
    out_path = TOPICS_OUT / f"{slug}.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    has_altin = "🎯 Altın Bilgiler" if (ALTIN_BILGILER.get(slug) and t["oncelik"] == "sicak") else ""
    print(f"✓ {out_path.name}  {has_altin}")

print(f"\n{len(topics)} ünite HTML üretildi. Sıcak ünitelerde altın bilgiler eklendi, TBD kutucukları kaldırıldı.")
