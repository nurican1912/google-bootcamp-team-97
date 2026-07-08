# Sprint 1 — PharmaBot

**Sprint tarihi:** 19 Haziran – 5 Temmuz 2026
**Sprint hedefi:** Projenin temelini oluşturacak, güvenilir ve kaliteli bir Türkçe ilaç bilgisi veri setinin toplanması ve doğrulanması. PharmaBot bir RAG (Retrieval-Augmented Generation) sistemi olduğu için ürünün doğruluğu doğrudan kaynak verinin kalitesine bağlıdır; bu nedenle geliştirmeye geçmeden önce sağlam bir veri temeli oluşturmak önceliklendirildi.

> Takım rolleri (Product Owner, Scrum Master, 3 Developer) ana [README](../../README.md) dosyasında belirtilmiştir.

---

## 1. Backlog Dağıtma Mantığı ve Story Seçimleri

Sprint 1 tamamen **veri toplama ve veri kalitesi** üzerine kurgulandı. RAG sistemlerinde modelin ürettiği cevabın güvenilirliği, arka plandaki verinin doğruluğuna ve tamlığına bağlıdır. Bu yüzden ilk sprintte kod geliştirmek yerine, ürünün üzerine kurulacağı veri katmanını sağlamlaştırmayı hedefledik.

**Story point mantığı:** Story'ler Fibonacci ölçeğinde (1, 2, 3, 5, 8) puanlandı. Story point, bir işin göreli efor/karmaşıklık büyüklüğünü ifade eder (saat değil). Sprint toplam kapasitesi **21 puan** olarak belirlendi; kılavuz kuralı gereği tek bir story'nin toplam puanın yarısını (10.5) geçmemesine dikkat edildi.

| # | User Story | Story Point | Durum |
|---|-----------|:-----------:|:-----:|
| 1 | İlaç bilgisi için güvenilir kaynakların (TİTCK KÜB/KT) belirlenmesi ve erişim yönteminin doğrulanması | 3 | Done |
| 2 | KÜB/KT dokümanlarının toplanması ve ham veri setinin oluşturulması | 8 | Done |
| 3 | Veri kalite kriterlerinin tanımlanması (güncellik, tamlık, format tutarlılığı) | 3 | Done |
| 4 | Toplanan verinin manuel kalite kontrolü ve doğrulaması | 5 | Done |
| 5 | Veri toplama otomasyonu için araştırma (spike) — teknik yaklaşımın belirlenmesi | 2 | Devam ediyor → Sprint 2'ye taşındı |

**Toplam planlanan:** 21 puan · **Tamamlanan:** 19 puan

---

## 2. Daily Scrum Notları

Bu sprintte ekip iletişimi **WhatsApp üzerinden asenkron** olarak yürütüldü. Sabit saatli formal bir daily scrum ritüeli uygulanmadı; koordinasyon, iş bölümü ve karşılaşılan engeller gün içinde grup üzerinden paylaşıldı.

Sprint boyunca ele alınan başlıca konular:
- Hangi TİTCK kaynağının (KÜB/KT) kullanılacağı ve erişim yönteminin belirlenmesi
- Dokümanların nasıl toplanacağı ve ham verinin nasıl organize edileceği
- Veriyi "kaliteli" kabul edebilmemiz için gereken kriterlerin tanımlanması
- Manuel kalite kontrolde tespit edilen eksik/tutarsız kayıtların ele alınması

Bu sprintte iletişim düzensiz ve asenkron kaldığı için ayrı bir kayıt tutulmadı. Sprint 2 aksiyonu olarak, her gün grup üzerinden kısa bir bireysel update formatına (dün ne yaptım / bugün ne yapacağım / engel var mı) geçilecektir.

---

## 3. Sprint Board

Bu sprintte ayrı bir board aracı (Miro/Trello/GitHub Projects) kullanılmadı; iş takibi WhatsApp üzerinden yürütüldü. Sprint sonundaki iş durumu aşağıdaki tabloda özetlenmiştir. Sprint 2'den itibaren board bir araç üzerinde tutulacaktır.

| Backlog | To Do | In Progress | Done |
|---------|-------|-------------|------|
| — | Veri toplama otomasyonu (spike sonrası) | Otomasyon araştırması | Kaynak belirleme (TİTCK) |
| | | | KÜB/KT doküman toplama |
| | | | Kalite kriterleri tanımlama |
| | | | Manuel kalite kontrol |

---

## 4. Ürün Durumu

Sprint 1 bir **veri altyapısı sprinti** olduğu için henüz kullanıcıya dönük bir arayüz veya çalışan uygulama çıktısı bulunmamaktadır. Bu sprintin somut çıktısı, PharmaBot'un RAG pipeline'ını besleyecek **doğrulanmış Türkçe ilaç bilgisi veri setidir.**

Sprint sonundaki durum:
- TİTCK KÜB/KT kaynaklarından ham veri toplandı.
- Veri, tanımlanan kalite kriterlerine göre manuel olarak doğrulandı.
- Ekip, verinin kalitesi ve kapsamı konusunda ortak bir değerlendirmeye vardı.
- Geliştirme (RAG pipeline) tarafına henüz başlanmadı; bu Sprint 2 hedefidir.

---

## 5. Sprint Review

**Hedef:** Güvenilir ve kaliteli bir ilaç bilgisi veri seti oluşturmak.

**Sonuç:** Hedef büyük ölçüde gerçekleştirildi. TİTCK KÜB/KT kaynaklarından veri toplandı, kalite kriterlerine göre doğrulandı ve ekip veri kalitesi konusunda ortak bir noktaya vardı. Veri toplama otomasyonu araştırma aşamasında kaldı ve Sprint 2'ye taşındı.

**Tamamlanan:**
- Güvenilir kaynak belirleme (TİTCK KÜB/KT)
- Ham veri setinin toplanması
- Kalite kriterlerinin tanımlanması
- Manuel kalite kontrol

**Tamamlanmayan / taşınan:**
- Veri toplama otomasyonu (Sprint 2'de geliştirilecek)

---

## 6. Sprint Retrospective

**İyi giden:**
- Ekip, veri toplama ve veri kalitesi konusunda net bir ortak anlayışa sahip oldu. RAG projesinde en kritik temel budur.
- Güvenilir ve otoriter bir kaynak (TİTCK KÜB/KT) belirlendi; bu, ürünün "sıfır halüsinasyon" hedefi için sağlam bir zemin oluşturdu.

**İyileştirilmesi gereken:**
- Sprint tamamen veri toplamaya odaklandığı için geliştirme (RAG pipeline) tarafına başlanamadı.
- Formal Scrum ritüelleri (sabit board, düzenli daily scrum kaydı) bu sprintte yürütülmedi; süreç kanıtları asenkron ve dağınık kaldı.
- Veri toplama manuel yürüdü; bu, ölçeklenmeyi zorlaştırıyor.

**Sprint 2 için aksiyonlar:**
1. Veri toplama otomasyonunu kurmak (manuel süreçten çıkmak).
2. Board'u bir araç üzerinde (tercihen GitHub Projects) tutmaya başlamak.
3. Günlük kısa WhatsApp update formatına geçmek.
4. RAG pipeline'a geçiş: embedding (BGE-M3) + vektör veritabanı (ChromaDB) + retrieval kurulumuna başlamak.
