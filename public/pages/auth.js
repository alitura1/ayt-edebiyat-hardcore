// REV6 M7 — Auth UI: giriş, kayıt, profil
import { authSignInEmail, authSignUpEmail, authSignInGoogle, authSignOut, authCurrentUser, onAuthChange } from '../lib/firebase.js';

function escape(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;');
}

export async function renderLogin() {
  window.__pageSetup = () => {
    const form = document.getElementById('loginForm');
    const errEl = document.getElementById('loginErr');
    const googleBtn = document.getElementById('googleBtn');

    form?.addEventListener('submit', async (e) => {
      e.preventDefault();
      errEl.textContent = '';
      const fd = new FormData(e.target);
      try {
        await authSignInEmail(fd.get('email'), fd.get('password'));
        location.hash = '#/hesap';
      } catch (err) {
        errEl.textContent = err.message || 'Giriş başarısız';
      }
    });

    googleBtn?.addEventListener('click', async () => {
      errEl.textContent = '';
      try {
        await authSignInGoogle();
        location.hash = '#/hesap';
      } catch (err) {
        errEl.textContent = err.message || 'Google girişi başarısız';
      }
    });
  };

  return `
    <div class="max-w-md mx-auto">
      <header class="mb-4">
        <h1 class="text-2xl font-bold">🔐 Giriş Yap</h1>
        <p class="text-sm text-slate-600 dark:text-slate-400">Cihazlar arası sync için.</p>
      </header>

      <button id="googleBtn" class="w-full mb-3 flex items-center justify-center gap-2 border-2 border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 py-2.5 rounded-md font-semibold">
        <svg width="18" height="18" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09 0-.73.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
        Google ile giriş yap
      </button>

      <div class="flex items-center my-3 text-xs text-slate-500">
        <div class="flex-1 h-px bg-slate-300 dark:bg-slate-700"></div>
        <span class="px-2">veya</span>
        <div class="flex-1 h-px bg-slate-300 dark:bg-slate-700"></div>
      </div>

      <form id="loginForm" class="space-y-3">
        <div>
          <label class="block text-sm font-semibold mb-1">E-posta</label>
          <input type="email" name="email" required class="w-full px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900" />
        </div>
        <div>
          <label class="block text-sm font-semibold mb-1">Şifre</label>
          <input type="password" name="password" required minlength="6" class="w-full px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900" />
        </div>
        <div id="loginErr" class="text-xs text-accent-500"></div>
        <button type="submit" class="w-full bg-primary-700 hover:bg-primary-900 text-white font-bold py-2.5 rounded-md">Giriş Yap</button>
      </form>

      <p class="text-sm text-center mt-4 text-slate-600 dark:text-slate-400">
        Hesabın yok mu? <a href="#/kayit" class="text-primary-700 dark:text-primary-100 underline">Kayıt ol</a>
      </p>
    </div>
  `;
}

export async function renderRegister() {
  window.__pageSetup = () => {
    const form = document.getElementById('regForm');
    const errEl = document.getElementById('regErr');

    form?.addEventListener('submit', async (e) => {
      e.preventDefault();
      errEl.textContent = '';
      const fd = new FormData(e.target);
      if (fd.get('password') !== fd.get('password2')) {
        errEl.textContent = 'Şifreler eşleşmiyor';
        return;
      }
      try {
        await authSignUpEmail(fd.get('email'), fd.get('password'));
        location.hash = '#/hesap';
      } catch (err) {
        errEl.textContent = err.message || 'Kayıt başarısız';
      }
    });
  };

  return `
    <div class="max-w-md mx-auto">
      <header class="mb-4">
        <h1 class="text-2xl font-bold">📝 Kayıt Ol</h1>
        <p class="text-sm text-slate-600 dark:text-slate-400">Tek hesap, her cihazda aynı ilerleme.</p>
      </header>

      <form id="regForm" class="space-y-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-5">
        <div>
          <label class="block text-sm font-semibold mb-1">E-posta</label>
          <input type="email" name="email" required class="w-full px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900" />
        </div>
        <div>
          <label class="block text-sm font-semibold mb-1">Şifre (en az 6 karakter)</label>
          <input type="password" name="password" required minlength="6" class="w-full px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900" />
        </div>
        <div>
          <label class="block text-sm font-semibold mb-1">Şifre tekrar</label>
          <input type="password" name="password2" required minlength="6" class="w-full px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900" />
        </div>
        <div id="regErr" class="text-xs text-accent-500"></div>
        <button type="submit" class="w-full bg-accent-500 hover:bg-accent-700 text-white font-bold py-2.5 rounded-md">Hesap Aç</button>
      </form>

      <p class="text-sm text-center mt-4 text-slate-600 dark:text-slate-400">
        Hesabın var mı? <a href="#/giris" class="text-primary-700 dark:text-primary-100 underline">Giriş yap</a>
      </p>
    </div>
  `;
}

export async function renderProfile() {
  const user = await authCurrentUser();
  if (!user) {
    return `
      <div class="max-w-md mx-auto text-center py-10">
        <p class="text-slate-500 mb-3">Henüz giriş yapmadın.</p>
        <a href="#/giris" class="inline-block bg-primary-700 text-white font-bold py-2 px-5 rounded-md">Giriş Yap</a>
      </div>
    `;
  }

  window.__pageSetup = () => {
    document.getElementById('logoutBtn')?.addEventListener('click', async () => {
      if (!confirm('Çıkış yapmak istediğine emin misin? Local ilerleme korunacak.')) return;
      await authSignOut();
      location.hash = '#/';
    });
  };

  return `
    <div class="max-w-md mx-auto">
      <header class="mb-4">
        <h1 class="text-2xl font-bold">👤 Hesabım</h1>
      </header>

      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-5 space-y-3">
        <div>
          <div class="text-xs text-slate-500">E-posta</div>
          <div class="font-semibold">${escape(user.email)}</div>
        </div>
        <div>
          <div class="text-xs text-slate-500">Kullanıcı ID</div>
          <div class="font-mono text-xs">${escape(user.uid)}</div>
        </div>
        <div>
          <div class="text-xs text-slate-500">Cihazlar arası sync</div>
          <div class="text-ok-500 font-bold">✓ Aktif</div>
          <div class="text-[10px] text-slate-500 mt-1">Her quiz/atış sonrası ilerleme cloud'a yedeklenir (3 sn debounced).</div>
        </div>
        <button id="logoutBtn" class="w-full mt-3 bg-accent-500 hover:bg-accent-700 text-white font-bold py-2 rounded-md">Çıkış Yap</button>
      </div>
    </div>
  `;
}
