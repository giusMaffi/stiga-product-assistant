"""
Claude API Client with Prompt Caching + Streaming Support + Cost Tracking
"""
import anthropic
from typing import List, Dict, Tuple, Iterator
from ..config import ANTHROPIC_API_KEY, MODEL_NAME, MAX_TOKENS, MODEL_TEMPERATURE, SYSTEM_PROMPT
import csv
from datetime import datetime
from pathlib import Path


class ClaudeClient:
    """Client per interagire con Claude API"""
    
    def __init__(self):
        """Inizializza il client"""
        print("🔄 Inizializzazione Claude Client...")
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = MODEL_NAME
        
        # Setup CSV logging per costi
        self.logs_dir = Path(__file__).parent.parent.parent / 'logs'
        self.logs_dir.mkdir(exist_ok=True)
        self.token_log_path = self.logs_dir / 'token_usage.csv'
        
        # Crea CSV se non esiste
        if not self.token_log_path.exists():
            with open(self.token_log_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'endpoint', 'input_tokens', 'cached_tokens', 
                    'output_tokens', 'cost_usd', 'cost_input', 'cost_cached', 'cost_output'
                ])
        
        print("✅ Claude Client pronto!")
    
    def _log_token_usage(self, endpoint: str, input_tokens: int, cached_tokens: int, output_tokens: int):
        """Salva usage tokens e calcola costi"""
        # Pricing Claude Sonnet 4 (per 1M tokens)
        PRICE_INPUT = 3.00
        PRICE_CACHED = 0.30
        PRICE_OUTPUT = 15.00
        
        # Calcola costi
        cost_input = (input_tokens / 1_000_000) * PRICE_INPUT
        cost_cached = (cached_tokens / 1_000_000) * PRICE_CACHED
        cost_output = (output_tokens / 1_000_000) * PRICE_OUTPUT
        cost_total = cost_input + cost_cached + cost_output
        
        # Salva in CSV
        try:
            with open(self.token_log_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    endpoint,
                    input_tokens,
                    cached_tokens,
                    output_tokens,
                    f"{cost_total:.6f}",
                    f"{cost_input:.6f}",
                    f"{cost_cached:.6f}",
                    f"{cost_output:.6f}"
                ])
        except Exception as e:
            print(f"⚠️ Errore log token usage: {e}")
    
    def format_products_for_context(self, products_with_scores: List[Tuple]) -> str:
        """Formatta prodotti per Claude - SOLO campi essenziali"""
        products_for_context = []
        ESSENTIAL = [
            # UNIVERSALI (tutti i prodotti)
            'Alimentazione',
            'Peso prodotto',
            'Larghezza prodotto',
            'Lunghezza prodotto',
            
            # ROBOT TAGLIAERBA
            'Area di taglio fino a',
            'Capacità batteria',
            'Altezze di taglio',
            'Pendenza massima',
            'Larghezza di taglio',
            'Tempo massimo di taglio per ciclo',
            
            # TRATTORINI
            'Cilindrata',
            'Capacità sacco raccolta',
            'Area di taglioinfo_outline',
            'Brand motore',
            'Capacità serbatoio carburante',
            'Numero di marce avanti',
            
            # DECESPUGLIATORI
            'Capacità batteria (consigliata)',
            'Capacità serbatoio carburante',
            'Diametro filo di nylon (millimetri)',
            'Cilindrata',
            'Avviamento',
            
            # TAGLIAERBA
            'Capacità sacco raccolta',
            'Altezze di taglio',
            'Avanzamento',
            'Cilindrata',
            'Capacità batteria',
            
            # ALTRI
            'Potenza',
            'Velocità dell\'aria',
            'Pressione',
            'Larghezza di taglio'
        ]
        
        for item in products_with_scores:
            if len(item) == 2:
                product, score = item
            else:
                product, score, _ = item
            
            all_specs = product.get('specifiche_tecniche', {})
            specs = {}
            for k in ESSENTIAL:
                v = all_specs.get(k) or all_specs.get(f'Specifiche tecniche - {k}')
                if v:
                    specs[k] = v
            
            desc = product.get('descrizione', '')
            
            products_for_context.append({
                'id': product.get('id'),
                'nome': product.get('nome'),
                'categoria': product.get('categoria'),
                'descrizione': desc[:150] + '...' if len(desc) > 150 else desc,
                'prezzo': product.get('prezzo'),
                'specifiche': specs
            })
        
        import json
        return json.dumps(products_for_context, ensure_ascii=False, indent=2)
    
    def chat(
        self,
        user_message: str,
        conversation_history: List[Dict] = None,
        products_context: str = None
    ) -> str:
        """
        Invia messaggio a Claude con prompt caching
        
        Args:
            user_message: Messaggio utente
            conversation_history: Storia conversazione
            products_context: Contesto prodotti (JSON)
        
        Returns:
            Risposta di Claude
        """
        # Prepara messaggi
        messages = []
        
        # Aggiungi storia
        if conversation_history:
            messages.extend(conversation_history)
        
        # Aggiungi messaggio corrente con contesto prodotti
        if products_context:
            content = f"""Messaggio utente: {user_message}

DATABASE PRODOTTI RILEVANTI:
{products_context}

RICORDA: Usa gli ID COMPLETI esatti dal JSON sopra nel tag <prodotti>."""
        else:
            content = user_message
        
        messages.append({
            'role': 'user',
            'content': content
        })
        
        # PROMPT CACHING: System prompt viene cachato
        response = self.client.messages.create(
            model=self.model,
            max_tokens=MAX_TOKENS,
            temperature=MODEL_TEMPERATURE,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=messages
        )
        
        # Log usage per monitoring
        usage = response.usage
        input_tokens = usage.input_tokens
        cached_tokens = getattr(usage, 'cache_read_input_tokens', 0)
        output_tokens = usage.output_tokens
        
        print(f"📊 Tokens - Input: {input_tokens} | Cached: {cached_tokens} | Output: {output_tokens}")
        
        # Salva in CSV per analisi costi
        self._log_token_usage('chat', input_tokens, cached_tokens, output_tokens)
        
        return response.content[0].text
    
    def stream_chat(
        self,
        user_message: str,
        conversation_history: List[Dict] = None,
        products_context: str = None
    ) -> Iterator[str]:
        """
        Invia messaggio a Claude con STREAMING
        
        Args:
            user_message: Messaggio utente
            conversation_history: Storia conversazione
            products_context: Contesto prodotti (JSON)
        
        Yields:
            Chunks di testo progressivi
        """
        # Prepara messaggi (stesso di chat())
        messages = []
        
        if conversation_history:
            messages.extend(conversation_history)
        
        if products_context:
            content = f"""Messaggio utente: {user_message}

DATABASE PRODOTTI RILEVANTI:
{products_context}

RICORDA: Usa gli ID COMPLETI esatti dal JSON sopra nel tag <prodotti>."""
        else:
            content = user_message
        
        messages.append({
            'role': 'user',
            'content': content
        })
        
        # STREAMING con prompt caching
        with self.client.messages.stream(
            model=self.model,
            max_tokens=MAX_TOKENS,
            temperature=MODEL_TEMPERATURE,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=messages
        ) as stream:
            for text in stream.text_stream:
                yield text
        
        # Log finale
        final_message = stream.get_final_message()
        usage = final_message.usage
        input_tokens = usage.input_tokens
        cached_tokens = getattr(usage, 'cache_read_input_tokens', 0)
        output_tokens = usage.output_tokens
        
        print(f"📊 Streaming Tokens - Input: {input_tokens} | Cached: {cached_tokens} | Output: {output_tokens}")
        
        # Salva in CSV per analisi costi
        self._log_token_usage('stream', input_tokens, cached_tokens, output_tokens)
