// localStorage state yönetimi
const KEY = 'edebiyat-state-v1';
const DAY_MS = 86400000;

const DEFAULT_STATE = {
  version: 2,
  progress: {},           // kartId -> {cozuldu, dogru, yanlis, son}
  hata_defteri: [],       // kartId[]
  custom_kartlar: [],     // {...kart}[]
  program_checkbox: {},   // "hafta1_pzt" -> bool
  ayarlar: { ses: false, soru_sayisi_default: 10 },
  // REV5 — Edebiyat Evreni
  due: {},                // kartId -> next_due_at (epoch ms) — auto resurface
  streak_correct: {},     // kartId -> üst üste doğru sayısı (mastery)
  streak: {               // günlük login streak
    current: 0,
    longest: 0,
    last_active_date: null,   // "YYYY-MM-DD"
    history: [],              // son 60 gün
  },
  atis: { best_run: 0 },  // Hızlı Atış üst üste max doğru
  daily_hero: { seen: {} }, // "YYYY-MM-DD" -> { authorSlug, miniQuizCardId, answered }
};

let cache = null;

export function loadState() {
  if (cache) return cache;
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      cache = { ...DEFAULT_STATE, ...JSON.parse(raw) };
    } else {
      cache = structuredClone(DEFAULT_STATE);
    }
  } catch (e) {
    console.warn('State load failed:', e);
    cache = structuredClone(DEFAULT_STATE);
  }
  return cache;
}

export function saveState(state) {
  cache = state;
  try {
    localStorage.setItem(KEY, JSON.stringify(state));
  } catch (e) {
    console.error('State save failed:', e);
  }
}

export function updateProgress(cardId, isCorrect) {
  const s = loadState();
  const p = s.progress[cardId] || { cozuldu: 0, dogru: 0, yanlis: 0, son: 0 };
  p.cozuldu++;
  if (isCorrect) p.dogru++; else p.yanlis++;
  p.son = Date.now();
  s.progress[cardId] = p;
  if (!isCorrect) {
    if (!s.hata_defteri.includes(cardId)) s.hata_defteri.push(cardId);
  } else {
    // Yeterince doğru çözdüyse hata defterinden çıkar
    if (p.dogru >= 2 && p.cozuldu - p.dogru < p.dogru) {
      s.hata_defteri = s.hata_defteri.filter(id => id !== cardId);
    }
  }
  saveState(s);
}

// REV5 — Auto Resurface (yanlışlar otomatik geri gelir)
// SRS değil, sade timer logic: yanlış→1g, doğru→3g/7g/14g/21g
export function recordSrs(cardId, isCorrect) {
  const s = loadState();
  const sc = s.streak_correct[cardId] || 0;
  if (isCorrect) {
    s.streak_correct[cardId] = sc + 1;
    let days;
    if (sc === 0) days = 3;
    else if (sc === 1) days = 7;
    else if (sc === 2) days = 14;     // 3. üst üste doğru = MASTERY
    else days = 21;                    // sonrası bakım modu
    s.due[cardId] = Date.now() + days * DAY_MS;
  } else {
    s.streak_correct[cardId] = 0;     // sıfırla
    s.due[cardId] = Date.now() + DAY_MS;  // 1 gün sonra geri gel
  }
  saveState(s);
}

export function dueCardIds(now = Date.now()) {
  const s = loadState();
  const out = [];
  for (const id in s.due) {
    if (s.due[id] <= now) out.push(id);
  }
  return out;
}

export function isMastered(cardId) {
  const s = loadState();
  return (s.streak_correct[cardId] || 0) >= 3;
}

export function addCustomCard(card) {
  const s = loadState();
  if (!card.id) {
    card.id = 'c' + Date.now().toString(36);
  }
  card.kaynak = 'manuel';
  s.custom_kartlar.push(card);
  saveState(s);
  return card.id;
}

export function updateCustomCard(id, patch) {
  const s = loadState();
  const i = s.custom_kartlar.findIndex(c => c.id === id);
  if (i >= 0) {
    s.custom_kartlar[i] = { ...s.custom_kartlar[i], ...patch };
    saveState(s);
    return true;
  }
  return false;
}

export function deleteCustomCard(id) {
  const s = loadState();
  s.custom_kartlar = s.custom_kartlar.filter(c => c.id !== id);
  saveState(s);
}

export function toggleProgramCheckbox(key) {
  const s = loadState();
  s.program_checkbox[key] = !s.program_checkbox[key];
  saveState(s);
  return s.program_checkbox[key];
}

export function exportAll() {
  return JSON.stringify(loadState(), null, 2);
}

export function importAll(jsonStr) {
  try {
    const data = JSON.parse(jsonStr);
    if (!data.version) throw new Error('Geçersiz veri (version yok)');
    saveState({ ...DEFAULT_STATE, ...data });
    cache = null;
    return true;
  } catch (e) {
    alert('Hatalı dosya: ' + e.message);
    return false;
  }
}

export function resetAll() {
  if (confirm('TÜM ilerleme, hata defteri ve manuel kartlar silinecek. Emin misin?')) {
    localStorage.removeItem(KEY);
    cache = null;
    location.reload();
  }
}

// Quiz oturumu için geçici storage (sessionStorage)
export function setSessionState(key, val) {
  sessionStorage.setItem('edebiyat-session-' + key, JSON.stringify(val));
}
export function getSessionState(key) {
  const v = sessionStorage.getItem('edebiyat-session-' + key);
  return v ? JSON.parse(v) : null;
}
