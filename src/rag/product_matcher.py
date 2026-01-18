"""
Product Matcher - Sistema intelligente di matching e re-ranking
"""
import re
from typing import List, Tuple, Dict

# Keywords accessori
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

ACCESSORY_CATEGORIES = [
    'accessori per robot tagliaerba', 'accessori per tagliaerba',
    'accessori per trattorini', 'accessori per decespugliatori',
    'accessori per motoseghe', 'accessori per idropulitrici',
    'kit batteria', 'ricambi', 'pezzi di ricambio',
    'accessori per tagliabordi e decespugliatori',
    'accessori per tagliaerba elicoidali',
    'accessori per trattorini a taglio frontale',
    'accessori per trattorini da giardino',
    'accessori per attrezzi multifunzione',
    'accessori per idropulitrici ad alta pressione',
    'accessori per motoseghe',
    'accessori per motozappe',
    'accessori per spazzaneve',
    'accessori per spazzatrici',
    'accessori cross categoria'
]


def is_accessory_query(query: str) -> bool:
    """Determina se la query cerca accessori"""
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    for keyword in ACCESSORY_KEYWORDS:
        if keyword in query_lower or keyword in query_words:
            return True
    return False


def is_accessory_product(product: dict) -> bool:
    """Determina se un prodotto è un accessorio"""
    categoria = product.get('categoria', '').lower()
    nome = product.get('nome', '').lower()
    
    # Check categoria PRIMA - più affidabile
    for cat in ACCESSORY_CATEGORIES:
        if cat.lower() in categoria:
            return True
    
    # Se la categoria è un prodotto principale, NON è un accessorio
    # (anche se ha "lama" nel nome, un tagliasiepi NON è un accessorio)
    main_categories = [
        'tagliasiepi', 'robot tagliaerba', 'tagliaerba', 'trattorini',
        'decespugliatori', 'motoseghe', 'idropulitrici', 'spazzaneve',
        'soffiatori', 'motozappe', 'biotrituratori', 'forbici da potatura',
        'cesoie per siepi', 'attrezzi multifunzione', 'tagliabordi',
        'arieggiatori e scarificatori', 'aspiratori trituratori',
        'attrezzi manuali per la coltivazione', 'falciatrici e coltivatori',
        'tagliaerba elicoidali', 'trattorini assiali', 'trattorini da giardino',
        'trattorini tagliaerba frontali', 'spazzatrici'
    ]
    
    for main_cat in main_categories:
        if main_cat in categoria:
            return False  # È un prodotto principale!
    
    # Solo DOPO verifica nel nome (per prodotti senza categoria chiara)
    nome_words = set(nome.split())
    for keyword in ACCESSORY_KEYWORDS:
        if keyword in nome or keyword in nome_words:
            return True
    
    return False


class ProductMatcher:
    """Sistema di matching e re-ranking prodotti"""
    
    def __init__(self):
        print("🔄 Caricamento ProductMatcher...")
        print("✅ Matcher pronto!")
    
    def extract_requirements(self, query: str) -> Dict:
        """Estrae requisiti dalla query"""
        requirements = {}
        query_lower = query.lower()
        
        # Estrai categoria
        category_patterns = {
            'robot tagliaerba': r'\brobot\b.*\btagliaerba\b|\btagliaerba\b.*\brobot\b',
            'robot': r'\brobot\b',
            'trattorino': r'\btrattorino\b',
            'tagliaerba': r'\btagliaerba\b',
            'decespugliatore': r'\bdecespugliator[ei]\b',
            'motosega': r'\bmotosega\b',
            'idropulitrice': r'\bidropulitric[ei]\b',
            'tagliasiepi': r'\btagliasiepi\b',
        }
        
        for category, pattern in category_patterns.items():
            if re.search(pattern, query_lower):
                requirements['categoria'] = category
                break
        
        # Estrai dimensioni
        mq_match = re.search(r'(\d+)\s*(?:m²|mq|metri)', query_lower)
        if mq_match:
            requirements['area_mq'] = int(mq_match.group(1))
        
        # Estrai budget
        budget_match = re.search(r'(\d+)\s*(?:€|euro)', query_lower)
        if budget_match:
            requirements['budget'] = int(budget_match.group(1))
        
        return requirements
    
    def rerank_products(
        self, 
        products_with_scores: List[Tuple[dict, float]],
        query: str
    ) -> List[Tuple[dict, float, List[str]]]:
        """Re-ranking con penalizzazione accessori"""
        
        cerca_accessori = is_accessory_query(query)
        requirements = self.extract_requirements(query)
        
        reranked = []
        
        for product, base_score in products_with_scores:
            score = base_score
            reasons = []
            
            # PENALIZZA ACCESSORI quando non cercati
            if is_accessory_product(product) and not cerca_accessori:
                score *= 0.1
                reasons.append("⚠️ Accessorio (penalizzato)")
            
            # BOOST per match area
            if 'area_mq' in requirements:
                specs = product.get('specifiche_tecniche', {})
                area_text = specs.get('Area di taglio fino a', '')
                
                if area_text:
                    area_match = re.search(r'(\d+)', area_text)
                    if area_match:
                        product_area = int(area_match.group(1))
                        required_area = requirements['area_mq']
                        
                        if product_area >= required_area * 0.8:
                            score *= 1.3
                            reasons.append(f"✅ Area ({product_area}mq)")
            
            # BOOST per budget
            if 'budget' in requirements:
                prezzo_text = product.get('prezzo', '')
                if prezzo_text and prezzo_text != 'Contattaci':
                    try:
                        prezzo = float(prezzo_text.replace('€', '').replace('.', '').replace(',', '.').strip())
                        if prezzo <= requirements['budget']:
                            score *= 1.2
                            reasons.append(f"✅ Budget ({int(prezzo)}€)")
                    except:
                        pass
            
            reranked.append((product, score, reasons))
        
        reranked.sort(key=lambda x: x[1], reverse=True)
        return reranked