#!/usr/bin/env python3
"""
Test scraper magazine con Selenium
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Setup Chrome headless
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)

url = "https://www.stiga.com/it/magazine/cura-intelligente-del-giardino/robot-tagliaerba-sicurezza-protezione"
print(f"🔍 Analizzando: {url}\n")

try:
    driver.get(url)
    time.sleep(4)  # Aspetta che JS carichi
    
    # Titolo
    try:
        title = driver.find_element(By.TAG_NAME, 'h1')
        print(f"📰 Titolo: {title.text}")
    except:
        print("📰 Titolo: N/A")
    
    # Prova diversi selettori per il contenuto
    selectors = [
        '.post-content p',
        '.article-content p', 
        '.cms-content p',
        '.page-content p',
        'article p',
        '.content-wrapper p',
        'main p'
    ]
    
    intro_found = False
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for el in elements[:10]:
                text = el.text.strip()
                # Filtra cookie banner e testi corti
                if (len(text) > 80 and 
                    'cookie' not in text.lower() and 
                    'javascript' not in text.lower() and
                    'accett' not in text.lower()):
                    print(f"📝 Intro ({selector}): {text[:300]}...")
                    intro_found = True
                    break
            if intro_found:
                break
        except:
            continue
    
    if not intro_found:
        # Fallback: stampa tutto il testo della pagina per debug
        print("\n🔍 DEBUG - Primi paragrafi trovati:")
        all_p = driver.find_elements(By.TAG_NAME, 'p')
        for i, p in enumerate(all_p[:15]):
            text = p.text.strip()
            if len(text) > 20:
                print(f"   {i}: {text[:100]}...")
    
finally:
    driver.quit()
