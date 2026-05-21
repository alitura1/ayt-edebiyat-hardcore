# AYT Hardcore — Edebiyat & Tarih Hazırlık Sitesi

YKS 2026 AYT için interaktif çalışma sitesi. **İki ders tek sitede**: Edebiyat ve Tarih.

- **AYT Edebiyat**: 192 ÖSYM sorusu (2018-2025), 85 yazar, 251 eser, 634 kart, 13 konu
- **AYT Tarih**: 79 ÖSYM sorusu (2018-2025), 62 kişi, 35 antlaşma, 36 savaş, 671 kart, 10 dönem

Kullanıcı giriş ekranında ders seçer; header'da kalıcı toggle ile geçiş. **State izolasyonu**: Edebiyat ↔ Tarih ilerlemeleri ayrı tutulur, biri kapatıldığında diğeri kaybolmaz.

## Özellikler

- 🔀 **Hibrit ders sistemi**: Edebiyat + Tarih, izole state, header toggle ile anında geçiş
- 🎯 **Quiz**: ÖSYM tarzı 4-5 şıklı test (Edebiyat: 634 / Tarih: 671 kart)
- 📚 **Konu öğretim sayfaları**: Edebiyat 13 konu / Tarih 10 dönem (İslam Öncesi Türk → Çağdaş Dünya)
- 👤 **Veritabanı**: Edebiyat 85 yazar / Tarih 62 tarihî kişi (padişah, lider, devlet adamı)
- ⚔️ **Tarih için**: 35 antlaşma + 36 savaş + Atatürk sözleri × ilke eşleme
- 🔮 **2026 tahminleri**: Boşluk haritası + olasılık tablosu (her ders ayrı)
- 📅 **4 haftalık çalışma programı**: 28 gün, konu+kart+checkpoint
- 📖 **Mini sözlük**: Edebiyat (akım × yazar × eser) / Tarih (padişah × yıl, antlaşma × madde)
- 🃏 **Hibrit kart sistemi**: Otomatik kartlar + manuel ekleme
- 📊 **İstatistikler**: Konu bazlı zayıflık, hata defteri otomatik tekrar (SRS)
- 🌙 **Dark mode + amber/mavi subject teması**
- 💾 **localStorage**: `state-v2-edebiyat` + `state-v2-tarih` ayrı namespace
- ☁️ **Firestore sync**: `users/{uid}/subjects/{subject}` namespace
- 🔥 **Streak + Daily Hero**: Günlük rastgele kişi/olay tahmin oyunu (Tarih için 3 mod)

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
