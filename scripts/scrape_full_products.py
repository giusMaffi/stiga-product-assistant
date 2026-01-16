#!/usr/bin/env python3
"""
Scraper completo per pagine prodotto STIGA - VERSIONE CORRETTA
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from bs4 import BeautifulSoup
import json
import time
from typing import Dict, List

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'it-IT,it;q=0.9',
}

def extract_specs_from_page(soup: BeautifulSoup) -> tuple[Dict[str, Dict], Dict[str, str]]:
    """
    Estrae specifiche tecniche dalla pagina
    Ritorna: (specs_by_section, flat_specs)
    """
    specs_by_section = {}
    flat_specs = {}
    
    # Trova il container delle specifiche
    specs_container = soup.find('div', {'id': 'product-specs'})
    if not specs_container:
        return specs_by_section, flat_specs
    
    # Trova tutte le sezioni (ogni h3 + le sue specifiche)
    current_section = None
    current_specs = {}
    
    # Cerca tutti gli elementi in ordine
    for elem in specs_container.descendants:
        # Nuova sezione?
        if elem.name == 'h3' and 'product-specs__title' in elem.get('class', []):
            # Salva sezione precedente se presente
            if current_section and current_specs:
                specs_by_section[current_section] = current_specs.copy()
            
            current_section = elem.get_text().strip()
            current_specs = {}
        
        # È una label (chiave)?
        if elem.name == 'div' and 'label' in elem.get('class', []):
            key = elem.get_text().strip()
            
            # Cerca il corrispondente data (valore)
            # Il data è tipicamente un sibling o in un parent comune
            parent = elem.parent
            if parent:
                data_elem = parent.find('div', class_='data')
                if data_elem:
                    value = data_elem.get_text().strip()
                    
                    if key and value and current_section:
                        current_specs[key] = value
                        flat_specs[f"{current_section} - {key}"] = value
    
    # Salva ultima sezione
    if current_section and current_specs:
        specs_by_section[current_section] = current_specs
    
    return specs_by_section, flat_specs

def extract_product_details(url: str) -> Dict:
    """Estrae tutti i dettagli da una pagina prodotto"""
    print(f"  🔍 Scraping: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        product = {
            'url': url,
            'nome': '',
            'categoria': '',
            'sottocategoria': '',
            'descrizione': '',
            'descrizione_completa': '',
            'caratteristiche': [],
            'specifiche_tecniche': {},
            'specifiche_per_sezione': {},
            'prezzo': '',
            'prezzo_originale': '',
            'immagini': [],
            'keywords': []
        }
        
        # === NOME ===
        h1 = soup.find('h1', class_='page-title')
        if h1:
            product['nome'] = h1.get_text().strip()
        
        # === BREADCRUMB / CATEGORIA ===
        breadcrumb = soup.find('div', class_='breadcrumbs')
        if breadcrumb:
            links = breadcrumb.find_all('a')
            if len(links) >= 2:
                # Prendi la penultima (categoria principale)
                product['categoria'] = links[-2].get_text().strip()
            if len(links) >= 3:
                # L'ultima è spesso il prodotto stesso, ma a volte è sottocategoria
                last_link_text = links[-1].get_text().strip()
                if last_link_text.lower() != product['nome'].lower():
                    product['sottocategoria'] = last_link_text
        
        # === PREZZI ===
        price_special = soup.find('span', class_='special-price')
        if price_special:
            price = price_special.find('span', class_='price')
            if price:
                product['prezzo'] = price.get_text().strip()
        
        price_old = soup.find('span', class_='old-price')
        if price_old:
            price = price_old.find('span', class_='price')
            if price:
                product['prezzo_originale'] = price.get_text().strip()
        
        if not product['prezzo']:
            price = soup.find('span', {'data-price-type': 'finalPrice'})
            if price:
                product['prezzo'] = price.get_text().strip()
        
        # === DESCRIZIONE ===
        # Cerca vari pattern di descrizione
        desc = soup.find('div', {'id': 'product-details'})
        if not desc:
            desc = soup.find('div', class_='product-details')
        if not desc:
            desc = soup.find('div', class_='product-description')
        
        if desc:
            paragraphs = desc.find_all('p', recursive=False)
            if not paragraphs:
                # Se non ci sono <p>, prendi tutto il testo
                text = desc.get_text().strip()
                if text:
                    product['descrizione'] = text[:300]
                    product['descrizione_completa'] = text
            else:
                product['descrizione'] = paragraphs[0].get_text().strip()
                product['descrizione_completa'] = '\n'.join(
                    [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
                )
        
        # === CARATTERISTICHE ===
        # Cerca bullet points features
        features_section = soup.find('div', {'id': 'product-features'})
        if not features_section:
            features_section = soup.find('div', class_='product-features')
        
        if features_section:
            features_list = features_section.find('ul')
            if features_list:
                features = features_list.find_all('li')
                product['caratteristiche'] = [
                    f.get_text().strip() 
                    for f in features 
                    if f.get_text().strip()
                ]
        
        # === SPECIFICHE TECNICHE ===
        specs_by_section, flat_specs = extract_specs_from_page(soup)
        product['specifiche_per_sezione'] = specs_by_section
        product['specifiche_tecniche'] = flat_specs
        
        # === IMMAGINI ===
        gallery = soup.find('div', class_='fotorama')
        if gallery:
            imgs = gallery.find_all('img')
            for img in imgs:
                src = img.get('src') or img.get('data-src')
                if src and 'placeholder' not in src.lower():
                    full_url = src if src.startswith('http') else f"https://www.stiga.com{src}"
                    if full_url not in product['immagini']:
                        product['immagini'].append(full_url)
        
        # Fallback immagine principale
        if not product['immagini']:
            main_img = soup.find('img', class_='gallery-placeholder__image')
            if main_img and main_img.get('src'):
                src = main_img['src']
                full_url = src if src.startswith('http') else f"https://www.stiga.com{src}"
                product['immagini'].append(full_url)
        
        # === KEYWORDS ===
        keywords = set()
        text = soup.get_text().lower()
        
        # Aggiungi nome prodotto come keywords
        if product['nome']:
            nome_parts = product['nome'].lower().split()
            keywords.update(nome_parts)
        
        # Keywords comuni
        common_kw = [
            'robot', 'trattorino', 'tagliaerba', 'batteria', 'elettrico',
            'scoppio', 'gps', 'app', 'autonomo', 'mulching', 'raccolta',
            'decespugliatore', 'motosega', 'soffiatore', 'idropulitrice',
            'epower', 'benzina', 'litio', 'brushless'
        ]
        
        for kw in common_kw:
            if kw in text:
                keywords.add(kw)
        
        # Limita a 15 keywords
        product['keywords'] = sorted(list(keywords))[:15]
        
        time.sleep(2)  # Rate limiting cortese
        return product
        
    except Exception as e:
        print(f"    ❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main"""
    print("="*70)
    print("🕷️  SCRAPER COMPLETO PAGINE PRODOTTO STIGA - V2")
    print("="*70)
    print()
    
    # Carica dataset
    dataset_path = Path(__file__).parent.parent / 'data' / 'stiga_products.json'
    
    print(f"📂 Caricamento dataset: {dataset_path}")
    with open(dataset_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"✅ Trovati {len(products)} prodotti\n")
    
    # Scraping
    updated_products = []
    errors = []
    
    for i, product in enumerate(products, 1):
        url = product.get('url')
        if not url:
            print(f"⚠️  [{i}/{len(products)}] URL mancante, salto...")
            updated_products.append(product)
            continue
        
        print(f"[{i}/{len(products)}] {product.get('nome', 'Unknown')}")
        
        new_data = extract_product_details(url)
        
        if new_data:
            new_data['id'] = product.get('id')
            updated_products.append(new_data)
            
            # Stats
            n_specs = len(new_data.get('specifiche_tecniche', {}))
            n_sections = len(new_data.get('specifiche_per_sezione', {}))
            n_features = len(new_data.get('caratteristiche', []))
            n_images = len(new_data.get('immagini', []))
            
            print(f"    ✅ Specs: {n_specs} ({n_sections} sezioni) | Features: {n_features} | Immagini: {n_images}\n")
        else:
            updated_products.append(product)
            errors.append(url)
            print(f"    ⚠️  Errore, mantenuti dati vecchi\n")
    
    # Salva
    output_path = dataset_path.parent / 'stiga_products_full.json'
    
    print("="*70)
    print(f"💾 Salvataggio in: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(updated_products, f, ensure_ascii=False, indent=2)
    
    print("✅ Salvato!\n")
    
    # Stats finali
    total_specs = sum(len(p.get('specifiche_tecniche', {})) for p in updated_products)
    total_features = sum(len(p.get('caratteristiche', [])) for p in updated_products)
    
    print("📊 STATISTICHE:")
    print(f"   Prodotti totali: {len(updated_products)}")
    print(f"   Aggiornati con successo: {len(updated_products) - len(errors)}")
    print(f"   Errori: {len(errors)}")
    print(f"   Specifiche tecniche totali: {total_specs}")
    print(f"   Caratteristiche totali: {total_features}")
    
    if errors:
        print("\n⚠️  Errori su:")
        for url in errors[:5]:
            print(f"   - {url}")
    
    print("\n" + "="*70)
    print("🎉 COMPLETATO!")
    print("="*70)
    print("\nProssimi passi:")
    print("1. Verifica un prodotto: cat data/stiga_products_full.json | jq '.[0]'")
    print("2. Se ok: mv data/stiga_products_full.json data/stiga_products.json")
    print("3. Rigenera embeddings: python scripts/generate_embeddings.py\n")

if __name__ == '__main__':
    main()