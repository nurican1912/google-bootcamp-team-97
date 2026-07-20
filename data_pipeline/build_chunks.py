"""
P3 - Chunk driver
=================
Bir ilac kaydini (P2 JSON'u) alir, KT ve KUB chunk'larini birlestirir.
Bolumleme basarisiz olursa (font-bozuk vb.) kor chunk'a duser + needs_review.
"""

import os
import json

from chunk_kt import build_kt_chunks, splitter
from chunk_kub import build_kub_chunks


def blind_chunks(text, meta, doc_type):
    """
    Fallback: bolum bulunamayan metni bolum-farkindaliksiz, kor sekilde
    parcalar. Her chunk section="bilinmiyor" ve needs_review=True etiketli.

    text    : belge metni (str)
    meta    : ilac kaydi (dict)
    doc_type: "kt" ya da "kub"
    return  : chunk listesi (list[dict])
    """
    chunks = []
    for piece in splitter.split_text(text):
        chunks.append({
            "text": piece,
            "section": "bilinmiyor",
            "doc_type": doc_type,
            "drug_id": meta["drug_id"],
            "drug_name": meta["drug_name"],
            "element": meta["element"],
            "needs_review": True,
        })
    return chunks


def chunk_drug(record):
    """
    Bir ilacin TUM chunk'larini uretir (KT + KUB birlikte).
    Her belge icin once bolum-farkindalikli chunk dener; None donerse
    blind_chunks fallback'ine duser.

    record: P2 JSON'u (dict) - documents + kunye iceren
    return: birlesik chunk listesi (list[dict])
    """
    all_chunks = []
    for doc in record["documents"]:
        if doc["doc_type"] == "kt":
            chunks = build_kt_chunks(doc["text"], record)
        else:
            chunks = build_kub_chunks(doc["text"], record)

        if chunks is None:
            chunks = blind_chunks(doc["text"], record, doc["doc_type"])

        all_chunks.extend(chunks)

    return all_chunks


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    path = os.path.join("data_pipeline", "output",
                        "majezik-100-mg-film-kapli-tablet-TTCKOnaylKTM.json")
    record = json.load(open(path, encoding="utf-8"))

    chunks = chunk_drug(record)
    print(f"MAJEZIK -> {len(chunks)} chunk (KT + KUB)")

    from collections import Counter
    by_doc = Counter(c["doc_type"] for c in chunks)
    print("belge tipine gore:", dict(by_doc))
