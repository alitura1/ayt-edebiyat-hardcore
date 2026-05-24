// REV20 — Hangi dersi çalışıyorsun? gate sayfası
// İlk açılışta veya header toggle'tan çağrılır.
// Migration: eski edebiyat-state-v1 → state-v2-edebiyat (Edebiyat seçildiğinde)
import { saveSubjectPreference, migrateOldData } from '../lib/store.js';
import { setDataSubject } from '../lib/data.js';
import { refreshSyncForSubject } from '../lib/sync.js';

export async function renderSelectSubject() {
  return `
    <section class="max-w-3xl mx-auto py-12 px-4">
      <div class="text-center mb-10">
        <h1 class="text-4xl md:text-5xl font-extrabold mb-3 text-primary-700 dark:text-primary-100">
          AYT Hardcore Hazırlık
        </h1>
        <p class="text-slate-600 dark:text-slate-400 text-lg">
          Hangi dersi çalışmak istiyorsun?
        </p>
        <p class="text-xs text-slate-500 mt-2">
          İstediğin zaman header'dan diğerine geçebilirsin.
        </p>
      </div>

      <div class="grid md:grid-cols-3 gap-5">
        <!-- Edebiyat -->
        <button id="selectEdebiyat" class="group block text-left p-6 rounded-2xl border-2 border-sky-500/30 hover:border-sky-500 hover:bg-sky-50 dark:hover:bg-sky-900/30 transition-all">
          <div class="text-5xl mb-3">📚</div>
          <h2 class="text-2xl font-bold text-sky-700 dark:text-sky-200 mb-2 group-hover:text-sky-800">
            AYT Edebiyat
          </h2>
          <p class="text-sm text-slate-600 dark:text-slate-400 mb-3">
            85 yazar · 600+ kart · 13 konu · 251 eser
          </p>
          <p class="text-xs text-slate-500 italic">
            Yazar avı, ezber atışı
          </p>
        </button>

        <!-- Tarih -->
        <button id="selectTarih" class="group block text-left p-6 rounded-2xl border-2 border-amber-500/30 hover:border-amber-500 hover:bg-amber-50 dark:hover:bg-amber-900/30 transition-all">
          <div class="text-5xl mb-3">⏳</div>
          <h2 class="text-2xl font-bold text-amber-700 dark:text-amber-200 mb-2 group-hover:text-amber-800">
            AYT Tarih
          </h2>
          <p class="text-sm text-slate-600 dark:text-slate-400 mb-3">
            10 dönem · ÖSYM 2018-2025 analizi · 600+ kart hedefi
          </p>
          <p class="text-xs text-slate-500 italic">
            Tarihçi olma, tarihi yendin sayılır
          </p>
        </button>

        <!-- TYT Fen -->
        <button id="selectFen" class="group block text-left p-6 rounded-2xl border-2 border-emerald-500/30 hover:border-emerald-500 hover:bg-emerald-50 dark:hover:bg-emerald-900/30 transition-all">
          <div class="text-5xl mb-3">⚗</div>
          <h2 class="text-2xl font-bold text-emerald-700 dark:text-emerald-200 mb-2 group-hover:text-emerald-800">
            TYT Fen
            <span class="text-xs bg-emerald-100 dark:bg-emerald-900 text-emerald-700 dark:text-emerald-200 rounded-full px-2 py-0.5 ml-1 font-normal">Yeni</span>
          </h2>
          <p class="text-sm text-slate-600 dark:text-slate-400 mb-3">
            24 ünite · Fizik · Kimya · Biyoloji · 8 yıl ÖSYM frekansı
          </p>
          <p class="text-xs text-slate-500 italic">
            Sıcak alanlardan netleri uçur, 4 hafta plan
          </p>
        </button>
      </div>

      <div class="mt-10 p-4 bg-slate-100 dark:bg-slate-800/60 rounded-xl text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
        <strong class="text-slate-800 dark:text-slate-200">Veri güvenliği:</strong>
        Mevcut Edebiyat verin korunur. Hibrit yapıya geçişle her ders ayrı bir alanda saklanır,
        ilerlemen kaybolmaz. İki dersi de aynı hesapla cloud üzerinden senkronize edebilirsin.
      </div>
    </section>
  `;
}

export function setupSelectSubject() {
  document.getElementById('selectEdebiyat')?.addEventListener('click', async () => {
    // Önce migration — eski edebiyat-state-v1 → state-v2-edebiyat
    try { migrateOldData('edebiyat'); } catch (e) { console.warn('Migration:', e); }
    saveSubjectPreference('edebiyat');
    setDataSubject('edebiyat');
    document.documentElement.setAttribute('data-subject', 'edebiyat');
    try { await refreshSyncForSubject('edebiyat'); } catch (e) { /* offline */ }
    location.hash = '#/';
    setTimeout(() => location.reload(), 50);
  });

  document.getElementById('selectTarih')?.addEventListener('click', async () => {
    saveSubjectPreference('tarih');
    setDataSubject('tarih');
    document.documentElement.setAttribute('data-subject', 'tarih');
    try { await refreshSyncForSubject('tarih'); } catch (e) { /* offline */ }
    location.hash = '#/';
    setTimeout(() => location.reload(), 50);
  });

  document.getElementById('selectFen')?.addEventListener('click', async () => {
    saveSubjectPreference('fen');
    setDataSubject('fen');
    document.documentElement.setAttribute('data-subject', 'fen');
    try { await refreshSyncForSubject('fen'); } catch (e) { /* offline */ }
    location.hash = '#/';
    setTimeout(() => location.reload(), 50);
  });
}
