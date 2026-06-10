// REV20 — Edebî Terimler/Kavramlar sözlüğü + kategoriden quiz
import { Data, getDataSubject } from '../lib/data.js';

function esc(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

export async function renderTerms() {
  const data = await Data.terms();
  const donemler = (data && data.donemler) || [];

  window.__pageSetup = () => {
    const q = document.getElementById('termsSearch');
    q?.addEventListener('input', () => {
      const term = q.value.toLowerCase().trim();
      let anyVisible = {};
      document.querySelectorAll('[data-term-row]').forEach(r => {
        const show = !term || r.dataset.termRow.toLowerCase().includes(term);
        r.style.display = show ? '' : 'none';
      });
      // boş kalan kategori bloklarını gizle
      document.querySelectorAll('[data-kat-block]').forEach(b => {
        const visible = b.querySelectorAll('[data-term-row]:not([style*="display: none"])').length;
        b.style.display = visible ? '' : 'none';
      });
    });
  };

  const totalTerim = donemler.reduce((s, d) => s + d.kategoriler.reduce((a, k) => a + k.terimler.length, 0), 0);

  if (!donemler.length) {
    return `<div class="text-center py-12 text-slate-500">Terim verisi yüklenemedi.</div>`;
  }

  return `
    <header class="mb-5">
      <h1 class="text-3xl font-bold mb-1">📚 Edebî Terimler & Kavramlar</h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm">
        Dönem-spesifik tür/terim/kavramlar (fütüvvetname, sefaretname, sagu, koşuk, gazel...) —
        <strong>${totalTerim} terim</strong>. Gözat, ara, kategoriden veya hepsinden quiz çöz.
      </p>
    </header>

    <div class="flex flex-wrap gap-2 mb-5 items-center">
      <input id="termsSearch" type="search" placeholder="Terim ara: fütüvvetname, sagu..."
        class="flex-1 min-w-[200px] px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900" />
      <a href="#/quiz?terim=hepsi&sayi=20" class="px-4 py-2 rounded-md bg-accent-500 text-white font-bold text-sm hover:bg-accent-600">
        🎯 Tüm terimlerden quiz
      </a>
    </div>

    ${donemler.map(d => `
      <section class="mb-7">
        <h2 class="text-lg font-bold mb-3 text-primary-700 dark:text-primary-100 border-b border-slate-200 dark:border-slate-700 pb-1">${esc(d.donem)}</h2>
        ${d.kategoriler.map(k => `
          <div data-kat-block class="mb-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden">
            <div class="flex items-center justify-between gap-2 px-3 py-2 bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-700">
              <h3 class="font-bold text-sm">${esc(k.kategori_label)} <span class="text-slate-400 font-normal">· ${k.terimler.length} terim</span></h3>
              <a href="#/quiz?terim=${encodeURIComponent(k.kategori)}&sayi=15"
                 class="text-[11px] font-bold px-2.5 py-1 rounded-full bg-primary-700 text-white hover:bg-primary-800 whitespace-nowrap">
                🎯 Bu kategoriden quiz
              </a>
            </div>
            <div class="divide-y divide-slate-100 dark:divide-slate-800">
              ${k.terimler.map(t => `
                <div data-term-row="${esc(t.terim)} ${esc(t.tanim)}" class="px-3 py-2.5">
                  <div class="font-semibold text-sm text-slate-900 dark:text-slate-100">${esc(t.terim)}</div>
                  <div class="text-sm text-slate-700 dark:text-slate-300 mt-0.5">${esc(t.tanim)}</div>
                  ${t.ornek ? `<div class="text-xs text-slate-500 mt-1">📖 ${esc(t.ornek)}</div>` : ''}
                  ${t.ayirt_edici ? `<div class="text-xs text-warn-600 dark:text-warn-400 mt-1">⚠ ${esc(t.ayirt_edici)}</div>` : ''}
                </div>
              `).join('')}
            </div>
          </div>
        `).join('')}
      </section>
    `).join('')}
  `;
}
