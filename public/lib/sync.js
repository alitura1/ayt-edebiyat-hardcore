// REV6 M8 — Hibrit sync: localStorage hep ana, cloud yedek (debounced)
// Login varsa her saveState'te 3 sn debounced cloud upload
// İlk login'de cloud → local merge (timestamp wins)
import { loadState, saveState } from './store.js';
import { getFirebase, fsGetUserDoc, fsSetUserDoc, onAuthChange } from './firebase.js';

const SYNC_DEBOUNCE_MS = 3000;
const MIN_SYNC_INTERVAL_MS = 30000;  // min 30 sn between writes (quota koruma)

let _syncTimer = null;
let _lastSyncAt = 0;
let _currentUid = null;
let _initialPullDone = false;

// Senkronize edilen alanlar (sessionStorage hariç)
const SYNC_KEYS = [
  'progress', 'hata_defteri', 'custom_kartlar',
  'program_checkbox', 'ayarlar',
  'due', 'streak_correct', 'streak', 'atis', 'daily_hero',
  'notify',
];

function pickSyncData(state) {
  const out = {};
  for (const k of SYNC_KEYS) {
    if (state[k] !== undefined) out[k] = state[k];
  }
  return out;
}

// Local + cloud merge — son timestamp (her field için) kazanır
// Basit yaklaşım: progress için kart başı son timestamp (p.son), diğerlerinde union
function mergeStates(local, cloud) {
  if (!cloud) return local;
  const merged = { ...local };

  // progress: kart başı en yeni son
  if (cloud.progress) {
    merged.progress = { ...local.progress };
    for (const id in cloud.progress) {
      const l = local.progress?.[id];
      const c = cloud.progress[id];
      if (!l || (c.son || 0) > (l.son || 0)) {
        merged.progress[id] = c;
      }
    }
  }

  // hata_defteri: union, ardından duplicate eliminate
  if (cloud.hata_defteri) {
    merged.hata_defteri = [...new Set([...(local.hata_defteri || []), ...cloud.hata_defteri])];
  }

  // custom_kartlar: id bazında union (son güncel kazanır)
  if (cloud.custom_kartlar) {
    const map = new Map();
    for (const c of (local.custom_kartlar || [])) map.set(c.id, c);
    for (const c of cloud.custom_kartlar) {
      if (!map.has(c.id)) map.set(c.id, c);
    }
    merged.custom_kartlar = Array.from(map.values());
  }

  // program_checkbox, ayarlar, notify: cloud overwrite (sade)
  for (const k of ['program_checkbox', 'ayarlar', 'notify']) {
    if (cloud[k]) merged[k] = { ...local[k], ...cloud[k] };
  }

  // due: en geç olanı seç (max)
  if (cloud.due) {
    merged.due = { ...local.due };
    for (const id in cloud.due) {
      if ((cloud.due[id] || 0) > (merged.due[id] || 0)) merged.due[id] = cloud.due[id];
    }
  }

  // streak_correct: max
  if (cloud.streak_correct) {
    merged.streak_correct = { ...local.streak_correct };
    for (const id in cloud.streak_correct) {
      if ((cloud.streak_correct[id] || 0) > (merged.streak_correct[id] || 0)) {
        merged.streak_correct[id] = cloud.streak_correct[id];
      }
    }
  }

  // streak: en uzun current + longest, last_active_date max
  if (cloud.streak) {
    merged.streak = merged.streak || {};
    merged.streak.current = Math.max(merged.streak.current || 0, cloud.streak.current || 0);
    merged.streak.longest = Math.max(merged.streak.longest || 0, cloud.streak.longest || 0);
    if (!merged.streak.last_active_date || (cloud.streak.last_active_date && cloud.streak.last_active_date > merged.streak.last_active_date)) {
      merged.streak.last_active_date = cloud.streak.last_active_date;
    }
    const hist = new Set([...(merged.streak.history || []), ...(cloud.streak.history || [])]);
    merged.streak.history = [...hist].sort().slice(-60);
  }

  // atis: best_run max
  if (cloud.atis) {
    merged.atis = merged.atis || {};
    merged.atis.best_run = Math.max(merged.atis.best_run || 0, cloud.atis.best_run || 0);
  }

  return merged;
}

async function pullFromCloud(uid) {
  try {
    const cloud = await fsGetUserDoc(uid, 'state');
    if (!cloud) return;
    const local = loadState();
    const merged = mergeStates(local, cloud);
    saveState(merged);
    console.log('[sync] cloud→local merge OK');
  } catch (e) {
    console.warn('[sync] pull failed', e);
  }
}

async function pushToCloud(uid) {
  try {
    const state = loadState();
    const data = pickSyncData(state);
    await fsSetUserDoc(uid, 'state', data);
    _lastSyncAt = Date.now();
    console.log('[sync] local→cloud OK');
  } catch (e) {
    console.warn('[sync] push failed', e);
  }
}

// store.js içinde her saveState çağrısında çağrılır
export function scheduleSync() {
  if (!_currentUid) return;  // login yok
  if (_syncTimer) clearTimeout(_syncTimer);
  const sinceLastSync = Date.now() - _lastSyncAt;
  const delay = Math.max(SYNC_DEBOUNCE_MS, MIN_SYNC_INTERVAL_MS - sinceLastSync);
  _syncTimer = setTimeout(() => pushToCloud(_currentUid), delay);
}

// App start'ta çağrılır
export async function initSync() {
  try {
    await getFirebase();  // Firebase yüklendi mi diye kontrol
    await onAuthChange(async (user) => {
      if (user) {
        _currentUid = user.uid;
        if (!_initialPullDone) {
          await pullFromCloud(user.uid);
          _initialPullDone = true;
        }
      } else {
        _currentUid = null;
        _initialPullDone = false;
      }
      // Auth state her değiştiğinde UI'a haber
      window.dispatchEvent(new CustomEvent('authchange', { detail: { user } }));
    });
  } catch (e) {
    console.warn('[sync] init failed (Firebase yüklenemedi)', e);
  }
}

export function currentSyncUid() { return _currentUid; }
