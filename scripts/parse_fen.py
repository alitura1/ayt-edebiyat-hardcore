"""REV26: TYT Fen çıkmış soruları PDF -> cards-auto.json + topics-index.json üretir.

Strateji:
- Input: C:\\Users\\Ali Tura Çetin\\Documents\\Fen Analiz\\tyt_fen_cikmis_sorular.pdf (61 sayfa)
- Yapı: sayfa 1-3 fizik freq tablo + kapak, 4-28 fizik sorular, 29 kimya freq, 30-45 kimya, 46 biyo freq, 47-61 biyo
- Ders detect: sayfa header text'inde FİZİK/KİMYA/BİYOLOJİ
- Konu detect: her ünitenin alt-konu başlıkları sayfa içinde italik/bold ayrı satır olarak çıkar
- Soru parse: N\\. ... A) B) C) D) E) ... YYYY-TYT pattern
- Cevap anahtarı PDF'te YOK -> dogru: null kaydedilir, manuel doldurma sonra

Output:
- public/data/fen/cards-auto.json — fn_NNNN, edebiyat schema uyumlu
- public/data/fen/topics-index.json — 24 ünite + frekans + yıllar
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import fitz

# Path fallback (Türkçe ç encoding)
PDF_PATHS = [
    r"C:\Users\Ali Tura Çetin\Documents\Fen Analiz\tyt_fen_cikmis_sorular.pdf",
    r"C:\Users\Ali Tura Cetin\Documents\Fen Analiz\tyt_fen_cikmis_sorular.pdf",
]
PDF = next((p for p in PDF_PATHS if Path(p).exists()), None)
assert PDF, "PDF bulunamadı!"

OUT_DIR_CANDS = [
    r"C:\Users\Ali Tura Çetin\Documents\Edebiyat Analiz\edebiyat-site\public\data\fen",
    r"C:\Users\Ali Tura Cetin\Documents\Edebiyat Analiz\edebiyat-site\public\data\fen",
]
OUT_DIR = next((Path(p) for p in OUT_DIR_CANDS if Path(p).exists()), None)
assert OUT_DIR, "Output dir bulunamadı!"

# --------- ÜNİTE HARİTASI (PDF frekans tablosundan ve plandan) ---------
# Her ünite: (kod, label, ders, alt_konular[konu_baslik regex pattern])
# Alt konular PDF'te bölüm header'ı olarak çıkar — regex case-insensitive
UNITS = [
    # Fizik 10 ünite
    {"code": "fizik_giris", "title": "Fizik Bilimine Giriş", "ders": "fizik", "toplam": 2, "mebi": "9-14",
     "alt": ["Fizik Biliminin Önemi", "Fiziksel Niceliklerin Sınıflandırılması", "Fiziğin Uygulama Alanları", "Bilim Araştırma Merkezleri"]},
    {"code": "fizik_madde", "title": "Madde ve Özellikleri", "ders": "fizik", "toplam": 6, "mebi": "15-25",
     "alt": ["Madde ve Özkütle", "Dayanıklılık", "Yapışma ve Birbirini Tutma"]},
    {"code": "fizik_hareket_kuvvet", "title": "Hareket ve Kuvvet", "ders": "fizik", "toplam": 9, "mebi": "26-44",
     "alt": ["Hareket", "Kuvvet", "Newton'ın Hareket Yasaları", "Newton'un Hareket Yasaları", "Sürtünme Kuvveti"]},
    {"code": "fizik_enerji", "title": "Enerji", "ders": "fizik", "toplam": 1, "mebi": "45-70",
     "alt": ["İş, Güç ve Enerji", "Mekanik Enerji", "Enerjinin Korunumu ve Enerji Dönüşümleri", "Verim", "Enerji Kaynakları"]},
    {"code": "fizik_isi_sicaklik", "title": "Isı ve Sıcaklık", "ders": "fizik", "toplam": 8, "mebi": "71-100",
     "alt": ["Isı ve Sıcaklık", "Hâl Değişimi", "Isıl Denge", "Enerji İletim Yolları ve Enerji İletim Hızı", "Genleşme"]},
    {"code": "fizik_elektrostatik", "title": "Elektrostatik", "ders": "fizik", "toplam": 3, "mebi": "101-110",
     "alt": ["Elektrik Yükleri"]},
    {"code": "fizik_elektrik_manyetizma", "title": "Elektrik ve Manyetizma", "ders": "fizik", "toplam": 6, "mebi": "111-130",
     "alt": ["Elektrik Akımı, Potansiyel Farkı ve Direnç", "Elektrik Devreleri", "Mıknatıs ve Manyetik Alan", "Akım ve Manyetik Alan"]},
    {"code": "fizik_basinc_kaldirma", "title": "Basınç ve Kaldırma Kuvveti", "ders": "fizik", "toplam": 5, "mebi": "131-145",
     "alt": ["Basınç", "Kaldırma Kuvveti"]},
    {"code": "fizik_dalgalar", "title": "Dalgalar", "ders": "fizik", "toplam": 5, "mebi": "146-165",
     "alt": ["Dalgalar", "Yay Dalgası", "Su Dalgası", "Ses Dalgası", "Ses Dalgaları", "Deprem Dalgası", "Deprem Dalgaları"]},
    {"code": "fizik_optik", "title": "Optik", "ders": "fizik", "toplam": 10, "mebi": "166-200",
     "alt": ["Aydınlanma", "Gölge", "Yansıma", "Düzlem Ayna", "Düzlem Aynalar", "Küresel Aynalar", "Kırılma", "Mercekler", "Prizmalar", "Renk"]},

    # Kimya 8 ünite
    {"code": "kimya_bilim", "title": "Kimya Bilimi", "ders": "kimya", "toplam": 7, "mebi": "9-20",
     "alt": ["Kimya Disiplinleri", "Kimyacıların Çalışma Alanları", "Kimyanın Sembolik Dili", "Kimya Uygulamalarında İş Sağlığı"]},
    {"code": "kimya_atom_periyodik", "title": "Atom ve Periyodik Sistem", "ders": "kimya", "toplam": 9, "mebi": "21-40",
     "alt": ["Atom Modelleri", "Atomun Yapısı", "Periyodik Sistem"]},
    {"code": "kimya_etkilesim", "title": "Kimyasal Türler Arası Etkileşimler", "ders": "kimya", "toplam": 8, "mebi": "41-55",
     "alt": ["Güçlü Etkileşimler", "Zayıf Etkileşimler", "Fiziksel ve Kimyasal Değişimler"]},
    {"code": "kimya_madde_halleri", "title": "Maddenin Hâlleri", "ders": "kimya", "toplam": 7, "mebi": "56-65",
     "alt": ["Sıvılar", "Gazlar", "Katılar"]},
    {"code": "kimya_temel_kanunlar", "title": "Kimyanın Temel Kanunları ve Hesaplamalar", "ders": "kimya", "toplam": 6, "mebi": "66-75",
     "alt": ["Kimyanın Temel Kanunları", "Mol Kavramı", "Kimyasal Tepkimelerde Hesaplamalar"]},
    {"code": "kimya_karisimlar", "title": "Karışımlar", "ders": "kimya", "toplam": 8, "mebi": "76-85",
     "alt": ["Homojen ve Heterojen Karışımlar", "Ayırma ve Saflaştırma Teknikleri"]},
    {"code": "kimya_asit_baz_tuz", "title": "Asitler, Bazlar ve Tuzlar", "ders": "kimya", "toplam": 8, "mebi": "86-93",
     "alt": ["Asitler ve Bazlar", "Asitlerin ve Bazların Tepkimeleri"]},
    {"code": "kimya_her_yerde", "title": "Kimya Her Yerde", "ders": "kimya", "toplam": 1, "mebi": "94-96",
     "alt": ["Yaygın Günlük Hayat Kimyasalları"]},

    # Biyoloji 6 ünite
    {"code": "bio_yasam_bilimi", "title": "Yaşam Bilimi Biyoloji", "ders": "biyoloji", "toplam": 7, "mebi": "9-44",
     "alt": ["Biyoloji ve Canlıların Ortak Özellikleri", "Canlıların Yapısında Bulunan Temel Bileşikler",
             "İnorganik Bileşikler", "Organik Bileşikler", "Karbonhidratlar", "Lipitler", "Proteinler", "Enzimler", "Vitaminler ve Hormonlar", "Nükleik Asitler", "ATP", "Sağlıklı Beslenme"]},
    {"code": "bio_hucre", "title": "Hücre", "ders": "biyoloji", "toplam": 9, "mebi": "45-99",
     "alt": ["Hücre", "Hücresel Yapılar", "Organeller"]},
    {"code": "bio_canlilar", "title": "Canlılar Dünyası", "ders": "biyoloji", "toplam": 8, "mebi": "100-110",
     "alt": ["Canlıların Çeşitliliği ve Sınıflandırılması", "Canlı Âlemleri ve Özellikleri", "Canlı Alemleri"]},
    {"code": "bio_bolunme", "title": "Hücre Bölünmeleri", "ders": "biyoloji", "toplam": 8, "mebi": "111-122",
     "alt": ["Mitoz", "Hücre Döngüsü", "Eşeysiz Üreme", "Mayoz", "Eşeyli Üreme"]},
    {"code": "bio_kalitim", "title": "Kalıtımın Genel İlkeleri", "ders": "biyoloji", "toplam": 8, "mebi": "123-145",
     "alt": ["Kalıtım", "Mendel İlkeleri", "Eş Baskınlık", "Çok Alellilik", "Kan Grupları", "Eşeye Bağlı Kalıtım", "Akraba Evliliği", "Soyağacı"]},
    {"code": "bio_ekosistem", "title": "Ekosistem Ekolojisi ve Güncel Çevre", "ders": "biyoloji", "toplam": 7, "mebi": "146-174",
     "alt": ["Ekosistem", "Çevre Sorunları", "Doğal Kaynaklar", "Biyolojik Çeşitlilik"]},
]

# Konu-başlığı -> ünite kodu lookup (alt konular)
def build_alt_lookup():
    m = {}
    for u in UNITS:
        for alt in u["alt"]:
            m[alt.lower().replace("'", "").replace("ı", "i")] = u["code"]
        # Ünite başlığının kendisi de alt olarak detect edilebilsin
        m[u["title"].lower().replace("'", "").replace("ı", "i")] = u["code"]
    return m

ALT_LOOKUP = build_alt_lookup()

def normalize_for_match(s):
    return s.lower().replace("'", "").replace("ı", "i").replace("’", "").strip()

def find_unite_for_heading(heading, default_ders):
    """Konu başlığı string'inden ünite kodu tahmin et."""
    nh = normalize_for_match(heading)
    # Exact match
    if nh in ALT_LOOKUP:
        return ALT_LOOKUP[nh]
    # Substring match
    for key, code in ALT_LOOKUP.items():
        if key in nh or nh in key:
            # Aynı ders kontrolü
            unit = next((u for u in UNITS if u["code"] == code), None)
            if unit and unit["ders"] == default_ders:
                return code
    return None

# --------- DERS DETECT (sayfa header) ---------
def detect_ders_for_page(page_text):
    """Sayfa text'inden ders tespit et (header'da büyük harfle yazılı)."""
    t = page_text[:600]  # ilk 600 char (header genelde üstte)
    if "FİZİK" in t or "FIZIK" in t:
        return "fizik"
    if "KİMYA" in t or "KIMYA" in t:
        return "kimya"
    if "BİYOLOJİ" in t or "BIYOLOJI" in t:
        return "biyoloji"
    return None

# --------- KONU BAŞLIĞI DETECT ---------
# Sayfa içinde, soru numaralarının arasında "Konu Adı" şeklinde başlık çıkar.
# Bunlar tek satır, kelime baş harfleri büyük (Title Case) veya UPPER, soru numarasından önce.
def extract_headings(page_text):
    """Sayfa text'inden konu başlıklarını çıkar. Her başlık (line_index, heading_text) döner."""
    lines = page_text.split("\n")
    headings = []
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or len(s) < 4 or len(s) > 80:
            continue
        # Soru numarasıyla başlıyorsa skip
        if re.match(r"^\d+\.\s*$", s):
            continue
        if re.match(r"^\d+\.\s", s):
            continue
        # Şık ile başlıyorsa skip
        if re.match(r"^[A-E]\)", s):
            continue
        # Sayfa numarası veya YKS Çıkmış Sorular gibi artifact'ler
        if "YKS Çıkmış Sorular" in s or "Ortaöğretim Genel" in s:
            continue
        if s in ("TYT", "FİZİK", "KİMYA", "BİYOLOJİ"):
            continue
        if re.match(r"^\d+$", s):  # sadece sayı
            continue
        # Roman rakamı + nokta
        if re.match(r"^[IVX]+\.", s):
            continue
        # Yıl tag'i
        if re.match(r"^\d{4}-TYT$", s):
            continue
        # Title Case (büyük başlangıçlı) ve içinde küçük harf var = potansiyel başlık
        # Veya tamamen UPPER (ünite adı) ve > 1 kelime
        words = s.split()
        if len(words) < 2 or len(words) > 8:
            continue
        # Hepsi sayı/punctuation ise atla
        if not any(w[0].isupper() if w else False for w in words):
            continue
        # Şu pattern'lara uy: ilk harf büyük + sonra başka büyük harf var
        # Heuristik: bilinen ALT_LOOKUP'ta var mı?
        if normalize_for_match(s) in ALT_LOOKUP:
            headings.append((i, s))
            continue
        # Bilinmiyorsa: çoğunlukla Title Case ve özel pattern'sız tek satır
        # Şu an pas — sadece bilinen başlıklar
    return headings

# --------- SORU PARSE ---------
def parse_questions_from_text(full_text, ders, page_offset=0):
    """Sayfaları birleştirilmiş text'ten soruları çıkarır."""
    questions = []

    # Header artifacts temizliği
    cleaned = full_text
    cleaned = re.sub(r"Ortaöğretim Genel Müdürlüğü", " ", cleaned)
    cleaned = re.sub(r"YKS Çıkmış Sorular", " ", cleaned)
    cleaned = re.sub(r"^\s*\d{3}\s*$", " ", cleaned, flags=re.MULTILINE)  # sayfa nos
    cleaned = re.sub(r"^\s*TYT\s*$", " ", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*(FİZİK|KİMYA|BİYOLOJİ)\s*$", " ", cleaned, flags=re.MULTILINE)

    # Soru başlangıçları: "N." veya "N.\t" satır başında
    # Pattern: yeni satır + sayı + nokta + tab/boşluk
    # Sorular numara sırasıyla 1-30+
    # Pattern: (?:^|\n)\s*(\d+)\.\s
    pat = re.compile(r"(?:^|\n)\s*(\d+)\.\s+", re.MULTILINE)
    starts = [(m.start(), int(m.group(1)), m.end()) for m in pat.finditer(cleaned)]

    # Ardışık olanları al (1,2,3,...) — false positive (örn. "I. ... II. ...") filtrele
    # Gerçek soru başlangıcı: önceki soru numarasından 1 büyük
    valid = []
    prev_n = 0
    for s_pos, n, e_pos in starts:
        # Sıra atlamaz, küçülmez ya da kabul edilebilir tekrar (yeni sayfa)
        if n == prev_n + 1 or (n == 1 and prev_n == 0):
            valid.append((s_pos, n, e_pos))
            prev_n = n
        elif n > prev_n + 1 and n <= prev_n + 5:
            # Atlama küçükse kabul (parse'da kaçırma olmuş olabilir)
            valid.append((s_pos, n, e_pos))
            prev_n = n
        elif n == prev_n:
            # Tekrar — skip
            pass
        else:
            # Çok büyük atlama: muhtemelen soru başlangıcı değil
            pass

    # Her geçerli soru için body'yi ayır
    for idx, (s_pos, n, e_pos) in enumerate(valid):
        end_pos = valid[idx + 1][0] if idx + 1 < len(valid) else len(cleaned)
        body = cleaned[e_pos:end_pos].strip()
        if len(body) < 20:
            continue

        # Yıl çıkar
        ym = re.search(r"(\d{4})-TYT", body)
        yil = int(ym.group(1)) if ym else None

        # Şıkları ayır
        options, soru_text = split_options(body)
        if not options:
            # Şık bulamadık, ham body'yi soru olarak al
            soru_text = clean_body(body)
            options = []
        else:
            soru_text = clean_body(soru_text)

        # Yıl tag'ini soru metninden çıkar
        soru_text = re.sub(r"\d{4}-TYT\s*$", "", soru_text).strip()

        questions.append({
            "num": n,
            "ders": ders,
            "yil": yil,
            "soru": soru_text,
            "secenekler": options,
            "dogru": None,  # Cevap anahtarı PDF'te yok
            "kaynak": "otomatik",
        })
    return questions


def split_options(body):
    """5 şık ayrı (A)..E))."""
    body_norm = body.replace("\t", " ")
    # Pattern: yeni satır ya da boşluk sonra harf + )
    pattern = r"(?:^|\s|\n)([A-E])\)\s*"
    matches = list(re.finditer(pattern, body_norm))

    # Sıralı A-E bul
    expected = ["A", "B", "C", "D", "E"]
    found = []
    last_idx = -1
    seq = []  # match objects, sıralı
    for m in matches:
        letter = m.group(1)
        if letter in expected:
            li = expected.index(letter)
            if li == last_idx + 1:
                seq.append(m)
                last_idx = li
                if len(seq) == 5:
                    break
            elif li == 0:
                # Yeni A başlangıcı (false positive sonrası)
                seq = [m]
                last_idx = 0

    if len(seq) != 5:
        return None, body_norm

    soru_text = body_norm[:seq[0].start()].strip()
    options = []
    for i, m in enumerate(seq):
        start = m.end()
        end = seq[i + 1].start() if i + 1 < len(seq) else len(body_norm)
        text = body_norm[start:end]
        # Yıl tag çıkar şık metninden
        text = re.sub(r"\d{4}-TYT.*$", "", text, flags=re.DOTALL)
        text = clean_body(text)
        options.append({"id": m.group(1), "text": text})
    return options, soru_text


def clean_body(s):
    s = s.replace("\t", " ").replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s+([\.,!?:;])", r"\1", s)
    return s.strip()


# --------- KONU TAGGING ---------
# Her soruya konu atamak için sayfa text'inde, sorudan önce gelen başlığı bul.
def tag_questions_with_konu(pages_data):
    """pages_data: [(page_num_0idx, ders, text)]
    Çıktı: her sorunun 'konu' field'ı."""
    tagged = []
    current_heading = None
    current_unit = None
    cumulative_num = 0  # her ders için sıfırlanır
    cumulative_per_ders = {"fizik": 0, "kimya": 0, "biyoloji": 0}

    for page_idx, ders, text in pages_data:
        # Bu sayfa'da başlık var mı?
        for line in text.split("\n"):
            s = line.strip()
            if not s:
                continue
            # Bilinen alt başlık mı?
            nm = normalize_for_match(s)
            if nm in ALT_LOOKUP:
                code = ALT_LOOKUP[nm]
                # Aynı ders mi?
                u = next((x for x in UNITS if x["code"] == code), None)
                if u and u["ders"] == ders:
                    current_heading = s
                    current_unit = code
        # Bu sayfa'daki soruları parse et
        qs = parse_questions_from_text(text, ders)
        for q in qs:
            # Numara o ders için arttıkça başlıkları güncelle
            # (Çoğu zaman aynı başlık altında birden fazla soru var, başlık değişmedikçe aynı kullanılır)
            q["konu"] = current_unit or ""
            q["alt_konu"] = current_heading or ""
            tagged.append(q)
    return tagged


def main():
    print(f"PDF: {PDF}")
    print(f"OUT: {OUT_DIR}")

    doc = fitz.open(PDF)
    n_pages = len(doc)
    print(f"Toplam sayfa: {n_pages}")

    # Her sayfa için ders + text
    pages_data = []
    current_ders = None
    skip_pages = set(range(0, 4))  # ilk 4 sayfa kapak/içindekiler (fizik freq tablo dahil — frekansı plan'dan alıyoruz)
    # Kimya freq tablo: sayfa 29 (index 28)
    skip_pages.add(28)
    # Biyo freq tablo: sayfa 46 (index 45)
    skip_pages.add(45)

    for i in range(n_pages):
        text = doc[i].get_text()
        ders = detect_ders_for_page(text)
        if ders:
            current_ders = ders
        if i in skip_pages:
            continue
        if not current_ders:
            continue
        pages_data.append((i, current_ders, text))

    doc.close()

    # Soruları parse et + konu tag
    all_questions = []
    current_heading_by_ders = {"fizik": None, "kimya": None, "biyoloji": None}
    current_unit_by_ders = {"fizik": None, "kimya": None, "biyoloji": None}

    # Tüm sayfa text'ini ders bazında birleştir (page separator ile)
    text_per_ders = {"fizik": "", "kimya": "", "biyoloji": ""}
    for page_idx, ders, text in pages_data:
        text_per_ders[ders] += "\n\n" + text

    # Her ders için: tek seferde parse + konu tagging by position
    cards = []
    card_id = 0
    for ders in ["fizik", "kimya", "biyoloji"]:
        full_text = text_per_ders[ders]
        if not full_text.strip():
            continue

        # 1) Konu başlığı pozisyonlarını bul (line-based scan)
        heading_positions = []  # [(char_pos, heading_text, unit_code)]
        pos = 0
        for line in full_text.split("\n"):
            line_start = pos
            stripped = line.strip()
            if stripped:
                nm = normalize_for_match(stripped)
                if nm in ALT_LOOKUP:
                    code = ALT_LOOKUP[nm]
                    u = next((x for x in UNITS if x["code"] == code), None)
                    if u and u["ders"] == ders:
                        heading_positions.append((line_start, stripped, code))
            pos += len(line) + 1  # +1 for \n

        # 2) Soruları parse et (tek seferde tüm ders metninden)
        questions = parse_questions_from_text(full_text, ders)

        # 3) Her sorunun text'teki başlangıç pozisyonunu bul, ona göre konu ata
        # parse_questions_from_text içinde pozisyon dönmesini değiştiremiyoruz, bu yüzden re-find yapacağız
        # Daha basit: parse fonksiyonunu güncelleyip pozisyon dönmesini sağlayacağım — alttaki yeni mantık
        # Burada questions'a doğrudan ekleyelim, konu tagging post-process
        for q in questions:
            card_id += 1
            # Heading lookup: sorunun yıl tag pozisyonuna en yakın önceki başlık
            # Q soru metnini full_text'te ara
            q_text_first = q["soru"][:50] if q["soru"] else ""
            q_pos = -1
            if q_text_first:
                q_pos = full_text.find(q_text_first)
            current_heading = None
            current_unit = None
            if q_pos > 0:
                # Bu pozisyondan önce gelen son başlık
                for hpos, htext, hcode in heading_positions:
                    if hpos < q_pos:
                        current_heading = htext
                        current_unit = hcode
                    else:
                        break

            cards.append({
                "id": f"fn_{card_id:04d}",
                "konu": current_unit or "",
                "alt_konu": current_heading or "",
                "ders": ders,
                "tip": "cikmis",
                "yil": q["yil"],
                "soru": q["soru"],
                "secenekler": q["secenekler"],
                "dogru": q["dogru"],
                "kaynak": "otomatik",
                "zorluk": "orta",
            })

    # Konusuz kartlar için propagation:
    # - Sıralı listeyi taram, boş konu için sonraki dolu konuyu kullan (LOOK-AHEAD)
    # - Hala boş kalırsa, önceki dolu konuyu kullan (forward fill)
    # - Yine boş ise ders'in ilk ünitesini default ata
    DERS_DEFAULT_UNIT = {"fizik": "fizik_giris", "kimya": "kimya_bilim", "biyoloji": "bio_yasam_bilimi"}
    n = len(cards)
    # 1) Look-ahead (boş ise sonraki aynı ders kartının konusu)
    for i in range(n):
        if not cards[i]["konu"]:
            for j in range(i + 1, n):
                if cards[j]["ders"] == cards[i]["ders"] and cards[j]["konu"]:
                    cards[i]["konu"] = cards[j]["konu"]
                    break
    # 2) Forward fill (önceki dolunun konusu)
    last_by_ders = {}
    for c in cards:
        if c["konu"]:
            last_by_ders[c["ders"]] = c["konu"]
        elif c["ders"] in last_by_ders:
            c["konu"] = last_by_ders[c["ders"]]
    # 3) Hâlâ boş ise ders default'u
    for c in cards:
        if not c["konu"]:
            c["konu"] = DERS_DEFAULT_UNIT.get(c["ders"], "")

    print(f"\nToplam kart: {len(cards)}")
    # Ders dağılımı
    from collections import Counter
    ders_count = Counter(c["ders"] for c in cards)
    print(f"Ders dağılımı: {dict(ders_count)}")
    konu_count = Counter(c["konu"] for c in cards)
    print(f"Konu dağılımı:")
    for k, v in sorted(konu_count.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")

    # cards-auto.json yaz
    cards_path = OUT_DIR / "cards-auto.json"
    with open(cards_path, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    print(f"✓ {cards_path}")

    # topics-index.json üret
    # Plan'daki toplam'ı kullan + cards-auto'dan yıllar dağılımı
    topics = []
    for u in UNITS:
        # Bu ünitedeki kartların yıllarını topla
        unit_cards = [c for c in cards if c["konu"] == u["code"]]
        yillar = {str(y): 0 for y in range(2018, 2026)}
        for c in unit_cards:
            if c["yil"]:
                yk = str(c["yil"])
                if yk in yillar:
                    yillar[yk] += 1
        # Eğer hiç kart yoksa, plan toplam ile yillar tüm 0 (manuel sonra düzeltilir)
        # Ortalama = toplam / 8
        ortalama = round(u["toplam"] / 8, 2)
        oncelik = "sicak" if u["toplam"] >= 5 else ("orta" if u["toplam"] >= 3 else "dusuk")
        kart_say = len(unit_cards)

        kisa_aciklama = {
            "fizik_giris": "Fizik nedir, alt dalları, ölçme ve birimler.",
            "fizik_madde": "Madde, özkütle, dayanıklılık, yapışma; en sıcak konu özkütle.",
            "fizik_hareket_kuvvet": "Hareket, kuvvet, Newton yasaları, sürtünme; her yıl 1-2 soru.",
            "fizik_enerji": "İş, güç, enerji çeşitleri ve dönüşümleri; düşük frekanslı.",
            "fizik_isi_sicaklik": "Isı-sıcaklık farkı, hâl değişimi, enerji iletim yolları; sıcak konu.",
            "fizik_elektrostatik": "Elektrik yükleri, yüklenme yolları; orta frekans.",
            "fizik_elektrik_manyetizma": "Devreler, akım, direnç; en çok sorulan: Elektrik Devreleri.",
            "fizik_basinc_kaldirma": "Basınç ve kaldırma kuvveti; klasik ÖSYM kalıbı.",
            "fizik_dalgalar": "Dalga türleri, yay/su/ses/deprem; periyodik test sorusu.",
            "fizik_optik": "Aydınlanma, yansıma, ayna, mercek; en çok sorulan fizik ünitesi.",
            "kimya_bilim": "Disiplinler, sembolik dil, güvenlik; sembolik dile dikkat.",
            "kimya_atom_periyodik": "Atom modelleri, yapı, periyodik sistem; ⭐ en sıcak kimya.",
            "kimya_etkilesim": "Güçlü/zayıf etkileşimler, fiziksel-kimyasal değişim.",
            "kimya_madde_halleri": "Sıvılar (en sık), gazlar, katılar.",
            "kimya_temel_kanunlar": "Kanunlar, mol, kimyasal hesaplamalar; hesap soruları.",
            "kimya_karisimlar": "Homojen-heterojen, ayırma teknikleri; ⭐ en sıcak.",
            "kimya_asit_baz_tuz": "Asitler, bazlar, tepkimeleri; ⭐ sıcak konu.",
            "kimya_her_yerde": "Günlük hayat kimyasalları; düşük öncelik.",
            "bio_yasam_bilimi": "Ortak özellikler, temel bileşikler; her yıl sorulur.",
            "bio_hucre": "Hücre yapısı, organeller, zar; ⭐ EN SICAK biyoloji konusu.",
            "bio_canlilar": "Sınıflandırma ve âlemler; her yıl gelir.",
            "bio_bolunme": "Mitoz, mayoz, eşeyli-eşeysiz üreme; ⭐ sıcak.",
            "bio_kalitim": "Mendel, alel, soyağacı, X'e bağlı; ⭐ sıcak — soyağacı klasik.",
            "bio_ekosistem": "Ekosistem, çevre sorunları, biyolojik çeşitlilik.",
        }.get(u["code"], "")

        topics.append({
            "slug": u["code"],
            "code": u["code"],
            "title": u["title"],
            "ders": u["ders"],
            "toplam": u["toplam"],
            "ortalama": ortalama,
            "oncelik": oncelik,
            "mebi_pages": u["mebi"],
            "yillar": yillar,
            "kart_say": kart_say,
            "alt_basliklar": len(u["alt"]),
            "kisa_aciklama": kisa_aciklama,
        })

    topics_path = OUT_DIR / "topics-index.json"
    with open(topics_path, "w", encoding="utf-8") as f:
        json.dump(topics, f, ensure_ascii=False, indent=2)
    print(f"✓ {topics_path}")
    print(f"\n24 ünite oluşturuldu. Sıcak: {sum(1 for t in topics if t['oncelik']=='sicak')}, Orta: {sum(1 for t in topics if t['oncelik']=='orta')}, Düşük: {sum(1 for t in topics if t['oncelik']=='dusuk')}")


if __name__ == "__main__":
    main()
