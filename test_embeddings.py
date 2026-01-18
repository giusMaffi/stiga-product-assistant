import json

with open('data/stiga_products.json', 'r') as f:
    products = json.load(f)

# Trova un tagliasiepi
tagliasiepi = [p for p in products if 'tagliasiepi' in p.get('categoria', '').lower()][0]

# Trova il troncarami che ha score alto
troncarami = [p for p in products if 'troncarami' in p.get('nome', '').lower()][0]

print('=== TAGLIASIEPI (score 0.427) ===')
print(f'Nome: {tagliasiepi["nome"]}')
print(f'Categoria: {tagliasiepi.get("categoria")}')
print(f'Descrizione: {tagliasiepi.get("descrizione", "")[:200]}...')
print()

print('=== TRONCARAMI (score 0.624 !!!) ===')
print(f'Nome: {troncarami["nome"]}')
print(f'Categoria: {troncarami.get("categoria")}')
print(f'Descrizione: {troncarami.get("descrizione", "")[:200]}...')
