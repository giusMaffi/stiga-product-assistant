# Stiga Product Assistant 🌱

Assistente conversazionale AI per la ricerca e comparazione di prodotti STIGA per giardinaggio.

## 🎯 Caratteristiche

- **Chat conversazionale** con AI (Claude) per trovare il prodotto perfetto
- **Sistema RAG** per recupero intelligente dei prodotti
- **Suggerimenti personalizzati** basati sulle esigenze dell'utente
- **Link diretti** alle pagine prodotto su stiga.com
- **Immagini prodotto** integrate nella chat
- **Interfaccia moderna** e responsive

## 📋 Prerequisiti

- Python 3.9+
- API Key Anthropic Claude
- macOS (o Linux/Windows con adattamenti)

## 🚀 Installazione

### 1. Clona il repository

```bash
git clone <your-repo>
cd stiga-product-assistant
```

### 2. Crea ambiente virtuale

```bash
python3 -m venv venv
source venv/bin/activate  # Su macOS/Linux
```

### 3. Installa dipendenze

```bash
pip install -r requirements.txt
```

### 4. Configura variabili d'ambiente

```bash
cp .env.example .env
# Modifica .env e inserisci la tua ANTHROPIC_API_KEY
```

### 5. Genera gli embeddings

```bash
python scripts/generate_embeddings.py
```

### 6. Avvia l'applicazione

```bash
python app/main.py
```

Apri il browser su `http://localhost:5000`

## 🏗️ Architettura

### Sistema RAG
1. **Embeddings**: Ogni prodotto viene convertito in un vettore semantico
2. **Retrieval**: Data una query utente, troviamo i prodotti più rilevanti
3. **Response**: Claude genera una risposta conversazionale con suggerimenti

### Flusso Conversazionale
```
Utente → Query → RAG Retrieval → Top-K Prodotti → Claude API → Risposta + Link/Immagini
```

## 📁 Struttura Progetto

```
stiga-product-assistant/
├── data/                  # Dataset e embeddings
├── src/                   # Codice sorgente
│   ├── rag/              # Sistema RAG
│   └── api/              # Client Claude API
├── app/                   # Applicazione web Flask
│   ├── static/           # CSS, JS, immagini
│   └── templates/        # Template HTML
├── scripts/              # Script utility
└── tests/                # Test
```

## 🔧 Configurazione

Modifica `src/config.py` per personalizzare:
- Modello Claude da utilizzare
- Numero di prodotti da recuperare (top-k)
- Temperatura del modello
- Prompt di sistema

## 🧪 Test

```bash
# Test del sistema RAG
python scripts/test_rag.py

# Test unitari
pytest tests/
```

## 🎨 Personalizzazione

### Stile
Modifica `app/static/css/style.css` per personalizzare l'aspetto della chat.

### Prompt
Modifica i prompt di sistema in `src/config.py` per cambiare il comportamento dell'assistente.

### Prodotti
Aggiungi/modifica prodotti in `data/stiga_products.json` e rigenera gli embeddings.

## 📝 Esempi di Query

- "Cerco un robot tagliaerba per un giardino di 500 m²"
- "Ho bisogno di un trattorino a batteria silenzioso"
- "Quale decespugliatore mi consigli per uso professionale?"
- "Differenza tra robot con e senza filo perimetrale?"

## 🤝 Contribuire

1. Fork del progetto
2. Crea un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT.

## 🙏 Riconoscimenti

- [Anthropic Claude](https://www.anthropic.com) per l'AI conversazionale
- [STIGA](https://www.stiga.com) per i dati prodotti
- [Sentence Transformers](https://www.sbert.net/) per gli embeddings
