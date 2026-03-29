# STIGA Product Assistant 🌱

Assistente conversazionale AI per la ricerca, comparazione e acquisto di prodotti STIGA per giardinaggio. Progetto live di [IntentifAI](https://www.intentifai.com) — proof-of-concept della piattaforma B2B2C di assistenti AI conversazionali per e-commerce.

**Live demo:** `https://stiga-product-assistant-production.up.railway.app`
_(credenziali: `stiga` / `StigaDemo2025!`)_

---

## Funzionalita

- Chat conversazionale con Claude (Anthropic) — consulente esperto STIGA dal 1934
- RAG ibrido — Sentence Transformers + re-ranking semantico su 500+ prodotti
- Streaming SSE — risposta progressiva token per token
- Comparatore prodotti — tabelle comparative generate dinamicamente da Claude
- Pannello prodotti in tempo reale — card con immagini, prezzi, link diretti a stiga.com
- Multi-lingua — risponde in italiano, inglese, tedesco, francese, spagnolo
- Prompt caching — ~85%+ cache hit rate, costo per query ridotto ~10x
- Analytics dashboard — tracciamento sessioni, query, CTR, confronti statistici (chi-quadro)
- Widget embed — versione iframe per integrazione su qualsiasi sito (stessa UX di index)

---

## Stack

- Backend: Flask + Gunicorn, Python 3.11
- AI: claude-sonnet-4-20250514 (Anthropic) con prompt caching
- RAG: paraphrase-multilingual-mpnet-base-v2 (Sentence Transformers)
- DB: PostgreSQL (Railway) — analytics e tracking
- Deploy: Railway (auto-deploy da GitHub main)
- Frontend: Vanilla JS + SSE + CSS custom

URL produzione: https://stiga-product-assistant-production.up.railway.app

---

## Setup Locale

```bash
git clone https://github.com/giusMaffi/stiga-product-assistant.git
cd stiga-product-assistant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Inserisci ANTHROPIC_API_KEY in .env
python scripts/generate_embeddings.py
python app/main.py
# → http://localhost:8000
```

---

## Struttura

```
stiga-product-assistant/
├── app/
│   ├── templates/
│   │   ├── index.html          # App principale (layout 40/60 chat + prodotti)
│   │   ├── widget.html         # Embed iframe (stessa UX, usa style.css)
│   │   ├── analytics.html      # Dashboard analytics
│   │   └── analytics_*.html    # Drill-down analytics
│   ├── static/
│   │   ├── css/style.css       # Stile unico (index + widget)
│   │   └── js/chat.js          # Chat + SSE + comparatore
│   ├── main.py                 # Flask app + query enrichment
│   ├── analytics_routes.py     # Blueprint analytics
│   └── analytics_tracker.py   # PostgreSQL event tracking
├── src/
│   ├── api/claude_client.py    # Claude API (streaming + caching)
│   ├── rag/                    # Retriever + matcher + embeddings
│   └── config.py               # System prompt + config
├── data/
│   ├── stiga_products.json     # Catalogo 500+ prodotti
│   └── embeddings/             # Pre-computed embeddings (.pkl)
├── scripts/generate_embeddings.py
├── utils/statistics.py         # Chi-square analytics
├── Procfile
└── railway.json
```

---

## Configurazione

Variabili d'ambiente Railway:
- ANTHROPIC_API_KEY (obbligatoria)
- DATABASE_URL (auto-inject da Railway Postgres)
- MODEL_NAME (opzionale, default: claude-sonnet-4-20250514)

---

## IntentifAI

Questo progetto e' il proof-of-concept della piattaforma IntentifAI.
Replica disponibile per altri settori (beauty, coffee, machinery).
Contatti: https://www.intentifai.com

 
deploy
