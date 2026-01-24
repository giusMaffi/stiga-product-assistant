#!/usr/bin/env python3
"""
Genera embeddings per tutti i prodotti - CON PRODUCT_IDS
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
    """Crea testo completo per embedding"""
    parts = []
    
    # Nome
    if product.get('nome'):
        parts.append(product['nome'])
    
    # Categoria (ripetuta 2 volte per boost)
    if product.get('categoria'):
        categoria = product['categoria']
        parts.append(f"{categoria} {categoria}")
    
    # Descrizione COMPLETA
    descrizione = product.get('descrizione_completa') or product.get('descrizione', '')
    if descrizione:
        parts.append(descrizione)
    
    # Caratteristiche
    if product.get('caratteristiche'):
        caratteristiche = product['caratteristiche']
        if caratteristiche and isinstance(caratteristiche[0], dict):
            chars_text = ". ".join([f"{c['titolo']}: {c['descrizione']}" for c in caratteristiche])
        else:
            chars_text = ", ".join(caratteristiche)
        parts.append("Caratteristiche: " + chars_text)
    
    # Specifiche tecniche
    specs = product.get('specifiche_tecniche', {})
    if specs:
        specs_text = []
        for key, value in specs.items():
            if value:
                specs_text.append(f"{key}: {value}")
        
        if specs_text:
            parts.append("Specifiche: " + ", ".join(specs_text))
    
    # Keywords
    if product.get('keywords'):
        parts.append("Keywords: " + ", ".join(product['keywords']))
    
    # Prezzo
    if product.get('prezzo'):
        parts.append(f"Prezzo: {product['prezzo']}")
    
    return " | ".join(parts)

def main():
    print("="*70)
    print("🚀 GENERAZIONE EMBEDDINGS PRODOTTI STIGA - FIXED")
    print("="*70)
    print()
    
    # Carica modello
    print(f"📦 Caricamento modello: {MODEL_NAME}")
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
    
    for product in tqdm(products, desc="Preparazione testi"):
        text = create_product_text(product)
        texts.append(text)
    
    print(f"✅ Preparati {len(texts)} testi")
    print()
    
    print("🧠 Encoding con modello...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    
    print(f"✅ Generati {len(embeddings)} embeddings")
    print(f"   Dimensione embeddings: {embeddings.shape}")
    print()
    
    # Crea directory output se non esiste
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Salva embeddings CON PRODUCT_IDS
    print(f"💾 Salvataggio embeddings in: {OUTPUT_PATH}")
    
    data_to_save = {
        'embeddings': embeddings,
        'product_ids': [p['id'] for p in products],  # CRITICAL FIX!
        'model_name': MODEL_NAME,
        'num_products': len(products),
        'embedding_dim': embeddings.shape[1]
    }
    
    with open(OUTPUT_PATH, 'wb') as f:
        pickle.dump(data_to_save, f)
    
    print("✅ Embeddings salvati con successo!")
    print()
    
    print("="*70)
    print("📊 STATISTICHE")
    print("="*70)
    print(f"Prodotti processati: {len(products)}")
    print(f"Product IDs salvati: {len(data_to_save['product_ids'])}")
    print(f"Embeddings generati: {len(embeddings)}")
    print(f"Dimensione embeddings: {embeddings.shape[1]}")
    print(f"Modello utilizzato: {MODEL_NAME}")
    print(f"File salvato: {OUTPUT_PATH}")
    print()
    
    print("="*70)
    print("🎉 GENERAZIONE COMPLETATA!")
    print("="*70)

if __name__ == '__main__':
    main()
