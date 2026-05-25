/**
 * sim-core.js — Custom sim'ler için ortak yardımcı lib.
 * Hiçbir dış kütüphane yok. Vanilla JS + Tailwind CDN ile çalışır.
 *
 * API:
 *   SimCore.makeDraggable(element, options) — mouse+touch sürükle
 *   SimCore.slider(container, options) — slider UI helper
 *   SimCore.animate(fn) — RAF döngüsü wrapper
 *   SimCore.physics2d(options) — basit yerçekimi + çarpışma
 *   SimCore.hypothesis(...) — tahmin-deney-sonuç UI flow
 *   SimCore.randomGauss() — normal dağılım random
 *   SimCore.dist(p1, p2) — euclidean mesafe
 *   SimCore.lerp(a, b, t) — linear interpolation
 *   SimCore.clamp(v, min, max)
 *   SimCore.svgPoint(svg, evt) — DOM event'i SVG koordinatına çevir
 */
window.SimCore = (function () {
  'use strict';

  // ============ DRAG-DROP ============
  // SVG veya HTML element'i sürüklenebilir yap. Mouse + touch.
  function makeDraggable(el, options = {}) {
    const {
      onStart = () => {},
      onMove = () => {},
      onEnd = () => {},
      bounds = null, // {x, y, w, h} veya fn(p)→p
      handle = null,  // alt-element CSS selector
      svg = null,     // SVG context (koordinat dönüşümü için)
    } = options;

    const handleEl = handle ? el.querySelector(handle) : el;
    let dragging = false;
    let startX = 0, startY = 0, offsetX = 0, offsetY = 0;

    function getPointerPos(e) {
      const evt = e.touches ? e.touches[0] : e;
      if (svg) {
        // SVG coordinate transformation
        const pt = svg.createSVGPoint();
        pt.x = evt.clientX;
        pt.y = evt.clientY;
        const ctm = svg.getScreenCTM();
        if (ctm) {
          const local = pt.matrixTransform(ctm.inverse());
          return { x: local.x, y: local.y };
        }
      }
      return { x: evt.clientX, y: evt.clientY };
    }

    function applyBounds(p) {
      if (!bounds) return p;
      if (typeof bounds === 'function') return bounds(p);
      const { x, y, w, h } = bounds;
      return {
        x: Math.max(x, Math.min(x + w, p.x)),
        y: Math.max(y, Math.min(y + h, p.y)),
      };
    }

    function start(e) {
      dragging = true;
      const p = getPointerPos(e);
      startX = p.x; startY = p.y;
      const cx = parseFloat(el.getAttribute?.('cx') || el.dataset?.x || 0);
      const cy = parseFloat(el.getAttribute?.('cy') || el.dataset?.y || 0);
      offsetX = cx; offsetY = cy;
      el.classList.add('dragging');
      try { onStart({ x: cx, y: cy, event: e }); } catch (err) { console.warn(err); }
      e.preventDefault();
    }

    function move(e) {
      if (!dragging) return;
      const p = getPointerPos(e);
      let nx = offsetX + (p.x - startX);
      let ny = offsetY + (p.y - startY);
      const bounded = applyBounds({ x: nx, y: ny });
      el.dataset.x = bounded.x;
      el.dataset.y = bounded.y;
      try { onMove(bounded, e); } catch (err) { console.warn(err); }
      e.preventDefault();
    }

    function end(e) {
      if (!dragging) return;
      dragging = false;
      el.classList.remove('dragging');
      try { onEnd({ x: parseFloat(el.dataset.x), y: parseFloat(el.dataset.y), event: e }); } catch (err) { console.warn(err); }
    }

    handleEl.addEventListener('mousedown', start);
    handleEl.addEventListener('touchstart', start, { passive: false });
    window.addEventListener('mousemove', move);
    window.addEventListener('touchmove', move, { passive: false });
    window.addEventListener('mouseup', end);
    window.addEventListener('touchend', end);

    handleEl.style.cursor = 'grab';
    handleEl.style.touchAction = 'none';

    return {
      destroy() {
        handleEl.removeEventListener('mousedown', start);
        handleEl.removeEventListener('touchstart', start);
        window.removeEventListener('mousemove', move);
        window.removeEventListener('touchmove', move);
        window.removeEventListener('mouseup', end);
        window.removeEventListener('touchend', end);
      },
    };
  }

  // ============ SLIDER ============
  // Slider UI: label + range input + canlı değer
  function slider(container, options = {}) {
    const { label, min = 0, max = 100, step = 1, value = 50, onChange = () => {}, fmt = (v) => v.toFixed(1) } = options;
    const wrap = document.createElement('div');
    wrap.className = 'sim-slider';
    wrap.innerHTML = `
      <label class="flex items-baseline justify-between mb-1 text-sm">
        <span class="font-bold">${label}</span>
        <span class="value text-amber-300 font-mono font-bold">${fmt(value)}</span>
      </label>
      <input type="range" min="${min}" max="${max}" step="${step}" value="${value}" class="w-full" />
    `;
    container.appendChild(wrap);
    const input = wrap.querySelector('input');
    const valueEl = wrap.querySelector('.value');
    let current = value;
    input.addEventListener('input', () => {
      current = parseFloat(input.value);
      valueEl.textContent = fmt(current);
      onChange(current);
    });
    return {
      get value() { return current; },
      set value(v) { input.value = v; current = v; valueEl.textContent = fmt(v); },
      element: wrap,
    };
  }

  // ============ ANIMATOR ============
  // requestAnimationFrame loop wrapper
  function animate(callback) {
    let running = true;
    let last = performance.now();
    function frame(now) {
      if (!running) return;
      const dt = (now - last) / 1000;
      last = now;
      try { callback(dt, now); } catch (err) { console.warn(err); }
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
    return {
      stop() { running = false; },
      pause() { running = false; },
      resume() { running = true; last = performance.now(); requestAnimationFrame(frame); },
    };
  }

  // ============ PHYSICS 2D (basit) ============
  // Yerçekimi + sınır çarpışması + sıvı kaldırma (opsiyonel)
  // Body: { x, y, vx, vy, r, density, color, restingY? }
  function physics2d(options = {}) {
    const {
      bodies = [],
      gravity = 200, // pixel/s² (görsel)
      bounds = { x: 0, y: 0, w: 400, h: 400 },
      fluidLevel = null, // y koordinatı; üzeri hava, altı sıvı
      fluidDensity = 1.0,
      onUpdate = () => {},
    } = options;

    const bodyList = [...bodies];

    function tick(dt) {
      for (const b of bodyList) {
        if (b.fixed) continue;

        // Yerçekimi
        let ay = gravity;

        // Sıvıda kaldırma kuvveti
        if (fluidLevel !== null && b.y + b.r > fluidLevel) {
          // Kısmen veya tam batık
          const batik = Math.min(b.y + b.r - fluidLevel, 2 * b.r);
          const batikOran = batik / (2 * b.r);
          const fkald = fluidDensity * gravity * batikOran;
          ay -= fkald / b.density * (1 / Math.max(b.density, 0.1));
          // Su direnci
          b.vy *= 0.92;
          b.vx *= 0.92;
        }

        b.vy += ay * dt;
        b.x += b.vx * dt;
        b.y += b.vy * dt;

        // Sınır çarpışmaları
        if (b.x - b.r < bounds.x) { b.x = bounds.x + b.r; b.vx *= -0.5; }
        if (b.x + b.r > bounds.x + bounds.w) { b.x = bounds.x + bounds.w - b.r; b.vx *= -0.5; }
        if (b.y + b.r > bounds.y + bounds.h) { b.y = bounds.y + bounds.h - b.r; b.vy *= -0.4; if (Math.abs(b.vy) < 5) b.vy = 0; }
        if (b.y - b.r < bounds.y) { b.y = bounds.y + b.r; b.vy *= -0.4; }
      }
      onUpdate(bodyList);
    }

    return {
      tick,
      bodies: bodyList,
      add(b) { bodyList.push(b); },
      remove(b) {
        const i = bodyList.indexOf(b);
        if (i >= 0) bodyList.splice(i, 1);
      },
      clear() { bodyList.length = 0; },
    };
  }

  // ============ HYPOTHESIS UI ============
  // Tahmin → Deney → Sonuç akışı için UI helper
  function hypothesis(container, options = {}) {
    const {
      soru = 'Sence ne olacak?',
      secenekler = [], // [{id, label}]
      onTahmin = () => {},
      onDeney = () => {}, // user "Deney Yap" tıklayınca
      onKontrol = () => {}, // returns { correct: boolean, sonuc: string }
    } = options;

    const wrap = document.createElement('div');
    wrap.className = 'hypothesis-card bg-amber-900/30 border-2 border-amber-500/40 rounded-xl p-3 mt-3';
    wrap.innerHTML = `
      <div class="text-xs uppercase tracking-wider text-amber-300 mb-2">🔬 Hipotez → Deney → Sonuç</div>
      <p class="text-sm font-bold mb-2">${soru}</p>
      <div class="grid gap-1.5 mb-2 hypothesis-options">
        ${secenekler.map(s => `<button class="hyp-opt px-3 py-1.5 bg-slate-700 hover:bg-slate-600 rounded text-xs text-left" data-id="${s.id}">${s.label}</button>`).join('')}
      </div>
      <button class="hyp-deney hidden w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded text-sm">🧪 Deneyi Başlat</button>
      <div class="hyp-sonuc hidden mt-2 p-2 bg-slate-800 rounded text-xs"></div>
    `;
    container.appendChild(wrap);

    let secilenTahmin = null;
    wrap.querySelectorAll('.hyp-opt').forEach(btn => {
      btn.addEventListener('click', () => {
        secilenTahmin = btn.dataset.id;
        wrap.querySelectorAll('.hyp-opt').forEach(b => b.classList.toggle('bg-amber-600', b === btn));
        wrap.querySelector('.hyp-deney').classList.remove('hidden');
        onTahmin(secilenTahmin);
      });
    });
    wrap.querySelector('.hyp-deney').addEventListener('click', () => {
      onDeney(secilenTahmin);
      setTimeout(() => {
        const sonuc = onKontrol(secilenTahmin) || { correct: false, sonuc: '—' };
        const sonucEl = wrap.querySelector('.hyp-sonuc');
        sonucEl.classList.remove('hidden');
        sonucEl.innerHTML = `<strong class="${sonuc.correct ? 'text-green-400' : 'text-amber-300'}">${sonuc.correct ? '✓ Doğru tahmin!' : '💡 Deney sonucu:'}</strong> ${sonuc.sonuc}`;
      }, 600);
    });

    return {
      reset() {
        secilenTahmin = null;
        wrap.querySelectorAll('.hyp-opt').forEach(b => b.classList.remove('bg-amber-600'));
        wrap.querySelector('.hyp-deney').classList.add('hidden');
        wrap.querySelector('.hyp-sonuc').classList.add('hidden');
      },
      get tahmin() { return secilenTahmin; },
    };
  }

  // ============ UTILS ============
  function randomGauss(mean = 0, stdDev = 1) {
    let u = 0, v = 0;
    while (u === 0) u = Math.random();
    while (v === 0) v = Math.random();
    return mean + stdDev * Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  }
  function dist(p1, p2) {
    const dx = p1.x - p2.x, dy = p1.y - p2.y;
    return Math.sqrt(dx * dx + dy * dy);
  }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

  // SVG koordinat dönüşümü
  function svgPoint(svg, evt) {
    const pt = svg.createSVGPoint();
    const e = evt.touches ? evt.touches[0] : evt;
    pt.x = e.clientX; pt.y = e.clientY;
    const ctm = svg.getScreenCTM();
    return ctm ? pt.matrixTransform(ctm.inverse()) : pt;
  }

  // Drop zone helper: bir SVG/HTML alanına drop bekler
  function dropZone(el, options = {}) {
    const { onDrop = () => {}, contains = null, highlight = 'drop-zone-active' } = options;
    el.classList.add('drop-zone');
    return {
      check(draggedEl, p) {
        const rect = el.getBoundingClientRect();
        const bb = el.getBBox ? el.getBBox() : null;
        const isOver = contains ? contains(p) : (
          bb ? (p.x >= bb.x && p.x <= bb.x + bb.width && p.y >= bb.y && p.y <= bb.y + bb.height) : false
        );
        el.classList.toggle(highlight, isOver);
        return isOver;
      },
      drop(draggedEl, p) {
        el.classList.remove(highlight);
        onDrop(draggedEl, p);
      },
    };
  }

  // CSS injection helper (sim'lerin paylaştığı stiller)
  function injectStyles() {
    if (document.getElementById('simcore-styles')) return;
    const style = document.createElement('style');
    style.id = 'simcore-styles';
    style.textContent = `
      .dragging { opacity: 0.7; cursor: grabbing !important; }
      .drop-zone { transition: all 0.15s; }
      .drop-zone-active { stroke: #fbbf24 !important; stroke-width: 3 !important; fill-opacity: 0.4 !important; }
      .sim-slider { margin-bottom: 0.75rem; }
      .sim-slider input[type=range] {
        -webkit-appearance: none; appearance: none;
        width: 100%; height: 8px; background: #1e293b; border-radius: 4px; outline: none;
      }
      .sim-slider input[type=range]::-webkit-slider-thumb {
        -webkit-appearance: none; width: 22px; height: 22px;
        background: #06b6d4; border-radius: 50%; cursor: pointer;
        box-shadow: 0 2px 8px rgba(6,182,212,0.5);
      }
      .sim-slider input[type=range]::-moz-range-thumb {
        width: 22px; height: 22px; background: #06b6d4; border-radius: 50%; cursor: pointer; border: none;
      }
      .hyp-opt { transition: background 0.15s; }
    `;
    document.head.appendChild(style);
  }

  // Init
  injectStyles();

  return {
    makeDraggable,
    slider,
    animate,
    physics2d,
    hypothesis,
    dropZone,
    randomGauss,
    dist,
    lerp,
    clamp,
    svgPoint,
  };
})();
