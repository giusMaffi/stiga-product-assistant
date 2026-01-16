"""
Modulo per generare e gestire embeddings dei prodotti
"""
import json
import pickle
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path

from src.config import EMBEDDING_MODEL, PRODUCTS_FILE, EMBEDDINGS_FILE


class ProductEmbedder:
    """Genera embeddings semantici per i prodotti STIGA"""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """
        Args:
            model_name: Nome del modello sentence-transformers da usare
        """
        print(f"📦 Caricamento modello embeddings: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.products = []
        self.embeddings = None
        
    def load_products(self, products_file: Path = PRODUCTS_FILE) -> List[Dict]:
        """Carica i prodotti dal file JSON"""
        print(f"📂 Caricamento prodotti da: {products_file}")
        with open(products_file, 'r', encoding='utf-8') as f:
            self.products = json.load(f)
        print(f"✅ Caricati {len(self.products)} prodotti")
        return self.products
    
    def create_product_text(self, product: Dict) -> str:
        """
        Crea una rappresentazione testuale completa del prodotto per l'embedding.
        Include nome, categoria, descrizione, caratteristiche e specifiche.
        """
        parts = []
        
        # Nome e categoria
        parts.append(f"Nome: {product['nome']}")
        parts.append(f"Categoria: {product['categoria']}")
        
        if 'sottocategoria' in product:
            parts.append(f"Tipo: {product['sottocategoria']}")
        
        # Descrizione
        parts.append(f"Descrizione: {product['descrizione']}")
        
        # Caratteristiche
        if 'caratteristiche' in product and product['caratteristiche']:
            caratteristiche_text = " ".join(product['caratteristiche'])
            parts.append(f"Caratteristiche: {caratteristiche_text}")
        
        # Specifiche tecniche chiave
        if 'specifiche' in product:
            specs = product['specifiche']
            specs_text = []
            
            # Specifiche più importanti per la ricerca
            key_specs = [
                'area_taglio_max', 'alimentazione', 'larghezza_taglio',
                'capacita_batteria', 'potenza', 'zone_taglio',
                'tipo_perimetro', 'autonomia'
            ]
            
            for key in key_specs:
                if key in specs and specs[key]:
                    # Formatta in modo leggibile
                    key_readable = key.replace('_', ' ').capitalize()
                    specs_text.append(f"{key_readable}: {specs[key]}")
            
            if specs_text:
                parts.append("Specifiche: " + ", ".join(specs_text))
        
        # Utilizzo consigliato
        if 'utilizzo_consigliato' in product:
            parts.append(f"Ideale per: {product['utilizzo_consigliato']}")
        
        # Keywords
        if 'keywords' in product and product['keywords']:
            parts.append(f"Tag: {' '.join(product['keywords'])}")
        
        return " | ".join(parts)
    
    def generate_embeddings(self) -> np.ndarray:
        """Genera embeddings per tutti i prodotti"""
        if not self.products:
            raise ValueError("Nessun prodotto caricato. Usa load_products() prima.")
        
        print("🔄 Generazione embeddings...")
        
        # Crea testi completi per ogni prodotto
        product_texts = [self.create_product_text(p) for p in self.products]
        
        # Genera embeddings
        self.embeddings = self.model.encode(
            product_texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        print(f"✅ Generati {len(self.embeddings)} embeddings")
        print(f"   Dimensione vettori: {self.embeddings.shape[1]}")
        
        return self.embeddings
    
    def save_embeddings(self, output_file: Path = EMBEDDINGS_FILE):
        """Salva embeddings e prodotti in un file pickle"""
        if self.embeddings is None:
            raise ValueError("Nessun embedding generato. Usa generate_embeddings() prima.")
        
        print(f"💾 Salvataggio embeddings in: {output_file}")
        
        data = {
            'products': self.products,
            'embeddings': self.embeddings,
            'model_name': self.model.get_sentence_embedding_dimension()
        }
        
        with open(output_file, 'wb') as f:
            pickle.dump(data, f)
        
        print("✅ Embeddings salvati con successo")
    
    @staticmethod
    def load_embeddings(embeddings_file: Path = EMBEDDINGS_FILE) -> Dict:
        """Carica embeddings e prodotti da file"""
        print(f"📂 Caricamento embeddings da: {embeddings_file}")
        
        with open(embeddings_file, 'rb') as f:
            data = pickle.load(f)
        
        print(f"✅ Caricati embeddings per {len(data['products'])} prodotti")
        return data


def main():
    """Script principale per generare embeddings"""
    embedder = ProductEmbedder()
    embedder.load_products()
    embedder.generate_embeddings()
    embedder.save_embeddings()
    print("\n🎉 Processo completato!")


if __name__ == "__main__":
    main()
