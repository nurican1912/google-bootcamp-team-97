"""
P3 - KT bolum-farkindalikli chunking
====================================
KT metnini 5 sabit basliktan bolumlere ayirir, uzun bolumleri alt-parcalar,
her parcaya section/doc_type/drug_id etiketi basar.
"""

import re

from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)


def find_kt_headings(text):
    """
    KT metnindeki bolum basliklarini bulur (1..5 ile baslayan satirlar).
    Her eslesme icin bir sozluk dondurur: {number, start, line}.

    text  : KT metni (str)
    return: eslesme listesi (list[dict])
    """
    pattern = r"(?m)^\s*([1-5])\.\s+(.+)$"

    result = []
    for m in re.finditer(pattern, text):
        result.append({
            "number": m.group(1),
            "start":  m.start(),
            "line":   m.group(0).strip(),
        })

    return result


def select_real_headings(headings):
    """
    find_kt_headings 10 eslesme dondurur: 5'i icindekiler listesinden,
    5'i gercek bolum baslangicindan. Bu fonksiyon gercek 5'ini secer.

    Yontem (geriye-zincir): son "5."i al, ondan ONCEKI son "4."u al,
    ondan onceki son "3."u... Boylece icindekiler elenir ve konum sirasi
    garanti artan olur.

    headings: find_kt_headings ciktisi (list[dict])
    return  : 1..5 sirali 5 baslik (list[dict]) ya da bulunamazsa None
    """
    selected = [None] * 5
    limit = float("inf")

    for n in range(5, 0, -1):
        candidates = [h for h in headings if h["number"] == str(n) and h["start"] < limit]
        if not candidates:
            return None
        pick = max(candidates, key=lambda h: h["start"])
        selected[n - 1] = pick
        limit = pick["start"]

    return selected


def split_kt_sections(text):
    """
    KT metnini 5 bolume ayirir.

    text  : KT metni (str)
    return: [{"number", "title", "text"}, ...] (5 elemanli)
            ya da bolunemezse None
    """
    headings = find_kt_headings(text)
    real = select_real_headings(headings)

    if real is None:
        return None

    sections = []
    for i, h in enumerate(real):
        start = h["start"]
        if i + 1 < len(real):
            end = real[i + 1]["start"]
        else:
            end = len(text)
        body = text[start:end].strip()
        sections.append({
            "number": h["number"],
            "title": h["line"],
            "text": body,
        })

    return sections


SECTION_BY_NUMBER = {
    "1": "endikasyon",
    "2": "uyari",
    "3": "kullanim",
    "4": "yan_etki",
    "5": "saklama",
}


def build_kt_chunks(text, meta):
    """
    KT metnini bolumlere ayirir, uzun bolumleri alt-parcalar ve
    her parcayi etiketli bir chunk'a cevirir.

    text  : KT metni (str)
    meta  : ilac kaydi (dict) - drug_id, drug_name, element iceren (P2 JSON'u)
    return: chunk listesi (list[dict]) ya da bolunemezse None
    """
    sections = split_kt_sections(text)
    if sections is None:
        return None

    chunks = []
    for s in sections:
        for piece in splitter.split_text(s["text"]):
            chunks.append({
                "text": piece,
                "section": SECTION_BY_NUMBER[s["number"]],
                "doc_type": "kt",
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
    kt_text = [d["text"] for d in data["documents"] if d["doc_type"] == "kt"][0]

    chunks = build_kt_chunks(kt_text, data)
    print(f"KT -> {len(chunks)} chunk")
    for c in chunks:
        print(f"  section={c['section']:<12} | {len(c['text'])} karakter")
