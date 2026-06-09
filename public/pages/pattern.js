// REV17 — /sistem sayfası: ÖSYM "matematiksel sistem" görselleştirmesi
// Konu × yıl heatmap + Top 30 yazar tablosu + periyodicity grafiği
import { Data } from '../lib/data.js';

const TOPIC_ORDER = [
  'sozcukte_anlam', 'cumlede_anlam', 'paragrafta_anlam',
  'siir_bilgisi', 'soz_sanatlari', 'nesir_bilgisi',
  'islamiyet_oncesi_gecis', 'halk_edebiyati', 'divan_edebiyati',
  'tanzimat', 'servet_i_funun_fecr_i_ati', 'milli_edebiyat', 'cumhuriyet',
  'geleneksel_tiyatro', 'masal_fabl_destan', 'edebi_akimlar'
];

const TOPIC_LABEL = {
  sozcukte_anlam: 'Sözcükte Anlam',
  cumlede_anlam: 'Cümlede Anlam',
  paragrafta_anlam: 'Paragrafta Anlam',
  siir_bilgisi: 'Şiir Bilgisi',
  soz_sanatlari: 'Söz Sanatları',
  nesir_bilgisi: 'Nesir Bilgisi',
  islamiyet_oncesi_gecis: 'İslamiyet Öncesi / Geçiş',
  halk_edebiyati: 'Halk Edebiyatı',
  divan_edebiyati: 'Divan Edebiyatı',
  tanzimat: 'Tanzimat',
  servet_i_funun_fecr_i_ati: 'Servet-i Fünun',
  milli_edebiyat: 'Milli Edebiyat',
  cumhuriyet: 'Cumhuriyet',
  geleneksel_tiyatro: 'Geleneksel Tiyatro',
  masal_fabl_destan: 'Masal / Fabl / Destan',
  edebi_akimlar: 'Edebi Akımlar',
};

const PRIORITY_COLOR = {
  'ÇOK YÜKSEK': 'bg-accent-500 text-white',
  'YÜKSEK': 'bg-warn-500 text-white',
  'ORTA': 'bg-primary-500 text-white',
  'DÜŞÜK': 'bg-slate-400 text-white',
  'İHMAL': 'bg-slate-300 text-slate-600',
};

function priorityBadge(p) {
  return `<span class="text-[10px] font-bold px-2 py-0.5 rounded ${PRIORITY_COLOR[p] || 'bg-slate-200'}">${p}</span>`;
}

function scoreBar(score, max = 100) {
  const pct = Math.round(score);
  const color = pct >= 80 ? 'bg-accent-500' : pct >= 60 ? 'bg-warn-500' : pct >= 40 ? 'bg-primary-500' : 'bg-slate-400';
  return `
    <div class="flex items-center gap-1.5">
      <div class="flex-1 h-2 bg-slate-200 dark:bg-slate-800 rounded overflow-hidden">
        <div class="${color} h-full transition-all" style="width:${pct}%"></div>
      </div>
      <span class="text-xs font-bold w-7 text-right">${pct}</span>
    </div>
  `;
}

export async function renderPattern() {
  // pattern_analysis.json'u doğrudan oku (Data helper'ı yok henüz)
  let pa = null;
  try {
    const res = await fetch('./data/edebiyat/pattern_analysis.json', { cache: 'no-cache' });
    if (res.ok) pa = await res.json();
  } catch (e) { /* no-op */ }

  if (!pa) {
    // Fallback: predictions.json'dan al
    const p = await Data.predictions();
    if (!p.pattern_konu_skorlari) {
      return `
        <div class="text-center py-12">
          <h1 class="text-2xl font-bold mb-3">🧮 Pattern Engine</h1>
          <p class="text-slate-500">pattern_analysis.json bulunamadı.</p>
        </div>
      `;
    }
    pa = {
      konular: (p.pattern_konu_skorlari || []).map(k => ({
        kod: k.kod, due_score: k.due_score, priority: k.priority,
        freq_8yil: k.freq, raw_count: k.raw_count,
        years_active: [], last_year: k.last_year, current_gap: k.current_gap,
        rationale: k.rationale,
      })),
      yazarlar: (p.top_20_yazar_2026 || []).map(y => ({
        name: y.ad, due_score: y.due_score, priority: y.priority,
        freq_8yil: y.freq, last_year: y.son_yil, current_gap: y.current_gap,
        rationale: y.rationale,
      })),
      span: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
    };
  }

  const span = pa.span || [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025];
  const konuByKod = {};
  for (const k of pa.konular || []) konuByKod[k.kod] = k;

  // ----- Heatmap: 16 konu × 8 yıl -----
  // Cell renk: yıl o konuda kaç soru. Yoğun = koyu kırmızı.
  const yearTopicCount = {};  // yearTopicCount[topic][year] = count
  // pattern_analysis.json'dan years_active liste, ama raw count per year yok
  // Yine de years_active ile binary işaretle (var/yok), raw_count başlık
  for (const k of pa.konular || []) {
    yearTopicCount[k.kod] = {};
    for (const y of (k.years_active || [])) {
      yearTopicCount[k.kod][y] = (yearTopicCount[k.kod][y] || 0) + 1;
    }
  }

  function heatCell(topic, year) {
    const k = konuByKod[topic];
    if (!k) return `<td class="border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 text-center text-[10px]">—</td>`;
    const has = k.years_active.includes(year);
    const cls = has ? 'bg-primary-500/40 dark:bg-primary-500/30' : 'bg-slate-50 dark:bg-slate-900';
    return `<td class="border border-slate-200 dark:border-slate-800 ${cls} text-center text-[10px] py-1">${has ? '●' : '·'}</td>`;
  }

  const konuList = TOPIC_ORDER.filter(k => konuByKod[k]);

  return `
    <header class="mb-6">
      <h1 class="text-3xl font-bold mb-1">🧮 Pattern Engine — ÖSYM Matematiksel Sistemi</h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm">8 yıllık veriden (2018-2025) konu × alt-konu × yazar bazlı periyodicity + gap analizi. <strong>Skor 80+ = vadesi geçti, 2026'da telafi olası</strong>.</p>
    </header>

    <!-- REV19c — 2026 Ziya Gökalp Anma Yılı callout -->
    <section class="mb-8 rounded-xl p-4 bg-gradient-to-r from-amber-400/20 to-yellow-300/10 border-2 border-amber-400/50">
      <div class="flex items-start gap-3">
        <div class="text-3xl">⭐</div>
        <div class="flex-1">
          <h2 class="text-lg font-bold text-amber-800 dark:text-amber-200">2026 Resmî Ziya Gökalp Anma Yılı</h2>
          <p class="text-sm text-slate-700 dark:text-slate-300 mt-1">
            TÜRKSOY, 2026'yı Ziya Gökalp'in <strong>150. doğum yılı</strong> dolayısıyla "Ziya Gökalp Anma Yılı" ilan etti (UNESCO başvurusu yapıldı).
            Pattern engine bunu manuel sinyalle birleştirdi: <strong>Ziya Gökalp → ÇOK YÜKSEK (85/100)</strong>.
            Anma yıllarında ilgili sanatçının sınavda öne çıkma ihtimali artar — <strong>Milli Edebiyat / Genç Kalemler</strong> çevresine (Ömer Seyfettin, Ali Canip) de göz at.
          </p>
          <div class="mt-2 flex flex-wrap gap-2 text-xs">
            <a href="#/yazarlar/ziya-gokalp" class="px-3 py-1 rounded-full bg-amber-500 text-white font-semibold hover:bg-amber-600">Ziya Gökalp profili →</a>
            <a href="#/quiz?yazar=ziya-gokalp&sayi=10" class="px-3 py-1 rounded-full border border-amber-500 text-amber-700 dark:text-amber-300 font-semibold hover:bg-amber-400/10">Ziya Gökalp'ten 10 soru çöz</a>
          </div>
        </div>
      </div>
      <p class="text-[11px] text-slate-500 mt-2 italic">Not: Anma yılı → ÖSYM'de soru garantisi değildir; istatistiksel bir ihtimal sinyalidir.</p>
    </section>

    <section class="mb-8">
      <h2 class="text-xl font-bold mb-3">📊 Konu × Yıl Heatmap</h2>
      <p class="text-sm text-slate-500 mb-3">Hangi konu hangi yıl gelmiş — periyodik desen göz yordamı.</p>
      <div class="overflow-x-auto bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
        <table class="w-full text-xs">
          <thead class="bg-primary-700 text-white">
            <tr>
              <th class="text-left px-2 py-2 sticky left-0 bg-primary-700">Konu</th>
              ${span.map(y => `<th class="text-center px-2 py-2 min-w-[40px]">${y}</th>`).join('')}
              <th class="text-center px-2 py-2">Skor</th>
              <th class="text-left px-2 py-2">Öncelik</th>
            </tr>
          </thead>
          <tbody>
            ${konuList.map(kod => {
              const k = konuByKod[kod];
              return `
                <tr class="border-t border-slate-200 dark:border-slate-800">
                  <td class="px-2 py-2 font-semibold sticky left-0 bg-white dark:bg-slate-900 z-10">${TOPIC_LABEL[kod] || kod}</td>
                  ${span.map(y => heatCell(kod, y)).join('')}
                  <td class="px-2 py-1 min-w-[120px]">${scoreBar(k.due_score)}</td>
                  <td class="px-2 py-2">${priorityBadge(k.priority)}</td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
      <p class="text-[11px] text-slate-500 mt-2">● = o yıl o konudan soru var · · = yok. Yoğun ● = düzenli; seyrek = periyodik aralıklı.</p>
    </section>

    <section class="mb-8">
      <h2 class="text-xl font-bold mb-3">🎯 Top 30 Yazar — Due Score</h2>
      <p class="text-sm text-slate-500 mb-3">Matematiksel formül: gap × freq × periyodicity. Yüksek skor = ÖSYM 2026'da bu yazara dönecek olasılığı yüksek.</p>
      <div class="overflow-x-auto bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
        <table class="w-full text-sm">
          <thead class="bg-primary-700 text-white">
            <tr>
              <th class="text-left px-3 py-2">#</th>
              <th class="text-left px-3 py-2">Yazar</th>
              <th class="text-center px-2 py-2 min-w-[140px]">Skor</th>
              <th class="text-left px-2 py-2">Öncelik</th>
              <th class="text-center px-2 py-2">Freq</th>
              <th class="text-center px-2 py-2">Son</th>
              <th class="text-center px-2 py-2">Gap</th>
            </tr>
          </thead>
          <tbody>
            ${(pa.yazarlar || []).slice(0, 30).map((y, i) => `
              <tr class="border-t border-slate-200 dark:border-slate-800">
                <td class="px-3 py-2 text-slate-500">${i + 1}</td>
                <td class="px-3 py-2 font-semibold">${y.name}</td>
                <td class="px-2 py-1">${scoreBar(y.due_score)}</td>
                <td class="px-2 py-2">${priorityBadge(y.priority)}</td>
                <td class="text-center px-2 py-2 text-xs text-slate-500">${y.freq_8yil}</td>
                <td class="text-center px-2 py-2 text-xs text-slate-500">${y.last_year ?? '—'}</td>
                <td class="text-center px-2 py-2 text-xs">
                  <span class="${y.current_gap >= 3 ? 'text-accent-500 font-bold' : 'text-slate-500'}">${y.current_gap ?? '—'}</span>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </section>

    <section class="mb-8 bg-primary-500/10 border-2 border-primary-500/30 rounded-lg p-5">
      <h3 class="font-bold mb-2">🧠 Formül Açıklaması</h3>
      <ul class="text-sm space-y-1 text-slate-700 dark:text-slate-300">
        <li><strong>freq_8yil</strong> — 2018-2025 arası farklı yıllarda kaç defa geldi</li>
        <li><strong>current_gap</strong> — 2026'ya kalan boş yıl sayısı (last_year - 2026)</li>
        <li><strong>expected_period</strong> — 8 / freq (her N yılda bir gelmesi beklenir)</li>
        <li><strong>gap_ratio</strong> — current_gap / expected_period (1'den büyük = vadesi geçti)</li>
        <li><strong>recency_decay</strong> — geçen yıl geldi ise düşük (0.2-0.6), 2+ yıl önce geldi ise tam (1.0)</li>
        <li><strong>trend_bonus</strong> — son 3 yıl ardışık gelmiş + freq orta = yükseliş trendi, +18</li>
      </ul>
      <div class="mt-3 text-xs text-slate-600 dark:text-slate-400 font-mono bg-white dark:bg-slate-900 p-2 rounded">
        due_score = 100 × (gap_ratio)^0.7 × log₁₀(1+freq) × recency_decay × (1 + 0.3·periodic_regularity) + trend_bonus
      </div>
    </section>

    <section class="text-center">
      <a href="#/tahminler" class="inline-block px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 text-sm font-semibold">📜 Tahminler sayfasına geç</a>
      <a href="#/quiz/setup" class="inline-block ml-2 px-4 py-2 bg-accent-600 text-white rounded-md hover:bg-accent-700 text-sm font-semibold">🎯 Bu skorlarla quiz çöz</a>
    </section>
  `;
}
