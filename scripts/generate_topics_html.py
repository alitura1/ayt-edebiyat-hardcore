"""
13 konu için HTML dosyalarını üret.
Mock HtmlDoc objesi → sections_topics içeriği aynı API ile HTML'e dönüşür.
"""
import sys, io, json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = Path(__file__).parent.parent.parent  # Edebiyat Analiz/
sys.path.insert(0, str(BASE))

SITE = Path(__file__).parent.parent / 'public' / 'data' / 'topics'
SITE.mkdir(parents=True, exist_ok=True)


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


class HtmlDoc:
    """python-docx Document API'sini simüle eden HTML üreteci."""
    def __init__(self):
        self.html = []
        self.in_list = False
        self.list_items = []

    def _flush_list(self):
        if self.in_list and self.list_items:
            self.html.append('<ul>')
            self.html.extend(self.list_items)
            self.html.append('</ul>')
            self.list_items = []
        self.in_list = False

    def append(self, frag):
        self._flush_list()
        self.html.append(frag)

    def add_li(self, frag):
        self.in_list = True
        self.list_items.append(frag)

    def output(self):
        self._flush_list()
        return '\n'.join(self.html)


# Renkler (helper'lardan kopya)
class _Color:
    def __init__(self, r,g,b): self.r, self.g, self.b = r,g,b

CLR_PRIMARY = _Color(0x1F, 0x3A, 0x5F)
CLR_ACCENT = _Color(0xC4, 0x1E, 0x3A)
CLR_HIGHLIGHT = _Color(0xFF, 0xC1, 0x07)
CLR_MUTED = _Color(0x6C, 0x75, 0x7D)
CLR_GREEN = _Color(0x2E, 0x7D, 0x32)
CLR_DARK = _Color(0x21, 0x21, 0x21)
CLR_HIGHLIGHT_BG = "FFF3CD"
CLR_DANGER_BG = "F8D7DA"
CLR_OK_BG = "D4EDDA"
CLR_LIGHT_BG = "E8EEF4"


# === HTML helper'lar (sections_topics API'sini taklit) ===

def add_heading(doc, text, level):
    h = max(2, min(level + 1, 6))  # H1 üst başlık (sayfa header), bizim h2+
    doc.append(f'<h{h}>{esc(text)}</h{h}>')

def add_para(doc, text, bold=False, italic=False, size=None, color=None, align=None):
    style = ''
    if bold: text = f'<strong>{esc(text)}</strong>'
    else: text = esc(text)
    if italic: text = f'<em>{text}</em>'
    if color is CLR_ACCENT: style = 'color:#C41E3A;'
    elif color is CLR_PRIMARY: style = 'color:#1F3A5F;'
    elif color is CLR_GREEN: style = 'color:#2E7D32;'
    elif color is CLR_MUTED: style = 'color:#6C757D;'
    style_attr = f' style="{style}"' if style else ''
    doc.append(f'<p{style_attr}>{text}</p>')

def add_bullet(doc, text, level=0):
    indent = '&nbsp;' * (level * 4)
    doc.add_li(f'<li>{indent}{esc(text)}</li>')

def add_numbered(doc, text):
    doc.add_li(f'<li>{esc(text)}</li>')

def add_horizontal_rule(doc):
    doc.append('<hr>')

def add_callout(doc, title, body, bg_color=None, title_color=None):
    cls = 'osym-box'  # default sarı
    if bg_color == CLR_OK_BG: cls = 'ezber-box'
    elif bg_color == CLR_DANGER_BG: cls = 'tuzak-box'
    elif bg_color == CLR_LIGHT_BG: cls = 'mebi-box'
    title_html = f'<strong>{esc(title)}</strong>' if title else ''
    body_html = ''
    if isinstance(body, str):
        body_html = f'<div>{esc(body)}</div>'
    else:
        for line in body:
            body_html += f'<div>{esc(line)}</div>'
    doc.append(f'<div class="{cls}">{title_html}{body_html}</div>')

def add_tuzak(doc, body):
    add_callout(doc, '⚠ TUZAK', body, bg_color=CLR_DANGER_BG)

def add_ezber(doc, title, body):
    add_callout(doc, f'✓ EZBER PAKETİ — {title}', body, bg_color=CLR_OK_BG)

def add_osym_note(doc, body):
    add_callout(doc, 'ÖSYM NASIL SORUYOR', body, bg_color=CLR_HIGHLIGHT_BG)

def add_mebi_ref(doc, pages, note=""):
    note_html = f' — <em>{esc(note)}</em>' if note else ''
    doc.append(f'<div class="mebi-box"><strong>📘 MEBİ KONU ÖZETİ</strong> → ayt-tde.pdf sayfa <strong>{esc(pages)}</strong>{note_html}</div>')

def add_table_from_data(doc, headers, rows, col_widths_cm=None, first_col_bold=False):
    html = ['<table>']
    html.append('<thead><tr>')
    for h in headers:
        html.append(f'<th>{esc(h)}</th>')
    html.append('</tr></thead>')
    html.append('<tbody>')
    for row in rows:
        html.append('<tr>')
        for i, c in enumerate(row):
            bold = first_col_bold and i == 0
            cv = f'<strong>{esc(c)}</strong>' if bold else esc(c)
            html.append(f'<td>{cv}</td>')
        html.append('</tr>')
    html.append('</tbody></table>')
    doc.append('\n'.join(html))

def add_sample_question(doc, qno, year, topic, content_preview, answer=None, ipucu=None):
    doc.append(f'<div class="osym-box"><strong>📌 Soru {qno} ({year}) — {esc(topic)}</strong><br><em>{esc(content_preview)}</em>'
               + (f'<br>→ <strong>Cevap: {esc(answer)}</strong>' if answer else '')
               + (f'<br><small>İpucu: {esc(ipucu)}</small>' if ipucu else '')
               + '</div>')

def add_subtopic_block(*args, **kwargs):
    pass  # used directly in section files


# Monkey-patch ile sections_topics modülünün helpers'ını override et
import docx_helpers
import mebi_map

# Override
docx_helpers.add_heading = add_heading
docx_helpers.add_para = add_para
docx_helpers.add_bullet = add_bullet
docx_helpers.add_numbered = add_numbered
docx_helpers.add_callout = add_callout
docx_helpers.add_tuzak = add_tuzak
docx_helpers.add_ezber = add_ezber
docx_helpers.add_osym_note = add_osym_note
docx_helpers.add_mebi_ref = add_mebi_ref
docx_helpers.add_table_from_data = add_table_from_data
docx_helpers.add_horizontal_rule = add_horizontal_rule
docx_helpers.add_sample_question = add_sample_question
docx_helpers.add_subtopic_block = add_subtopic_block
docx_helpers.CLR_PRIMARY = CLR_PRIMARY
docx_helpers.CLR_ACCENT = CLR_ACCENT
docx_helpers.CLR_HIGHLIGHT = CLR_HIGHLIGHT
docx_helpers.CLR_MUTED = CLR_MUTED
docx_helpers.CLR_GREEN = CLR_GREEN
docx_helpers.CLR_DARK = CLR_DARK
docx_helpers.CLR_HIGHLIGHT_BG = CLR_HIGHLIGHT_BG
docx_helpers.CLR_DANGER_BG = CLR_DANGER_BG
docx_helpers.CLR_OK_BG = CLR_OK_BG
docx_helpers.CLR_LIGHT_BG = CLR_LIGHT_BG


# topic_header'ın frequency table'ı için
def topic_header_html(doc, no, title, total, dist, mebi_code=None):
    # Bu bölümde Header'ı atlıyoruz çünkü site sayfası kendi header'ı koyar
    # Sadece frequency table + MEBİ ref koy
    headers = ['Yıl'] + [str(2018+i) for i in range(8)] + ['Top.']
    row = ['Soru'] + [str(d) if d > 0 else '—' for d in dist] + [str(total)]
    add_table_from_data(doc, headers, [row])
    if mebi_code:
        m = mebi_map.MEBI_TOPIC.get(mebi_code)
        if m:
            add_mebi_ref(doc, m['pages'], m['note'])


# Şimdi sections_topics içeriğini al
# sub_mebi fonksiyonu zaten add_mebi_ref kullanıyor, patch'lendi
import sections_topics
import sections_topics2

# sections_topics içindeki topic_header'ı override et
sections_topics.topic_header = topic_header_html
sections_topics2.topic_header = topic_header_html


# REVİZYON 4 — Ek alt başlıklar
import topic_extras

# Slug → (ana fonksiyon, ek alt başlık fonksiyonu) mapping
TOPIC_FUNCS = [
    ('divan_edebiyati', sections_topics.divan_section, None),
    ('cumhuriyet', sections_topics.cumhuriyet_section, None),
    ('siir_bilgisi', sections_topics.siir_bilgisi_section, topic_extras.siir_bilgisi_extras),
    ('soz_sanatlari', sections_topics.soz_sanatlari_section, None),
    ('nesir_bilgisi', sections_topics2.nesir_bilgisi_section, topic_extras.nesir_bilgisi_extras),
    ('tanzimat', sections_topics2.tanzimat_section, None),
    ('servet-i-funun', sections_topics2.servet_funun_section, None),
    ('milli_edebiyat', sections_topics2.milli_edebiyat_section, None),
    ('halk_edebiyati', sections_topics2.halk_edebiyati_section, topic_extras.halk_extras),
    ('islamiyet-oncesi-gecis', sections_topics2.islamiyet_oncesi_section, topic_extras.islamiyet_oncesi_extras),
    ('geleneksel-tiyatro', sections_topics2.geleneksel_tiyatro_section, topic_extras.geleneksel_tiyatro_extras),
    ('masal-fabl-destan', sections_topics2.masal_destan_section, topic_extras.masal_destan_extras),
    ('edebi_akimlar', sections_topics2.edebi_akimlar_section, None),
]


def main():
    print(f"13 konu HTML üretiliyor → {SITE}")
    for slug, func, extras in TOPIC_FUNCS:
        doc = HtmlDoc()
        try:
            func(doc)
            if extras:
                extras(doc)
        except Exception as e:
            print(f"  ✗ {slug} HATA: {e}")
            continue
        html = doc.output()
        out_path = SITE / f'{slug}.html'
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        size_kb = out_path.stat().st_size / 1024
        extras_note = ' [+extras]' if extras else ''
        print(f"  ✓ {slug}.html ({size_kb:.1f} KB, {len(html.split(chr(10)))} satır){extras_note}")


if __name__ == '__main__':
    main()
