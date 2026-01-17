#!/usr/bin/env python3
"""
Genera embeddings per tutti i prodotti
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import pickle
from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm

# Config
MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
PRODUCTS_PATH = Path(__file__).parent.parent / 'data' / 'stiga_products.json'
OUTPUT_PATH = Path(__file__).parent.parent / 'data' / 'embeddings' / 'products_embeddings.pkl'

def create_product_text(product: dict) -> str:
    """
    Crea testo completo per embedding
    
    IMPORTANTE: Usa descrizione_completa (non descrizione breve) 
    per massimizzare qualità retrieval
    """
    parts = []
    
    # Nome
    if product.get('nome'):
        parts.append(product['nome'])
    
    # Categoria
    if product.get('categoria'):
        parts.append(f"Categoria: {product['categoria']}")
    
    # Descrizione COMPLETA (non troncata!)
    # Usa descrizione_completa se disponibile, altrimenti descrizione
    descrizione = product.get('descrizione_completa') or product.get('descrizione', '')
    if descrizione:
        parts.append(descrizione)
    
    # Caratteristiche
    if product.get('caratteristiche'):
        # Supporta sia lista di stringhe che lista di dizionari
        caratteristiche = product['caratteristiche']
        if caratteristiche and isinstance(caratteristiche[0], dict):
            # Nuovo formato: lista di {titolo, descrizione}
            chars_text = ". ".join([f"{c['titolo']}: {c['descrizione']}" for c in caratteristiche])
        else:
            # Vecchio formato: lista di stringhe
            chars_text = ", ".join(caratteristiche)
        parts.append("Caratteristiche: " + chars_text)
    
    # Specifiche tecniche (TUTTE, non solo le importanti)
    specs = product.get('specifiche_tecniche', {})
    if specs:
        specs_text = []
        for key, value in specs.items():
            if value:  # Solo se non vuoto
                specs_text.append(f"{key}: {value}")
        
        if specs_text:
            parts.append("Specifiche: " + ", ".join(specs_text))
    
    # Keywords
    if product.get('keywords'):
        parts.append("Keywords: " + ", ".join(product['keywords']))
    
    # Prezzo (importante per query tipo "economico", "budget")
    if product.get('prezzo'):
        parts.append(f"Prezzo: {product['prezzo']}")
    
    return " | ".join(parts)

def main():
    print("="*70)
    print("🚀 GENERAZIONE EMBEDDINGS PRODOTTI STIGA")
    print("="*70)
    print()
    
    # Carica modello
    print(f"📦 Caricamento modello: {MODEL_NAME}")
    print("   (Questo può richiedere alcuni minuti al primo avvio...)")
    model = SentenceTransformer(MODEL_NAME)
    print("✅ Modello caricato!")
    print()
    
    # Carica prodotti
    print(f"📂 Caricamento prodotti da: {PRODUCTS_PATH}")
    with open(PRODUCTS_PATH, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"✅ Caricati {len(products)} prodotti")
    print()
    
    # Genera embeddings
    print("🔄 Generazione embeddings...")
    texts = []
    prodotti_con_descrizione_completa = 0
    prodotti_con_descrizione_breve = 0
    
    for product in tqdm(products, desc="Preparazione testi"):
        # Statistiche su quale descrizione usiamo
        if product.get('descrizione_completa'):
            prodotti_con_descrizione_completa += 1
        else:
            prodotti_con_descrizione_breve += 1
        
        text = create_product_text(product)
        texts.append(text)
    
    print(f"✅ Preparati {len(texts)} testi")
    print(f"   - Con descrizione completa: {prodotti_con_descrizione_completa}")
    print(f"   - Con descrizione breve: {prodotti_con_descrizione_breve}")
    print()
    
    print("🧠 Encoding con modello (può richiedere qualche minuto)...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    
    print(f"✅ Generati {len(embeddings)} embeddings")
    print(f"   Dimensione embeddings: {embeddings.shape}")
    print()
    
    # Crea directory output se non esiste
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Salva embeddings
    print(f"💾 Salvataggio embeddings in: {OUTPUT_PATH}")
    
    data_to_save = {
        'embeddings': embeddings,
        'model_name': MODEL_NAME,
        'num_products': len(products),
        'embedding_dim': embeddings.shape[1]
    }
    
    with open(OUTPUT_PATH, 'wb') as f:
        pickle.dump(data_to_save, f)
    
    print("✅ Embeddings salvati con successo!")
    print()
    
    # Statistiche
    print("="*70)
    print("📊 STATISTICHE")
    print("="*70)
    print(f"Prodotti processati: {len(products)}")
    print(f"Embeddings generati: {len(embeddings)}")
    print(f"Dimensione embeddings: {embeddings.shape[1]}")
    print(f"Modello utilizzato: {MODEL_NAME}")
    print(f"File salvato: {OUTPUT_PATH}")
    print()
    
    print("="*70)
    print("🎉 GENERAZIONE COMPLETATA!")
    print("="*70)
    print()
    print("Ora puoi avviare l'app con: python app/app.py")
    print()

if __name__ == '__main__':
    main()