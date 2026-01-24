"""
Claude API Client with Prompt Caching
"""
import anthropic
from typing import List, Dict, Tuple
from ..config import ANTHROPIC_API_KEY, MODEL_NAME, MAX_TOKENS, MODEL_TEMPERATURE, SYSTEM_PROMPT

class ClaudeClient:
    """Client per interagire con Claude API"""
    
    def __init__(self):
        """Inizializza il client"""
        print("🔄 Inizializzazione Claude Client...")
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = MODEL_NAME
        print("✅ Claude Client pronto!")
    
    def format_products_for_context(self, products_with_scores: List[Tuple]) -> str:
        """
        Formatta prodotti per il contesto di Claude
        
        Args:
            products_with_scores: Lista di tuple (product, score, reasons)
        
        Returns:
            Stringa JSON formattata
        """
        products_for_context = []
        
        for item in products_with_scores:
            if len(item) == 2:
                product, score = item
                reasons = []
            else:
                product, score, reasons = item
            
            products_for_context.append({
                'id': product.get('id'),
                'nome': product.get('nome'),
                'categoria': product.get('categoria'),
                'descrizione': product.get('descrizione'),
                'prezzo': product.get('prezzo'),
                'specifiche_tecniche': product.get('specifiche_tecniche', {}),
                'url': product.get('url'),
                'score': float(round(score, 3))
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
        print(f"📊 Tokens - Input: {usage.input_tokens} | Cached: {getattr(usage, 'cache_read_input_tokens', 0)} | Output: {usage.output_tokens}")
        
        return response.content[0].text
