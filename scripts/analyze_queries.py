#!/usr/bin/env python3
"""
Analisi query utenti - STIGA Product Assistant
"""
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Path al file di log
LOG_FILE = Path(__file__).parent.parent / 'logs' / 'user_queries.log'


def parse_log_line(line):
    """Parse una riga di log"""
    try:
        parts = line.split(' - ', 1)
        if len(parts) >= 2:
            timestamp_str = parts[0]
            data = json.loads(parts[1])
            data['timestamp'] = datetime.fromisoformat(timestamp_str)
            return data
    except:
        return None


def analyze_logs(days=None):
    """
    Analizza i log delle query utenti
    
    Args:
        days: Analizza solo ultimi N giorni (None = tutti)
    """
    if not LOG_FILE.exists():
        print(f"❌ File log non trovato: {LOG_FILE}")
        print("   Nessuna query ancora registrata.")
        return
    
    # Leggi tutti i log
    queries = []
    results = []
    sessions = defaultdict(list)
    
    cutoff_date = None
    if days:
        cutoff_date = datetime.now() - timedelta(days=days)
    
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            data = parse_log_line(line)
            if not data:
                continue
            
            # Filtra per data se richiesto
            if cutoff_date and data['timestamp'] < cutoff_date:
                continue
            
            if data['type'] == 'query':
                queries.append(data)
                sessions[data['session']].append(data)
            elif data['type'] == 'results':
                results.append(data)
    
    # Stampa report
    print("="*80)
    print("📊 ANALISI QUERY UTENTI - STIGA PRODUCT ASSISTANT")
    print("="*80)
    print()
    
    if days:
        print(f"📅 Periodo analizzato: Ultimi {days} giorni")
    else:
        print(f"📅 Periodo analizzato: Tutti i log disponibili")
    print()
    
    # Statistiche generali
    print("="*80)
    print("📈 STATISTICHE GENERALI")
    print("="*80)
    print(f"Totale query: {len(queries)}")
    print(f"Totale sessioni: {len(sessions)}")
    print(f"Media query per sessione: {len(queries) / len(sessions) if sessions else 0:.1f}")
    print()
    
    # Query più frequenti
    print("="*80)
    print("🔍 QUERY PIÙ FREQUENTI")
    print("="*80)
    query_texts = [q['query'].lower().strip() for q in queries]
    query_counts = Counter(query_texts)
    
    for i, (query, count) in enumerate(query_counts.most_common(20), 1):
        percentage = (count / len(queries)) * 100
        print(f"{i:2d}. [{count:3d}x | {percentage:5.1f}%] {query}")
    print()
    
    # Categorie più cercate
    print("="*80)
    print("🏷️  CATEGORIE PIÙ MOSTRATE")
    print("="*80)
    all_categories = []
    for result in results:
        all_categories.extend(result.get('categories', []))
    
    category_counts = Counter(all_categories)
    for i, (cat, count) in enumerate(category_counts.most_common(15), 1):
        percentage = (count / len(results)) * 100 if results else 0
        print(f"{i:2d}. [{count:3d}x | {percentage:5.1f}%] {cat}")
    print()
    
    # Prodotti più mostrati
    print("="*80)
    print("📦 PRODOTTI PIÙ MOSTRATI (TOP 20)")
    print("="*80)
    all_products = []
    for result in results:
        all_products.extend(result.get('top_products', []))
    
    product_counts = Counter(all_products)
    for i, (prod, count) in enumerate(product_counts.most_common(20), 1):
        print(f"{i:2d}. [{count:3d}x] {prod}")
    print()
    
    # Analisi lunghezza query
    print("="*80)
    print("📏 ANALISI LUNGHEZZA QUERY")
    print("="*80)
    lengths = [q['query_length'] for q in queries]
    if lengths:
        print(f"Media caratteri: {sum(lengths) / len(lengths):.1f}")
        print(f"Minima: {min(lengths)} caratteri")
        print(f"Massima: {max(lengths)} caratteri")
        
        # Distribuzione
        short = len([l for l in lengths if l < 20])
        medium = len([l for l in lengths if 20 <= l < 50])
        long = len([l for l in lengths if l >= 50])
        
        print()
        print("Distribuzione:")
        print(f"  Corte (<20 char):   {short:4d} ({short/len(lengths)*100:5.1f}%)")
        print(f"  Medie (20-50 char): {medium:4d} ({medium/len(lengths)*100:5.1f}%)")
        print(f"  Lunghe (>50 char):  {long:4d} ({long/len(lengths)*100:5.1f}%)")
    print()
    
    # Comparazioni richieste
    print("="*80)
    print("⚖️  COMPARAZIONI")
    print("="*80)
    comparisons = len([r for r in results if r.get('has_comparison', False)])
    if results:
        print(f"Comparazioni richieste: {comparisons} ({comparisons/len(results)*100:.1f}%)")
    else:
        print("Nessuna comparazione ancora richiesta")
    print()
    
    # Query senza risultati
    print("="*80)
    print("⚠️  QUERY SENZA RISULTATI")
    print("="*80)
    no_results = [r for r in results if r['products_count'] == 0]
    if no_results:
        print(f"Totale: {len(no_results)} ({len(no_results)/len(results)*100:.1f}%)")
        print()
        print("Query che non hanno trovato prodotti:")
        
        # Trova le query corrispondenti
        no_result_sessions = {r['session']: r['timestamp'] for r in no_results}
        failed_queries = []
        
        for q in queries:
            if q['session'] in no_result_sessions:
                # Trova il result corrispondente per timestamp
                for r in no_results:
                    if r['session'] == q['session'] and abs((r['timestamp'] - q['timestamp']).total_seconds()) < 2:
                        failed_queries.append(q['query'])
                        break
        
        failed_counter = Counter(failed_queries)
        for query, count in failed_counter.most_common(10):
            print(f"  [{count}x] {query}")
    else:
        print("✅ Tutte le query hanno trovato risultati!")
    print()
    
    # Sessioni più attive
    print("="*80)
    print("👥 SESSIONI PIÙ ATTIVE")
    print("="*80)
    session_lengths = [(session, len(queries)) for session, queries in sessions.items()]
    session_lengths.sort(key=lambda x: x[1], reverse=True)
    
    for i, (session, count) in enumerate(session_lengths[:10], 1):
        print(f"{i:2d}. Sessione {session}: {count} query")
    print()
    
    print("="*80)
    print("✅ ANALISI COMPLETATA")
    print("="*80)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Analizza query utenti STIGA Product Assistant')
    parser.add_argument('--days', type=int, help='Analizza solo ultimi N giorni', default=None)
    
    args = parser.parse_args()
    
    analyze_logs(days=args.days)


if __name__ == '__main__':
    main()