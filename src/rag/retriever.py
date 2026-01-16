"""
Product Retriever - Semantic search sui prodotti
"""
import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer

from ..config import (
    PRODUCTS_FILE,
    EMBEDDINGS_FILE,
    EMBEDDING_MODEL,
    TOP_K_PRODUCTS
)


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
        
        # Carica modello per query encoding
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        
        print(f"✅ Caricati {len(self.products)} prodotti")
        print(f"✅ Embeddings shape: {self.embeddings.shape}")
    
    def search(
        self, 
        query: str, 
        top_k: int = TOP_K_PRODUCTS,
        filters: Optional[Dict] = None
    ) -> List[Tuple[dict, float]]:
        """
        Cerca prodotti rilevanti per la query
        """
        # Encode query
        query_embedding = self.model.encode([query])[0]
        
        # Calcola similarità
        similarities = np.dot(self.embeddings, query_embedding)
        
        # Crea lista candidati con scores
        candidates = []
        for idx, score in enumerate(similarities):
            product = self.products[idx]
            
            # Applica filtri se presenti
            if filters:
                if 'categoria' in filters:
                    cat_filter = filters['categoria'].lower()
                    prod_cat = product.get('categoria', '').lower()
                    if cat_filter not in prod_cat:
                        continue
            
            candidates.append((product, float(score)))
        
        # Ordina per score
        candidates.sort(key=lambda x: x[1], reverse=True)
        
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