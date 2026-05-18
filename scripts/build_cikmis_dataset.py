"""
REV6 M1 — annotated_questions.json -> public/data/cikmis-sorular.json
192 sorunun raw_text'i temizlenip, parse edilip, yazar profillerine + eser detaylarına bağlanır.
Cevap anahtarı şu an yok (PDF'te kayıt yok). İleride ÖSYM resmi cevap anahtarı eklenebilir.
"""
import json, sys, io, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = Path(__file__).parent.parent.parent  # Edebiyat Analiz/
SRC = BASE / 'annotated_questions.json'
OUT = Path(__file__).parent.parent / 'public' / 'data' / 'cikmis-sorular.json'


def parse_options(raw_text):
    """raw_text içinden A-E şıklarını ayır."""
    # Pattern: "A) ... B) ... C) ... D) ... E) ..."
    # Tüm A-E'yi yakala, son şıktan sonra yıl kalır
    pattern = re.compile(r'([A-E])\)\s*(.*?)(?=\s+[A-E]\)|$)', re.DOTALL)
    matches = pattern.findall(raw_text)
    if not matches:
        return None
    options = []
    for letter, text in matches:
        text = text.strip()
        # son E şıkından sonra yıl etiketi ("2018-AYT") gelirse temizle
        text = re.sub(r'\s*\d{4}-AYT\s*$', '', text)
        text = re.sub(r'\s+', ' ', text)
        options.append({'id': letter, 'text': text})
    return options


def split_question_and_options(raw_text):
    """Soru gövdesi + şıkları ayır."""
    # İlk "A)" pozisyonunu bul
    m = re.search(r'\bA\)\s', raw_text)
    if not m:
        return raw_text.strip(), None
    body = raw_text[:m.start()].strip()
    opts_text = raw_text[m.start():]
    opts = parse_options(opts_text)
    # Soru numarası başında ise (örn "95.") ayır
    body = re.sub(r'^\d+\.\s*', '', body)
    # Yıl etiketini sondan temizle
    body = re.sub(r'\s*\d{4}-AYT\s*$', '', body)
    body = re.sub(r'\s+', ' ', body).strip()
    return body, opts


def main():
    if not SRC.exists():
        print(f"HATA: {SRC} yok")
        return
    src = json.loads(SRC.read_text(encoding='utf-8'))
    questions = src['questions']
    print(f"Kaynak: {len(questions)} soru")

    output = {
        'meta': {
            'count': len(questions),
            'years': sorted(set(q['year'] for q in questions)),
            'source': 'MEB Ortaöğretim Genel Müdürlüğü resmi çıkmış sorular 2018-2025',
            'note': 'Doğru cevaplar henüz işaretlenmedi — ÖSYM resmi cevap anahtarları sonra eklenebilir',
        },
        'questions': []
    }

    parsed_ok = 0
    parsed_fail = 0
    for q in questions:
        raw = q.get('raw_text', '').strip()
        body, opts = split_question_and_options(raw)
        parsed = {
            'qno': q['question_no'],
            'year': q['year'],
            'topic': q['topic_code'],
            'topic_label': q.get('topic_label', ''),
            'soru': body,
            'secenekler': opts or [],
            'has_options': bool(opts),
            'page': q.get('page_no'),
            'mentioned_authors': q.get('mentioned_authors', []),
            'mentioned_works': q.get('mentioned_works', []),
            'mentioned_movements': q.get('mentioned_movements', []),
            'tags': q.get('question_type_tags', []),
        }
        output['questions'].append(parsed)
        if opts:
            parsed_ok += 1
        else:
            parsed_fail += 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')

    size_kb = OUT.stat().st_size / 1024
    print(f"✓ {OUT.name} yazıldı ({size_kb:.1f} KB)")
    print(f"  şık parse edilen: {parsed_ok}")
    print(f"  şık parse edilmeyen: {parsed_fail}")
    print(f"  yıl aralığı: {output['meta']['years'][0]}-{output['meta']['years'][-1]}")


if __name__ == '__main__':
    main()
