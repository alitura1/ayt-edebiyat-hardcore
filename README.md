# AYT Edebiyat — Hardcore Hazırlık Sitesi

YKS 2026 AYT Türk Dili ve Edebiyatı bölümü için interaktif çalışma sitesi.

**192 ÖSYM sorusu (2018-2025)** analiz edilmiş, ÖSYM'nin mantığı, tuzakları, tekrar eden yazarları ve 2026 tahminleri tek site içinde.

## Özellikler

- 🎯 **Quiz**: ÖSYM tarzı 4-5 şıklı test, 467 otomatik kart
- 📚 **13 Konu öğretim sayfası**: Divan, Cumhuriyet, Edebi Akımlar... her birinde MEBİ özet PDF sayfa referansları gömülü
- 👤 **85 Yazar veritabanı**: Hangi yıl hangi eserle çıkmış, MEBİ sayfası nerede
- 🔮 **2026 tahminleri**: Boşluk haritası + güçlü adaylar (Yedi Meşaleciler, Hisarcılar...)
- 📅 **1 aylık çalışma programı**: Doküman + MEBİ + sorular paralel takvim, checkbox'lı ilerleme
- 📖 **Mini sözlük**: Akım × yazar × eser tabloları
- 🃏 **Hibrit kart sistemi**: Otomatik kartlar + manuel ekleme
- 📊 **İstatistikler**: Konu bazlı zayıflık, hata defteri otomatik tekrar
- 🌙 **Dark mode + mobile-first responsive**
- 💾 **localStorage**: Tüm ilerleme tarayıcıda, hesap gerekmez

## Mimari

- Statik HTML + Vanilla JS (ES6 modules)
- TailwindCSS (CDN)
- JSON veriler (`public/data/`)
- localStorage (progress, custom kartlar, ayarlar)

## Local çalıştırma

```bash
cd edebiyat-site
python -m http.server 8000 -d public
# Tarayıcı: http://localhost:8000
```

## Vercel deploy

```bash
cd edebiyat-site
vercel --prod
```

## Veri güncelleme

```bash
# Tüm JSON'ları yeniden üret
python scripts/generate_data.py

# Konu HTML'lerini yeniden üret
python scripts/generate_topics_html.py
```

## Kaynaklar

- MEB Ortaöğretim Genel Müdürlüğü — YKS Çıkmış Sorular 2018-2025 (AYT EA)
- MEBİ — AYT Türk Dili ve Edebiyatı Konu Özetleri (192 sayfa)
