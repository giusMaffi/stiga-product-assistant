#!/usr/bin/env python3
"""
Scraper completo magazine STIGA
SICURO: salva in file NUOVO, non modifica nulla
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import json
from pathlib import Path
from tqdm import tqdm

DELAY = 3  # Secondi tra richieste

# Lista articoli da scrappare (trovati prima)
ARTICLE_URLS = [
    "https://www.stiga.com/it/magazine/cura-intelligente-del-giardino/robot-tagliaerba-sicurezza-protezione",
    "https://www.stiga.com/it/magazine/cura-intelligente-del-giardino/aprile-quali-sono-le-novita-del-nostro-robot-tagliaerba-autonomo",
    "https://www.stiga.com/it/magazine/cura-intelligente-giardino/robot-tagliaerba-fa-bene-al-tuo-prato-fa-bene-a-te",
    "https://www.stiga.com/it/magazine/esperto-del-giardino/aprile-in-giardino",
    "https://www.stiga.com/it/magazine/esperto-del-giardino/come-aiutare-gli-animaletti-a-proteggersi-in-inverno",
    "https://www.stiga.com/it/magazine/esperto-del-giardino/consigli-essenziali-per-una-potatura-efficace",
    "https://www.stiga.com/it/magazine/esperto-del-giardino/cosa-fiorisce-in-ottobre",
    "https://www.stiga.com/it/magazine/esperto-del-giardino/i-migliori-semi-da-piantare-a-novembre",
    "https://www.stiga.com/it/magazine/esperto-del-giardino/i-migliori-semi-da-piantare-a-settembre",
    "https://www.stiga.com/it/magazine/esperto-del-giardino/novembre-in-giardino",
    "https://www.stiga.com/it/magazine/esperto-del-giardino/perche-scegliere-un-trattorino-elettrico",
    "https://www.stiga.com/it/magazine/esperto-del-giardino/settembre-in-giardino",
    "https://www.stiga.com/it/magazine/natura-in-movimento/il-mondo-segreto-della-tua-siepe",
    "https://www.stiga.com/it/magazine/real-garden-stories/real-garden-care-stories-episodio-2",
]

def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

def extract_article(driver, url):
    """Estrae dati da un articolo"""
    article = {
        'url': url,
        'titolo': '',
        'intro': '',
        'categoria': ''
    }
    
    try:
        driver.get(url)
        time.sleep(DELAY)
        
        # Categoria dall'URL
        parts = url.split('/')
        if len(parts) >= 6:
            article['categoria'] = parts[-2].replace('-', ' ').title()
        
        # Titolo
        try:
            title = driver.find_element(By.TAG_NAME, 'h1')
            article['titolo'] = title.text.strip()
        except:
            pass
        
        # Intro
        selectors = ['.article-content p', '.post-content p', '.cms-content p', 'article p', 'main p']
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements[:10]:
                    text = el.text.strip()
                    if (len(text) > 80 and 
                        'cookie' not in text.lower() and 
                        'javascript' not in text.lower() and
                        'accett' not in text.lower()):
                        article['intro'] = text[:500]
                        break
                if article['intro']:
                    break
            except:
                continue
                
    except Exception as e:
        print(f"    ⚠️ Errore: {e}")
    
    return article

def main():
    print("=" * 70)
    print("📰 SCRAPING MAGAZINE STIGA")
    print("=" * 70)
    print()
    
    driver = setup_driver()
    articles = []
    
    try:
        for url in tqdm(ARTICLE_URLS, desc="Articoli"):
            article = extract_article(driver, url)
            if article['titolo']:
                articles.append(article)
                print(f"    ✅ {article['titolo'][:50]}...")
            else:
                print(f"    ⚠️ Nessun titolo: {url}")
    finally:
        driver.quit()
    
    # Salva
    output_path = Path(__file__).parent.parent / 'data' / 'magazine_articles.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Salvati {len(articles)} articoli in {output_path}")
    print("\n📊 ARTICOLI PER CATEGORIA:")
    cats = {}
    for a in articles:
        cat = a.get('categoria', 'Altro')
        cats[cat] = cats.get(cat, 0) + 1
    for cat, count in sorted(cats.items()):
        print(f"   {cat}: {count}")

if __name__ == '__main__':
    main()
