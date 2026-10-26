# plothole-eval

Framework evaluasi LLM untuk deteksi plot hole pada naskah film.

## Setup
```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env    # lalu isi API key
python -m plothole info
```

## Data & hak cipta
Naskah dan teks ground truth tidak disimpan di repo. Repo hanya menyimpan
URL sumber, timestamp snapshot Wayback, dan hash SHA-256. Data dibuat ulang
dengan scraper.