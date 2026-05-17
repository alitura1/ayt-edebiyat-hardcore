import { Data, TOPIC_LABELS, topicLabel } from '../lib/data.js';
import { loadState, addCustomCard, updateCustomCard, deleteCustomCard } from '../lib/store.js';

export async function renderCardList() {
  const auto = await Data.cards();
  const state = loadState();
  const custom = state.custom_kartlar;

  window.__pageSetup = () => {
    const q = document.getElementById('cardSearch');
    const f = document.getElementById('cardFilter');
    function run() {
      const term = (q.value || '').toLowerCase().trim();
      const fv = f.value;
      document.querySelectorAll('[data-card-row]').forEach(r => {
        const t = r.dataset.cardRow.toLowerCase();
        const k = r.dataset.kaynak;
        let show = true;
        if (term && !t.includes(term)) show = false;
        if (fv && fv !== 'hepsi' && k !== fv) show = false;
        r.style.display = show ? '' : 'none';
      });
    }
    q?.addEventListener('input', run);
    f?.addEventListener('change', run);

    document.querySelectorAll('[data-del]').forEach(btn => {
      btn.addEventListener('click', () => {
        if (confirm('Bu kartı sil?')) {
          deleteCustomCard(btn.dataset.del);
          location.reload();
        }
      });
    });
  };

  return `
    <header class="mb-4 flex items-center justify-between gap-3 flex-wrap">
      <div>
        <h1 class="text-3xl font-bold mb-1">🃏 Kart Havuzu</h1>
        <p class="text-sm text-slate-500">${auto.length} otomatik + ${custom.length} özel kart</p>
      </div>
      <a href="#/kartlar/yeni" class="bg-accent-500 hover:bg-accent-700 text-white font-bold py-2 px-4 rounded-md">+ Yeni Kart</a>
    </header>
    <div class="flex gap-2 mb-3 flex-wrap">
      <input id="cardSearch" type="search" placeholder="Soru/yazar/konu ara..." class="flex-1 min-w-[200px] px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900" />
      <select id="cardFilter" class="px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900">
        <option value="hepsi">Tüm kartlar</option>
        <option value="otomatik">Sadece otomatik</option>
        <option value="manuel">Sadece özel (manuel)</option>
      </select>
    </div>
    <div class="space-y-2">
      ${[...custom, ...auto].map(c => `
        <div data-card-row="${escapeQ(c.soru + ' ' + topicLabel(c.konu) + ' ' + (c.aciklama || ''))}" data-kaynak="${c.kaynak || 'otomatik'}"
             class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-3">
          <div class="flex items-start justify-between gap-2 mb-1">
            <div class="text-xs text-slate-500 flex items-center gap-2 flex-wrap">
              <span class="bg-primary-50 dark:bg-primary-900/50 text-primary-700 dark:text-primary-100 px-1.5 py-0.5 rounded">${topicLabel(c.konu)}</span>
              ${c.alt_konu ? `<span>${c.alt_konu}</span>` : ''}
              <span>· ${c.tip || 'soru'}</span>
              ${c.kaynak === 'manuel' ? '<span class="text-accent-500">· özel</span>' : ''}
            </div>
            ${c.kaynak === 'manuel' ? `
              <div class="flex gap-1">
                <a href="#/kartlar/${c.id}" class="text-xs px-2 py-0.5 rounded hover:bg-slate-100 dark:hover:bg-slate-800">✏️</a>
                <button data-del="${c.id}" class="text-xs px-2 py-0.5 rounded hover:bg-slate-100 dark:hover:bg-slate-800">🗑️</button>
              </div>
            ` : ''}
          </div>
          <p class="text-sm">${truncate(c.soru, 200)}</p>
          <p class="text-xs text-ok-500 mt-1">→ ${c.dogru}) ${(c.secenekler.find(s => s.id === c.dogru) || {}).text || ''}</p>
        </div>
      `).join('')}
    </div>
  `;
}

function escapeQ(s) { return (s || '').replace(/"/g, '&quot;'); }
function truncate(s, n) { return (s || '').length > n ? s.slice(0, n) + '...' : s; }

export async function renderCardNew(editId) {
  let card = null;
  if (editId) {
    const state = loadState();
    card = state.custom_kartlar.find(c => c.id === editId);
    if (!card) return `<p>Kart bulunamadı.</p>`;
  }

  window.__pageSetup = () => {
    const form = document.getElementById('cardForm');
    form?.addEventListener('submit', e => {
      e.preventDefault();
      const d = new FormData(form);
      const secenekler = ['A','B','C','D','E']
        .filter(id => (d.get('opt_' + id) || '').trim())
        .map(id => ({ id, text: d.get('opt_' + id).trim() }));
      if (secenekler.length < 2) { alert('En az 2 şık girmelisin.'); return; }
      const dogru = d.get('dogru');
      if (!secenekler.find(s => s.id === dogru)) { alert('Doğru cevap şıklardan biri olmalı.'); return; }
      const obj = {
        konu: d.get('konu'),
        alt_konu: d.get('alt_konu') || '',
        tip: d.get('tip') || 'eser-yazar',
        soru: d.get('soru').trim(),
        secenekler,
        dogru,
        aciklama: (d.get('aciklama') || '').trim(),
        tuzak: (d.get('tuzak') || '').trim(),
        mebi_sayfa: (d.get('mebi_sayfa') || '').trim(),
        zorluk: d.get('zorluk') || 'orta',
      };
      if (editId) {
        updateCustomCard(editId, obj);
      } else {
        addCustomCard(obj);
      }
      location.hash = '#/kartlar';
    });
  };

  return `
    <nav class="text-sm mb-3 text-slate-500"><a href="#/kartlar" class="hover:underline">← Kart havuzu</a></nav>
    <h1 class="text-3xl font-bold mb-4">${editId ? '✏️ Kartı Düzenle' : '➕ Yeni Kart'}</h1>
    <form id="cardForm" class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-5 space-y-3 max-w-2xl">
      <div class="grid sm:grid-cols-2 gap-3">
        <label class="block">
          <span class="text-sm font-semibold">Konu</span>
          <select name="konu" required class="w-full mt-1 px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900">
            ${Object.entries(TOPIC_LABELS).map(([c,l]) => `<option value="${c}" ${card?.konu===c?'selected':''}>${l}</option>`).join('')}
          </select>
        </label>
        <label class="block">
          <span class="text-sm font-semibold">Alt Konu (opsiyonel)</span>
          <input name="alt_konu" type="text" value="${card?.alt_konu || ''}" placeholder="gazel, halit_ziya..." class="w-full mt-1 px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900" />
        </label>
      </div>
      <label class="block">
        <span class="text-sm font-semibold">Soru</span>
        <textarea name="soru" required rows="3" class="w-full mt-1 px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900">${card?.soru || ''}</textarea>
      </label>

      <fieldset class="border border-slate-200 dark:border-slate-700 rounded-md p-3">
        <legend class="text-sm font-semibold px-1">Şıklar</legend>
        ${['A','B','C','D','E'].map(id => {
          const opt = card?.secenekler?.find(s => s.id === id);
          return `
            <div class="flex gap-2 items-center mb-2">
              <label class="flex items-center gap-1">
                <input type="radio" name="dogru" value="${id}" ${card?.dogru===id?'checked':''} required title="Doğru cevap" />
                <span class="text-sm font-bold w-5">${id}</span>
              </label>
              <input name="opt_${id}" type="text" value="${(opt?.text || '').replace(/"/g,'&quot;')}" placeholder="Şık ${id} metni (boş bırakılırsa atlanır)" class="flex-1 px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900" />
            </div>
          `;
        }).join('')}
        <p class="text-xs text-slate-500 mt-1">Soldaki yuvarlağı işaretle = doğru cevap. Boş bırakılan şıklar atlanır.</p>
      </fieldset>

      <label class="block">
        <span class="text-sm font-semibold">Açıklama (cevap niye doğru)</span>
        <textarea name="aciklama" rows="2" class="w-full mt-1 px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900">${card?.aciklama || ''}</textarea>
      </label>
      <label class="block">
        <span class="text-sm font-semibold">Tuzak Notu (opsiyonel)</span>
        <textarea name="tuzak" rows="2" placeholder="Çeldiriciler neden cazip..." class="w-full mt-1 px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900">${card?.tuzak || ''}</textarea>
      </label>
      <div class="grid sm:grid-cols-3 gap-3">
        <label class="block">
          <span class="text-sm font-semibold">MEBİ Sayfa</span>
          <input name="mebi_sayfa" type="text" value="${card?.mebi_sayfa || ''}" placeholder="47-48" class="w-full mt-1 px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900" />
        </label>
        <label class="block">
          <span class="text-sm font-semibold">Zorluk</span>
          <select name="zorluk" class="w-full mt-1 px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900">
            <option value="kolay" ${card?.zorluk==='kolay'?'selected':''}>Kolay</option>
            <option value="orta" ${card?.zorluk==='orta'?'selected':''}>Orta</option>
            <option value="zor" ${card?.zorluk==='zor'?'selected':''}>Zor</option>
          </select>
        </label>
        <label class="block">
          <span class="text-sm font-semibold">Tip</span>
          <input name="tip" type="text" value="${card?.tip || 'eser-yazar'}" placeholder="eser-yazar, akim-tanim..." class="w-full mt-1 px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900" />
        </label>
      </div>
      <button type="submit" class="w-full bg-accent-500 hover:bg-accent-700 text-white font-bold py-2.5 rounded-md">${editId ? 'Kaydet' : 'Kartı Ekle'}</button>
    </form>
  `;
}
