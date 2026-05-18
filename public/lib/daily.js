// REV6 — "Şu Anki Yazar": sayfa her açılışta veya yenile butonunda farklı yazar
// Son 20 yazarı history'de tut, peş peşe tekrar etmesin
import { altKonuToAuthorSlug, slugify } from './data.js';
import { loadState, saveState } from './store.js';

// Anekdotu olan + soru_sayisi >= 1 olanlardan rastgele seç
// state.daily_hero.history son 20 yazarı tutar (tekrar etmemek için)
export function dailyHero(authors, cards) {
  const enriched = authors.filter(a => a.anekdot && a.soru_sayisi >= 1);
  const basePool = enriched.length ? enriched : authors.filter(a => a.soru_sayisi >= 1);
  if (basePool.length === 0) return { author: null, miniCard: null };

  const s = loadState();
  if (!s.daily_hero) s.daily_hero = { seen: {}, history: [] };
  if (!Array.isArray(s.daily_hero.history)) s.daily_hero.history = [];
  const recent = new Set(s.daily_hero.history.slice(-20));

  // Önce recent dışı havuz dene, hepsi tükenmişse tüm havuzdan seç
  const fresh = basePool.filter(a => !recent.has(slugify(a.name)));
  const pool = fresh.length ? fresh : basePool;

  const author = pool[Math.floor(Math.random() * pool.length)];

  // Yazara ait kart random seç
  // REV7 — doğru cevap yazarın adını içeren kartları FİLTRELE (spoiler önlemi)
  const slug = slugify(author.name);
  const aCards = cards.filter(c => altKonuToAuthorSlug(c.alt_konu) === slug);
  const nameLower = author.name.toLowerCase();
  const filteredCards = aCards.filter(c => {
    const correct = c.secenekler?.find(o => o.id === c.dogru);
    if (!correct) return false;
    // Cevap yazarın adının bir parçası ise spoiler — atla
    return !correct.text.toLowerCase().includes(nameLower);
  });
  const miniCard = filteredCards.length
    ? filteredCards[Math.floor(Math.random() * filteredCards.length)]
    : null;

  // History'ye kaydet (son 40'ı tut)
  s.daily_hero.history.push(slug);
  while (s.daily_hero.history.length > 40) s.daily_hero.history.shift();
  saveState(s);

  return { author, miniCard };
}

// Geçmişi temizle (settings'den çağrılabilir)
export function resetHeroHistory() {
  const s = loadState();
  if (!s.daily_hero) s.daily_hero = { seen: {}, history: [] };
  s.daily_hero.history = [];
  saveState(s);
}
