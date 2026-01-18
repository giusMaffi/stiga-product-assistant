import json

with open('data/stiga_products.json', 'r') as f:
    products = json.load(f)

tagliasiepi = [p for p in products if 'tagliasiepi' in p.get('categoria', '').lower()][0]
troncarami = [p for p in products if 'troncarami' in p.get('nome', '').lower()][0]

print("=== PAROLE IN COMUNE ===")
print()

# Testo completo tagliasiepi
ts_text = f"{tagliasiepi.get('nome', '')} {tagliasiepi.get('categoria', '')} {tagliasiepi.get('descrizione', '')} {tagliasiepi.get('descrizione_completa', '')}"
ts_words = set(ts_text.lower().split())

# Testo completo troncarami  
tr_text = f"{troncarami.get('nome', '')} {troncarami.get('categoria', '')} {troncarami.get('descrizione', '')} {troncarami.get('descrizione_completa', '')}"
tr_words = set(tr_text.lower().split())

# Query
query_words = set("tagliasiepi".lower().split())

print(f"Query 'tagliasiepi' appare in tagliasiepi text: {'tagliasiepi' in ts_text.lower()}")
print(f"Query 'tagliasiepi' appare in troncarami text: {'tagliasiepi' in tr_text.lower()}")
print()

# Parole in comune
common = ts_words.intersection(tr_words)
print(f"Parole in comune: {len(common)}")
print("Prime 20:", list(common)[:20])
