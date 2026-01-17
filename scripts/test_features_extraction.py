#!/usr/bin/env python3
"""
Test estrazione caratteristiche - SOLO TEST, non modifica nulla
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
}

def extract_features(url: str) -> dict:
    """Estrae caratteristiche dalla pagina prodotto"""
    print(f"🔍 Analizzando: {url}\n")
    
    response = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    result = {
        'caratteristiche': [],
        'tecnologie': []
    }
    
    # === CARATTERISTICHE (product-features__box) ===
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
    
    # === TECNOLOGIE (product-technology__slide) ===
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
    
    return result

# Test su A 6v
url = "https://www.stiga.com/it/2r7114128-st1-a-6v.html"
features = extract_features(url)

print("=" * 60)
print("📦 CARATTERISTICHE TROVATE:", len(features['caratteristiche']))
print("=" * 60)
for i, f in enumerate(features['caratteristiche'], 1):
    print(f"\n{i}. {f['titolo']}")
    print(f"   {f['descrizione'][:100]}...")

print("\n" + "=" * 60)
print("🔧 TECNOLOGIE TROVATE:", len(features['tecnologie']))
print("=" * 60)
for i, t in enumerate(features['tecnologie'], 1):
    print(f"\n{i}. {t['titolo']}")
    print(f"   {t['descrizione'][:100]}...")
