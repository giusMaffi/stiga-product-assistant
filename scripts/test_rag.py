#!/usr/bin/env python3
"""
Script per testare il sistema RAG completo
"""

import sys
from pathlib import Path

# Aggiungi la directory root al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag import ProductRetriever, ProductMatcher
from src.api import ClaudeClient

def test_retrieval():
    """Test del retrieval"""
    print("\n" + "="*60)
    print("TEST 1: RETRIEVAL")
    print("="*60 + "\n")
    
    retriever = ProductRetriever()
    
    test_queries = [
        "robot tagliaerba per giardino piccolo 300 mq",
        "trattorino elettrico silenzioso per 4000 metri quadri",
        "decespugliatore professionale a scoppio",
    ]
    
    for query in test_queries:
        print(f"🔍 Query: '{query}'")
        results = retriever.search(query, top_k=3)
        
        for i, (product, score) in enumerate(results, 1):
            print(f"\n   {i}. {product['nome']} (score: {score:.3f})")
            print(f"      Categoria: {product['categoria']}")
            if 'specifiche' in product:
                specs = product['specifiche']
                if 'area_taglio_max' in specs:
                    print(f"      Area: {specs['area_taglio_max']}")
        print()

def test_matching():
    """Test del matcher"""
    print("\n" + "="*60)
    print("TEST 2: INTELLIGENT MATCHING")
    print("="*60 + "\n")
    
    matcher = ProductMatcher()
    
    test_queries = [
        "Cerco robot per 500 m² con GPS",
        "Trattorino a batteria per giardino grande, budget 2000 euro",
    ]
    
    for query in test_queries:
        print(f"🔍 Query: '{query}'")
        requirements = matcher.extract_requirements(query)
        print(f"   Requisiti estratti:")
        for key, value in requirements.items():
            print(f"      - {key}: {value}")
        print()

def test_full_pipeline():
    """Test della pipeline completa"""
    print("\n" + "="*60)
    print("TEST 3: PIPELINE COMPLETA (RAG + CLAUDE)")
    print("="*60 + "\n")
    
    # Inizializza componenti
    retriever = ProductRetriever()
    matcher = ProductMatcher()
    claude = ClaudeClient()
    
    # Query di test
    query = "Ho un giardino di circa 600 metri quadri. Vorrei un robot tagliaerba senza dover installare fili. Cosa mi consigli?"
    
    print(f"👤 Utente: {query}\n")
    
    # 1. Retrieval
    print("📊 Step 1: Retrieval prodotti rilevanti...")
    products_with_scores = retriever.search(query, top_k=5)
    print(f"   Trovati {len(products_with_scores)} prodotti\n")
    
    # 2. Re-ranking con matcher
    print("🎯 Step 2: Re-ranking intelligente...")
    reranked = matcher.rerank_products(products_with_scores, query)
    print(f"   Prodotti ri-ordinati per rilevanza\n")
    
    # 3. Formatta contesto per Claude
    print("📝 Step 3: Preparazione contesto...")
    products_context = claude.format_products_for_context(reranked[:3])  # Top 3
    
    # 4. Genera risposta con Claude
    print("🤖 Step 4: Generazione risposta con Claude...\n")
    print("-" * 60)
    response = claude.chat(query, products_context=products_context)
    print(response)
    print("-" * 60)

def main():
    """Main"""
    print("="*60)
    print("TEST SISTEMA RAG STIGA PRODUCT ASSISTANT")
    print("="*60)
    
    try:
        # Test 1: Retrieval
        test_retrieval()
        
        # Test 2: Matching
        test_matching()
        
        # Test 3: Pipeline completa
        test_full_pipeline()
        
        print("\n" + "="*60)
        print("✅ TUTTI I TEST COMPLETATI CON SUCCESSO!")
        print("="*60 + "\n")
        
    except FileNotFoundError as e:
        print(f"\n❌ ERRORE: {e}")
        print("\n💡 Hai generato gli embeddings?")
        print("   Esegui: python scripts/generate_embeddings.py\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRORE: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
