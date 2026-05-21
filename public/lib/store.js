// localStorage state yönetimi — REV20: HİBRİT (Edebiyat + Tarih)
const LEGACY_KEY = 'edebiyat-state-v1';
const SUBJECT_PREF_KEY = 'subject-preference';
const MIGRATION_FLAG = 'migrated-v2';
const DAY_MS = 86400000;

const VALID_SUBJECTS = ['edebiyat', 'tarih'];

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
  daily_hero: { seen: {} }, // "YYYY-MM-DD" -> { entityId, miniQuizCardId, answered, mode }
};

let cache = null;
let _currentSubject = null;

// ============ SUBJECT MANAGEMENT (REV20) ============

function getStorageKey(subject) {
  // Subject yoksa null döner → loadState legacy fallback'a düşer
  if (!subject) return null;
  return `state-v2-${subject}`;
}

export function setCurrentSubject(subject) {
  if (!VALID_SUBJECTS.includes(subject)) {
    throw new Error('Geçersiz ders: ' + subject);
  }
  _currentSubject = subject;
  cache = null;  // Cache reset — yeni subject'in state'ini yükler
}

export function getCurrentSubject() {
  return _currentSubject;
}

export function loadSubjectPreference() {
  try {
    const saved = localStorage.getItem(SUBJECT_PREF_KEY);
    if (saved && VALID_SUBJECTS.includes(saved)) {
      _currentSubject = saved;
      return saved;
    }
  } catch (e) { /* localStorage erişimi engellendi */ }
  return null;
}

export function saveSubjectPreference(subject) {
  if (!VALID_SUBJECTS.includes(subject)) return false;
  try {
    localStorage.setItem(SUBJECT_PREF_KEY, subject);
    setCurrentSubject(subject);
    return true;
  } catch (e) {
    console.error('Subject preference save failed:', e);
    return false;
  }
}

// ============ MIGRATION (REV20) ============

export function migrateOldData(targetSubject = 'edebiyat') {
  // Eski edebiyat-state-v1 anahtarı varsa state-v2-edebiyat'a kopyala
  // Hedef key zaten varsa merge yap (en yeni timestamp wins)
  try {
    const oldRaw = localStorage.getItem(LEGACY_KEY);
    if (!oldRaw) return false;  // Eski veri yok

    const oldData = JSON.parse(oldRaw);
    const newKey = getStorageKey(targetSubject);
    if (!newKey) return false;

    const existingRaw = localStorage.getItem(newKey);
    let merged = oldData;

    if (existingRaw) {
      // Çakışma — basit merge (mevcut + eski'den eksikleri ekle)
      const existing = JSON.parse(existingRaw);
      merged = { ...DEFAULT_STATE, ...existing };
      // progress merge (en yeni son timestamp wins)
      for (const id in (oldData.progress || {})) {
        if (!merged.progress[id] ||
            (oldData.progress[id].son || 0) > (merged.progress[id].son || 0)) {
          merged.progress[id] = oldData.progress[id];
        }
      }
      // hata_defteri union
      const hd = new Set([...(merged.hata_defteri || []), ...(oldData.hata_defteri || [])]);
      merged.hata_defteri = Array.from(hd);
      // custom_kartlar union by id
      const ckMap = new Map();
      for (const c of (merged.custom_kartlar || [])) ckMap.set(c.id, c);
      for (const c of (oldData.custom_kartlar || [])) {
        if (!ckMap.has(c.id)) ckMap.set(c.id, c);
      }
      merged.custom_kartlar = Array.from(ckMap.values());
    }

    localStorage.setItem(newKey, JSON.stringify(merged));
    localStorage.setItem(MIGRATION_FLAG, 'true');
    // Eski key'i hemen silme — 1 sürüm boyunca yedek tut
    console.log(`[migration] ${LEGACY_KEY} → ${newKey} OK`);
    return true;
  } catch (e) {
    console.error('[migration] failed:', e);
    return false;
  }
}

// ============ STATE LOAD/SAVE ============

export function loadState() {
  if (cache) return cache;
  try {
    if (!_currentSubject) {
      // Subject seçilmemiş — legacy fallback (gate öncesi durumlar için)
      const legacyRaw = localStorage.getItem(LEGACY_KEY);
      if (legacyRaw) {
        cache = { ...DEFAULT_STATE, ...JSON.parse(legacyRaw) };
      } else {
        cache = structuredClone(DEFAULT_STATE);
      }
    } else {
      // Subject set — SADECE o subject'in key'inden oku, izolasyonu koru
      const key = getStorageKey(_currentSubject);
      const raw = localStorage.getItem(key);
      if (raw) {
        cache = { ...DEFAULT_STATE, ...JSON.parse(raw) };
      } else {
        cache = structuredClone(DEFAULT_STATE);
      }
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
    let key = getStorageKey(_currentSubject);
    if (!key) key = LEGACY_KEY;  // Subject set edilmemişse legacy'e yaz
    localStorage.setItem(key, JSON.stringify(state));
  } catch (e) {
    console.error('State save failed:', e);
  }
  // REV6 — Cloud sync (login varsa debounced push)
  try {
    if (typeof window !== 'undefined' && window.__syncHook) {
      window.__syncHook();
    }
  } catch(e) { /* ignore */ }
}

// ============ EXISTING API (unchanged behavior) ============

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
  const subj = _currentSubject || 'edebiyat';
  if (confirm(`${subj.toUpperCase()} dersine ait TÜM ilerleme, hata defteri ve manuel kartlar silinecek. Emin misin?`)) {
    const key = getStorageKey(_currentSubject) || LEGACY_KEY;
    localStorage.removeItem(key);
    cache = null;
    location.reload();
  }
}

// Quiz oturumu için geçici storage (sessionStorage) — subject-aware
function sessionKey(key) {
  const subj = _currentSubject || 'edebiyat';
  return `${subj}-session-${key}`;
}

export function setSessionState(key, val) {
  sessionStorage.setItem(sessionKey(key), JSON.stringify(val));
}
export function getSessionState(key) {
  const v = sessionStorage.getItem(sessionKey(key));
  return v ? JSON.parse(v) : null;
}
