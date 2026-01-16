#!/usr/bin/env python3
"""
Scopre tutti i prodotti STIGA scansionando le pagine categoria
"""

import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
}

BASE_URL = "https://www.stiga.com"

# Categorie principali da esplorare
CATEGORY_URLS = [
    "/it/prodotti-finiti/taglio-del-prato.html",
    "/it/prodotti-finiti/taglio-del-prato/robot-tagliaerba.html",
    "/it/prodotti-finiti/taglio-del-prato/trattorini-tagliaerba.html",
    "/it/prodotti-finiti/taglio-del-prato/tagliaerba.html",
    "/it/prodotti-finiti/taglio-e-rifinitura.html",
    "/it/prodotti-finiti/pulizia-del-giardino.html",
    "/it/prodotti-finiti/cura-e-manutenzione.html",
]

def extract_product_urls_from_page(url: str) -> list:
    """Estrae URL prodotti da una pagina categoria"""
    print(f"  📄 Scansiono: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        product_urls = set()
        
        # Cerca link prodotto (pattern comune: /it/[codice]-[nome].html)
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Pattern prodotto STIGA: contiene codici tipo 2r7101428-st1
            if '.html' in href and any(c.isdigit() for c in href):
                # Evita URL categoria
                if 'prodotti-finiti' not in href and 'category' not in href:
                    full_url = urljoin(BASE_URL, href)
                    if BASE_URL in full_url:
                        product_urls.add(full_url)
        
        print(f"    ✅ Trovati {len(product_urls)} prodotti")
        time.sleep(1)  # Rate limiting
        return list(product_urls)
        
    except Exception as e:
        print(f"    ❌ Errore: {e}")
        return []

def find_subcategories(url: str) -> list:
    """Trova sottocategorie in una pagina categoria"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        subcats = []
        
        # Cerca link a sottocategorie
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'prodotti-finiti' in href and '.html' in href:
                full_url = urljoin(BASE_URL, href)
                if full_url not in CATEGORY_URLS and full_url not in subcats:
                    subcats.append(full_url)
        
        return subcats[:10]  # Max 10 sottocategorie per categoria
        
    except Exception as e:
        return []

def main():
    print("="*70)
    print("🔍 SCOPERTA PRODOTTI STIGA")
    print("="*70)
    print()
    
    all_product_urls = set()
    all_categories = set(CATEGORY_URLS)
    
    # Esplora categorie principali
    for cat_url in CATEGORY_URLS:
        full_url = urljoin(BASE_URL, cat_url)
        print(f"\n📂 Categoria: {full_url}")
        
        # Trova prodotti in questa categoria
        products = extract_product_urls_from_page(full_url)
        all_product_urls.update(products)
        
        # Cerca sottocategorie
        print("  🔎 Cerco sottocategorie...")
        subcats = find_subcategories(full_url)
        
        for subcat in subcats:
            if subcat not in all_categories:
                print(f"\n  📂 Sottocategoria: {subcat}")
                all_categories.add(subcat)
                
                sub_products = extract_product_urls_from_page(subcat)
                all_product_urls.update(sub_products)
        
        time.sleep(2)
    
    # Risultati
    product_list = sorted(list(all_product_urls))
    
    print("\n" + "="*70)
    print("📊 RISULTATI")
    print("="*70)
    print(f"Categorie esplorate: {len(all_categories)}")
    print(f"Prodotti unici trovati: {len(product_list)}")
    print()
    
    # Salva lista prodotti
    output = {
        'total_products': len(product_list),
        'categories_explored': len(all_categories),
        'product_urls': product_list
    }
    
    output_path = 'data/all_product_urls.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Lista salvata in: {output_path}")
    print()
    
    # Mostra primi 10
    print("📋 Primi 10 prodotti trovati:")
    for i, url in enumerate(product_list[:10], 1):
        print(f"  {i}. {url}")
    
    if len(product_list) > 10:
        print(f"  ... e altri {len(product_list) - 10}")
    
    print("\n" + "="*70)
    print("🎉 SCOPERTA COMPLETATA!")
    print("="*70)
    print("\nProssimo step:")
    print("  python scripts/scrape_all_discovered.py")
    print()

if __name__ == '__main__':
    main()