#!/usr/bin/env python3
"""
Test scraper magazine STIGA
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
}

# Test su un articolo
url = "https://www.stiga.com/it/magazine/cura-intelligente-del-giardino/robot-tagliaerba-sicurezza-protezione"

print(f"🔍 Analizzando: {url}\n")

response = requests.get(url, headers=HEADERS, timeout=30)
soup = BeautifulSoup(response.content, 'html.parser')

# Titolo
title = soup.find('h1')
print(f"📰 Titolo: {title.get_text().strip() if title else 'N/A'}")

# Meta description
meta_desc = soup.find('meta', {'name': 'description'})
if meta_desc:
    print(f"📝 Meta: {meta_desc.get('content', '')[:200]}...")

# Primo paragrafo come intro
article = soup.find('div', class_='post-content') or soup.find('article') or soup.find('div', class_='content')
if article:
    first_p = article.find('p')
    if first_p:
        print(f"📝 Intro: {first_p.get_text().strip()[:200]}...")

# Immagine
og_image = soup.find('meta', {'property': 'og:image'})
if og_image:
    print(f"🖼️ Immagine: {og_image.get('content', 'N/A')}")

# Categoria (dall'URL)
parts = url.split('/')
if len(parts) >= 6:
    categoria = parts[-2].replace('-', ' ').title()
    print(f"📂 Categoria: {categoria}")
