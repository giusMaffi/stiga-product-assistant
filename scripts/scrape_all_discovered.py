#!/usr/bin/env python3
"""
Scraper per tutti i prodotti scoperti da discover_all_products.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from bs4 import BeautifulSoup
import json
import time
from typing import Dict
from tqdm import tqdm

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
}

def extract_specs_from_page(soup: BeautifulSoup) -> tuple:
    """Estrae specifiche tecniche dalla pagina"""
    specs_by_section = {}
    flat_specs = {}
    
    specs_container = soup.find('div', {'id': 'product-specs'})
    if not specs_container:
        return specs_by_section, flat_specs
    
    current_section = None
    current_specs = {}
    
    for elem in specs_container.descendants:
        if elem.name == 'h3' and 'product-specs__title' in elem.get('class', []):
            if current_section and current_specs:
                specs_by_section[current_section] = current_specs.copy()
            
            current_section = elem.get_text().strip()
            current_specs = {}
        
        if elem.name == 'div' and 'label' in elem.get('class', []):
            key = elem.get_text().strip()
            parent = elem.parent
            if parent:
                data_elem = parent.find('div', class_='data')
                if data_elem:
                    value = data_elem.get_text().strip()
                    
                    if key and value and current_section:
                        current_specs[key] = value
                        flat_specs[f"{current_section} - {key}"] = value
    
    if current_section and current_specs:
        specs_by_section[current_section] = current_specs
    
    return specs_by_section, flat_specs

def extract_product_details(url: str, product_id: str) -> Dict:
    """Estrae tutti i dettagli da una pagina prodotto"""
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        product = {
            'id': product_id,
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
        
        # === BREADCRUMB / CATEGORIA - Versione robusta ===
        breadcrumb = soup.find('nav', class_='breadcrumbs') or soup.find('div', class_='breadcrumbs') or soup.find('ol', class_='breadcrumb')
        
        if breadcrumb:
            # Prova diversi pattern di breadcrumb
            links = breadcrumb.find_all('a')
            
            if len(links) >= 3:
                # Prendi la penultima categoria (ignora Home e prodotto)
                cat_text = links[-2].get_text().strip()
                product['categoria'] = cat_text
            elif len(links) >= 2:
                cat_text = links[-1].get_text().strip()
                # Se non è il nome prodotto, usalo come categoria
                if cat_text.lower() != product['nome'].lower():
                    product['categoria'] = cat_text
        
        # === Fallback: inferisci categoria dall'URL ===
        if not product['categoria'] and url:
            url_lower = url.lower()
            if 'robot-tagliaerba' in url_lower or 'robot' in url_lower:
                product['categoria'] = 'Robot tagliaerba'
            elif 'trattorini' in url_lower or 'trattorino' in url_lower:
                product['categoria'] = 'Trattorini'
            elif 'tagliaerba' in url_lower and 'robot' not in url_lower and 'trattorini' not in url_lower:
                product['categoria'] = 'Tagliaerba'
            elif 'decespugliator' in url_lower or 'trimmer' in url_lower or 'tagliabordi' in url_lower:
                product['categoria'] = 'Decespugliatori'
            elif 'tagliasiepi' in url_lower or 'siepi' in url_lower:
                product['categoria'] = 'Tagliasiepi'
            elif 'motosega' in url_lower or 'sega' in url_lower:
                product['categoria'] = 'Motoseghe'
            elif 'soffiator' in url_lower or 'aspirator' in url_lower:
                product['categoria'] = 'Soffiatori'
            elif 'idropulit' in url_lower or 'pulitrice' in url_lower:
                product['categoria'] = 'Idropulitrici'
            elif 'cesoie' in url_lower or 'forbici' in url_lower:
                product['categoria'] = 'Cesoie'
        
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
        desc = soup.find('div', {'id': 'product-details'})
        if not desc:
            desc = soup.find('div', class_='product-details')
        
        if desc:
            paragraphs = desc.find_all('p', recursive=False)
            if paragraphs:
                product['descrizione'] = paragraphs[0].get_text().strip()
                product['descrizione_completa'] = '\n'.join(
                    [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
                )
            else:
                text = desc.get_text().strip()
                if text:
                    product['descrizione'] = text[:300]
                    product['descrizione_completa'] = text
        
        # === CARATTERISTICHE ===
        features_section = soup.find('div', {'id': 'product-features'})
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
        
        if not product['immagini']:
            main_img = soup.find('img', class_='gallery-placeholder__image')
            if main_img and main_img.get('src'):
                src = main_img['src']
                full_url = src if src.startswith('http') else f"https://www.stiga.com{src}"
                product['immagini'].append(full_url)
        
        # === KEYWORDS ===
        keywords = set()
        text = soup.get_text().lower()
        
        if product['nome']:
            keywords.update(product['nome'].lower().split())
        
        if product['categoria']:
            keywords.update(product['categoria'].lower().split())
        
        common_kw = [
            'robot', 'trattorino', 'tagliaerba', 'batteria', 'elettrico',
            'scoppio', 'gps', 'app', 'autonomo', 'mulching', 'raccolta',
            'decespugliatore', 'motosega', 'soffiatore', 'idropulitrice',
            'epower', 'benzina', 'litio', 'brushless', 'tagliasiepi', 'cesoie'
        ]
        
        for kw in common_kw:
            if kw in text:
                keywords.add(kw)
        
        product['keywords'] = sorted(list(keywords))[:15]
        
        time.sleep(2)  # Rate limiting
        return product
        
    except Exception as e:
        print(f"    ❌ Errore su {url}: {e}")
        return None

def main():
    print("="*70)
    print("🕷️  SCRAPING COMPLETO PRODOTTI STIGA (122 prodotti)")
    print("="*70)
    print()
    
    # Carica URL scoperti
    urls_file = Path(__file__).parent.parent / 'data' / 'all_product_urls.json'
    
    print(f"📂 Caricamento URL da: {urls_file}")
    with open(urls_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        product_urls = data['product_urls']
    
    print(f"✅ Trovati {len(product_urls)} prodotti da scrapare\n")
    
    # Scraping
    products = []
    errors = []
    
    for i, url in enumerate(tqdm(product_urls, desc="Scraping prodotti"), 1):
        # Genera ID dal URL
        product_id = url.split('/')[-1].replace('.html', '')
        
        product_data = extract_product_details(url, product_id)
        
        if product_data:
            products.append(product_data)
        else:
            errors.append(url)
    
    # Salva
    output_path = Path(__file__).parent.parent / 'data' / 'stiga_products_122.json'
    
    print("\n" + "="*70)
    print(f"💾 Salvataggio in: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print("✅ Salvato!\n")
    
    # Stats
    total_specs = sum(len(p.get('specifiche_tecniche', {})) for p in products)
    categories = {}
    for p in products:
        cat = p.get('categoria', 'Senza categoria')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("📊 STATISTICHE:")
    print(f"   Prodotti totali: {len(products)}")
    print(f"   Successi: {len(products)}")
    print(f"   Errori: {len(errors)}")
    print(f"   Specifiche tecniche totali: {total_specs}")
    
    print("\n📂 CATEGORIE TROVATE:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"   {cat}: {count}")
    
    if errors:
        print(f"\n⚠️  Errori su {len(errors)} URL")
    
    print("\n" + "="*70)
    print("🎉 COMPLETATO!")
    print("="*70)
    print("\nProssimi passi:")
    print("1. Verifica categorie: cat data/stiga_products_122.json | grep 'categoria'")
    print("2. Se ok: mv data/stiga_products_122.json data/stiga_products.json")
    print("3. Rigenera embeddings: python scripts/generate_embeddings.py\n")

if __name__ == '__main__':
    main()