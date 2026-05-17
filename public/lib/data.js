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

export const Data = {
  cards: () => loadJSON('./data/cards-auto.json'),
  topicsIndex: () => loadJSON('./data/topics-index.json'),
  topicHTML: (slug) => loadText(`./data/topics/${slug}.html`),
  authors: () => loadJSON('./data/authors.json'),
  predictions: () => loadJSON('./data/predictions.json'),
  program: () => loadJSON('./data/program.json'),
  glossary: () => loadJSON('./data/glossary.json'),
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
  return str.toLowerCase()
    .replace(/ş/g,'s').replace(/ç/g,'c').replace(/ğ/g,'g')
    .replace(/ı/g,'i').replace(/ö/g,'o').replace(/ü/g,'u')
    .replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
}
