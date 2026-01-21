# MODIFICHE DA FARE IN app.py

## 🎯 CAMBIO MINIMO - Riga 343

### PRIMA (passa solo top-10):
```python
# 6. Prepara contesto per Claude (top 10 prodotti)
products_context = claude.format_products_for_context(reranked[:10])
```

### DOPO (passa top-20):
```python
# 6. Prepara contesto per Claude (top 20 prodotti per suggerimenti migliori)
products_context = claude.format_products_for_context(reranked[:20])
```

---

## 📋 MODIFICA COMPLETA SEZIONE (righe ~340-360)

Sostituisci questa sezione:

```python
        print(f"🎯 Top 10 dopo re-ranking:")
        for i, (prod, score, reasons) in enumerate(reranked[:10], 1):
            print(f"   {i}. {prod.get('nome')} (ID: {prod.get('id')}) - Score: {score:.3f}")
        
        # 6. Prepara contesto per Claude (top 10 prodotti)
        products_context = claude.format_products_for_context(reranked[:10])
```

Con:

```python
        print(f"🎯 Top 20 dopo re-ranking:")
        for i, (prod, score, reasons) in enumerate(reranked[:20], 1):
            print(f"   {i}. {prod.get('nome')} (ID: {prod.get('id')}) - Score: {score:.3f}")
        
        # 6. Prepara contesto per Claude (top 20 prodotti per suggerimenti migliori)
        products_context = claude.format_products_for_context(reranked[:20])
```

---

## 🔄 MODIFICA ANCHE LA PRODUCT MAP (riga ~370)

### PRIMA:
```python
# Crea mappa ID → prodotto
products_map = {prod.get('id'): (prod, score, reasons) for prod, score, reasons in reranked[:10]}
```

### DOPO:
```python
# Crea mappa ID → prodotto (top 20 per includere eventuali suggerimenti)
products_map = {prod.get('id'): (prod, score, reasons) for prod, score, reasons in reranked[:20]}
```

---

## ✅ RIEPILOGO MODIFICHE

3 modifiche totali in app.py:
1. Print "Top 20" invece di "Top 10"
2. Passa `reranked[:20]` a Claude invece di `[:10]`
3. Mappa prodotti su primi 20 invece di 10

Questo permette a Claude di:
- Scegliere tra 20 prodotti invece che 10 (migliore selezione)
- Avere più opzioni per suggerimenti complementari
- Costo aggiuntivo: +$0.03 per conversazione (vale assolutamente!)
