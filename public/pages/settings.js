import { exportAll, importAll, resetAll, loadState } from '../lib/store.js';

export async function renderSettings() {
  window.__pageSetup = () => {
    document.getElementById('btnExport')?.addEventListener('click', () => {
      const blob = new Blob([exportAll()], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `edebiyat-${new Date().toISOString().slice(0,10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
    });
    document.getElementById('importFile')?.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        if (importAll(reader.result)) {
          alert('Veri başarıyla yüklendi.');
          location.reload();
        }
      };
      reader.readAsText(file);
    });
    document.getElementById('btnReset')?.addEventListener('click', resetAll);
  };

  const state = loadState();
  return `
    <header class="mb-6">
      <h1 class="text-3xl font-bold mb-1">⚙️ Ayarlar</h1>
    </header>
    <div class="space-y-4 max-w-xl">
      <section class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4">
        <h3 class="font-bold mb-2">Veri Yedekleme</h3>
        <p class="text-sm text-slate-500 mb-3">Tüm ilerleme, hata defteri ve özel kartları JSON olarak indir/yükle. Cihazlar arası taşıma için.</p>
        <div class="flex gap-2 flex-wrap">
          <button id="btnExport" class="bg-primary-700 hover:bg-primary-900 text-white px-4 py-2 rounded-md font-semibold">📤 Dışa Aktar</button>
          <label class="bg-primary-700 hover:bg-primary-900 text-white px-4 py-2 rounded-md font-semibold cursor-pointer">
            📥 İçe Aktar
            <input id="importFile" type="file" accept="application/json" class="hidden" />
          </label>
        </div>
      </section>

      <section class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4">
        <h3 class="font-bold mb-2">Mevcut Veri</h3>
        <ul class="text-sm space-y-1 text-slate-600 dark:text-slate-400">
          <li>Çözülen kart: ${Object.keys(state.progress).length}</li>
          <li>Hata defteri: ${state.hata_defteri.length}</li>
          <li>Özel (manuel) kart: ${state.custom_kartlar.length}</li>
          <li>Program checkbox: ${Object.keys(state.program_checkbox).length}</li>
        </ul>
      </section>

      <section class="bg-accent-500/10 border-2 border-accent-500/30 rounded-lg p-4">
        <h3 class="font-bold mb-2 text-accent-500">⚠️ Tehlikeli Bölge</h3>
        <p class="text-sm text-slate-500 mb-3">Tüm ilerleme, hata defteri ve özel kartlar silinir. Geri alınamaz.</p>
        <button id="btnReset" class="bg-accent-500 hover:bg-accent-700 text-white px-4 py-2 rounded-md font-semibold">🗑️ Tümünü Sıfırla</button>
      </section>

      <section class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4 text-xs text-slate-500">
        <p>AYT Edebiyat Hardcore v1 — Statik web uygulaması, tüm veriler tarayıcında (localStorage). Sunucu yok, hesap yok, takip yok.</p>
      </section>
    </div>
  `;
}
