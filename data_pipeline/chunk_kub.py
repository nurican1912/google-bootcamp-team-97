"""
P3 - KUB bolum-farkindalikli chunking
=====================================
KUB metnini numarali basliklardan (1., 4.5. gibi) bolumlere ayirir.
KT'nin ikizi ama iki farki var:
  - Basliklar IKI-SEVIYELI (4.1, 4.2, 4.5 ...)
  - Metin icinde capraz-referanslar var ("bkz. Bolum 4.5") -> elenmeli
"""

import re

from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)


def find_kub_headings(text):
    """
    KUB metnindeki numarali basliklari bulur.
    Hem ust-seviye (1., 2., ...) hem alt-seviye (4.1, 4.5, ...) yakalanir.
    Her eslesme icin {number, start, line} dondurur.

    Bu asamada capraz-referanslar da yakalanabilir; sonraki adimda eleyecegiz.

    text  : KUB metni (str)
    return: eslesme listesi (list[dict])
    """
    pattern = r"(?m)^[ \t]*(\d{1,2}(?:\.\d{1,2})?)\.?[ \t]+([A-ZÇĞİÖŞÜ].*)$"

    result = []
    for m in re.finditer(pattern, text):
        result.append({
            "number": m.group(1),
            "start":  m.start(),
            "line":   m.group(0).strip(),
        })

    return result


def _number_tuple(number):
    """
    Baslik numarasini sayisal tuple'a cevirir (sirali kiyas icin).
    "4.5" -> (4, 5)   |   "4" -> (4, 0)   |   "10" -> (10, 0)
    """
    parts = number.split(".")
    major = int(parts[0])
    minor = int(parts[1]) if len(parts) > 1 else 0
    return (major, minor)


def select_kub_headings(headings):
    """
    Gercek basliklari secer (ileri-monotonik): numarasi en son tutulandan
    KESINLIKLE buyuk olani tut. Boylece govdedeki numarali liste ogeleri
    (orn. "1. Haftada...") ve gec gelen capraz-referanslar elenir.

    headings: find_kub_headings ciktisi (list[dict])
    return  : filtrelenmis, sirali baslik listesi (list[dict])
    """
    kept = []
    last = (-1, -1)
    for h in headings:
        num = _number_tuple(h["number"])
        if num > last:
            kept.append(h)
            last = num    
    return kept

def split_kub_sections(text):
    """
    KUB metnini numarali basliklardan bolumlere ayirir.
    find_kub_headings + select_kub_headings ile gercek basliklari bulur,
    her basligin start'indan bir sonrakine kadar metni keser.

    text  : KUB metni (str)
    return: [{"number", "title", "text"}, ...] ya da baslik yoksa None
    """
    headings = find_kub_headings(text)
    filtered = select_kub_headings(headings)

    if not filtered:
        return None

    sections = []
    for i, h in enumerate(filtered):
        start = h["start"]
        if i + 1 < len(filtered):
            end = filtered[i + 1]["start"]
        else:
            end = len(text)
        piece = text[start:end].strip()
        sections.append({
            "number": h["number"],
            "title": h["line"],
            "text": piece,
        })
    return sections


SECTION_BY_KUB = {
    "4.1": "endikasyon",
    "4.2": "doz",
    "4.3": "kontrendikasyon",
    "4.4": "uyari",
    "4.5": "etkilesim",
    "4.6": "gebelik",
    "4.7": "arac_kullanimi",
    "4.8": "yan_etki",
    "4.9": "doz_asimi",
    "5.1": "farmakodinamik",
    "5.2": "farmakokinetik",
    "5.3": "klinik_guvenlilik",
    "6.1": "yardimci_madde",
    "6.3": "raf_omru",
    "6.4": "saklama_kub",
    "6.5": "ambalaj",
    "2": "bilesim",
}


def build_kub_chunks(text, meta):
    """
    KUB metnini bolumlere ayirir, uzun bolumleri alt-parcalar ve
    her parcayi etiketli bir chunk'a cevirir.

    Bilinen bolumler SECTION_BY_KUB'dan guzel etiket alir; bilinmeyenler
    "kub_<numara>" seklinde turetilmis etiket alir (hicbir bolum kaybolmaz).

    text  : KUB metni (str)
    meta  : ilac kaydi (dict)
    return: chunk listesi (list[dict]) ya da bolunemezse None
    """
    sections = split_kub_sections(text)
    if sections is None:
        return None

    chunks = []
    for s in sections:
        section = SECTION_BY_KUB.get(s["number"], "kub_" + s["number"])
        for piece in splitter.split_text(s["text"]):
            chunks.append({
            "text": piece,
            "section": section,
            "doc_type": "kub",
            "drug_id": meta["drug_id"],
            "drug_name": meta["drug_name"],
            "element": meta["element"],
        })


    return chunks

        

    



if __name__ == "__main__":
    import sys, json, os
    sys.stdout.reconfigure(encoding="utf-8")

    path = os.path.join("data_pipeline", "output",
                        "majezik-100-mg-film-kapli-tablet-TTCKOnaylKTM.json")
    data = json.load(open(path, encoding="utf-8"))
    kub_text = [d["text"] for d in data["documents"] if d["doc_type"] == "kub"][0]

    headings = find_kub_headings(kub_text)
    print(f"find_kub_headings -> {len(headings)} baslik (ham)")

    real = select_kub_headings(headings)
    print(f"select_kub_headings -> {len(real)} baslik (filtreli)")

    print("\n--- build_kub_chunks ---")
    chunks = build_kub_chunks(kub_text, data)
    print(f"KUB -> {len(chunks)} chunk")
    for c in chunks:
        print(f"  section={c['section']:<16} | {len(c['text'])} karakter")
