import { Data, getDataSubject } from '../lib/data.js';
import { loadState, toggleProgramCheckbox } from '../lib/store.js';

// REV14 — Konu metnindeki anahtar kelimelerden slug çıkarır (Edebiyat)
const TOPIC_HINTS_EDEBIYAT = [
  ['divan', 'divan_edebiyati'],
  ['tanzimat', 'tanzimat'],
  ['servet', 'servet_i_funun_fecr_i_ati'],
  ['fecr-i ati', 'servet_i_funun_fecr_i_ati'],
  ['milli edeb', 'milli_edebiyat'],
  ['milli ed', 'milli_edebiyat'],
  ['cumhuriyet', 'cumhuriyet'],
  ['halk edeb', 'halk_edebiyati'],
  ['halk siir', 'halk_edebiyati'],
  ['asik', 'halk_edebiyati'],
  ['islamiyet', 'islamiyet_oncesi_gecis'],
  ['gecis', 'islamiyet_oncesi_gecis'],
  ['gokturk', 'islamiyet_oncesi_gecis'],
  ['orhun', 'islamiyet_oncesi_gecis'],
  ['tiyatro', 'geleneksel_tiyatro'],
  ['karagoz', 'geleneksel_tiyatro'],
  ['orta oyun', 'geleneksel_tiyatro'],
  ['meddah', 'geleneksel_tiyatro'],
  ['masal', 'masal_fabl_destan'],
  ['fabl', 'masal_fabl_destan'],
  ['destan', 'masal_fabl_destan'],
  ['halk hikay', 'masal_fabl_destan'],
  ['akim', 'edebi_akimlar'],
  ['siir bilgisi', 'siir_bilgisi'],
  ['nazim', 'siir_bilgisi'],
  ['kafiye', 'siir_bilgisi'],
  ['vezin', 'siir_bilgisi'],
  ['aruz', 'siir_bilgisi'],
  ['hece', 'siir_bilgisi'],
  ['nesir', 'nesir_bilgisi'],
  ['soz san', 'soz_sanatlari'],
];

// REV20 — Tarih TOPIC_HINTS
const TOPIC_HINTS_TARIH = [
  // REV25 — İlk Çağ Uygarlıkları (yeni dönem, başa eklendi)
  ['ilk cag', 'ilk_cag'],
  ['sumer', 'ilk_cag'],
  ['misir', 'ilk_cag'],
  ['hitit', 'ilk_cag'],
  ['frig', 'ilk_cag'],
  ['lidya', 'ilk_cag'],
  ['iyon', 'ilk_cag'],
  ['urartu', 'ilk_cag'],
  ['mezopotamya', 'ilk_cag'],
  ['kanunlar dogu', 'ilk_cag'],
  ['hammurabi', 'ilk_cag'],
  ['urgakina', 'ilk_cag'],
  ['ziggurat', 'ilk_cag'],
  ['ilk cag medeniyet', 'ilk_cag'],
  ['medeniyet havza', 'ilk_cag'],
  // İslam Öncesi Türk
  ['islam oncesi turk', 'islam_oncesi_turk'],
  ['hun', 'islam_oncesi_turk'],
  ['gokturk', 'islam_oncesi_turk'],
  ['uygur', 'islam_oncesi_turk'],
  ['mete', 'islam_oncesi_turk'],
  ['boylardan devlete', 'islam_oncesi_turk'],
  // İslam Tarihi
  ['islam tarihi', 'islam_tarihi'],
  ['hz. muhammed', 'islam_tarihi'],
  ['halife', 'islam_tarihi'],
  ['4 halife', 'islam_tarihi'],
  ['emevi', 'islam_tarihi'],
  ['abbasi', 'islam_tarihi'],
  ['islamiyet yayil', 'islam_tarihi'],
  // Türk-İslam
  ['turk-islam', 'turk_islam'],
  ['karahanli', 'turk_islam'],
  ['gazneli', 'turk_islam'],
  ['selcuklu', 'turk_islam'],
  ['malazgirt', 'turk_islam'],
  ['beylik', 'turk_islam'],
  ['hacli', 'turk_islam'],
  ['anadolu beylik', 'turk_islam'],
  // Osmanlı Kuruluş
  ['osmanli kurulus', 'osmanli_kurulus'],
  ['osman bey', 'osmanli_kurulus'],
  ['orhan bey', 'osmanli_kurulus'],
  ['i. murat', 'osmanli_kurulus'],
  ['yildirim', 'osmanli_kurulus'],
  ['fetret', 'osmanli_kurulus'],
  ['tımar', 'osmanli_kurulus'],
  ['devsirme', 'osmanli_kurulus'],
  ['yeniceri', 'osmanli_kurulus'],
  // Osmanlı Yükseliş
  ['osmanli yukselis', 'osmanli_yukselis'],
  ['fatih', 'osmanli_yukselis'],
  ['yavuz', 'osmanli_yukselis'],
  ['kanuni', 'osmanli_yukselis'],
  ['istanbul fethi', 'osmanli_yukselis'],
  ['caldiran', 'osmanli_yukselis'],
  ['mohac', 'osmanli_yukselis'],
  ['hilafet', 'osmanli_yukselis'],
  // Osmanlı Duraklama / Modernleşme
  ['duraklama', 'osmanli_duraklama'],
  ['gerileme', 'osmanli_duraklama'],
  ['koprulu', 'osmanli_duraklama'],
  ['karlofca', 'osmanli_duraklama'],
  ['pasarofca', 'osmanli_duraklama'],
  ['kucuk kaynarca', 'osmanli_duraklama'],
  ['lale devri', 'osmanli_duraklama'],
  ['nizam-i cedid', 'osmanli_duraklama'],
  ['vaka-i hayriye', 'osmanli_duraklama'],
  ['tanzimat', 'osmanli_duraklama'],
  ['islahat', 'osmanli_duraklama'],
  ['mesrutiyet', 'osmanli_duraklama'],
  ['ii. mahmut', 'osmanli_duraklama'],
  ['ii. abdulhamid', 'osmanli_duraklama'],
  // Osmanlı Dağılma + I. Dünya
  ['dagilma', 'osmanli_dagilma'],
  ['trablusgarp', 'osmanli_dagilma'],
  ['balkan sav', 'osmanli_dagilma'],
  ['ittihat', 'osmanli_dagilma'],
  ['i. dunya', 'osmanli_dagilma'],
  ['canakkale', 'osmanli_dagilma'],
  ['sarikamis', 'osmanli_dagilma'],
  ["kut'ul amare", 'osmanli_dagilma'],
  ['mondros', 'osmanli_dagilma'],
  ['sevr', 'osmanli_dagilma'],
  // Millî Mücadele
  ['milli mucadele', 'milli_mucadele'],
  ['samsun', 'milli_mucadele'],
  ['havza', 'milli_mucadele'],
  ['amasya gen', 'milli_mucadele'],
  ['erzurum kong', 'milli_mucadele'],
  ['sivas kong', 'milli_mucadele'],
  ['misak-i milli', 'milli_mucadele'],
  ['tbmm', 'milli_mucadele'],
  ['gumru', 'milli_mucadele'],
  ['moskova ant', 'milli_mucadele'],
  ['ankara ant', 'milli_mucadele'],
  ['i. inonu', 'milli_mucadele'],
  ['ii. inonu', 'milli_mucadele'],
  ['sakarya', 'milli_mucadele'],
  ['buyuk taarruz', 'milli_mucadele'],
  ['dumlupinar', 'milli_mucadele'],
  ['mudanya', 'milli_mucadele'],
  ['lozan', 'milli_mucadele'],
  ['kuvayimilliye', 'milli_mucadele'],
  // Atatürk Dönemi
  ['ataturk donemi', 'ataturk_donemi'],
  ['cumhuriyet ilan', 'ataturk_donemi'],
  ['inkilap', 'ataturk_donemi'],
  ['hilafet kald', 'ataturk_donemi'],
  ['medeni kanun', 'ataturk_donemi'],
  ['latin alf', 'ataturk_donemi'],
  ['soyadi', 'ataturk_donemi'],
  ['altu', 'ataturk_donemi'],
  ['6 ilke', 'ataturk_donemi'],
  ['cumhuriyetcilik', 'ataturk_donemi'],
  ['milliyetcilik', 'ataturk_donemi'],
  ['halkcilik', 'ataturk_donemi'],
  ['devletcilik', 'ataturk_donemi'],
  ['laiklik', 'ataturk_donemi'],
  ['inkilapcilik', 'ataturk_donemi'],
  // II. Dünya + Çağdaş
  ['ii. dunya', 'ikinci_dunya_cagdas'],
  ['nato', 'ikinci_dunya_cagdas'],
  ['soguk savas', 'ikinci_dunya_cagdas'],
  ['kore', 'ikinci_dunya_cagdas'],
  ['ataturk dis', 'ikinci_dunya_cagdas'],
  ['montro', 'ikinci_dunya_cagdas'],
  ['hatay', 'ikinci_dunya_cagdas'],
];

// REV28 — Fen TOPIC_HINTS
const TOPIC_HINTS_FEN = [
  // Biyoloji
  ['hucre', 'bio_hucre'], ['organel', 'bio_hucre'], ['zar gec', 'bio_hucre'],
  ['kalitim', 'bio_kalitim'], ['mendel', 'bio_kalitim'], ['soyagac', 'bio_kalitim'], ['gen', 'bio_kalitim'],
  ['bolunme', 'bio_bolunme'], ['mitoz', 'bio_bolunme'], ['mayoz', 'bio_bolunme'], ['ureme', 'bio_bolunme'],
  ['canlilar dunyasi', 'bio_canlilar'], ['sinifland', 'bio_canlilar'], ['alem', 'bio_canlilar'],
  ['ekosistem', 'bio_ekosistem'], ['besin zinciri', 'bio_ekosistem'], ['biyolojik cesit', 'bio_ekosistem'],
  ['yasam bilimi', 'bio_yasam_bilimi'], ['bilesik', 'bio_yasam_bilimi'], ['organik', 'bio_yasam_bilimi'], ['inorganik', 'bio_yasam_bilimi'], ['enzim', 'bio_yasam_bilimi'],
  // Fizik
  ['optik', 'fizik_optik'], ['mercek', 'fizik_optik'], ['ayna', 'fizik_optik'], ['kirilma', 'fizik_optik'], ['aydinlanma', 'fizik_optik'],
  ['hareket', 'fizik_hareket_kuvvet'], ['kuvvet', 'fizik_hareket_kuvvet'], ['newton', 'fizik_hareket_kuvvet'], ['surtunme', 'fizik_hareket_kuvvet'],
  ['enerji', 'fizik_enerji'],
  ['isi', 'fizik_isi_sicaklik'], ['sicaklik', 'fizik_isi_sicaklik'], ['genlesme', 'fizik_isi_sicaklik'], ['hal degis', 'fizik_isi_sicaklik'],
  ['elektrik', 'fizik_elektrik_manyetizma'], ['devre', 'fizik_elektrik_manyetizma'], ['manyetik', 'fizik_elektrik_manyetizma'],
  ['basinc', 'fizik_basinc_kaldirma'], ['kaldirma', 'fizik_basinc_kaldirma'],
  ['dalga', 'fizik_dalgalar'], ['ses', 'fizik_dalgalar'],
  ['ozkutle', 'fizik_madde'], ['madde ve', 'fizik_madde'], ['yapisma', 'fizik_madde'],
  ['fizik bilim', 'fizik_giris'],
  // Kimya
  ['periyodik', 'kimya_atom_periyodik'], ['atom', 'kimya_atom_periyodik'], ['izotop', 'kimya_atom_periyodik'],
  ['etkilesim', 'kimya_etkilesim'], ['bag', 'kimya_etkilesim'], ['kovalent', 'kimya_etkilesim'], ['iyonik', 'kimya_etkilesim'],
  ['madde halleri', 'kimya_madde_halleri'], ['gaz', 'kimya_madde_halleri'], ['sivi', 'kimya_madde_halleri'],
  ['mol', 'kimya_temel_kanunlar'], ['kimyanin kanun', 'kimya_temel_kanunlar'], ['stokiyo', 'kimya_temel_kanunlar'],
  ['karisim', 'kimya_karisimlar'], ['homojen', 'kimya_karisimlar'], ['heterojen', 'kimya_karisimlar'],
  ['asit', 'kimya_asit_baz_tuz'], ['baz', 'kimya_asit_baz_tuz'], ['ph', 'kimya_asit_baz_tuz'],
  ['kimya bilimi', 'kimya_bilim'], ['sembolik dil', 'kimya_bilim'],
  ['gunluk hayat kimya', 'kimya_her_yerde'],
];

function getTopicHints() {
  const s = getDataSubject();
  if (s === 'tarih') return TOPIC_HINTS_TARIH;
  if (s === 'fen')   return TOPIC_HINTS_FEN;
  return TOPIC_HINTS_EDEBIYAT;
}

function normalizeTr(s) {
  return (s || '').toLowerCase()
    .replace(/ş/g, 's').replace(/ç/g, 'c').replace(/ğ/g, 'g')
    .replace(/ı/g, 'i').replace(/ö/g, 'o').replace(/ü/g, 'u');
}

function konuToSlug(konuText) {
  if (!konuText) return null;
  const lower = normalizeTr(konuText);
  // "TEKRAR" veya "deneme" sözcükleri varsa link verme (özet/sınav günleri)
  if (lower.includes('tekrar') || lower.includes('deneme')) return null;
  for (const [key, slug] of getTopicHints()) {
    const normKey = normalizeTr(key);
    if (lower.includes(normKey)) return slug;
  }
  return null;
}

// REV15 — Konu metninden alt başlık anchor'ı çıkar (slugify edilmiş heading id)
const ANCHOR_HINTS = [
  // Divan
  { match: /nazim bicim|nazim biç/, anchor: 'gazel' },
  { match: /16-18|fuzuli|baki/, anchor: '16-yuzyil-zirve-sairleri-fuzuli-ve-baki' },
  { match: /14-15|ahmedi|seyhi/, anchor: '14-15-yuzyil-onculeri' },
  { match: /17.*nef|nabi/, anchor: '17-yuzyil-nef-i-ve-nabi' },
  { match: /18.*nedim|seyh galip/, anchor: '18-yuzyil-nedim-ve-seyh-galip' },
  // Cumhuriyet
  { match: /garip|orhan veli|i\.? yeni/, anchor: 'garip-i-yeni' },
  { match: /ii\.? yeni|ikinci yeni/, anchor: 'ikinci-yeni' },
  { match: /toplumcu|nazim hikmet/, anchor: 'toplumcu-gercekci-siir' },
  { match: /modernist|oguz atay|tanpinar/, anchor: 'modernist-roman' },
  { match: /yedi mesale/, anchor: 'yedi-mesaleciler' },
  { match: /hisar/, anchor: 'hisarcilar' },
  { match: /sait faik/, anchor: 'sait-faik-abasiyanik' },
  { match: /saf siir|hece|yahya kemal/, anchor: 'saf-siir' },
  // Tanzimat
  { match: /tanzimat.*ilk|i\.? donem|sinasi|namik kemal/, anchor: 'tanzimat-i-donem' },
  { match: /tanzimat.*ii|ii\.? donem|recaizade|hamit/, anchor: 'tanzimat-ii-donem' },
  // Servet-i Fünun
  { match: /servet/, anchor: 'servet-i-funun-siir' },
  { match: /fecr-i ati|fecr-i a/, anchor: 'fecr-i-ati' },
  // Milli Edebiyat
  { match: /milli edeb|omer seyfettin|ziya gokalp|mehmet emin/, anchor: 'milli-edebiyat-siir-ve-hikaye' },
  // Halk
  { match: /asik|karacaoglan|kosma/, anchor: 'asik-edebiyati' },
  { match: /tekke|yunus emre|tasavvuf/, anchor: 'tekke-edebiyati' },
  { match: /anonim halk|mani|turk[uü]/, anchor: 'anonim-halk-siiri' },
  // İslamiyet öncesi
  { match: /destan/, anchor: 'destanlar-detayi' },
  { match: /orhun|gokturk/, anchor: 'orhun-yazitlari-detayi' },
  // Geleneksel tiyatro
  { match: /karagoz/, anchor: 'karagoz' },
  { match: /orta oyun/, anchor: 'orta-oyunu' },
  { match: /meddah/, anchor: 'meddah' },
  // Masal/Fabl/Destan
  { match: /masal/, anchor: 'masal-yapisi' },
  { match: /fabl/, anchor: 'fabl' },
  { match: /halk hikay/, anchor: 'halk-hikayeleri-detayi' },
  // Söz sanatları
  { match: /benzetme|tesbih/, anchor: 'benzetme' },
  { match: /istiare/, anchor: 'istiare' },
  { match: /soz san/, anchor: 'benzetme' },  // ilk söz sanatı
  // Şiir bilgisi
  { match: /kafiye|redif/, anchor: 'kafiye-turleri' },
  { match: /vezin|aruz/, anchor: 'aruz-vezni' },
  { match: /hece/, anchor: 'hece-vezni' },
  { match: /siir bilgisi/, anchor: 'nazim-birimi-turleri' },
  // Nesir
  { match: /roman tur/, anchor: 'roman-turleri' },
  { match: /hikaye tur/, anchor: 'hikaye-turleri' },
  { match: /nesir/, anchor: 'roman-turleri' },
  // Akımlar
  { match: /klasisizm/, anchor: 'klasisizm' },
  { match: /romantizm/, anchor: 'romantizm' },
  { match: /realizm/, anchor: 'realizm' },
  { match: /sembolizm/, anchor: 'sembolizm' },
  { match: /akim/, anchor: 'klasisizm' },  // genel akım dersinde ilk akıma git
];

function konuToAnchor(konuText) {
  if (!konuText) return null;
  const norm = normalizeTr(konuText);
  for (const { match, anchor } of ANCHOR_HINTS) {
    if (match.test(norm)) return anchor;
  }
  return null;
}

function escapeAttr(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
function escapeText(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

export async function renderProgram() {
  const p = await Data.program();
  const state = loadState();
  const checks = state.program_checkbox || {};
  const isFen = getDataSubject() === 'fen';

  window.__pageSetup = () => {
    document.querySelectorAll('[data-check]').forEach(box => {
      box.addEventListener('change', () => {
        toggleProgramCheckbox(box.dataset.check);
        updateProgressBar();
      });
    });
    updateProgressBar();
  };

  function updateProgressBar() {
    const total = document.querySelectorAll('[data-check]').length;
    const done = document.querySelectorAll('[data-check]:checked').length;
    const pb = document.getElementById('progBar');
    const pl = document.getElementById('progLabel');
    if (pb && pl) {
      const pct = total > 0 ? Math.round((done/total)*100) : 0;
      pb.style.width = pct + '%';
      pl.textContent = `${done} / ${total} gün tamamlandı (%${pct})`;
    }
  }

  const headerSub = isFen
    ? `Her gün için: <strong>📺 Video</strong> → <strong>📘 MEBİ özet</strong> → <strong>📝 Tarama testi</strong> → <strong>🎯 Site quiz</strong> → <strong>🔬 Simülasyon</strong>.<br><span class="text-xs">💡 Konu başlığına tıkla → site içi üniteye git · Video link'ine tıkla → YouTube açılır · Tik kutusu → tamamlandı</span>`
    : `Her gün için: <strong>(R)</strong> Bu site rehberi · <strong>(M)</strong> MEBİ özet PDF · <strong>(S)</strong> Çıkmış sorular pratik.<br><span class="text-xs">💡 Konu kutusuna tıkla → o konuya git · Tik kutusu → tamamlandı</span>`;

  return `
    <header class="mb-6">
      <h1 class="text-3xl font-bold mb-1">📅 ${isFen ? 'TYT Fen' : ''} 4 Haftalık Program</h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm">${headerSub}</p>
    </header>

    <div class="mb-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-3">
      <div class="flex items-center justify-between text-sm mb-1">
        <span class="font-semibold">İlerleme</span>
        <span id="progLabel" class="text-slate-500"></span>
      </div>
      <div class="h-2 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
        <div id="progBar" class="h-full bg-ok-500 transition-all" style="width:0%"></div>
      </div>
    </div>

    ${p.haftalar.map((hafta, hi) => `
      <section class="mb-6">
        <h2 class="text-xl font-bold mb-2 text-primary-700 dark:text-primary-100">
          Hafta ${hi+1}: ${hafta.baslik}
        </h2>
        ${hafta.vurgu ? `<p class="text-xs text-slate-600 dark:text-slate-400 mb-3 italic">${hafta.vurgu}</p>` : ''}
        <div class="space-y-2">
          ${hafta.gunler.map((g, gi) => {
            const key = `h${hi+1}_${g.gun.toLowerCase()}`;
            const checked = checks[key] ? 'checked' : '';
            const slug = konuToSlug(g.konu);
            const anchor = slug ? konuToAnchor(g.konu) : null;
            const href = slug ? (anchor ? `#/konular/${slug}#${anchor}` : `#/konular/${slug}`) : null;

            // FEN detaylı render
            if (isFen) {
              const dersBadge = g.ders === 'biyoloji' ? 'bg-emerald-600' : g.ders === 'kimya' ? 'bg-purple-600' : g.ders === 'fizik' ? 'bg-blue-600' : 'bg-slate-500';
              const dersIcon = g.ders === 'biyoloji' ? '🧬' : g.ders === 'kimya' ? '🧪' : g.ders === 'fizik' ? '⚛' : '📚';
              const videoUrl = g.video?.url || '';
              const videoLabel = g.video?.baslik || g.rehber || '';
              const showVideo = videoUrl && videoLabel;

              const inner = `
                <div class="flex items-baseline gap-2 mb-2 flex-wrap">
                  <span class="font-bold text-sm bg-primary-700 text-white px-2 py-0.5 rounded">${g.gun}</span>
                  <span class="inline-flex items-center gap-1 text-xs font-bold ${dersBadge} text-white px-2 py-0.5 rounded">${dersIcon} ${g.ders || ''}</span>
                  <span class="font-semibold text-sm">${escapeText(g.konu)}</span>
                  ${slug ? `<span class="text-[10px] text-primary-700 dark:text-primary-100 font-bold opacity-80">→ üniteye git</span>` : ''}
                  ${g.sure_tahmini ? `<span class="ml-auto text-[10px] text-slate-500">⏱ ${escapeText(g.sure_tahmini)}</span>` : ''}
                </div>

                <div class="grid gap-1.5 text-xs">
                  ${showVideo ? `
                    <div class="bg-red-50 dark:bg-red-900/20 border border-red-500/30 rounded px-2 py-1.5">
                      <a href="${escapeAttr(videoUrl)}" target="_blank" rel="noopener" class="flex items-start gap-2 hover:underline" onclick="event.stopPropagation()">
                        <span class="text-red-600 dark:text-red-400 font-bold flex-shrink-0">📺 Video:</span>
                        <span class="text-slate-700 dark:text-slate-200">${escapeText(videoLabel)} <span class="text-[10px] opacity-70">↗</span></span>
                      </a>
                    </div>
                  ` : ''}

                  ${g.mebi && g.mebi !== '—' ? `
                    <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-500/30 rounded px-2 py-1.5">
                      <span class="text-blue-700 dark:text-blue-300 font-bold">📘 MEBİ:</span>
                      <span class="text-slate-700 dark:text-slate-200">${escapeText(g.mebi)}</span>
                    </div>
                  ` : ''}

                  ${g.tarama && g.tarama !== '—' ? `
                    <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-500/30 rounded px-2 py-1.5">
                      <span class="text-amber-700 dark:text-amber-300 font-bold">📝 Tarama:</span>
                      <span class="text-slate-700 dark:text-slate-200">${escapeText(g.tarama)}</span>
                    </div>
                  ` : ''}

                  ${g.site_quiz && g.site_quiz !== '—' ? `
                    <div class="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-500/30 rounded px-2 py-1.5">
                      <span class="text-emerald-700 dark:text-emerald-300 font-bold">🎯 Site Quiz:</span>
                      <span class="text-slate-700 dark:text-slate-200">${escapeText(g.site_quiz)}</span>
                    </div>
                  ` : ''}

                  ${g.simulasyon && g.simulasyon !== '—' ? `
                    <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-500/30 rounded px-2 py-1.5">
                      <span class="text-purple-700 dark:text-purple-300 font-bold">🔬 Simülasyon:</span>
                      <span class="text-slate-700 dark:text-slate-200">${escapeText(g.simulasyon)}</span>
                      <a href="#/simulasyonlar" class="ml-1 text-[10px] text-purple-700 dark:text-purple-300 underline" onclick="event.stopPropagation()">→ aç</a>
                    </div>
                  ` : ''}

                  ${g.check ? `
                    <div class="bg-slate-100 dark:bg-slate-800/50 border-l-4 border-slate-400 dark:border-slate-600 rounded px-2 py-1.5 mt-1">
                      <span class="text-slate-700 dark:text-slate-200 font-bold">✅ Günün Hedefi:</span>
                      <span class="text-slate-600 dark:text-slate-300">${escapeText(g.check)}</span>
                    </div>
                  ` : ''}
                </div>
              `;
              return `
                <div class="flex items-start gap-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-2 has-[input:checked]:bg-ok-500/5 has-[input:checked]:border-ok-500/30">
                  <label class="cursor-pointer p-1 -m-1 flex items-center" title="Tamamlandı işaretle">
                    <input type="checkbox" data-check="${key}" ${checked} class="w-5 h-5 cursor-pointer" />
                  </label>
                  ${href ? `
                    <a href="${href}" class="flex-1 min-w-0 p-2 -m-2 rounded hover:bg-slate-50 dark:hover:bg-slate-800/50 transition">
                      ${inner}
                    </a>
                  ` : `
                    <div class="flex-1 min-w-0 p-2 -m-2">
                      ${inner}
                    </div>
                  `}
                </div>
              `;
            }

            // EDEBİYAT / TARİH render (eski schema)
            const inner = `
              <div class="flex items-baseline gap-2 mb-1 flex-wrap">
                <span class="font-bold text-sm bg-primary-700 text-white px-2 py-0.5 rounded">${g.gun}</span>
                <span class="font-semibold text-sm">${g.konu}</span>
                ${slug ? `<span class="text-[10px] text-primary-700 dark:text-primary-100 font-bold opacity-80">→ ${anchor ? 'alt başlığa' : 'konuya'} git</span>` : ''}
              </div>
              <div class="grid sm:grid-cols-3 gap-1 text-xs text-slate-600 dark:text-slate-400">
                <div><strong class="text-primary-700 dark:text-primary-100">R:</strong> ${g.rehber}</div>
                <div><strong class="text-primary-700 dark:text-primary-100">M:</strong> ${g.mebi}</div>
                <div><strong class="text-primary-700 dark:text-primary-100">S:</strong> ${g.sorular}</div>
              </div>
            `;
            return `
              <div class="flex items-start gap-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-2 has-[input:checked]:bg-ok-500/5 has-[input:checked]:border-ok-500/30">
                <label class="cursor-pointer p-1 -m-1 flex items-center" title="Tamamlandı işaretle">
                  <input type="checkbox" data-check="${key}" ${checked} class="w-5 h-5 cursor-pointer" />
                </label>
                ${href ? `
                  <a href="${href}" class="flex-1 min-w-0 p-2 -m-2 rounded hover:bg-slate-50 dark:hover:bg-slate-800/50 transition">
                    ${inner}
                  </a>
                ` : `
                  <div class="flex-1 min-w-0 p-2 -m-2">
                    ${inner}
                  </div>
                `}
              </div>
            `;
          }).join('')}
        </div>
      </section>
    `).join('')}
  `;
}
