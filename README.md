# google-bootcamp-team-97
# 💊 PharmaBot — Akıllı İlaç Bilgi Asistanı

## Takım 97

## Takım Elemanları ve Rolleri

| İsim | Rol |
|------|-----|
| Yakup İnan | Scrum Master 
| Nurican Özsaygılı | Product Owner 
| Elif Eren | Developer 


---

## Ürün İsmi
**PharmaBot**

---

## Ürün Açıklaması

PharmaBot, kullanıcıların ilaçlar hakkında güvenilir bilgiye hızlıca ulaşmasını sağlayan, yapay zeka destekli bir ilaç bilgi asistanıdır. Kullanıcılar ilaç adını yazarak ilacın kullanım talimatını, yan etkilerini, dozaj bilgisini ve birden fazla ilacın birlikte kullanılıp kullanılamayacağını öğrenebilir. Sistem, Türkiye'de ruhsatlı ilaçların prospektüs ve kullanma talimatlarından oluşan bir bilgi tabanı üzerinde RAG (Retrieval-Augmented Generation) mimarisiyle çalışmaktadır.

---

## Ürün Özellikleri

### Temel Özellikler (MVP)
- 💬 **Doğal dil ile ilaç sorgulama** — "Parol ne işe yarar?" gibi serbest metin sorularına yanıt
- ⚠️ **İlaç etkileşim kontrolü** — İki veya daha fazla ilacın birlikte kullanım güvenliğini sorgulama
- 📋 **Kullanım talimatı** — Aç karnına mı, tok karnına mı, günde kaç kez gibi detaylar
- 🔬 **Yan etki bilgisi** — Görülme sıklığına göre sınıflandırılmış yan etkiler
- 💊 **Dozaj bilgisi** — Yetişkin, çocuk ve yaşlı için doz bilgileri

### Orta Katman Özellikler
- 🧠 **Konuşma hafızası** — Aynı oturumda önceki sorular bağlama dahil edilir
- 👤 **Kullanıcı profili** — Kronik hastalık ve sürekli kullanılan ilaç listesi tutulur
- 🚨 **Kişiselleştirilmiş uyarı** — Kullanıcının profiline göre risk bildirimi
- 🔍 **Etken madde bazlı arama** — Ticari isim yerine etken madde ile sorgulama

### Ekstra Özellikler
- 🤖 **AI Agent** — Çok adımlı sorguları otomatik yönetir
- 📊 **Dashboard** — En çok sorgulanan ilaçlar ve etkileşimler
- 🌐 **Canlı deploy** — Web üzerinden erişilebilir uygulama

---

## Hedef Kitle

- **Birincil:** İlaç kullanmadan önce veya kullanırken bilgi edinmek isteyen genel kullanıcılar
- **İkincil:** Birden fazla ilaç kullanan kronik hastalık hastaları
- **Üçüncül:** Yakınlarının ilaçları hakkında bilgi almak isteyen bakıcılar ve aile bireyleri

**Yaş aralığı:** 18-70  
**Teknik seviye:** Akıllı telefon veya bilgisayar kullanan herkes  
**Konum:** Türkiye

---

## Teknik Stack

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python, FastAPI |
| AI / RAG | LangChain, ChromaDB |
| LLM | OpenAI GPT-4o / Llama 3 |
| Frontend | React, Tailwind CSS |
| Veritabanı | PostgreSQL |
| Veri Kaynağı | ilacabak.com, DrugBank |
| Deploy | Vercel (frontend), Railway (backend) |

---

## Product Backlog

### 🔴 Sprint 1 (19 Haziran – 5 Temmuz)
| # | User Story | Öncelik |
|---|-----------|---------|
| 1 | Kullanıcı olarak ilaç adını yazıp temel bilgilere ulaşmak istiyorum | Yüksek |
| 2 | Kullanıcı olarak ilacın yan etkilerini öğrenmek istiyorum | Yüksek |
| 3 | Kullanıcı olarak ilacı aç mı tok mu almam gerektiğini bilmek istiyorum | Yüksek |
| 4 | Geliştirici olarak ilaç verilerini ChromaDB'ye gömmek istiyorum | Yüksek |
| 5 | Geliştirici olarak temel RAG pipeline'ını kurmak istiyorum | Yüksek |
| 6 | Kullanıcı olarak basit bir chat arayüzü üzerinden soru sormak istiyorum | Yüksek |

### 🟡 Sprint 2 (6 Temmuz – 19 Temmuz)
| # | User Story | Öncelik |
|---|-----------|---------|
| 7 | Kullanıcı olarak iki ilacı birlikte kullanıp kullanamayacağımı öğrenmek istiyorum | Yüksek |
| 8 | Kullanıcı olarak birden fazla ilaç için aynı anda etkileşim kontrolü yaptırmak istiyorum | Orta |
| 9 | Kullanıcı olarak konuşma geçmişimin hatırlanmasını istiyorum | Orta |
| 10 | Kullanıcı olarak kendi ilaç listemi kaydedip profil oluşturmak istiyorum | Orta |
| 11 | Kullanıcı olarak etken madde adıyla da arama yapabilmek istiyorum | Orta |

### 🟢 Sprint 3 (20 Temmuz – 2 Ağustos)
| # | User Story | Öncelik |
|---|-----------|---------|
| 12 | Kullanıcı olarak profilime göre kişiselleştirilmiş uyarı almak istiyorum | Orta |
| 13 | Kullanıcı olarak uygulamaya tarayıcıdan herhangi bir cihazda erişmek istiyorum | Yüksek |
| 14 | Geliştirici olarak AI agent entegrasyonunu tamamlamak istiyorum | Orta |
| 15 | Geliştirici olarak uygulamayı production ortamına deploy etmek istiyorum | Yüksek |
| 16 | Kullanıcı olarak arayüzün mobil uyumlu olmasını istiyorum | Düşük |

---

## Yasal Uyarı

> PharmaBot yalnızca bilgilendirme amaçlıdır. Kesinlikle tıbbi tavsiye niteliği taşımaz. İlaç kullanımı konusunda mutlaka doktorunuza veya eczacınıza danışınız.

---

## Proje Takvimi

| Aşama | Tarih |
|-------|-------|
| Takımların Açıklanması | 12 Haziran 2026 |
| Sprint 1 | 19 Haziran – 5 Temmuz 2026 |
| Sprint 2 | 6 Temmuz – 19 Temmuz 2026 |
| Sprint 3 | 20 Temmuz – 2 Ağustos 2026 |
| Ürün Teslimi | 2 Ağustos 2026 |
| Top 10 Sunum | 14 Ağustos 2026 |