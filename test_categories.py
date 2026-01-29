"""
Test Automatico - Tutte le Categorie STIGA Product Assistant
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
AUTH = ("stiga", "StigaDemo2025!")
SESSION_ID = f"test_{int(time.time())}"

# Categorie e query di test
TEST_CASES = [
    {
        "categoria": "Robot tagliaerba",
        "query": "hai robot tagliaerba?",
        "confronto": "confronta A 4 e A 8",
        "expected_keywords": ["robot", "area di taglio", "batteria"]
    },
    {
        "categoria": "Trattorini",
        "query": "hai trattorini?",
        "confronto": "confronta Combi 372 e Estate 384 M",
        "expected_keywords": ["trattorino", "motore", "larghezza"]
    },
    {
        "categoria": "Tagliaerba",
        "query": "hai tagliaerba?",
        "confronto": "confronta Multiclip 47 e Collector 48 AE Kit",
        "expected_keywords": ["tagliaerba", "taglio", "raccolta"]
    },
    {
        "categoria": "Decespugliatori",
        "query": "hai decespugliatori?",
        "confronto": "confronta SBC 900 D AE e BC 700e B",
        "expected_keywords": ["decespugliator", "batteria", "larghezza"]
    },
    {
        "categoria": "Motoseghe",
        "query": "hai motoseghe?",
        "confronto": None,  # Skip se non ci sono prodotti da confrontare
        "expected_keywords": ["motosega", "barra", "catena"]
    },
    {
        "categoria": "Tagliasiepi",
        "query": "hai tagliasiepi?",
        "confronto": None,
        "expected_keywords": ["tagliasiepi", "lama", "taglio"]
    },
    {
        "categoria": "Idropulitrici",
        "query": "hai idropulitrici?",
        "confronto": None,
        "expected_keywords": ["idropulitrice", "pressione", "bar"]
    },
    {
        "categoria": "Soffiatori",
        "query": "hai soffiatori?",
        "confronto": None,
        "expected_keywords": ["soffiator", "aria", "velocità"]
    }
]

def send_message(message):
    """Invia messaggio all'API"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": message, "session_id": SESSION_ID},
            auth=AUTH,
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def check_response(data, expected_keywords):
    """Verifica che la risposta contenga le keywords attese"""
    response_text = data.get('response', '').lower()
    products = data.get('products', [])
    
    found_keywords = []
    for keyword in expected_keywords:
        if keyword.lower() in response_text or any(keyword.lower() in str(p).lower() for p in products):
            found_keywords.append(keyword)
    
    return {
        'has_response': bool(response_text),
        'has_products': len(products) > 0,
        'product_count': len(products),
        'keywords_found': found_keywords,
        'keywords_missing': [k for k in expected_keywords if k not in found_keywords]
    }

def test_category_switch():
    """Test cambio categoria (robot -> trattorini -> robot)"""
    print("\n" + "="*70)
    print("TEST CAMBIO CATEGORIA (Memoria Bloccata Fix)")
    print("="*70)
    
    results = []
    
    # Test 1: Robot
    print("\n1. Query: 'hai robot?'")
    data1 = send_message("hai robot?")
    time.sleep(1)
    products1 = len(data1.get('products', []))
    print(f"   ✓ Prodotti robot: {products1}")
    results.append(("Robot iniziale", products1 > 0, products1))
    
    # Test 2: Trattorini (cambio categoria)
    print("\n2. Query: 'hai trattorini?'")
    data2 = send_message("hai trattorini?")
    time.sleep(1)
    products2 = len(data2.get('products', []))
    response2 = data2.get('response', '').lower()
    has_trattorini = 'trattorini' in response2 or 'trattorino' in response2
    print(f"   ✓ Prodotti trattorini: {products2}")
    print(f"   ✓ Risposta contiene 'trattorini': {has_trattorini}")
    results.append(("Cambio a trattorini", products2 > 0 and has_trattorini, products2))
    
    # Test 3: Robot di nuovo
    print("\n3. Query: 'hai robot?'")
    data3 = send_message("hai robot?")
    time.sleep(1)
    products3 = len(data3.get('products', []))
    response3 = data3.get('response', '').lower()
    has_robot = 'robot' in response3
    print(f"   ✓ Prodotti robot: {products3}")
    print(f"   ✓ Risposta contiene 'robot': {has_robot}")
    results.append(("Ritorno a robot", products3 > 0 and has_robot, products3))
    
    return results

def run_tests():
    """Esegue tutti i test"""
    print("="*70)
    print(f"TEST AUTOMATICO - STIGA PRODUCT ASSISTANT")
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Session: {SESSION_ID}")
    print("="*70)
    
    all_results = []
    
    # Test 1: Tutte le categorie
    print("\n" + "="*70)
    print("TEST 1: RICERCA PER CATEGORIA")
    print("="*70)
    
    for test_case in TEST_CASES:
        categoria = test_case['categoria']
        query = test_case['query']
        expected = test_case['expected_keywords']
        
        print(f"\n📦 Categoria: {categoria}")
        print(f"   Query: '{query}'")
        
        # Invia query
        data = send_message(query)
        time.sleep(2)  # Pausa tra richieste
        
        # Verifica risposta
        check = check_response(data, expected)
        
        print(f"   ✓ Risposta ricevuta: {check['has_response']}")
        print(f"   ✓ Prodotti trovati: {check['product_count']}")
        print(f"   ✓ Keywords trovate: {', '.join(check['keywords_found'])}")
        if check['keywords_missing']:
            print(f"   ⚠ Keywords mancanti: {', '.join(check['keywords_missing'])}")
        
        success = check['has_response'] and check['product_count'] > 0
        all_results.append((categoria, success, check['product_count']))
    
    # Test 2: Confronti
    print("\n" + "="*70)
    print("TEST 2: CONFRONTI PRODOTTI")
    print("="*70)
    
    for test_case in TEST_CASES:
        if not test_case['confronto']:
            continue
            
        categoria = test_case['categoria']
        confronto = test_case['confronto']
        
        print(f"\n⚖️  Categoria: {categoria}")
        print(f"   Query: '{confronto}'")
        
        # Invia confronto
        data = send_message(confronto)
        time.sleep(2)
        
        response = data.get('response', '').lower()
        products = data.get('products', [])
        comparator = data.get('comparator')
        
        has_table = 'caratteristica' in response or comparator is not None
        has_2_products = len(products) >= 2
        
        print(f"   ✓ Tabella confronto: {has_table}")
        print(f"   ✓ Due prodotti: {has_2_products}")
        print(f"   ✓ Prodotti nel confronto: {len(products)}")
        
        success = has_table and has_2_products
        all_results.append((f"Confronto {categoria}", success, len(products)))
    
    # Test 3: Cambio categoria
    switch_results = test_category_switch()
    all_results.extend(switch_results)
    
    # Report finale
    print("\n" + "="*70)
    print("REPORT FINALE")
    print("="*70)
    
    total_tests = len(all_results)
    passed = sum(1 for _, success, _ in all_results if success)
    failed = total_tests - passed
    
    print(f"\n📊 Statistiche:")
    print(f"   Total tests: {total_tests}")
    print(f"   ✅ Passed: {passed} ({passed/total_tests*100:.1f}%)")
    print(f"   ❌ Failed: {failed} ({failed/total_tests*100:.1f}%)")
    
    print(f"\n📋 Dettaglio:")
    for name, success, count in all_results:
        status = "✅ PASS" if success else "❌ FAIL"
        detail = f"({count} prodotti)" if isinstance(count, int) else ""
        print(f"   {status} - {name} {detail}")
    
    print(f"\n⏰ End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    return passed == total_tests

if __name__ == "__main__":
    try:
        success = run_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrotto dall'utente")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Errore durante i test: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
