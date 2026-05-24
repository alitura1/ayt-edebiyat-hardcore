"""Cevap anahtarı PDF'inden okunan answer key'i cards-auto.json'a uygular.

Source: Kullanıcının paylaştığı CEVAP ANAHTARI görseli (TYT Çıkmış Sorular PDF ekstra)
Strategy: ders + num ile cards-auto'da match → dogru alanını doldur.
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
CARDS_PATH = DATA_DIR / "cards-auto.json"

# Cevap anahtarı (görselden manuel okundu)
ANSWERS = {
    "fizik": {
        1: "E", 2: "B", 3: "C", 4: "B", 5: "A", 6: "E", 7: "D", 8: "E", 9: "C", 10: "E",
        11: "D", 12: "A", 13: "E", 14: "B", 15: "D", 16: "E", 17: "A", 18: "D", 19: "D", 20: "D",
        21: "B", 22: "C", 23: "A", 24: "B", 25: "E", 26: "A", 27: "D", 28: "A", 29: "E", 30: "B",
        31: "E", 32: "D", 33: "B", 34: "A", 35: "E", 36: "D", 37: "E", 38: "A", 39: "A", 40: "D",
        41: "D", 42: "A", 43: "A", 44: "A", 45: "D", 46: "B", 47: "D", 48: "C", 49: "C", 50: "A",
        51: "C", 52: "E", 53: "C", 54: "D", 55: "D", 56: "A",
    },
    "kimya": {
        1: "A", 2: "C", 3: "A", 4: "E", 5: "B", 6: "C", 7: "B", 8: "D", 9: "E", 10: "B",
        11: "C", 12: "B", 13: "E", 14: "C", 15: "C", 16: "D", 17: "A", 18: "A", 19: "D", 20: "A",
        21: "D", 22: "C", 23: "C", 24: "C", 25: "D", 26: "C", 27: "B", 28: "C", 29: "A", 30: "C",
        31: "A", 32: "E", 33: "C", 34: "E", 35: "D", 36: "C", 37: "A", 38: "A", 39: "B", 40: "B",
        41: "E", 42: "B", 43: "B", 44: "B", 45: "A", 46: "D", 47: "D", 48: "D", 49: "C", 50: "A",
        # 51. soru görselde "51.." okunamadı → null
        52: "E", 53: "C", 54: "A",
    },
    "biyoloji": {
        1: "C", 2: "B", 3: "E", 4: "E", 5: "D", 6: "A", 7: "D", 8: "C", 9: "B", 10: "B",
        11: "D", 12: "A", 13: "D", 14: "D", 15: "B", 16: "E", 17: "C", 18: "B", 19: "A", 20: "E",
        21: "E", 22: "D", 23: "E", 24: "A", 25: "E", 26: "C", 27: "B", 28: "E", 29: "D", 30: "E",
        31: "C", 32: "B", 33: "D", 34: "D", 35: "D", 36: "D", 37: "E", 38: "E", 39: "C", 40: "C",
        41: "E", 42: "D", 43: "D", 44: "E", 45: "E", 46: "E", 47: "E",
    },
}

# Yükle
with open(CARDS_PATH, encoding="utf-8") as f:
    cards = json.load(f)

filled = 0
missing = 0
mismatch = []  # ders+num eşleşmeyen kartlar

for c in cards:
    ders = c.get("ders")
    num = c.get("num")
    if not ders or not num:
        missing += 1
        continue
    answer = ANSWERS.get(ders, {}).get(num)
    if answer:
        c["dogru"] = answer
        filled += 1
    else:
        c["dogru"] = None
        mismatch.append(f"{ders}#{num}")

# Yaz
with open(CARDS_PATH, "w", encoding="utf-8") as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

# Rapor
from collections import Counter
by_ders = Counter(c["ders"] for c in cards if c.get("dogru"))
print(f"✓ Toplam kart: {len(cards)}")
print(f"✓ Cevap doldurulan: {filled}")
print(f"  Ders dağılımı (cevaplı): {dict(by_ders)}")
print(f"✗ Cevap bulunamayan: {len(mismatch)} {mismatch[:10] if mismatch else ''}")
print(f"  num/ders eksik kart: {missing}")
print(f"\nNot: Kimya #51 görselde 'cevap noksanlığı' (51..) — null bırakıldı.")

# Hangi cevap anahtarı slot'ları kullanılmadı? (parser kaçırmış olabilir)
used_slots = {(c["ders"], c["num"]) for c in cards if c.get("ders") and c.get("num")}
unused = []
for ders, ans in ANSWERS.items():
    for num in ans:
        if (ders, num) not in used_slots:
            unused.append(f"{ders}#{num}")
if unused:
    print(f"\n⚠ Parser kaçırdı (cevap var ama kart yok): {unused}")
