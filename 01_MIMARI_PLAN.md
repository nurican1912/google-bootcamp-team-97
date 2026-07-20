# PharmaBot — Mimari Plan

> Google Bootcamp Team 97 · Türkçe, yapay zeka destekli **kişisel ilaç bilgi asistanı**
> Son güncelleme: 2026-07-13

---

## 1. Proje nedir, ne değildir?

**Ne:** Kullanıcının doğal dille ("Majezik ne işe yarar?", "X ve Y'yi birlikte alabilir miyim?", "bu ilacı kullanırken greyfurt yiyebilir miyim?") sorduğu soruları, **resmî TİTCK ilaç belgelerine (KT + KUB) dayanarak** cevaplayan bir chatbot. Üye kullanıcılar için bir profil (yaş, kilo, kullandığı ilaçlar, alerjenler) tutup **kişiye özel proaktif uyarılar** üretir.

**Ne değil:** Teşhis koyan, kişiye özel doz belirleyen, doktor yerine geçen bir sistem değil. Cevaplar yalnız belgelerdeki bilgiden üretilir; belge yoksa "bilmiyorum" der. (Yasal uyarı ve sorumluluk sözleşmesi arayüz/üyelik katmanında.)

**Ayırt edici özellik:** Sıradan bir "ilaç arama motoru" değil — kullanıcı profilini bilgiye katarak **kişisel danışman** gibi davranır. Asıl değer burada.

---

## 2. Özellikler

### İlk adım (MVP)
- Doğal dil ile ilaç sorusu → KT/KUB'a dayalı, kaynaklı cevap
- **İki ilacın birlikte kullanımı (etkileşim) kontrolü**
- Üye profili (ad, soyad, yaş, kilo, boy, cinsiyet, kullanılan ilaçlar, alerjenler)
- **Profil-tabanlı proaktif uyarı:** soru cevaplandıktan sonra, kullanıcının kullandığı ilaçlar / alerjenler / besinlerle çakışma varsa uyarı ekler

### Sonraki fazlar
Tüm MVP-sonrası özellikler ve data engineering yükseltmeleri **§12 Ürün Yol Haritası**'nda fazlanmış ve önceliklendirilmiş halde.

---

## 3. Veri kaynağı

| Konu | Değer |
|---|---|
| Kaynak | TİTCK KUB/KT (`getkubktviewdatatable` endpoint) |
| Toplama scripti | `catalog.py` → `manifest.jsonl` (mevcut) |
| Kayıt | **15.584 benzersiz ilaç** |
| Her ilaç için | `KT.pdf` (Kullanma Talimatı / hasta dili), `KUB.pdf` (Kısa Ürün Bilgisi / teknik), `meta.json` |
| meta.json alanları | name, element (etkin madde), firm, date_kt/kub, sha256, kaynak URL |
| PDF tipi | **Metin-tabanlı** (taranmış değil) → OCR gerekmez |
| Yerel yol | `D:\titck_kubkt_data` |

**Kritik yapısal avantaj:** KT belgeleri **sabit 5 bölüm** içerir:
1. … nedir ve ne için kullanılır?
2. … kullanmadan önce dikkat edilmesi gerekenler
3. … nasıl kullanılır?
4. Olası yan etkiler nelerdir?
5. … saklanması

Bu sabit yapı, "bölüm-farkındalıklı" parçalamayı (bkz. §6) mümkün kılar — projenin en büyük kalite kaldıracı. KUB ise teknik başlıklar içerir; **"diğer ilaçlarla etkileşim"** ve **besin etkileşimi** bilgisi asıl burada.

---

## 4. Teknoloji Stack

| Katman | Seçim | Neden |
|---|---|---|
| PDF metin çıkarma | **PyMuPDF (fitz)** | Hızlı, temiz, metin-PDF'lerde birebir |
| Embedding | **BAAI/bge-m3** | Açık/ücretsiz, yerelde çalışır, Türkçe güçlü, hibrit aramaya uygun |
| Vektör DB | **ChromaDB** (kalıcı) | Basit, hızlı kurulum; metadata filtreleme; ekip öğreniyor |
| Arama | **Hibrit** = BM25 + dense | İlaç adı exact-match sever; ikisi birleşince isabet artar |
| Orkestrasyon | **LangGraph** (LangChain üstüne) | Dallı/kararlı akış: chatbot + etkileşim + kişisel kontrol düğümleri |
| İsim çözümleme | **rapidfuzz** | "mannitol" → "%10 MANNİTOL ÇÖZELTİSİ" eşleme |
| İlişkisel DB | **PostgreSQL** | Kullanıcı, profil, sohbet geçmişi, ilaç künye tablosu |
| Backend | **FastAPI** (SSE stream) | Async, hızlı, streaming cevap |
| Frontend | **React + Tailwind** | Sohbet arayüzü + kaynak/citation gösterimi |
| Değerlendirme | **RAGAS** + ~50 soruluk Türkçe eval seti | Halüsinasyon/sadakat ölçümü |
| Deploy | **Vercel** (frontend) + **Railway** (backend, Postgres, Chroma kalıcı disk) | Basit, ücretsiz kademeler |
| LLM | ⏳ **karar bekliyor** — aday: Gemini Flash / Claude Haiku / GPT-4o-mini | Config'te swappable; eval ile seçilecek |

---

## 5. Katmanlı mimari

```
┌─ İNGESTION (offline, tek sefer + güncelleme) ────────────────┐
│ catalog.py ✅ → download → PyMuPDF çıkar                     │
│   → bölüm-farkındalıklı parçala (regex başlık) + etiketle    │
│   → BGE-m3 embed → Chroma'ya indeksle                        │
│   → yapısal künye (etkin madde, yardımcı maddeler) → Postgres│
└──────────────────────────────────────────────────────────────┘
┌─ ÇİFT BİLGİ KAYNAĞI ─────────────────────────────────────────┐
│ Chroma (RAG)     → serbest-metin sorular                     │
│ Postgres (yapısal)→ kesin kontroller: alerjen, etkileşim,    │
│                     kişisel profil                           │
└──────────────────────────────────────────────────────────────┘
┌─ BEYİN (LangGraph) ──────────────────────────────────────────┐
│ soru → isim çöz → [router] → ana cevap (hibrit RAG)          │
│      → kişisel kontrol düğümü → guardrail → kaynaklı cevap    │
└──────────────────────────────────────────────────────────────┘
┌─ API (FastAPI/SSE) ──── FRONTEND (React+Tailwind) ───────────┐
└──────────────────────────────────────────────────────────────┘
```

---

## 6. Kaliteyi belirleyen 3 yöntem

### 6.1 Bölüm-farkındalıklı chunking
KT'nin 5 sabit başlığı (ve KUB başlıkları) regex ile kesilir; her chunk şu etiketlerle saklanır:
- `doc_type`: `kt | kub`
- `section`: `endikasyon | kullanim | yan_etki | saklama | uyari | etkilesim | doz | farmakoloji …`
- `drug_id`, `drug_name`, `etkin_madde`

Böylece "yan etkileri neler?" sorusunda doğrudan `section=yan_etki` filtresiyle aranır → yanlış bağlam gelme ihtimali düşer → halüsinasyon minimuma iner.

### 6.2 İsim çözümleme (entity linking)
Retrieval'dan **önce** `rapidfuzz` ile sorgudaki ilaç adı, 15k ilaç + etkin madde listesine eşlenir. Marka isimleri Türkçe karakter + doz + firma içerdiği için embedding tek başına yetmez.

### 6.3 Hibrit arama
`EnsembleRetriever` = **BM25** (kelime/exact eşleşme, ilaç adı için) + **BGE-m3 dense** (anlamsal). İkisinin skorları birleştirilir.

---

## 7. Kişiselleştirme mimarisi

**Postgres tabloları:**
```
users            (id, ad, soyad, yaş, kilo, boy, cinsiyet)
user_medications (user_id, etkin_madde)     ← MARKA DEĞİL, etkin madde olarak
user_allergens   (user_id, madde)
drugs            (id, ad, etkin_madde, yardimci_maddeler[], firm)
```
`drugs` künye tablosu meta.json + PDF'ten çıkarılıp yapısal tutulur → alerjen/etkileşim kontrolü RAG'a gerek kalmadan **kesin ve anında** yapılır.

**Akış örneği:**
```
"Majezik kullanabilir miyim?"
  → isim çöz: Majezik → etkin madde = deksketoprofen
  → ANA CEVAP (RAG: KT'den ne olduğu / nasıl kullanıldığı)
  → KİŞİSEL KONTROL (profili yükle):
       • kullandığın ilaçlar ↔ deksketoprofen → KUB etkileşim
       • alerjenlerin ↔ etkin + yardımcı maddeler
  → varsa uyarı EKLE:
    "Not: Düzenli A ilacı kullanıyorsun; deksketoprofen ile
     etkileşir, birlikte kullanımı önerilmez."
```
Besin sorusu ("şu meyveyi yiyebilir miyim?") aynı düğümde: besini tespit et → kullandığı ilaçların KUB gıda-etkileşim bölümüne bak → uyar.

> **Neden etkin madde?** Etkileşimler KUB'da madde/sınıf düzeyinde yazılıdır; marka üzerinden eşleşmez. Resolver marka→etkin madde çevirir.

---

## 8. Guardrail (halüsinasyon ~0 hedefi)

Teknik kaldıraçlar:
- **Sıkı grounding:** model yalnız getirilen bağlamdan cevaplar; bağlam yoksa "bu bilgi elimde yok" der.
- **Zorunlu citation:** her cevabın altında kaynak (ilaç + KT/KUB + onay tarihi).
- **Düşük temperature:** modeli metne sadık tutar.
- Yüksek kaliteli veri + bölüm-filtreli retrieval yanlış bağlam ihtimalini baştan düşürür.

Yasal/uyarı katmanı (ürün kararı, arayüzde): filigran "bu bir AI, hata yapabilir, doktora danışın" + üyelikte sorumluluk sözleşmesi.

---

## 8.1 Çok-dillilik (TR + EN)

**Karar:** Bot, sorunun dilinde cevap verir — Türkçe soruya Türkçe, İngilizce soruya İngilizce. **Veri Türkçe kalır**; bu bir *sorgu/cevap-anı* meselesidir, veri hattını (P2–P7) değiştirmez.

Nasıl çalışır:
- **Retrieval:** BGE-m3 çok-dilli/cross-lingual olduğundan İngilizce sorgu Türkçe chunk'ları bulabilir (dense taraf taşır). Değişiklik gerekmez.
- **Cevap (P8):** grounding prompt'una "soru hangi dildeyse o dilde cevapla" kuralı eklenir. Dil tespiti LLM'de ya da `langdetect` ile.
- **Citation:** kaynaklar orijinal Türkçe kalır.

---

## 9. Repo yapısı

```
google-bootcamp-team-97/
├─ data_pipeline/
│   ├─ catalog.py        # ✅ mevcut
│   ├─ download.py       # PDF indir
│   ├─ extract.py        # PyMuPDF → ham metin
│   ├─ chunk.py          # bölüm-farkındalıklı parçala + etiketle
│   └─ index.py          # BGE-m3 embed → Chroma
├─ backend/
│   ├─ main.py           # FastAPI + SSE
│   ├─ graph/            # LangGraph düğümleri
│   │   ├─ router.py     # soru tipi (bilgi / etkileşim)
│   │   ├─ retrieve.py   # hibrit retriever
│   │   ├─ interaction.py# etkileşim + kişisel kontrol
│   │   └─ answer.py     # cevap + guardrail + citation
│   ├─ resolver.py       # rapidfuzz isim çözümleme
│   ├─ db.py             # Postgres (kullanıcı, geçmiş, künye)
│   └─ prompts/          # TR sistem promptları
├─ frontend/             # React + Tailwind
└─ README.md             # ✅ mevcut
```

---

## 10. Açık kararlar

| # | Karar | Durum |
|---|---|---|
| 1 | **LLM modeli** | Gemini Flash / Claude Haiku / GPT-4o-mini arasından, Türkçe eval setinde faithfulness + maliyet ölçülüp seçilecek. Kod swappable. |
| 2 | Chroma barındırma | Railway persistent volume (öneri) vs Chroma Cloud |
| 3 | Sohbet hafızası ayrıntısı | LangGraph state + Postgres kaydı |

---

## 11. Yol haritası (kaba)

1. **Veri hattı:** download → extract → chunk → index (çalışan Chroma)
2. **Yapısal katman:** Postgres künye tablosu (etkin madde, yardımcı maddeler)
3. **RAG çekirdeği:** hibrit retriever + resolver
4. **LangGraph:** router → retrieve → answer (temel chatbot)
5. **Etkileşim + kişisel kontrol düğümü**
6. **Auth + profil + Postgres geçmiş**
7. **FastAPI SSE + React arayüz**
8. **Eval (RAGAS) + model seçimi**
9. **Deploy**

---

## 12. Ürün Yol Haritası (Roadmap / Backlog)

> **Terminoloji notu:** MVP = ilk çalışan minimum ürün. Sonrasında gelen özellikler bütününe sektörde **Product Backlog** ya da **Roadmap** denir. Fazlama için yaygın adlandırma: **Fast Follow** (MVP'den hemen sonraki yakın-vade), **Later / Icebox** ("buzdolabı" — ileride). Önceliklendirme çerçevesi olarak **MoSCoW** kullanılır: *Must / Should / Could / Won't-for-now*. Aşağıda bu çerçeveyle düzenlendi.

### Faz 0 — MVP · *Must have* (şu an)
- Doğal dil ilaç sorusu → KT/KUB'a dayalı kaynaklı cevap
- İki ilaç etkileşim kontrolü
- Üye profili + profil-tabanlı proaktif uyarı
- Guardrail (grounding + citation)

> **UX kararı (2026-07-15):** MVP'de **tüm özellikler chatbot içinde** (router → düğüm). Muadil/etkileşim düz metin yerine **kart** olarak render edilir. Ayrı sekmeler (muadil bul paneli, çok-ilaç etkileşim kontrol paneli) **Faz 1+**'e ertelendi — aynı backend düğümlerini kullanacakları için sonradan eklemek ~sıfır iş.
>
> **Kapsam kararları (2026-07-15, elimizdeki KT/KUB verisiyle):**
> - **Doz:** kişiye özel doz *hesabı* YOK (güvenlik + guardrail). Sadece belgedeki (KUB 4.2 Pozoloji) doz ifadesi **aktarılır** + "kesin doz için doktor/eczacı" notu.
> - **Etkileşim:** garanti motor değil; KUB 4.5'e dayalı **uyarı/öneri** ("etkileşim kontrolü", "motor" deme).
> - **Muadil:** veri hazır (`element` alanı) → düşük maliyetli erken kazanç; **"aynı etkin maddeyi içeren ilaçlar"** diye sunulur ("resmî eşdeğer" değil — TİTCK eşdeğer listesiyle çapraz kontrol edilmeden).

### Faz 1 — Fast Follow · *Should have* (MVP'den hemen sonra, ürün özellikleri)
- Etkin madde bazlı **muadil / eşdeğer ilaç** bulma (veri hazır — MVP'de chatbot kartı, Faz 1'de "muadil bul" sekmesi)
- **Gebelik / emzirme** filtreleri (KUB ilgili bölümlerinden)
- **Ayrı sekmeler:** çok-ilaç etkileşim kontrol paneli (profildeki ilaçları seç → matris), muadil bul paneli
- Sohbet geçmişi + çok-turlu bağlam iyileştirmesi
- Reranker ile isabet artırımı (`bge-reranker-v2-m3`)

### Faz 2 — Veri Platformu / Data Engineering · *Should / Could* (portföy değeri yüksek)
Mevcut ingestion (elle çalışan script) → gerçek, orkestre edilen bir data pipeline'a dönüştürülür. Portföyde **hem RAG hem data engineering** anlatır.

| Yetenek | Şimdi | Hedef |
|---|---|---|
| **Orkestrasyon** | ❌ Yok (elle çalıştırılan script) | **Prefect/Airflow DAG** — cron ile TİTCK yoklama, otomatik tetikleme, retry, izleme |
| **Veri kalite kontrolleri** | ❌ Gayrı resmi | Boş chunk / encoding hatası / duplicate / **bölüm-çıkarma başarısız** tespiti; geçemeyen `needs_review`'e düşer |
| **Gözlemlenebilirlik** | ❌ Yok | Log, metrik (kaç yeni/işlendi/DQ'dan düştü/hata), alert |

Detay:
- **Otomatik tetikleme** = zamanlanmış *polling* (TİTCK webhook sunmaz) + `manifest` delta tespiti (yeni `folder` / değişmiş `sha256`) → sadece delta işlenir.
- **Idempotent + `drug_id` upsert** sayesinde tekrar çalışma duplicate üretmez.
- Araç önerisi: **Prefect** (hafif, Pythonic, hızlı öğrenilir) — *Airflow* daha çok CV keyword'ü ama ağır altyapı ister.
- **Ön koşul (şimdi yapılır):** P1–P4 idempotent, sha256-tabanlı, `drug_id` ile upsert eden temiz fonksiyonlar olarak yazılır → Faz 2'de bunları task'a sarmak neredeyse sıfır iş.

### Faz 3 — Later / Icebox · *Could / Won't-for-now*
- Sesli giriş (Whisper)
- İlaç hatırlatıcı / kişisel ilaç takvimi
- Çok dillilik
- Mobil uygulama
- Canlı-web aracı (korpusta olmayan sorular için arama-artırımlı fallback)
