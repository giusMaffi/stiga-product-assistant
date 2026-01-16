#!/usr/bin/env python3
"""
Scraper completo catalogo STIGA: Prodotti + Accessori
Usa URL reali delle pagine categoria per categorie accurate al 100%
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from bs4 import BeautifulSoup
import json
import time
from typing import Dict, List
from tqdm import tqdm

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
}

BASE_URL = "https://www.stiga.com"

# ========== PRODOTTI ==========
PRODUCT_CATEGORIES = {
    # Taglio del prato
    "Robot tagliaerba": [
        "/it/prodotti-finiti/taglio-del-prato/robot-tagliaerba.html"
    ],
    "Tagliaerba": [
        "/it/prodotti-finiti/taglio-del-prato/tagliaerba.html",
        "/it/prodotti-finiti/taglio-del-prato/tagliaerba.html?p=2"
    ],
    "Trattorini tagliaerba frontali": [
        "/it/prodotti-finiti/taglio-del-prato/trattorini-a-taglio-frontale.html"
    ],
    "Trattorini da giardino": [
        "/it/prodotti-finiti/taglio-del-prato/trattorini-da-giardino.html"
    ],
    "Trattorini assiali": [
        "/it/prodotti-finiti/taglio-del-prato/trattorini-da-giardino-assiali.html"
    ],
    "Tagliaerba elicoidali": [
        "/it/prodotti-finiti/taglio-del-prato/tagliaerba-elicoidali.html"
    ],
    
    # Sfalcio di prato e siepi
    "Cesoie per siepi": [
        "/it/prodotti-finiti/sfalcio-di-prato-e-siepi/cesoie-per-siepi.html"
    ],
    "Tagliasiepi": [
        "/it/prodotti-finiti/sfalcio-di-prato-e-siepi/tagliasiepi.html"
    ],
    "Tagliabordi": [
        "/it/prodotti-finiti/sfalcio-di-prato-e-siepi/tagliabordi.html"
    ],
    "Decespugliatori": [
        "/it/prodotti-finiti/sfalcio-di-prato-e-siepi/tagliabordi-e-decespugliatori.html"
    ],
    
    # Legname e potatura
    "Attrezzi multifunzione": [
        "/it/prodotti-finiti/legname-e-potatura/attrezzi-multifunzione.html"
    ],
    "Biotrituratori": [
        "/it/prodotti-finiti/legname-e-potatura/biotrituratori.html"
    ],
    "Motoseghe": [
        "/it/prodotti-finiti/legname-e-potatura/motoseghe.html"
    ],
    "Forbici da potatura": [
        "/it/prodotti-finiti/legname-e-potatura/forbici-da-potatura.html"
    ],
    
    # Pulizia di aree esterne
    "Soffiatori e aspiratori": [
        "/it/prodotti-finiti/pulizia-di-aree-esterne/soffiatori-e-aspiratori.html"
    ],
    "Aspiratori trituratori": [
        "/it/prodotti-finiti/pulizia-di-aree-esterne/aspiratori-trituratori.html"
    ],
    "Idropulitrici ad alta pressione": [
        "/it/prodotti-finiti/pulizia-di-aree-esterne/idropulitrici-ad-alta-pressione.html"
    ],
    "Spazzatrici": [
        "/it/prodotti-finiti/pulizia-di-aree-esterne/spazzatrici.html"
    ],
    "Spazzaneve": [
        "/it/prodotti-finiti/pulizia-di-aree-esterne/spazzaneve.html"
    ],
    
    # Preparazione del terreno
    "Arieggiatori e scarificatori": [
        "/it/prodotti-finiti/preparazione-del-terreno/arieggiatori-e-scarificatori.html"
    ],
    "Motozappe": [
        "/it/prodotti-finiti/preparazione-del-terreno/motozappe.html"
    ],
    "Falciatrici e coltivatori": [
        "/it/prodotti-finiti/preparazione-del-terreno/falciatrici-e-coltivatori.html"
    ],
    "Attrezzi manuali per la coltivazione": [
        "/it/prodotti-finiti/preparazione-del-terreno/attrezzi-per-il-giardino.html"
    ],
}

# ========== ACCESSORI ==========
ACCESSORY_CATEGORIES = {
    # Taglio dell'erba
    "Accessori per robot tagliaerba": [
        "/it/accessori/robot.html"
    ],
    "Accessori per trattorini da giardino": [
        "/it/accessori/trattorini-da-giardino.html",
        "/it/accessori/trattorini-da-giardino.html?p=2"
    ],
    "Accessori per trattorini a taglio frontale": [
        "/it/accessori/trattorini-a-taglio-frontale.html",
        "/it/accessori/trattorini-a-taglio-frontale.html?p=2"
    ],
    "Accessori per tagliaerba elicoidali": [
        "/it/accessori/tagliaerba-elicoidali.html"
    ],
    
    # Rifinitura di prato e siepi
    "Accessori per tagliabordi e decespugliatori": [
        "/it/accessori/decespugliatori.html",
        "/it/accessori/decespugliatori.html?p=2"
    ],
    
    # Potatura di alberi e arbusti
    "Accessori per attrezzi multifunzione": [
        "/it/accessori/attrezzi-multifunzione.html"
    ],
    "Accessori per motoseghe": [
        "/it/accessori/motoseghe.html"
    ],
    
    # Pulizie di aree esterne
    "Accessori per idropulitrici ad alta pressione": [
        "/it/accessori/idropulitrici-ad-alta-pressione.html"
    ],
    "Accessori per spazzatrici": [
        "/it/accessori/spazzatrici.html"
    ],
    "Accessori per spazzaneve": [
        "/it/accessori/spazzaneve.html"
    ],
    
    # Cura del suolo
    "Accessori per motozappe": [
        "/it/accessori/motozappe.html"
    ],
    
    # Multi-categoria
    "Kit batteria": [
        "/it/accessori/kit-batteria.html"
    ],
    "Accessori Cross Categoria": [
        "/it/accessori/accessori-cross-categoria.html"
    ]
}

def extract_product_urls_from_category(category_url: str) -> List[str]:
    """Estrae tutti gli URL prodotti da una pagina categoria"""
    try:
        full_url = BASE_URL + category_url if not category_url.startswith('http') else category_url
        response = requests.get(full_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        product_urls = []
        
        # Trova tutti i link prodotto nella griglia
        product_links = soup.find_all('a', class_='product-item-link')
        
        for link in product_links:
            href = link.get('href')
            if href and '.html' in href and '/it/' in href:
                # Assicurati che sia URL completo
                if not href.startswith('http'):
                    href = BASE_URL + href if href.startswith('/') else BASE_URL + '/' + href
                
                # Evita duplicati
                if href not in product_urls:
                    product_urls.append(href)
        
        time.sleep(1)  # Rate limiting
        return product_urls
        
    except Exception as e:
        print(f"    ⚠️  Errore: {e}")
        return []

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

def extract_product_details(url: str, product_id: str, categoria: str) -> Dict:
    """Estrae tutti i dettagli da una pagina prodotto"""
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        product = {
            'id': product_id,
            'url': url,
            'nome': '',
            'categoria': categoria,
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
                    full_url = src if src.startswith('http') else f"{BASE_URL}{src}"
                    if full_url not in product['immagini']:
                        product['immagini'].append(full_url)
        
        if not product['immagini']:
            main_img = soup.find('img', class_='gallery-placeholder__image')
            if main_img and main_img.get('src'):
                src = main_img['src']
                full_url = src if src.startswith('http') else f"{BASE_URL}{src}"
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
            'epower', 'benzina', 'litio', 'brushless', 'tagliasiepi', 'cesoie',
            'accessorio', 'ricambio', 'kit'
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
    print("🕷️  SCRAPING COMPLETO CATALOGO STIGA")
    print("    Prodotti (23 categorie) + Accessori (13 categorie)")
    print("="*70)
    print()
    
    # Unisci tutte le categorie
    all_categories = {}
    
    # Prodotti
    for cat, urls in PRODUCT_CATEGORIES.items():
        all_categories[cat] = urls if isinstance(urls, list) else [urls]
    
    # Accessori
    for cat, urls in ACCESSORY_CATEGORIES.items():
        all_categories[cat] = urls if isinstance(urls, list) else [urls]
    
    print(f"📂 Totale categorie da scrapare: {len(all_categories)}\n")
    
    # Step 1: Raccogliere tutti gli URL prodotti con categoria
    print("="*70)
    print("📦 STEP 1: Raccolta URL prodotti dalle categorie")
    print("="*70)
    print()
    
    product_mapping = {}  # {url: categoria}
    
    for categoria, cat_urls in all_categories.items():
        print(f"🔍 {categoria}")
        
        for cat_url in cat_urls:
            product_urls = extract_product_urls_from_category(cat_url)
            print(f"   └─ {len(product_urls)} prodotti")
            
            for url in product_urls:
                product_mapping[url] = categoria
    
    print(f"\n✅ Totale prodotti unici trovati: {len(product_mapping)}")
    
    # Step 2: Scrapare dettagli di ogni prodotto
    print("\n" + "="*70)
    print("🔧 STEP 2: Scraping dettagli prodotti")
    print("="*70)
    print()
    
    products = []
    errors = []
    
    for url, categoria in tqdm(product_mapping.items(), desc="Prodotti"):
        product_id = url.split('/')[-1].replace('.html', '')
        
        product_data = extract_product_details(url, product_id, categoria)
        
        if product_data:
            products.append(product_data)
        else:
            errors.append(url)
    
    # Salva
    output_path = Path(__file__).parent.parent / 'data' / 'stiga_products.json'
    
    print("\n" + "="*70)
    print(f"💾 Salvataggio in: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print("✅ Salvato!")
    
    # Stats
    total_specs = sum(len(p.get('specifiche_tecniche', {})) for p in products)
    categories = {}
    for p in products:
        cat = p.get('categoria', 'Senza categoria')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n" + "="*70)
    print("📊 STATISTICHE FINALI")
    print("="*70)
    print(f"Prodotti totali: {len(products)}")
    print(f"Successi: {len(products)}")
    print(f"Errori: {len(errors)}")
    print(f"Specifiche tecniche totali: {total_specs}")
    
    print("\n📂 PRODOTTI PER CATEGORIA:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"   {cat}: {count}")
    
    if errors:
        print(f"\n⚠️  Errori su {len(errors)} URL:")
        for err in errors[:10]:
            print(f"   - {err}")
        if len(errors) > 10:
            print(f"   ... e altri {len(errors) - 10}")
    
    print("\n" + "="*70)
    print("🎉 COMPLETATO!")
    print("="*70)
    print("\nProssimo passo:")
    print("python scripts/generate_embeddings.py\n")

if __name__ == '__main__':
    main()