#!/usr/bin/env python3
"""
Scraper completo catalogo STIGA: Prodotti + Accessori
Versione robusta con retry, timeout aumentato e salvataggio progressivo
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from bs4 import BeautifulSoup
import json
import time
from typing import Dict, List, Optional
from tqdm import tqdm

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
}

BASE_URL = "https://www.stiga.com"

# Configurazione robusta
TIMEOUT = 30  # Aumentato da 15s
DELAY_BETWEEN_REQUESTS = 4  # Aumentato da 2s
MAX_RETRIES = 3  # Tentativi per prodotto
SAVE_EVERY = 50  # Salva ogni N prodotti

# ========== PRODOTTI ==========
PRODUCT_CATEGORIES = {
    "Robot tagliaerba": ["/it/prodotti-finiti/taglio-del-prato/robot-tagliaerba.html"],
    "Tagliaerba": [
        "/it/prodotti-finiti/taglio-del-prato/tagliaerba.html",
        "/it/prodotti-finiti/taglio-del-prato/tagliaerba.html?p=2"
    ],
    "Trattorini tagliaerba frontali": ["/it/prodotti-finiti/taglio-del-prato/trattorini-a-taglio-frontale.html"],
    "Trattorini da giardino": ["/it/prodotti-finiti/taglio-del-prato/trattorini-da-giardino.html"],
    "Trattorini assiali": ["/it/prodotti-finiti/taglio-del-prato/trattorini-da-giardino-assiali.html"],
    "Tagliaerba elicoidali": ["/it/prodotti-finiti/taglio-del-prato/tagliaerba-elicoidali.html"],
    "Cesoie per siepi": ["/it/prodotti-finiti/sfalcio-di-prato-e-siepi/cesoie-per-siepi.html"],
    "Tagliasiepi": ["/it/prodotti-finiti/sfalcio-di-prato-e-siepi/tagliasiepi.html"],
    "Tagliabordi": ["/it/prodotti-finiti/sfalcio-di-prato-e-siepi/tagliabordi.html"],
    "Decespugliatori": ["/it/prodotti-finiti/sfalcio-di-prato-e-siepi/tagliabordi-e-decespugliatori.html"],
    "Attrezzi multifunzione": ["/it/prodotti-finiti/legname-e-potatura/attrezzi-multifunzione.html"],
    "Biotrituratori": ["/it/prodotti-finiti/legname-e-potatura/biotrituratori.html"],
    "Motoseghe": ["/it/prodotti-finiti/legname-e-potatura/motoseghe.html"],
    "Forbici da potatura": ["/it/prodotti-finiti/legname-e-potatura/forbici-da-potatura.html"],
    "Soffiatori e aspiratori": ["/it/prodotti-finiti/pulizia-di-aree-esterne/soffiatori-e-aspiratori.html"],
    "Aspiratori trituratori": ["/it/prodotti-finiti/pulizia-di-aree-esterne/aspiratori-trituratori.html"],
    "Idropulitrici ad alta pressione": ["/it/prodotti-finiti/pulizia-di-aree-esterne/idropulitrici-ad-alta-pressione.html"],
    "Spazzatrici": ["/it/prodotti-finiti/pulizia-di-aree-esterne/spazzatrici.html"],
    "Spazzaneve": ["/it/prodotti-finiti/pulizia-di-aree-esterne/spazzaneve.html"],
    "Arieggiatori e scarificatori": ["/it/prodotti-finiti/preparazione-del-terreno/arieggiatori-e-scarificatori.html"],
    "Motozappe": ["/it/prodotti-finiti/preparazione-del-terreno/motozappe.html"],
    "Falciatrici e coltivatori": ["/it/prodotti-finiti/preparazione-del-terreno/falciatrici-e-coltivatori.html"],
    "Attrezzi manuali per la coltivazione": ["/it/prodotti-finiti/preparazione-del-terreno/attrezzi-per-il-giardino.html"],
}

# ========== ACCESSORI ==========
ACCESSORY_CATEGORIES = {
    "Accessori per robot tagliaerba": ["/it/accessori/robot.html"],
    "Accessori per trattorini da giardino": [
        "/it/accessori/trattorini-da-giardino.html",
        "/it/accessori/trattorini-da-giardino.html?p=2"
    ],
    "Accessori per trattorini a taglio frontale": [
        "/it/accessori/trattorini-a-taglio-frontale.html",
        "/it/accessori/trattorini-a-taglio-frontale.html?p=2"
    ],
    "Accessori per tagliaerba elicoidali": ["/it/accessori/tagliaerba-elicoidali.html"],
    "Accessori per tagliabordi e decespugliatori": [
        "/it/accessori/decespugliatori.html",
        "/it/accessori/decespugliatori.html?p=2"
    ],
    "Accessori per attrezzi multifunzione": ["/it/accessori/attrezzi-multifunzione.html"],
    "Accessori per motoseghe": ["/it/accessori/motoseghe.html"],
    "Accessori per idropulitrici ad alta pressione": ["/it/accessori/idropulitrici-ad-alta-pressione.html"],
    "Accessori per spazzatrici": ["/it/accessori/spazzatrici.html"],
    "Accessori per spazzaneve": ["/it/accessori/spazzaneve.html"],
    "Accessori per motozappe": ["/it/accessori/motozappe.html"],
    "Kit batteria": ["/it/accessori/kit-batteria.html"],
    "Accessori Cross Categoria": ["/it/accessori/accessori-cross-categoria.html"]
}

def extract_product_urls_from_category(category_url: str) -> List[str]:
    """Estrae URL prodotti da pagina categoria"""
    try:
        full_url = BASE_URL + category_url if not category_url.startswith('http') else category_url
        response = requests.get(full_url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        product_urls = []
        product_links = soup.find_all('a', class_='product-item-link')
        
        for link in product_links:
            href = link.get('href')
            if href and '.html' in href and '/it/' in href:
                if not href.startswith('http'):
                    href = BASE_URL + href if href.startswith('/') else BASE_URL + '/' + href
                if href not in product_urls:
                    product_urls.append(href)
        
        time.sleep(1)
        return product_urls
        
    except Exception as e:
        print(f"    ⚠️  Errore: {e}")
        return []

def extract_specs_from_page(soup: BeautifulSoup) -> tuple:
    """Estrae specifiche tecniche"""
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

def extract_product_details_with_retry(url: str, product_id: str, categoria: str) -> Optional[Dict]:
    """Estrae dettagli prodotto con retry automatico"""
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
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
            
            # NOME
            h1 = soup.find('h1', class_='page-title')
            if h1:
                product['nome'] = h1.get_text().strip()
            
            # PREZZI
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
            
            # DESCRIZIONE
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
            
            # CARATTERISTICHE
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
            
            # SPECIFICHE
            specs_by_section, flat_specs = extract_specs_from_page(soup)
            product['specifiche_per_sezione'] = specs_by_section
            product['specifiche_tecniche'] = flat_specs
            
            # IMMAGINI
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
            
            # KEYWORDS
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
            
            time.sleep(DELAY_BETWEEN_REQUESTS)
            return product
            
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                print(f"    ⏱️  Timeout tentativo {attempt + 1}/{MAX_RETRIES}, riprovo...")
                time.sleep(5)  # Aspetta 5s prima di riprovare
            else:
                print(f"    ❌ Timeout definitivo dopo {MAX_RETRIES} tentativi")
                return None
                
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"    ⚠️  Errore tentativo {attempt + 1}/{MAX_RETRIES}: {str(e)[:50]}...")
                time.sleep(5)
            else:
                print(f"    ❌ Errore definitivo: {str(e)[:100]}")
                return None
    
    return None

def save_progress(products: List[Dict], output_path: Path):
    """Salva progresso corrente"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def main():
    print("="*70)
    print("🕷️  SCRAPING COMPLETO CATALOGO STIGA")
    print("    Prodotti (23 categorie) + Accessori (13 categorie)")
    print("    Configurazione robusta: timeout 30s, retry 3x, save ogni 50")
    print("="*70)
    print()
    
    # Unisci categorie
    all_categories = {}
    for cat, urls in PRODUCT_CATEGORIES.items():
        all_categories[cat] = urls if isinstance(urls, list) else [urls]
    for cat, urls in ACCESSORY_CATEGORIES.items():
        all_categories[cat] = urls if isinstance(urls, list) else [urls]
    
    print(f"📂 Totale categorie: {len(all_categories)}\n")
    
    # STEP 1: Raccolta URL
    print("="*70)
    print("📦 STEP 1: Raccolta URL prodotti")
    print("="*70)
    print()
    
    product_mapping = {}
    
    for categoria, cat_urls in all_categories.items():
        print(f"🔍 {categoria}")
        for cat_url in cat_urls:
            product_urls = extract_product_urls_from_category(cat_url)
            print(f"   └─ {len(product_urls)} prodotti")
            for url in product_urls:
                product_mapping[url] = categoria
    
    print(f"\n✅ Totale prodotti: {len(product_mapping)}")
    
    # STEP 2: Scraping con salvataggio progressivo
    print("\n" + "="*70)
    print("🔧 STEP 2: Scraping dettagli (con salvataggio progressivo)")
    print("="*70)
    print()
    
    output_path = Path(__file__).parent.parent / 'data' / 'stiga_products.json'
    products = []
    errors = []
    
    for idx, (url, categoria) in enumerate(tqdm(product_mapping.items(), desc="Prodotti"), 1):
        product_id = url.split('/')[-1].replace('.html', '')
        product_data = extract_product_details_with_retry(url, product_id, categoria)
        
        if product_data:
            products.append(product_data)
        else:
            errors.append(url)
        
        # Salvataggio progressivo
        if idx % SAVE_EVERY == 0:
            save_progress(products, output_path)
            print(f"\n    💾 Salvataggio progressivo: {len(products)} prodotti\n")
    
    # Salvataggio finale
    save_progress(products, output_path)
    
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
    print(f"Tasso successo: {len(products)/len(product_mapping)*100:.1f}%")
    print(f"Specifiche tecniche: {total_specs}")
    
    print("\n📂 PRODOTTI PER CATEGORIA:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"   {cat}: {count}")
    
    if errors:
        print(f"\n⚠️  Prodotti con errore ({len(errors)}):")
        for err in errors[:10]:
            print(f"   - {err}")
        if len(errors) > 10:
            print(f"   ... e altri {len(errors) - 10}")
    
    print("\n" + "="*70)
    print("🎉 COMPLETATO!")
    print("="*70)
    print(f"\n💾 File salvato: {output_path}")
    print("\nProssimo passo:")
    print("python scripts/generate_embeddings.py\n")

if __name__ == '__main__':
    main()