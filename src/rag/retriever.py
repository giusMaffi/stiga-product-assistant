"""
Product Retriever - Semantic search sui prodotti
"""
import json
import pickle
import re
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from ..config import (
    PRODUCTS_FILE,
    EMBEDDINGS_FILE,
    EMBEDDING_MODEL,
    TOP_K_PRODUCTS
)


def is_accessory_query(query: str) -> bool:
    """Determina se la query cerca accessori"""
    ACCESSORY_KEYWORDS = [
        'accessorio', 'accessori', 'ricambio', 'ricambi', 'kit', 'pezzo', 'pezzi',
        'lama', 'lame', 'cavo', 'cavi', 'perimetrale', 'bobina', 'stazione', 'base', 
        'ricarica', 'chiodi', 'picchetti', 'installazione', 'connettore', 'copertura',
        'piatto', 'piatti', 'sacco', 'sacchi', 'raccoglierba', 'mulching',
        'filo', 'testina', 'testine', 'rocchetto', 'catena', 'catene', 'barra',
        'lancia', 'spazzola', 'ugello', 'tubo', 'detergente', 'prolunga',
        'batteria', 'batterie', 'caricabatterie', 'alimentatore',
        'filtro', 'candela', 'guarnizione', 'molla'
    ]
    
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    for keyword in ACCESSORY_KEYWORDS:
        if keyword in query_lower or keyword in query_words:
            return True
    return False


class ProductRetriever:
    """Gestisce il retrieval semantico dei prodotti"""
    
    def __init__(self):
        """Inizializza il retriever"""
        print("🔄 Caricamento ProductRetriever...")
        
        # Carica prodotti
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            self.products = json.load(f)
        
        # Carica embeddings
        with open(EMBEDDINGS_FILE, 'rb') as f:
            data = pickle.load(f)
            self.embeddings = data['embeddings']
            self.model_name = data['model_name']
            
            # CRITICAL: Usa product_ids per mappare embeddings → prodotti
            if 'product_ids' in data:
                self.product_ids = data['product_ids']
                # Crea mappatura product_id → indice embedding
                self.id_to_embedding_idx = {pid: i for i, pid in enumerate(self.product_ids)}
                # Crea mappatura product_id → prodotto
                self.id_to_product = {p['id']: p for p in self.products}
                print(f"✅ Mappatura product_ids caricata: {len(self.product_ids)} prodotti")
            else:
                # Fallback: assume ordine array (vecchio comportamento)
                print("⚠️ WARNING: product_ids non trovato, uso ordine array")
                self.product_ids = None
        
        # Carica modello per query encoding
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        
        print(f"✅ Caricati {len(self.products)} prodotti")
        print(f"✅ Embeddings shape: {self.embeddings.shape}")
    
    def _detect_exact_category_match(self, query: str) -> Optional[str]:
        """
        Rileva se la query contiene esattamente il nome di una categoria
        Ritorna la categoria se trovata, altrimenti None
        """
        query_lower = query.lower().strip()
        
        # Mappa categorie esatte (query → categoria nel database)
        exact_categories = {
            'tagliasiepi': 'Tagliasiepi',
            'robot tagliaerba': 'Robot tagliaerba',
            'robot': 'Robot tagliaerba',
            'tagliaerba': 'Tagliaerba',
            'trattorino': 'Trattorini da giardino',
            'trattorini': 'Trattorini da giardino',
            'decespugliatore': 'Decespugliatori',
            'decespugliatori': 'Decespugliatori',
            'motosega': 'Motoseghe',
            'motoseghe': 'Motoseghe',
            'idropulitrice': 'Idropulitrici ad alta pressione',
            'idropulitrici': 'Idropulitrici ad alta pressione',
            'spazzaneve': 'Spazzaneve',
            'soffiatore': 'Soffiatori e aspiratori',
            'soffiatori': 'Soffiatori e aspiratori',
            'biotrituratore': 'Biotrituratori',
            'biotrituratori': 'Biotrituratori',
            'motozappa': 'Motozappe',
            'motozappe': 'Motozappe',
            'spazzatrice': 'Spazzatrici',
            'spazzatrici': 'Spazzatrici',
        }
        
        # Check se la query è esattamente una categoria
        if query_lower in exact_categories:
            return exact_categories[query_lower]
        
        # Check se la query contiene una categoria
        for key, cat in exact_categories.items():
            if key in query_lower:
                return cat
        
        return None
    
    def search(
        self, 
        query: str, 
        top_k: int = TOP_K_PRODUCTS,
        filters: Optional[Dict] = None,
        min_score: float = 0.0
    ) -> List[Tuple[dict, float]]:
        """
        Cerca prodotti rilevanti per la query
        """
        # 🆕 FIX: NON forzare categoria se cerca accessori
        cerca_accessori = is_accessory_query(query)
        
        # Check per match esatto categoria SOLO se NON cerca accessori
        # Verifica se c'è categoria ESPLICITA nella query
        query_lower = query.lower()
        has_explicit_category = any(
            cat_word in query_lower 
            for cat_word in ['robot', 'trattorini', 'trattorino', 'tagliaerba', 
                            'decespugliator', 'motosega', 'soffiator', 'idropulitric',
                            'tagliasiepi', 'spazzaneve']
        )
        
        if not cerca_accessori or has_explicit_category:
            # NON cerca accessori OPPURE ha categoria esplicita
            exact_category = self._detect_exact_category_match(query)
            
            if exact_category:
                print(f"🎯 Rilevata categoria esatta: '{exact_category}' dalla query '{query}'")
                # Forza filtro sulla categoria
                if not filters:
                    filters = {}
                filters['categoria'] = exact_category
        else:
            print(f"🔧 Query accessori rilevata nel retriever - NON forzo categoria")
        
        # Encode query
        query_embedding = self.model.encode([query])[0]
        
        # Calcola cosine similarity
        similarities = cosine_similarity(
            [query_embedding], 
            self.embeddings
        )[0]
        
        # Crea lista candidati con scores
        candidates = []
        for idx, score in enumerate(similarities):
            # Filtra per score minimo
            if score < min_score:
                continue
                
            # Usa mappatura product_ids se disponibile
            if self.product_ids:
                product_id = self.product_ids[idx]
                product = self.id_to_product.get(product_id)
                if not product:
                    continue  # Skip se prodotto non trovato
            else:
                product = self.products[idx]  # Fallback vecchio comportamento
            
            # Applica filtri se presenti
            if filters:
                if 'categoria' in filters:
                    cat_filter = filters['categoria'].lower()
                    prod_cat = product.get('categoria', '').lower()
                    
                    # Match ESATTO (non parziale) per evitare accessori
                    # "Robot tagliaerba" deve matchare "robot tagliaerba" 
                    # ma NON "accessori per robot tagliaerba"
                    if prod_cat != cat_filter:
                        continue
            
            candidates.append((product, float(score)))
        
        # Ordina per score
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Log per debug
        if len(candidates) > 0:
            print(f"🔍 Query: '{query}' → Trovati {len(candidates)} prodotti")
            if filters and 'categoria' in filters:
                print(f"   Filtrati per categoria: {filters['categoria']}")
            print(f"   Top 3 scores: {[round(c[1], 3) for c in candidates[:3]]}")
        else:
            print(f"⚠️  Query: '{query}' → Nessun prodotto trovato!")
        
        # Ritorna top K
        return candidates[:top_k]
    
    def get_product_by_id(self, product_id: str) -> Optional[dict]:
        """Trova prodotto per ID"""
        for product in self.products:
            if product.get('id') == product_id:
                return product
        return None
    
    def get_all_categories(self) -> List[str]:
        """Ottieni lista di tutte le categorie"""
        categories = set()
        for product in self.products:
            if product.get('categoria'):
                categories.add(product['categoria'])
        return sorted(list(categories))