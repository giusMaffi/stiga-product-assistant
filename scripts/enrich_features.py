#!/usr/bin/env python3
"""
Arricchisce i prodotti con caratteristiche e tecnologie
SICURO: salva in file NUOVO, non modifica l'originale
"""

import json
import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
}

TIMEOUT = 30
DELAY = 3  # Secondi tra richieste

def extract_features(url: str) -> dict:
    """Estrae caratteristiche e tecnologie dalla pagina prodotto"""
    
    result = {
        'caratteristiche': [],
        'tecnologie': []
    }
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # === CARATTERISTICHE ===
        features_section = soup.find('div', {'id': 'product-features'})
        if features_section:
            boxes = features_section.find_all('div', class_='product-features__box')
            for box in boxes:
                title_elem = box.find('div', class_='product-features__box-title')
                text_elem = box.find('div', class_='product-features__box-text')
                
                if title_elem and text_elem:
                    feature = {
                        'titolo': title_elem.get_text().strip(),
                        'descrizione': text_elem.get_text().strip()
                    }
                    result['caratteristiche'].append(feature)
        
        # === TECNOLOGIE ===
        tech_section = soup.find('div', {'id': 'product-technology'})
        if tech_section:
            slides = tech_section.find_all('div', class_='product-technology__slide')
            for slide in slides:
                title_elem = slide.find('div', class_='product-technology__slide-title')
                text_elem = slide.find('div', class_='tsu-truncate-text__content')
                
                if title_elem:
                    tech = {
                        'titolo': title_elem.get_text().strip(),
                        'descrizione': text_elem.get_text().strip() if text_elem else ''
                    }
                    result['tecnologie'].append(tech)
        
        time.sleep(DELAY)
        
    except Exception as e:
        print(f"    ⚠️ Errore: {e}")
    
    return result

def main():
    print("=" * 70)
    print("🔧 ARRICCHIMENTO DATI PRODOTTI STIGA")
    print("    Estrazione caratteristiche e tecnologie")
    print("=" * 70)
    print()
    
    # Percorsi
    input_path = Path(__file__).parent.parent / 'data' / 'stiga_products.json'
    output_path = Path(__file__).parent.parent / 'data' / 'stiga_products_enriched.json'
    
    # Carica prodotti esistenti
    print(f"📂 Caricamento da: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"✅ Caricati {len(products)} prodotti\n")
    
    # Arricchisci ogni prodotto
    enriched_count = 0
    
    for product in tqdm(products, desc="Arricchimento"):
        url = product.get('url')
        if not url:
            continue
        
        features = extract_features(url)
        
        # Aggiorna prodotto
        product['caratteristiche'] = features['caratteristiche']
        product['tecnologie'] = features['tecnologie']
        
        if features['caratteristiche'] or features['tecnologie']:
            enriched_count += 1
    
    # Salva in file NUOVO
    print(f"\n💾 Salvataggio in: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    # Statistiche
    total_features = sum(len(p.get('caratteristiche', [])) for p in products)
    total_tech = sum(len(p.get('tecnologie', [])) for p in products)
    
    print("\n" + "=" * 70)
    print("📊 STATISTICHE")
    print("=" * 70)
    print(f"Prodotti totali: {len(products)}")
    print(f"Prodotti arricchiti: {enriched_count}")
    print(f"Caratteristiche totali: {total_features}")
    print(f"Tecnologie totali: {total_tech}")
    print(f"\n✅ File salvato: {output_path}")
    print("\n⚠️  PROSSIMI PASSI (quando sei soddisfatto):")
    print("1. Verifica: head -100 data/stiga_products_enriched.json")
    print("2. Backup:   cp data/stiga_products.json data/stiga_products_backup.json")
    print("3. Replace:  mv data/stiga_products_enriched.json data/stiga_products.json")
    print("4. Rigenera: python3 scripts/generate_embeddings.py")

if __name__ == '__main__':
    main()
