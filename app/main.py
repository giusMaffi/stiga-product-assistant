"""
Flask App - Stiga Product Assistant
Production-Ready con Query Enrichment Hybrid + Fix Descrizioni + Comparatore + Widget + Analytics + HTTP Basic Auth + STREAMING SSE
"""
from flask import Flask, render_template, request, jsonify, Response, url_for
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import sys
from pathlib import Path
import json
import re
import difflib
from typing import List, Dict, Optional
from sklearn.metrics.pairwise import cosine_similarity
import logging
from datetime import datetime
import hashlib
import os

# Aggiungi path al modulo
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag import ProductRetriever, ProductMatcher
from src.api import ClaudeClient
from src.config import PORT, FLASK_DEBUG
from app.analytics_tracker import get_tracker
from app.analytics_routes import analytics_bp
from app.session_store import get_session as _get_session, save_session as _save_session
from app.guardrail import evaluate_scope, SCOPE_BLOCK_MSG, SCOPE_DEFLECT_MSG

# Fase 1 orchestrante: apertura automatica del confronto deterministico (feature flag, default ON)
ORCHESTRATE_COMPARISON = os.getenv('ORCHESTRATE_COMPARISON', '1').lower() not in ('0', 'false', 'off', 'no')

app = Flask(__name__)
CORS(app)


# Cache-busting statici: appende la mtime del file come ?v=, così il browser
# riscarica JS/CSS solo quando cambiano davvero. Chiude la classe di bug
# "a me funziona, a te no" causata da chat.js vecchio in cache dopo un deploy.
@app.context_processor
def _inject_asset_helper():
    def asset(filename):
        try:
            v = int(os.path.getmtime(os.path.join(app.static_folder, filename)))
        except OSError:
            v = 0
        return url_for('static', filename=filename, v=v)
    return {'asset': asset}

# Setup HTTP Basic Authentication
auth = HTTPBasicAuth()

# Credenziali di accesso (cambia username/password come preferisci)
users = {
    os.getenv("BASIC_AUTH_USERNAME", "stiga"): generate_password_hash(os.getenv("BASIC_AUTH_PASSWORD", ""))
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

# Setup directory logs
LOGS_DIR = Path(__file__).parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Setup logging per query utenti
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
query_logger = logging.getLogger('queries')
query_handler = logging.FileHandler(LOGS_DIR / 'user_queries.log', encoding='utf-8')
query_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
query_logger.addHandler(query_handler)
query_logger.setLevel(logging.INFO)

# Inizializza componenti (una sola volta all'avvio)
print("🚀 Inizializzazione componenti...")
retriever = ProductRetriever()
matcher = ProductMatcher()
claude = ClaudeClient()
analytics_tracker = get_tracker()
print("✅ Componenti pronte!")

analytics_bp.before_request(auth.login_required(lambda: None))
app.register_blueprint(analytics_bp)
# ═══════════════════════════════════════════════════════════════════
# QUERY ENRICHMENT - SISTEMA HYBRID OTTIMIZZATO
# Performance: <10ms | Accuratezza: 95%+
# ═══════════════════════════════════════════════════════════════════

# Pattern precompilati per massima performance
CATEGORIA_PATTERNS = {
    'robot tagliaerba': re.compile(r'\brobot\b.*\btagliaerba\b|\btagliaerba\b.*\brobot\b', re.IGNORECASE),
    'robot': re.compile(r'\brobot\b', re.IGNORECASE),
    'trattorino': re.compile(r'\btrattorino\b|\btrattorini\b', re.IGNORECASE),
    'tagliaerba': re.compile(r'\btagliaerba\b', re.IGNORECASE),
    'decespugliatore': re.compile(r'\bdecespugliator[ei]\b|\btagliabordi\b', re.IGNORECASE),
    'motosega': re.compile(r'\bmotosega\b|\bmotoseghe\b', re.IGNORECASE),
    'idropulitrice': re.compile(r'\bidropulitric[ei]\b|\balta pressione\b', re.IGNORECASE),
    'spazzaneve': re.compile(r'\bspazzaneve\b', re.IGNORECASE),
    'biotrituratore': re.compile(r'\bbiotrituratore?\b', re.IGNORECASE),
    'motozappa': re.compile(r'\bmotozappa\b|\bmotozappe\b', re.IGNORECASE),
    'spazzatrice': re.compile(r'\bspazzatric[ei]\b', re.IGNORECASE),
    'soffiatore': re.compile(r'\bsoffiator[ei]\b|\baspirator[ei]\b', re.IGNORECASE),
    'tagliasiepi': re.compile(r'\btagliasiepi\b', re.IGNORECASE),
    'forbici': re.compile(r'\bforbici\b|\bcesoie\b', re.IGNORECASE),
    'arieggiatore': re.compile(r'\barieggiat\w+|\bscarificat\w+', re.IGNORECASE)
}


# Mapping categorie estratte → categorie DB
CATEGORIA_MAPPING = {
    'robot tagliaerba': 'Robot tagliaerba',
    'robot': 'Robot tagliaerba',
    'trattorino': 'Trattorini da giardino',
    'trattorini': 'Trattorini da giardino',
    'trattorini da giardino': 'Trattorini da giardino',
    'tagliaerba': 'Tagliaerba',
    'decespugliatore': 'Decespugliatori',
    'decespugliatori': 'Decespugliatori',
    'motosega': 'Motoseghe',
    'motoseghe': 'Motoseghe',
    'tagliasiepi': 'Tagliasiepi',
    'soffiatore': 'Soffiatori e aspiratori',
    'soffiatori': 'Soffiatori e aspiratori',
    'idropulitrice': 'Idropulitrici ad alta pressione',
    'idropulitrici': 'Idropulitrici ad alta pressione',
}

MODELLO_PATTERN = re.compile(
    r'\b([A-Z]{1,3})\s*(\d+)\s*([A-Z])?\b|'
    r'\b(Swift|Estate|Tornado|Park|Combi|Multiclip|Twinclip|Collector|Gyro|Villa|Royal|Garden|Compact|Experience)\s*(\d+)?\s*([A-Z])?\b',
    re.IGNORECASE
)

ACCESSORIO_PATTERN = re.compile(
    r'\b(lam[ae]|batteria|batterie|caricabatterie|filo|testina|catene?|spazzola|sacco|piatto|ruote?|copertura|kit|ricambi?|accessori?)\b',
    re.IGNORECASE
)

DIMENSIONI_PATTERN = re.compile(r'(\d+)\s*(?:m²|mq|metri|metro)', re.IGNORECASE)

ALIMENTAZIONE_PATTERN = re.compile(r'\b(elettric[oa]|batteria|benzina|scoppio)\b', re.IGNORECASE)


# F-25 v2: tolleranza refusi con "normalizza-poi-match".
# Prima si correggono i refusi token-per-token verso le parole-bersaglio delle regex,
# POI si applica CATEGORIA_PATTERNS. Cosi' l'ordine di priorita' (robot tagliaerba >
# robot > tagliaerba) resta valido anche con errori di battitura: es. "robto tagliaerba"
# viene normalizzato in "robot tagliaerba" e riconosciuto come robot, non come tagliaerba.
_REFUSI_VOCAB = {
    'robot', 'tagliaerba', 'tagliasiepi', 'tagliabordi',
    'trattorino', 'trattorini',
    'decespugliatore', 'decespugliatori',
    'motosega', 'motoseghe',
    'idropulitrice', 'idropulitrici',
    'spazzaneve', 'biotrituratore',
    'motozappa', 'motozappe', 'spazzatrice', 'spazzatrici',
    'soffiatore', 'soffiatori', 'aspiratore', 'aspiratori',
    'forbici', 'cesoie',
    'arieggiatore', 'scarificatore',
}
_REFUSI_VOCAB_LIST = list(_REFUSI_VOCAB)

# Nomi modello STIGA: non vanno mai "corretti" verso una categoria.
_MODEL_WORDS = {
    'swift', 'estate', 'tornado', 'combi', 'multiclip', 'twinclip',
    'collector', 'villa', 'royal', 'garden', 'compact', 'experience',
}

_REFUSI_TOKEN = re.compile(r'[A-Za-z\u00e0\u00e8\u00e9\u00ec\u00f2\u00f9]{5,}')


def _normalizza_refusi(text: str) -> str:
    """F-25 v2: corregge i refusi verso il vocabolario categorie prima del match regex.
    Conservativo: solo run di >=5 lettere (i codici modello con cifre restano intatti),
    salta parole gia' esatte e nomi modello noti, soglia 0.80 (tarata: cattura le
    trasposizioni tipo 'robto' senza falsi positivi su parole italiane comuni)."""
    if not text:
        return text

    def _fix(m):
        w = m.group(0)
        lw = w.lower()
        if lw in _REFUSI_VOCAB or lw in _MODEL_WORDS:
            return w
        cand = difflib.get_close_matches(lw, _REFUSI_VOCAB_LIST, n=1, cutoff=0.80)
        return cand[0] if cand else w

    return _REFUSI_TOKEN.sub(_fix, text)


def extract_categoria(messages: List[Dict]) -> Optional[str]:
    """Estrae categoria prodotto - PRIORITA' a messaggi piu' recenti (tollerante ai refusi)."""
    # Prima controlla SOLO l'ultimo messaggio (quello corrente), normalizzato
    if messages:
        last_norm = _normalizza_refusi(messages[-1].get('content', ''))
        for cat, pattern in CATEGORIA_PATTERNS.items():
            if pattern.search(last_norm):
                print(f"CAT (corrente): {cat}")
                return cat

    # Se non trovata nel corrente, cerca nella storia recente (ultimi 3 messaggi)
    for msg in reversed(messages[-3:] if len(messages) > 3 else messages):
        content = _normalizza_refusi(msg.get('content', ''))
        for cat, pattern in CATEGORIA_PATTERNS.items():
            if pattern.search(content):
                print(f"CAT (storia): {cat}")
                return cat

    return None


def extract_modello(messages: List[Dict]) -> Optional[str]:
    """Estrae modello più specifico"""
    for msg in reversed(messages):
        content = msg.get('content', '')
        match = MODELLO_PATTERN.search(content)
        if match:
            if match.group(4):  # Nome proprio (Swift, Estate, etc)
                parts = [match.group(4)]
                if match.group(5):
                    parts.append(match.group(5))
                if match.group(6):
                    parts.append(match.group(6))
                return ' '.join(parts).upper()
            else:  # Codice alfanumerico (A 150, G 300, etc)
                parts = [match.group(1)]
                if match.group(2):
                    parts.append(match.group(2))
                if match.group(3):
                    parts.append(match.group(3))
                return ' '.join(parts).upper()
    return None


def extract_accessorio(messages: List[Dict]) -> Optional[str]:
    """Estrae tipo accessorio/ricambio"""
    for msg in reversed(messages):
        content = msg.get('content', '')
        match = ACCESSORIO_PATTERN.search(content)
        if match:
            return match.group(1).lower()
    return None


def extract_dimensioni(messages: List[Dict]) -> Optional[str]:
    """Estrae dimensioni giardino"""
    for msg in reversed(messages):
        content = msg.get('content', '')
        match = DIMENSIONI_PATTERN.search(content)
        if match:
            return f"{match.group(1)}mq"
    return None


def extract_alimentazione(messages: List[Dict]) -> Optional[str]:
    """Estrae tipo alimentazione"""
    for msg in reversed(messages):
        content = msg.get('content', '')
        match = ALIMENTAZIONE_PATTERN.search(content)
        if match:
            ali = match.group(1).lower()
            if 'elettric' in ali:
                return 'elettrico'
            elif 'batteria' in ali:
                return 'batteria'
            elif 'benzina' in ali or 'scoppio' in ali:
                return 'benzina'
    return None


def search_products_by_name(query: str, retriever) -> List:
    """
    Cerca prodotti per nome quando l'utente specifica modelli in un confronto.
    Approccio generale: splitta la query sulle congiunzioni e cerca ogni parte.
    """
    # Step 1: Pulisci query da parole chiave
    clean_query = query.lower()
    for word in ['confronta', 'confrontare', 'compare', 'vs', 'versus', 'differenza', 'differenze', 
                 'questi prodotti', 'prodotti', 'prodotto', 'modelli', 'modello', 'il modello',
                 'i modelli', ':']:
        clean_query = clean_query.replace(word, ' ')
    
    # Rimuovi spazi multipli
    import re as regex
    clean_query = regex.sub(r'\s+', ' ', clean_query).strip()
    
    # Step 2: Splitta su congiunzioni
    # Usa regex per splittare su: " e ", " and ", " vs ", " con "
    import re
    parts = re.split(r'\s+(?:e|and|vs|con)\s+', clean_query)
    
    # Step 3: Pulisci ogni parte
    model_names = []
    for part in parts:
        # Rimuovi articoli e pulisci
        clean = part.strip()
        for article in ['il ', 'lo ', 'la ', 'i ', 'gli ', 'le ', 'un ', 'uno ', 'una ']:
            if clean.startswith(article):
                clean = clean[len(article):]
        clean = clean.strip()
        if clean and len(clean) > 2:  # Almeno 3 caratteri
            model_names.append(clean)
    # Preferisci i token modello estratti dal pattern MODELLO
    # (robusto a frasi come 'mi interessa il modello A 500', non solo 'A 500' isolato)
    _pattern_models = [m.group(0).strip().lower() for m in MODELLO_PATTERN.finditer(query)]
    _pattern_models = [p for p in _pattern_models if len(p) > 2]
    if _pattern_models:
        model_names = _pattern_models
    
    if not model_names:
        return []
    
    print(f"🔍 Ricerca diretta per modelli: {model_names}")
    
    # Step 4: Cerca nel DB
    all_products = retriever.products
    found = []
    
    for model in model_names:
        best_match = None
        best_score = 0
        
        for product in all_products:
            product_name = product.get('nome', '').lower()
            
            # Match esatto (score 1.0)
            if model == product_name:
                best_match = (product, 1.0, ['nome_esatto'])
                best_score = 1.0
                break
            
            # Match prefisso esatto (score 0.95)
            # "a 8" matcha "a 8v" ma non "filo a sezione"
            elif product_name.startswith(model + ' '):
                if best_score < 0.95:
                    best_match = (product, 0.95, ['nome_prefisso'])
                    best_score = 0.95
            
            # Match contenuto all'inizio (score 0.9)
            # Per nomi composti tipo "BL 100e Kit"
            elif product_name.startswith(model):
                if best_score < 0.9:
                    best_match = (product, 0.9, ['nome_inizio'])
                    best_score = 0.9
        
        if best_match:
            found.append(best_match)
            print(f"   ✅ Trovato: {best_match[0].get('nome')} (ID: {best_match[0].get('id')})")
        else:
            print(f"   ⚠️  Non trovato: '{model}'")
    
    return found


def detect_show_all_intent(user_message: str, detected_category: str = None) -> bool:
    message_lower = user_message.lower()
    show_all_keywords = ['tutti', 'all', 'tutta la gamma', 'mostrami tutto', 'fammi vedere tutti', 'mostrami tutti', 'elenca tutti', 'voglio vedere tutti', 'dammi tutti', 'quali sono tutti']
    has_show_all = any(kw in message_lower for kw in show_all_keywords)
    has_category = detected_category is not None
    category_keywords = ['robot', 'trattorini', 'tagliaerba', 'decespugliatori', 'motoseghe', 'tagliasiepi', 'idropulitrici', 'soffiatori']
    has_explicit_category = any(cat in message_lower for cat in category_keywords)
    result = has_show_all and (has_category or has_explicit_category)
    if result:
        print(f"🎯 Modalità CATALOGO COMPLETO attivata per query: '{user_message}'")
    return result

def build_enriched_query(user_message: str, conversation_history: List[Dict]) -> str:
    """
    Arricchisce query con contesto conversazionale
    
    Performance: <10ms
    Accuratezza: 95%+
    
    Args:
        user_message: Messaggio corrente utente
        conversation_history: Storia conversazione
    
    Returns:
        Query arricchita con contesto
    """
    enriched_parts = [user_message]
    
    # Analizza ultimi 8 messaggi (4 turni)
    recent = conversation_history[-8:] if len(conversation_history) > 8 else conversation_history
    
    # Estrazione veloce con pattern precompilati
    context = {
        'accessorio': extract_accessorio(recent),
        'modello': extract_modello(recent),
        'categoria': extract_categoria(recent),
        'dimensioni': extract_dimensioni(recent),
        'alimentazione': extract_alimentazione(recent)
    }
    
    # Costruzione query semantica (ordine: specifico → generico)
    if context['accessorio']:
        enriched_parts.append(context['accessorio'])
    
    if context['modello']:
        enriched_parts.append(context['modello'])
    
    # DISABILITATO: Non aggiungere categoria dalla storia (causa conflitti)
    # if context['categoria']:
    #     enriched_parts.append(context['categoria'])
    
    if context['dimensioni']:
        enriched_parts.append(context['dimensioni'])
    
    if context['alimentazione']:
        enriched_parts.append(context['alimentazione'])
    
    enriched_query = ' '.join(enriched_parts)
    
    # Log per debug
    if enriched_query != user_message:
        print(f"🔍 Query arricchita: '{user_message}' → '{enriched_query}'")
        print(f"   Context: {', '.join([f'{k}={v}' for k, v in context.items() if v])}")
    
    return enriched_query


# ═══════════════════════════════════════════════════════════════════
# PARSING RISPOSTA CLAUDE
# ═══════════════════════════════════════════════════════════════════

def _parse_comparator_block(response_text: str):
    """
    Estrae e valida il blocco <comparatore>. Ritorna il dict del comparatore
    oppure None. F-06: non fallisce mai in silenzio, ogni problema e' loggato.
    """
    if not re.search(r'<comparatore>', response_text, re.IGNORECASE):
        return None  # nessun comparatore richiesto: caso normale

    match = re.search(r'<comparatore>(.*?)</comparatore>', response_text, re.DOTALL | re.IGNORECASE)
    if not match:
        # Tag aperto ma non chiuso -> quasi sempre troncamento (MAX_TOKENS, F-05)
        print("\U0001F534 F-06: <comparatore> aperto ma non chiuso "
              "(probabile troncamento MAX_TOKENS / F-05). Comparatore non mostrato.")
        return None

    raw = match.group(1).strip()
    # rimuovi eventuali fence markdown ```json ... ```
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw).strip()

    data = None
    for cand in (raw, re.sub(r',\s*([}\]])', r'\1', raw)):  # 2o tentativo: togli trailing commas
        try:
            data = json.loads(cand)
            break
        except json.JSONDecodeError:
            continue

    if data is None:
        print(f"\U0001F534 F-06: comparatore JSON non parsabile, NON mostrato. Contenuto: {raw[:200]}")
        return None

    # Validazione forma attesa dal frontend (formatComparisonTable):
    # richiede 'prodotti' (lista) e 'attributi' (lista). Senza, il frontend
    # renderizzerebbe un contenitore vuoto -> meglio scartare in modo pulito.
    if not isinstance(data, dict) or not data.get('prodotti') or not isinstance(data.get('attributi'), list):
        chiavi = list(data.keys()) if isinstance(data, dict) else type(data).__name__
        print(f"\U0001F534 F-06: comparatore forma inattesa (manca prodotti/attributi), scartato. Chiavi: {chiavi}")
        return None

    return data


def parse_claude_response(response_text: str) -> tuple:
    """
    Parsea risposta Claude nel formato XML in modo robusto.

    Obiettivi F-06 (niente rotture silenziose sul comparatore):
    - Il testo mostrato all'utente non deve MAI contenere tag strutturali
      (<risposta>/<prodotti>/<comparatore>), nemmeno se manca il wrapper
      <risposta> o se la risposta viene troncata a meta' tag.
    - Il comparatore non deve sparire in silenzio: JSON malformato o troncato
      viene loggato in modo evidente e, se recuperabile, riparato.

    Returns:
        (testo_risposta, lista_id_prodotti, comparator_data)
    """
    try:
        # DEBUG - stampa risposta completa
        print("\n" + "="*80)
        print("RAW CLAUDE RESPONSE:")
        print(response_text)
        print("="*80 + "\n")

        # 1) TESTO RISPOSTA
        risposta_match = re.search(r'<risposta>(.*?)</risposta>', response_text, re.DOTALL)
        if risposta_match:
            text = risposta_match.group(1).strip()
        else:
            # Wrapper mancante: usa tutto il testo ma rimuovi i blocchi strutturali
            # (anche se troncati / non chiusi) per non far trapelare tag "fantasma".
            text = response_text
            text = re.sub(r'<prodotti>.*?</prodotti>', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<comparatore>.*?</comparatore>', '', text, flags=re.DOTALL | re.IGNORECASE)
            # blocchi aperti e non chiusi (troncamento): butta via dal tag in poi
            text = re.sub(r'<prodotti>.*$', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<comparatore>.*$', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'</?risposta>', '', text, flags=re.IGNORECASE).strip()
            print("\u26A0\uFE0F F-06: wrapper <risposta> assente, testo ripulito dai tag strutturali")

        # Belt-and-suspenders: nessun tag noto deve restare nel testo mostrato
        text = re.sub(r'</?(?:risposta|prodotti|comparatore)>', '', text, flags=re.IGNORECASE).strip()

        # Rimuovi IDs prodotti dal testo se Claude li ha messi per errore in coda
        text = re.sub(r'[a-z0-9]+-[a-z0-9]+-[a-z0-9-]+(?:,[a-z0-9]+-[a-z0-9]+-[a-z0-9-]+)*$', '', text, flags=re.IGNORECASE).strip()

        # 2) IDS PRODOTTI
        prodotti_match = re.search(r'<prodotti>(.*?)</prodotti>', response_text, re.DOTALL)
        if prodotti_match:
            ids_string = prodotti_match.group(1).strip()
            product_ids = [i.strip() for i in ids_string.split(',') if i.strip()] if ids_string else []
        else:
            product_ids = []

        # 3) COMPARATORE (robusto: no rottura silenziosa)
        comparator_data = _parse_comparator_block(response_text)

        return text, product_ids, comparator_data

    except Exception as e:
        print(f"\u26A0\uFE0F Errore parsing risposta Claude: {e}")
        import traceback
        traceback.print_exc()
        # Ultima spiaggia: non mostrare mai i tag grezzi all'utente
        safe = re.sub(r'</?(?:risposta|prodotti|comparatore)>', '', response_text, flags=re.IGNORECASE).strip()
        return safe, [], None


def clean_product_description(product: Dict) -> str:
    """
    Pulisce e prepara descrizione prodotto per visualizzazione
    Limita a ~280 caratteri evitando troncamenti innaturali
    """
    desc = product.get('descrizione', '')
    
    # Rimuovi HTML tags
    desc_clean = re.sub(r'<[^>]+>', '', desc)
    
    # Rimuovi multipli spazi/newline
    desc_clean = re.sub(r'\s+', ' ', desc_clean).strip()
    
    # Tronca intelligentemente
    if len(desc_clean) > 280:
        # Cerca punto/virgola/newline naturale entro 350 caratteri
        cutoff = desc_clean.rfind('.', 200, 350)
        if cutoff == -1:
            cutoff = desc_clean.rfind(',', 200, 350)
        if cutoff == -1:
            cutoff = desc_clean.rfind('\n', 200, 350)
        
        if 200 < cutoff < 350:
            desc_clean = desc_clean[:cutoff + 1]
        else:
            desc_clean = desc_clean[:280].strip() + '...'
    
    # Fallback se ancora vuota o troppo corta
    if len(desc_clean) < 20:
        desc_clean = f"{product.get('categoria', 'Prodotto')} STIGA di alta qualità."
    
    return desc_clean


# ═══════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════

@app.route('/')
@auth.login_required
def index():
    """Pagina principale"""
    return render_template('index.html')


@app.route('/widget')
@auth.login_required
def widget():
    """Versione widget per embed in iframe"""
    return render_template('widget.html')


@app.route('/api/chat', methods=['POST'])
@auth.login_required
def chat():
    """Endpoint principale per chat con l'assistente"""
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Log query utente (con session hash per privacy)
    session_hash = hashlib.md5(session_id.encode()).hexdigest()[:8]
    language = data.get('language', 'it')
    analytics_tracker.log_query(session_id=session_hash, query=user_message, language=language)
    query_logger.info(json.dumps({
        'type': 'query',
        'timestamp': datetime.now().isoformat(),
        'session': session_hash,
        'query': user_message,
        'query_length': len(user_message)
    }, ensure_ascii=False))
    
    try:
        # 1. Recupera storia conversazione
        session = _get_session(session_id)
        history = session['history']
        
        # 2. Rileva richiesta di confronto con prodotti precedenti
        confronto_keywords = ['confronta', 'confrontali', 'confronto', 'mettili a confronto', 
                             'compare', 'comparison', 'vs', 'differenz', 'quale scegliere',
                             'quale mi consigli tra', 'meglio tra']
        is_confronto = any(kw in user_message.lower() for kw in confronto_keywords)
        use_previous_products = False
        
        if is_confronto and session.get('last_products'):
            # Verifica se l'utente si riferisce ai prodotti precedenti
            # (non specifica nuovi modelli nella richiesta)
            new_model_match = MODELLO_PATTERN.search(user_message)
            if not new_model_match:
                use_previous_products = True
                print(f"🔄 Confronto richiesto - uso prodotti precedenti: {session['last_products']}")
        # F-26: follow-up senza nuove info -> riusa i prodotti precedenti ed evita la deriva.
        # Guardia (fix refuso 'taglierba'): NON riusare se e' una richiesta di catalogo/browse
        # o se cita una categoria (anche con refusi) -> altrimenti resta appeso ai prodotti confrontati.
        _msg_low = user_message.lower()
        if (not use_previous_products and session.get('last_products')
                and not MODELLO_PATTERN.search(user_message)
                and not extract_categoria([{'role': 'user', 'content': user_message}])
                and not DIMENSIONI_PATTERN.search(user_message)
                and not ALIMENTAZIONE_PATTERN.search(user_message)
                and not ACCESSORIO_PATTERN.search(user_message)
                and not any(_k in _msg_low for _k in ('tutti', 'tutte', 'mostrami', 'mostra', 'fai vedere', 'fammi vedere', 'vedere', 'elenca', 'gamma', 'quali sono'))
                and not any(_c in _msg_low for _c in ('robot', 'trattorin', 'tagli', 'decespugli', 'motoseg', 'tagliasiep', 'idropulit', 'soffiator', 'spazzaneve', 'motozapp', 'biotritur', 'arieggiat', 'forbici'))):
            use_previous_products = True
        # 3. Arricchisci query con contesto conversazionale
        # Includi messaggio corrente nella storia per extract_categoria
        current_history = history + [{'role': 'user', 'content': user_message}]
        enriched_query = build_enriched_query(user_message, current_history)
        
        # 4. Estrai requisiti per creare filtri
        requirements = matcher.extract_requirements(enriched_query)
        
        # 5. Retrieval o uso prodotti precedenti
        if use_previous_products:
            # Usa i prodotti mostrati in precedenza per il confronto
            reranked = []
            for pid in session['last_products']:
                product = retriever.get_product_by_id(pid)
                if product:
                    reranked.append((product, 1.0, ['confronto_richiesto']))
            print(f"📦 Uso {len(reranked)} prodotti precedenti per confronto")
        elif MODELLO_PATTERN.search(user_message):
            # Modello specifico nominato (confronto o singolo) -> ricerca diretta per nome
            # (evita la confusione semantica tra codici simili, es. A 1000 vs A 100v)
            print("\U0001F3AF Modello specifico rilevato - ricerca diretta per nome")
            reranked = search_products_by_name(user_message, retriever)
            if not reranked:
                print("⚠️ Ricerca diretta fallita, uso retrieval semantico")
                # Fallback a retrieval normale
                filters = {}
                if 'categoria' in requirements:
                    cat = requirements['categoria']
                    filters['categoria'] = CATEGORIA_MAPPING.get(cat.lower(), cat)
                products_with_scores = retriever.search(enriched_query, top_k=20, filters=filters)
                reranked = matcher.rerank_products(products_with_scores, enriched_query)
        else:
            # Flusso normale: retrieval + reranking
            filters = {}
            if 'categoria' in requirements:
                cat = requirements['categoria']
                filters['categoria'] = CATEGORIA_MAPPING.get(cat.lower(), cat)
                print(f"🔍 Filtro categoria attivo: {filters['categoria']}")
            
            products_with_scores = retriever.search(enriched_query, top_k=20, filters=filters)
            print(f"📦 Trovati {len(products_with_scores)} prodotti dal retriever")
            
            reranked = matcher.rerank_products(products_with_scores, enriched_query)

        # Rileva modalità mostra tutti
        # IMPORTANTE: usa extract_categoria direttamente, non requirements (che può essere vuoto)
        current_history_with_msg = history + [{'role': 'user', 'content': user_message}]
        detected_category_raw = extract_categoria(current_history_with_msg)
        print(f"🔍 DEBUG detected_category from extract_categoria: {detected_category_raw}")
        
        # Normalizza categoria per frontend (trattorino → Trattorini da giardino)
        detected_category = None
        if detected_category_raw:
            detected_category = CATEGORIA_MAPPING.get(detected_category_raw.lower(), detected_category_raw)
            print(f"🔍 DEBUG detected_category MAPPED: {detected_category}")
        show_all = detect_show_all_intent(user_message, detected_category)
        products_limit = 20 if show_all else 10

        # F-33 Guardrail scope: blocca il fuori-tema PRIMA di generare (nessuna chiamata al modello per l'off-topic)
        _scope = evaluate_scope(
            user_message, detected_category_raw, use_previous_products,
            bool(MODELLO_PATTERN.search(user_message)), claude.classify_scope
        )
        if _scope != 'ok':
            _canned = SCOPE_BLOCK_MSG if _scope == 'block' else SCOPE_DEFLECT_MSG
            print(f"\U0001F6E1 F-33 scope={_scope} -> risposta canned, nessuna generazione")
            session['history'].append({'role': 'user', 'content': user_message})
            session['history'].append({'role': 'assistant', 'content': _canned})
            _save_session(session_id, session)
            return jsonify({
                'response': _canned, 'products': [], 'comparator': None,
                'total_count': 0, 'category': None, 'show_all': False
            })
        
        print(f"🎯 Top 10 dopo re-ranking:")
        for i, (prod, score, reasons) in enumerate(reranked[:products_limit], 1):
            print(f"   {i}. {prod.get('nome')} (ID: {prod.get('id')}) - Score: {score:.3f}")
        
        # 6. Se show_all, bypassa Claude e mostra tutti
        if show_all:
            # Modalità catalogo: mostra TUTTI i prodotti senza filtro Claude
            selected_product_ids = [prod[0]['id'] for prod in reranked[:products_limit]]
            response_text = f"Ecco tutti i prodotti disponibili ({len(selected_product_ids)}):"
            comparator_data = None
            print(f"📋 Modalità CATALOGO: mostro tutti i {len(selected_product_ids)} prodotti")
        else:
            # 6. Prepara contesto per Claude (top 10 prodotti)
            products_context = claude.format_products_for_context(reranked[:products_limit])
            
            # 7. Genera risposta (Claude riceve prodotti come contesto)
            raw_response = claude.chat(
                user_message,
                conversation_history=history,
                products_context=products_context
            )
            
            # 8. Parsea risposta per estrarre testo, IDs prodotti e comparatore
            response_text, selected_product_ids, comparator_data = parse_claude_response(raw_response)
        
        print(f"💬 Risposta Claude: {response_text[:100]}...")
        print(f"🏷️  Prodotti selezionati da Claude: {selected_product_ids}")
        
        # 9. Aggiorna storia (salva solo testo pulito)
        session['history'].append({
            'role': 'user',
            'content': user_message
        })
        session['history'].append({
            'role': 'assistant',
            'content': response_text
        })
        
        # 10. Salva i prodotti mostrati per confronti futuri
        if selected_product_ids:
            session['last_products'] = selected_product_ids

        # F-02: persisti lo stato sessione (Postgres con fallback in memoria)
        _save_session(session_id, session)
        
        # 11. Prepara prodotti per il frontend (SOLO quelli selezionati da Claude)
        products_data = []
        
        if selected_product_ids:
            # Crea mappa ID → prodotto
            products_map = {prod.get('id'): (prod, score, reasons) for prod, score, reasons in reranked[:products_limit]}
            
            # Aggiungi solo i prodotti selezionati da Claude, nell'ordine specificato
            for product_id in selected_product_ids:
                if product_id in products_map:
                    product, score, reasons = products_map[product_id]
                    
                    # Estrai specifiche importanti
                    specs_dict = {}
                    specs = product.get('specifiche_tecniche', {})
                    
                    important_keys = [
                        'Area di taglio fino a',
                        'Alimentazione', 
                        'Capacità batteria',
                        'Pendenza massima',
                        'Larghezza di taglio',
                        'Tempo massimo di taglio per ciclo'
                    ]
                    
                    for key in important_keys:
                        value = specs.get(key) or specs.get(f'Specifiche tecniche - {key}')
                        if value:
                            specs_dict[key] = value
                    
                    # Gestione immagini
                    immagini = product.get('immagini', [])
                    image_url = immagini[0] if immagini else "/static/images/stiga-robot.webp"
                    
                    # Estrai descrizione pulita
                    descrizione_display = clean_product_description(product)
                    
                    products_data.append({
                        'id': product.get('id'),
                        'nome': product.get('nome'),
                        'categoria': product.get('categoria', ''),
                        'descrizione': descrizione_display,
                        'prezzo': product.get('prezzo', 'Contattaci'),
                        'prezzo_originale': product.get('prezzo_originale', ''),
                        'url': product.get('url', ''),
                        'image_url': image_url,
                        'score': float(round(score, 2)),
                        'specs': specs_dict
                    })
                else:
                    print(f"⚠️ Prodotto {product_id} selezionato da Claude ma non trovato nella top 10")
        
        print(f"📦 Invio {len(products_data)} prodotti al frontend\n")
        
        # Prepara dati per tracking
        product_ids = [p.get('id', '') for p in products_data]
        product_names = [p['nome'] for p in products_data]
        categories = [p['categoria'] for p in products_data if p.get('categoria')]
        
        # Log risultati (file log)
        query_logger.info(json.dumps({
            'type': 'results',
            'timestamp': datetime.now().isoformat(),
            'session': session_hash,
            'products_count': len(products_data),
            'top_products': product_names[:5],
            'categories': list(set(categories)),
            'has_comparison': comparator_data is not None
        }, ensure_ascii=False))
        
        # Log risultati (database) - UNICA chiamata con product_names
        analytics_tracker.log_results(
            session_id=session_hash,
            products_count=len(products_data),
            products_shown=product_ids,
            product_names=product_names,
            categories=categories,
            has_comparison=(comparator_data is not None)
        )
        
        # Fase 1 orchestrante: se intento di confronto e 2-3 prodotti mostrati, apri il comparatore deterministico
        _action = None
        if ORCHESTRATE_COMPARISON and is_confronto and 2 <= len(products_data) <= 3:
            _action = {'type': 'confronta', 'products': [{'id': p['id']} for p in products_data]}
            print(f"\U0001F9ED Fase1 orchestrante: confronto deterministico su {len(products_data)} prodotti")

        return jsonify({
            'response': response_text,
            'products': products_data,
            'comparator': comparator_data,
            'total_count': len(reranked) if reranked else 0,
            'category': detected_category,
            'show_all': show_all,
            'action': _action
        })
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        
        # Log errore con analytics_tracker
        analytics_tracker.log_error(
            session_id=session_hash,
            error_message=str(e),
            error_type=type(e).__name__
        )
        import traceback
        traceback.print_exc()
        
        # Log errore (file log)
        query_logger.info(json.dumps({
            'type': 'error',
            'timestamp': datetime.now().isoformat(),
            'session': session_hash,
            'error': str(e)
        }, ensure_ascii=False))
        
        return jsonify({'error': 'Errore interno del server'}), 500


@app.route('/api/track/click', methods=['POST'])
@auth.login_required  
def track_product_click():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        product_name = data.get('product_name')
        product_id = data.get('product_id', '')
        product_category = data.get('product_category', '')
        language = data.get('language', 'it')
        
        if not session_id or not product_name:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Hash session_id per privacy
        session_hash = hashlib.md5(session_id.encode()).hexdigest()[:8]
        
        success = analytics_tracker.log_product_click(
            session_id=session_hash,
            product_name=product_name,
            product_id=product_id,
            product_category=product_category,
            language=language
        )
        
        if success:
            return jsonify({'status': 'ok'})
        else:
            return jsonify({'status': 'error'}), 503
    except Exception as e:
        print(f"❌ Track click error: {e}")
        return jsonify({'error': 'Errore interno del server'}), 500

@app.route('/api/track/session', methods=['POST'])
@auth.login_required
def track_session_start():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        language = data.get('language', 'it')
        user_agent = request.headers.get('User-Agent')
        
        if not session_id:
            return jsonify({'error': 'Missing session_id'}), 400
        
        # Hash session_id per privacy
        session_hash = hashlib.md5(session_id.encode()).hexdigest()[:8]
        
        analytics_tracker.log_session_start(
            session_id=session_hash,
            language=language,
            user_agent=user_agent
        )
        return jsonify({'status': 'ok'})
    except Exception as e:
        print(f"❌ Track session error: {e}")
        return jsonify({'error': 'Errore interno del server'}), 500

@app.route('/api/categories', methods=['GET'])
@auth.login_required
def get_categories():
    """Ottieni tutte le categorie disponibili"""
    categories = retriever.get_all_categories()
    return jsonify({'categories': categories})


@app.route('/api/product/<product_id>', methods=['GET'])
@auth.login_required
def get_product(product_id):
    """Ottieni dettagli di un prodotto specifico"""
    product = retriever.get_product_by_id(product_id)
    if product:
        return jsonify(product)
    return jsonify({'error': 'Product not found'}), 404


if __name__ == '__main__':
    print(f"\n🌐 Avvio server su http://localhost:{PORT}")
    print(f"   Debug mode: {FLASK_DEBUG}")
    print(f"   Logs directory: {LOGS_DIR}")
    print(f"   🔒 Autenticazione attiva - Username: stiga")
    print(f"\n   Apri il browser e vai su http://localhost:{PORT}\n")
    app.run(debug=FLASK_DEBUG, port=PORT, host='0.0.0.0')
