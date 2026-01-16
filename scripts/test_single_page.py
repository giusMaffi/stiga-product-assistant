#!/usr/bin/env python3
"""Test scraping di una singola pagina per debug"""

import requests
from bs4 import BeautifulSoup

url = "https://www.stiga.com/it/2r7101428-st1-a-4.html"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
}

print(f"Fetching: {url}\n")

response = requests.get(url, headers=HEADERS, timeout=15)
soup = BeautifulSoup(response.content, 'html.parser')

# Test 1: Cerca accordion
print("="*70)
print("TEST 1: Cerca container accordion")
print("="*70)

accordion = soup.find('div', {'id': 'product-specs__accordion'})
print(f"Accordion trovato: {accordion is not None}")

if not accordion:
    # Prova altre varianti
    print("\nProvando selettori alternativi...")
    
    alt1 = soup.find('div', id='product-specs')
    print(f"  #product-specs: {alt1 is not None}")
    
    alt2 = soup.find('div', class_='product-specs')
    print(f"  .product-specs: {alt2 is not None}")
    
    alt3 = soup.find_all('div', class_=lambda x: x and 'spec' in x.lower())
    print(f"  Divs con 'spec' nel nome: {len(alt3)}")

# Test 2: Cerca sezioni collapsible
print("\n" + "="*70)
print("TEST 2: Cerca sezioni collapsible")
print("="*70)

collapsibles = soup.find_all('div', {'data-role': 'collapsible'})
print(f"Sezioni collapsible trovate: {len(collapsibles)}")

if collapsibles:
    print("\nPrima sezione:")
    print(collapsibles[0].prettify()[:500])

# Test 3: Cerca specifiche in qualsiasi modo
print("\n" + "="*70)
print("TEST 3: Cerca testo 'Specifiche tecniche'")
print("="*70)

specs_text = soup.find_all(string=lambda text: text and 'Specifiche tecniche' in text)
print(f"Trovate {len(specs_text)} occorrenze")

if specs_text:
    for i, text in enumerate(specs_text[:3], 1):
        parent = text.parent
        print(f"\n  Occorrenza {i}:")
        print(f"  Tag parent: {parent.name}")
        print(f"  Classes: {parent.get('class')}")
        print(f"  ID: {parent.get('id')}")

# Test 4: Trova tutte le label/data pairs
print("\n" + "="*70)
print("TEST 4: Cerca coppie label/data")
print("="*70)

labels = soup.find_all('div', class_='label')
print(f"Trovati {len(labels)} elementi con class='label'")

if labels:
    print("\nPrimi 5 label:")
    for label in labels[:5]:
        sibling = label.find_next_sibling('div', class_='data')
        if sibling:
            print(f"  {label.get_text().strip()}: {sibling.get_text().strip()}")

print("\n" + "="*70)
print("FINE TEST")
print("="*70)