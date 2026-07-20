# PharmaBot — Yapılanlar (Teknik Anlatım)

> Bugüne kadar inşa edilenlerin, `01_MIMARI_PLAN.md`'ye bağlı, adım adım açıklaması.
> Son güncelleme: 2026-07-20

---

## 0. Büyük resim — bu iş mimarinin neresi?

Mimarideki **İngestion (offline veri hattı)** katmanını inşa ediyoruz (bkz. `01_MIMARI_PLAN.md` §5):

```
catalog.py ✅ → download ✅ → PyMuPDF çıkar (P2) ✅
   → bölüm-farkındalıklı parçala + etiketle (P3) 🔄 ŞU AN
   → BGE-m3 embed → Chroma'ya indeksle (P4) ⬜
   → yapısal künye → Postgres (P5) ⬜
```

Kavramsal olarak bu bir **veri hattı / ETL**: **E**xtract (PDF→metin), **T**ransform (temizle, bölümle, chunk'la, etiketle), **L**oad (Chroma'ya yaz). Şu an **Transform** aşamasının kalbindeyiz.

---

## 1. P0 — Proje Kurulumu ✅

Kod yazmadan önceki zemin:
- **venv** (sanal ortam), **Python 3.10.7** — paketleri izole tutmak için (torch/langchain sürüm hassas).
- **requirements.txt** — bağımlılık listesi. Öğrenme-dostu: her parçada ihtiyaç doğunca paket açılıyor.
- **.env / .env.example** — makineye özel yol (`DATA_ROOT=D:\titck_kubkt_data`) ve sırlar koda gömülmez. `.env` git'e girmez.
- **Klasör iskeleti** — `data_pipeline/`, `backend/`, `frontend/` (mimari §9'a göre).
- **Git** — yerel klasör uzak repoya bağlandı (`nurican1912/google-bootcamp-team-97`).
- Kişisel notlar (`00_ILERLEME`, `02_OGRENME_PLANI`, `03_OGRENDIKLERIM`) `.gitignore`'da.

**Veri durumu:** P1 (indirme) zaten bitmiş bulundu — `docs/` altında 15.584 klasör, 31.122 PDF (ilaç başına KT+KUB+meta.json). O yüzden P1 atlandı.

---

## 2. P2 — Metin Çıkarma (`data_pipeline/extract.py`) ✅

**Amaç:** Her ilacın PDF'lerinden metni çıkarıp, künyeyle birlikte ilaç başına bir JSON'a yazmak.

**Kavram:** TİTCK PDF'lerinin çoğu **metin-tabanlı** (taranmış değil) → PyMuPDF metin katmanını doğrudan okur, OCR gerekmez. *(Not: %7.6'sı aslında taranmış çıktı — bkz. §4.)*

Dosya 3 katman halinde okunur (küçükten büyüğe):

### KATMAN 1 — tek PDF → metin
- **`extract_pdf_text(pdf_path)`** — PDF'i açar, her sayfada `page.get_text()` çağırır, hepsini birleştirip tek string döndürür. Dosya yoksa/bozuksa **hata fırlatır** (dürüst davranır).
- **`extract_if_exists(pdf_path)`** — `extract_pdf_text`'in **güvenli** sürümü: dosya yoksa ya da okunamıyorsa `None` döner (batch'te tek bozuk PDF tüm işi çökertmesin). *Tasarım: "fail-loud core, fail-soft wrapper" — işi yapmak ile hataya karar vermek ayrı sorumluluklar.*

### KATMAN 2 — tek ilaç → kayıt (dict)
- **`read_meta(folder_path)`** — `meta.json`'u okur, `json.load` ile Python dict'e çevirir.
- **`process_drug(folder_path)`** — künyeyi + KT/KUB metinlerini birleştirir, tek kayıt üretir:
  ```json
  {
    "drug_id", "drug_name", "element", "firm", "date_kt", "date_kub",
    "documents": [ {"doc_type":"kt","text":"..."}, {"doc_type":"kub","text":"..."} ]
  }
  ```
  Eksik PDF varsa o belge listeye eklenmez → ilaç komple kaybolmaz.
- **`save_record(record, output_dir)`** — kaydı `<drug_id>.json` olarak yazar. **utf-8 + `ensure_ascii=False`** → Türkçe karakterler bozulmaz.

### KATMAN 3 — tüm ilaçlar (batch)
- **`iter_drug_folders(data_root)`** — `docs/` altındaki tüm ilaç klasörlerini tek tek üreten **generator** (`yield`). Hepsini belleğe yüklemez.
- **`process_all(data_root, output_dir, limit)`** — her klasörü işler + kaydeder. **Idempotent**: çıktı zaten varsa atlar (çökerse kaldığı yerden devam). Tek ilaç hata verirse çökmez, sayar.

**Sonuç:** `process_all(limit=None)` → **15.584 ilaç → `output/*.json`, 0 çökme.** Çıktı ~1 GB (repoya girmez, `data_pipeline/samples/` içinde 2 örnek var).

**Kavramlar:** JSON↔dict (kutu vs kurulmuş mobilya), RAM vs disk (ara JSON = checkpoint), encoding (metin bellekte doğru, yazarken utf-8 şart), idempotency, generator.

---

## 3. P3 — Bölüm-Farkındalıklı Chunking (`chunk_kt.py` + `chunk_kub.py`) 🔄

**Amaç (mimari §6.1):** Metni KT'nin **5 sabit başlığına** göre bölümlere ayırmak ve her parçaya `section`/`doc_type`/`drug_id` etiketi basmak. Bu, projenin **en büyük kalite kaldıracı**: "yan etkileri neler?" sorusunda `section=yan_etki` filtresiyle aranır → yanlış bağlam ihtimali düşer → halüsinasyon azalır.

**Chunk nedir:** Küçük bir metin parçası + onu tanımlayan etiketler. Vektör DB'de (Chroma) **tek bir aranabilir birim**. Hem arama birimi hem cevap malzemesi.

### KT tarafı — TAMAM ✅
- **`find_kt_headings(text)`** — regex ile `1.`…`5.` ile başlayan satırları bulur. Kalıp: `r"(?m)^\s*([1-5])\.\s+(.+)$"`. Her eşleşme için `{number, start, line}` döndürür.
- **`select_real_headings(headings)`** — KT'de başlıklar **iki kez** geçer (önce "içindekiler" listesi, sonra gerçek bölüm). Bu fonksiyon **geriye-zincir** algoritmasıyla gerçek 5'ini seçer: sondan başla (son 5 → ondan önceki son 4 → …). İçindekiler elenir, sıra garanti artan olur.
- **`split_kt_sections(text)`** — seçilen 5 başlığın `start` konumlarından metni **5 bölüme keser** (`text[start:end]`). Her bölüm: `{number, title, text}`.
- **`SECTION_BY_NUMBER`** — numara→etiket tablosu: `1→endikasyon, 2→uyari, 3→kullanim, 4→yan_etki, 5→saklama`.
- **`build_kt_chunks(text, meta)`** — bölümleri **etiketli chunk**'a çevirir. Uzun bölümleri **LangChain `RecursiveCharacterTextSplitter`** (chunk_size=1000, overlap=150) ile alt-parçalar. Her chunk: `{text, section, doc_type, drug_id, drug_name, element}`.

**Sonuç:** MAJEZİK KT → 5 bölüm → **20 chunk** (uzun "uyari" 8'e, "yan_etki" 6'ya bölündü; hepsi doğru `section` etiketli).

**Strateji seçimleri veriyle yapıldı:** 200 ilaçta üç yöntem ölçüldü — gap-tabanlı %68, son-geçiş %89.6, **geriye-zincir %97.8** (kazanan). Ders: sezgi değil, **veri karar verir**.

### KUB tarafı — TAMAM ✅ (`chunk_kub.py`)
KT'nin ikizi, farklı regex + filtre:
- **`find_kub_headings`** — iki-seviyeli regex (`\d{1,2}(?:\.\d{1,2})?`). `[ \t]+` (aynı satır şartı) sayfa numaralarını + çapraz-referansları eler; başlık uzunluk sınırı yok (4.5 etkileşimi kaçırmasın diye).
- **`select_kub_headings`** — **ileri-monotonik** filtre: numarası son tutulandan büyükse tut. Gövde liste öğeleri ("1. Haftada...") ve geç atıfları eler. (`_number_tuple` ile sayısal kıyas: `"4.5"→(4,5)`.)
- **`split_kub_sections`** — başlık start'larından dilimle (KT ile aynı mantık).
- **`SECTION_BY_KUB` + `build_kub_chunks`** — **tüm bölümler alınır**: önemliler güzel etiket (`4.5→etkilesim`, `4.2→doz`, `4.6→gebelik`, `4.8→yan_etki`, **`6.1→yardimci_madde`**), bilinmeyenler `.get()` ile `kub_<no>` türetilmiş etiket → hiçbir bölüm kaybolmaz.

**Sonuç:** MAJEZİK KUB → 74 chunk. `etkilesim` (7) + `yardimci_madde` yakalandı.

### Driver + fallback — TAMAM ✅ (`build_chunks.py`)
- **`blind_chunks`** — fallback: bölüm bulunamayan (font-bozuk) metni kör parçalar, `section="bilinmiyor"` + `needs_review=True`.
- **`chunk_drug(record)`** — bir ilacın KT + KUB chunk'larını birleştirir; `build_*_chunks` `None` dönerse `blind_chunks`'a düşer. **MAJEZİK → 94 chunk (20 KT + 74 KUB).**

**Tüm 15.584'te doğrulama (2026-07-20):** işlenen 14.504 · boş 1.080 · **toplam 1.091.595 chunk** (ort 75.3/ilaç) · fallback 646 · **çökme 0.** İskelet sağlam.

---

## 4. Yol boyu keşfedilen veri kalitesi gerçeği

`find_kt_headings` tüm 15.584 ilaçta test edildi:
- ✅ **14.167 (%90.9)** temiz bölümleniyor.
- ⚠️ **235 (%1.5)** — KT metni var ama bölümlenemiyor (font-bozuk veya yapısal fark) → **fallback** (kör chunk + `needs_review`).
- ❌ **1.182 (%7.6)** — KT metni boş. Kök nedenler (kök-neden analiziyle bulundu):
  - **Taranmış görüntü PDF** (metin katmanı yok, sayfa=resim) → OCR gerekir.
  - **KT.pdf yok** → KUB varsa onu kullan.
  - **Mükerrer kayıt** (boş kopya + dolu kopya) → dedup.

**MVP kararı:** 235 + 1.182 için fallback/needs_review; **OCR + dedup Faz 2** (veri kalite platformu — portföyde data engineering değeri).

*Not: Mimari plandaki "hepsi metin-tabanlı, OCR gerekmez" varsayımı veriyle test edilince kısmen yanlış çıktı — varsayımları ölçmenin önemi.*

---

## 5. NEREDE KALDIK

- **Bitti:** P0 ✅ · P2 ✅ (15.584 ilaç işlendi) · P3 KT chunking ✅
- **Şu an:** P3 KUB tarafı — `find_kub_headings` + `SECTION_BY_KUB` + `build_kub_chunks` tasarlanıyor.
- **Sıradaki adımlar:**
  1. KUB kardeş fonksiyonları (tüm bölümler, çapraz-referans filtresi)
  2. Fallback (bölünemeyen → kör chunk + needs_review) + tüm ilaçları chunk'layan driver
  3. **P4** — BGE-m3 ile embed + ChromaDB'ye yükleme
  4. P5 (Postgres künye) · P6 (resolver) · P7 (hibrit retriever) · P8+ (LangGraph chatbot)

---

## 6. Üretilen dosyalar
```
data_pipeline/
├─ extract.py      # P2 - metin çıkarma (7 fonksiyon)
├─ chunk_kt.py     # P3 - KT chunking (tamam)
├─ chunk_kub.py    # P3 - KUB chunking (tamam)
├─ build_chunks.py # P3 - driver: chunk_drug (KT+KUB birleştir) + fallback
├─ output/         # 15.584 JSON (gitignore - türetilmiş veri)
└─ samples/        # 2 örnek çıktı + README (repoda görünür)
```
