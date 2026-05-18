// JSON data loader — fetch + cache
const cache = new Map();

async function loadJSON(path) {
  if (cache.has(path)) return cache.get(path);
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Veri yüklenemedi: ${path} (${res.status})`);
  const data = await res.json();
  cache.set(path, data);
  return data;
}

async function loadText(path) {
  if (cache.has(path)) return cache.get(path);
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Metin yüklenemedi: ${path} (${res.status})`);
  const txt = await res.text();
  cache.set(path, txt);
  return txt;
}

async function loadCardsCombined() {
  // 554 otomatik + 80 alıntı kartı tek havuzda
  const auto = await loadJSON('./data/cards-auto.json');
  let alinti = [];
  try { alinti = await loadJSON('./data/cards-alinti.json'); } catch(e) { /* opsiyonel */ }
  return [...auto, ...alinti];
}

export const Data = {
  cards: () => {
    if (!cache.has('__combined_cards__')) {
      cache.set('__combined_cards__', loadCardsCombined());
    }
    return cache.get('__combined_cards__');
  },
  topicsIndex: () => loadJSON('./data/topics-index.json'),
  topicHTML: (slug) => loadText(`./data/topics/${slug}.html`),
  authors: () => loadJSON('./data/authors.json'),
  predictions: () => loadJSON('./data/predictions.json'),
  program: () => loadJSON('./data/program.json'),
  glossary: () => loadJSON('./data/glossary.json'),
  cikmis: () => loadJSON('./data/cikmis-sorular.json'),
  works: () => loadJSON('./data/works.json'),
  groups: () => loadJSON('./data/groups.json'),
};

// Etiketler
export const TOPIC_LABELS = {
  divan_edebiyati: 'Divan Edebiyatı',
  cumhuriyet: 'Cumhuriyet Dönemi',
  siir_bilgisi: 'Şiir Bilgisi',
  soz_sanatlari: 'Söz Sanatları',
  nesir_bilgisi: 'Nesir Bilgisi',
  tanzimat: 'Tanzimat',
  servet_i_funun_fecr_i_ati: 'Servet-i Fünun / Fecr-i Âti',
  milli_edebiyat: 'Milli Edebiyat',
  halk_edebiyati: 'Halk Edebiyatı',
  islamiyet_oncesi_gecis: 'İslamiyet Öncesi / Geçiş',
  geleneksel_tiyatro: 'Geleneksel Tiyatro',
  masal_fabl_destan: 'Masal / Fabl / Destan',
  edebi_akimlar: 'Edebi Akımlar',
};

export function topicLabel(code) { return TOPIC_LABELS[code] || code; }

export function slugify(str) {
  // REV15 — Türkçe büyük İ "i + combining dot above" → ASCII 'i' garanti
  return String(str)
    .normalize('NFD').replace(/[̀-ͯ]/g, '')  // diacritics (dot above, cedilla, breve)
    .toLowerCase()
    .replace(/ı/g, 'i')  // noktasız ı (NFD'de aynı kalır)
    .replace(/ş/g,'s').replace(/ç/g,'c').replace(/ğ/g,'g')
    .replace(/ö/g,'o').replace(/ü/g,'u')
    .replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
}

// REV5 — Dönem rozet renkleri (Tailwind class'ları) ve etiketi
export const PERIOD_THEME = {
  islamiyet_oncesi_gecis: { bg:'bg-amber-100 dark:bg-amber-900/40',   text:'text-amber-800 dark:text-amber-200',   label:'İslamiyet Öncesi', dot:'bg-amber-500' },
  divan_edebiyati:        { bg:'bg-yellow-100 dark:bg-yellow-900/40', text:'text-yellow-900 dark:text-yellow-200', label:'Divan',             dot:'bg-yellow-500' },
  halk_edebiyati:         { bg:'bg-emerald-100 dark:bg-emerald-900/40', text:'text-emerald-800 dark:text-emerald-200', label:'Halk',          dot:'bg-emerald-500' },
  tanzimat:               { bg:'bg-purple-100 dark:bg-purple-900/40', text:'text-purple-800 dark:text-purple-200', label:'Tanzimat',          dot:'bg-purple-500' },
  servet_i_funun_fecr_i_ati: { bg:'bg-violet-100 dark:bg-violet-900/40', text:'text-violet-800 dark:text-violet-200', label:'Servet-i Fünun / Fecr-i Âti', dot:'bg-violet-500' },
  milli_edebiyat:         { bg:'bg-indigo-100 dark:bg-indigo-900/40', text:'text-indigo-800 dark:text-indigo-200', label:'Milli Edebiyat',    dot:'bg-indigo-500' },
  cumhuriyet:             { bg:'bg-red-100 dark:bg-red-900/40',       text:'text-red-800 dark:text-red-200',       label:'Cumhuriyet',        dot:'bg-red-500' },
  edebi_akimlar:          { bg:'bg-slate-200 dark:bg-slate-700/60',   text:'text-slate-800 dark:text-slate-200',   label:'Edebi Akımlar',     dot:'bg-slate-500' },
  siir_bilgisi:           { bg:'bg-sky-100 dark:bg-sky-900/40',       text:'text-sky-800 dark:text-sky-200',       label:'Şiir Bilgisi',      dot:'bg-sky-500' },
  nesir_bilgisi:          { bg:'bg-teal-100 dark:bg-teal-900/40',     text:'text-teal-800 dark:text-teal-200',     label:'Nesir Bilgisi',     dot:'bg-teal-500' },
  soz_sanatlari:          { bg:'bg-pink-100 dark:bg-pink-900/40',     text:'text-pink-800 dark:text-pink-200',     label:'Söz Sanatları',     dot:'bg-pink-500' },
  geleneksel_tiyatro:     { bg:'bg-orange-100 dark:bg-orange-900/40', text:'text-orange-800 dark:text-orange-200', label:'Geleneksel Tiyatro',dot:'bg-orange-500' },
  masal_fabl_destan:      { bg:'bg-lime-100 dark:bg-lime-900/40',     text:'text-lime-800 dark:text-lime-200',     label:'Masal/Fabl/Destan', dot:'bg-lime-500' },
};

export function periodTheme(donem) {
  return PERIOD_THEME[donem] || { bg:'bg-slate-100 dark:bg-slate-800', text:'text-slate-700 dark:text-slate-300', label:donem||'—', dot:'bg-slate-400' };
}

// REV5 — Cards'taki alt_konu (örn. "şeyh_galip") <-> author slug (örn. "seyh-galip") köprüsü
// cards-auto.json'da alt_konu underscore + Türkçe karakterli, authors.json adından slugify yapılır
export function altKonuToAuthorSlug(altKonu) {
  if (!altKonu) return '';
  return slugify(String(altKonu).replace(/_/g, ' '));
}
