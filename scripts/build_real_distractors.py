# -*- coding: utf-8 -*-
"""
REV19c — Gerçek ÖSYM Çeldiri Birliktelikleri

Çıkmış 192 sorunun ŞIK YAZARLARINI (siklar_yazarlari) inceler: ÖSYM bir soruda
hangi yazarları BİRLİKTE şık yaptıysa, bunlar gerçek (otantik) çeldiri çiftleridir.
Bu, "aynı dönem rastgele" yerine ÖSYM'nin fiilen kullandığı tuzakları verir.

Output: data/real_distractors.json
  { yazar: [co_occurring_yazar, ...] }   (frekansa göre sıralı)
"""
import json
import sys
import io
from pathlib import Path
from collections import defaultdict, Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent.parent
CIKMIS = ROOT / 'edebiyat-site' / 'public' / 'data' / 'edebiyat' / 'cikmis-sorular.json'
OUT = ROOT / 'data' / 'real_distractors.json'

# Alias birleştirme (kısa form → kanonik) — all_authors ile tutarlı
ALIAS = {
    'Recaizade': 'Recaizade Mahmut Ekrem',
    'Ahmet Mithat': 'Ahmet Mithat Efendi',
    'Refik Halit': 'Refik Halit Karay',
    'Yakup Kadri': 'Yakup Kadri Karaosmanoğlu',
    'Abdülhak Hamit': 'Abdülhak Hamit Tarhan',
    'Yahya Kemal': 'Yahya Kemal Beyatlı',
    'Necati': 'Necati Bey',
    'Neşâti': 'Neşati',
}


def canon(n):
    return ALIAS.get(n, n)


def main():
    d = json.load(open(CIKMIS, encoding='utf-8'))
    qs = d.get('questions', [])
    co = defaultdict(Counter)
    nq = 0
    for q in qs:
        sy = q.get('siklar_yazarlari', [])
        # Şık (in_option) yazarları = gerçek çeldiriciler + doğru
        names = sorted(set(canon(s['name']) for s in sy
                           if s.get('name') and s.get('role') == 'in_option'))
        if len(names) < 2:
            continue
        nq += 1
        for a in names:
            for b in names:
                if a != b:
                    co[a][b] += 1
    result = {a: [n for n, _ in c.most_common()] for a, c in co.items()}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f'✓ real_distractors.json: {len(result)} yazar, {nq} sorudan → {OUT}')
    # En zengin 12
    for a in sorted(result, key=lambda x: -len(result[x]))[:12]:
        print(f'  {a:<24} ÖSYM çeldirileri: {", ".join(result[a][:5])}')


if __name__ == '__main__':
    main()
