# Örnek çıktılar (samples)

Bunlar `extract.py`'nin (P2) ürettiği çıktıdan **birkaç temsili örnek**.

Tüm çıktı (`data_pipeline/output/`, 15.584 dosya, ~1 GB) repoya **girmez** — türetilmiş
veridir, `extract.py` çalıştırılınca yeniden üretilir. Bu klasör sadece **formatı
göstermek** için birkaç örnek tutar.

## Format (ilaç başına bir JSON)

```json
{
  "drug_id": "...",         // klasör adı = benzersiz kimlik
  "drug_name": "...",
  "element": "...",         // etkin madde
  "firm": "...",
  "date_kt": "...",
  "date_kub": "...",
  "documents": [
    { "doc_type": "kt",  "text": "<KT tam metni>" },
    { "doc_type": "kub", "text": "<KUB tam metni>" }
  ]
}
```

## Kendi çıktını üretmek

```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); \
from data_pipeline.extract import process_all; \
process_all(os.getenv('DATA_ROOT'), 'data_pipeline/output', limit=None)"
```
(Önce `.env` içinde `DATA_ROOT`'u TİTCK veri klasörüne ayarla.)
