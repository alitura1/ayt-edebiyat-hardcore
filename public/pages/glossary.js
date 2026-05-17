import { Data } from '../lib/data.js';

export async function renderGlossary() {
  const g = await Data.glossary();

  window.__pageSetup = () => {
    const q = document.getElementById('glossarySearch');
    q?.addEventListener('input', () => {
      const term = q.value.toLowerCase().trim();
      document.querySelectorAll('[data-row]').forEach(r => {
        const t = r.dataset.row.toLowerCase();
        r.style.display = !term || t.includes(term) ? '' : 'none';
      });
    });
  };

  return `
    <header class="mb-6">
      <h1 class="text-3xl font-bold mb-1">📖 Mini Sözlük</h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm">Tek bakışta tablolar: akımlar, dönemler, söz sanatları, Tanzimat "ilk"leri, alfabetik yazar-eser.</p>
    </header>

    <input id="glossarySearch" type="search" placeholder="Akım/yazar/eser ara..." class="w-full px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 mb-5" />

    ${g.bolumler.map(b => `
      <section class="mb-6">
        <h2 class="text-xl font-bold mb-2">${b.baslik}</h2>
        <div class="overflow-x-auto bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
          <table class="w-full text-sm">
            <thead class="bg-primary-700 text-white">
              <tr>${b.basliklar.map(h => `<th class="text-left px-2 py-2">${h}</th>`).join('')}</tr>
            </thead>
            <tbody>
              ${b.satirlar.map(row => `
                <tr data-row="${row.join(' ')}" class="border-t border-slate-200 dark:border-slate-800">
                  ${row.map((c, i) => `<td class="px-2 py-1.5 ${i === 0 ? 'font-semibold' : ''}">${c}</td>`).join('')}
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </section>
    `).join('')}
  `;
}
