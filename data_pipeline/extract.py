"""
P2 - Metin Cikarma
==================
TITCK PDF'lerinden (KT + KUB) temiz metni cikarip, kunye ile birlikte
ilac basina bir JSON dosyasi olarak kaydeder.

Dosya 3 katman halinde okunur (yukaridan asagi = kucukten buyuge):
  KATMAN 1: tek PDF   -> metin        (extract_pdf_text, extract_if_exists)
  KATMAN 2: tek ilac  -> kayit (dict) (read_meta, process_drug, save_record)
  KATMAN 3: tum ilaclar (batch)       (iter_drug_folders, process_all)
"""

import fitz
import json
import os


def extract_pdf_text(pdf_path):
    """
    Bir PDF'in TUM metnini tek bir string olarak dondurur.
    Dosya yoksa/bozuksa HATA FIRLATIR (durust davranir).

    pdf_path: PDF dosyasinin yolu (str)
    return  : PDF'teki tum metin (str)
    """
    doc = fitz.open(pdf_path)

    pieces = []
    for page in doc:
        page_text = page.get_text()
        pieces.append(page_text)

    doc.close()
    full_text = "".join(pieces)
    return full_text


def extract_if_exists(pdf_path):
    """
    extract_pdf_text'in GUVENLI surumu.
    PDF varsa metnini cikarir; dosya yoksa ya da okunamiyorsa None doner.
    Amac: batch calisirken tek bozuk/eksik PDF tum isi coketmesin.

    pdf_path: PDF yolu
    return  : metin (str) ya da None
    """
    if not os.path.exists(pdf_path):
        return None

    try:
        return extract_pdf_text(pdf_path)
    except Exception:
        return None


def read_meta(folder_path):
    """
    Bir ilac klasorundeki meta.json'u okur ve dict olarak dondurur.

    folder_path: ilac klasorunun yolu (icinde meta.json var)
    return     : meta.json icerigi (dict)
    """
    meta_path = os.path.join(folder_path, "meta.json")

    with open(meta_path, encoding="utf-8") as f:
        data = json.load(f)

    return data


def process_drug(folder_path):
    """
    Bir ilac klasorunu bastan sona isler: kunyeyi okur, KT + KUB metnini
    cikarir, hepsini tek bir kayit (dict) olarak dondurur.
    Eksik/bozuk PDF varsa o belge listeye eklenmez (ilac komple kaybolmaz).

    folder_path: ilac klasorunun yolu
    return     : ilacin tam kaydi (dict)
    """
    meta = read_meta(folder_path)
    drug_id = os.path.basename(folder_path)

    documents = []

    kt_text = extract_if_exists(os.path.join(folder_path, "KT.pdf"))
    if kt_text:
        documents.append({"doc_type": "kt", "text": kt_text})

    kub_text = extract_if_exists(os.path.join(folder_path, "KUB.pdf"))
    if kub_text:
        documents.append({"doc_type": "kub", "text": kub_text})

    record = {
        "drug_id":   drug_id,
        "drug_name": meta["name"],
        "element":   meta["element"],
        "firm":      meta["firm"],
        "date_kt":   meta["date_kt"],
        "date_kub":  meta["date_kub"],
        "documents": documents,
    }
    return record


def save_record(record, output_dir):
    """
    Bir ilac kaydini (dict) output_dir icine <drug_id>.json olarak yazar.
    utf-8 + ensure_ascii=False -> Turkce karakterler bozulmaz.

    record    : process_drug'in dondurdugu dict
    output_dir: cikti klasoru (orn. "data_pipeline/output")
    return    : yazilan dosyanin yolu (str)
    """
    os.makedirs(output_dir, exist_ok=True)

    out_path = os.path.join(output_dir, record["drug_id"] + ".json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

    return out_path


def iter_drug_folders(data_root):
    """
    data_root/docs altindaki TUM ilac klasorlerinin tam yolunu tek tek uretir.
    Generator: her cagrida bir yol verir, hepsini bellege yuklemez.

    data_root: veri koku (orn. .env'deki DATA_ROOT)
    yield     : her ilac klasorunun tam yolu (str)
    """
    docs_dir = os.path.join(data_root, "docs")

    for name in os.listdir(docs_dir):
        full = os.path.join(docs_dir, name)
        if os.path.isdir(full):
            yield full


def process_all(data_root, output_dir, limit=None):
    """
    Tum ilaclari isler: her klasor icin process_drug + save_record.
    Idempotent: cikti zaten varsa atlar, yarida kesilirse kaldigi yerden devam eder.
    Tek ilac hata verirse cokmez; sayar ve devam eder.

    limit: sadece ilk N ilaci isle (test icin). None -> hepsi.
    """
    done = 0
    skipped = 0
    failed = 0

    for i, folder in enumerate(iter_drug_folders(data_root)):
        if limit is not None and i >= limit:
            break

        drug_id = os.path.basename(folder)
        out_path = os.path.join(output_dir, drug_id + ".json")

        if os.path.exists(out_path):
            skipped += 1
            continue

        try:
            record = process_drug(folder)
            save_record(record, output_dir)
            done += 1
        except Exception as e:
            failed += 1
            print("HATA:", drug_id, "->", e)

    print(f"BITTI -> islenen: {done}, atlanan: {skipped}, hatali: {failed}")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    folder = r"D:\titck_kubkt_data\docs\majezik-100-mg-film-kapli-tablet-TTCKOnaylKTM"

    text = extract_pdf_text(folder + r"\KT.pdf")
    print("KT toplam karakter:", len(text))

    meta = read_meta(folder)
    print("meta tipi   :", type(meta))
    print("name        :", meta["name"])
    print("element     :", meta["element"])
    print("firm        :", meta["firm"])

    print("\n--- process_drug ---")
    record = process_drug(folder)
    print("kayit anahtarlari:", list(record.keys()))
    print("drug_id          :", record["drug_id"])
    print("drug_name        :", record["drug_name"])
    print("belge sayisi     :", len(record["documents"]))
    for doc in record["documents"]:
        print(f"  - {doc['doc_type']}: {len(doc['text'])} karakter")

    print("\n--- save_record ---")
    out_dir = os.path.join("data_pipeline", "output")
    saved_path = save_record(record, out_dir)
    print("kaydedildi ->", saved_path)

    with open(saved_path, encoding="utf-8") as f:
        reloaded = json.load(f)
    print("geri okundu, drug_name:", reloaded["drug_name"])
    print("geri okundu, kt uzunluk:", len(reloaded["documents"][0]["text"]))
