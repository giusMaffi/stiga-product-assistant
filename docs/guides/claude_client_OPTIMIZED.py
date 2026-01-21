"""
Claude API Client - OTTIMIZZATO con Prompt Caching + Top-20 + Suggerimenti Complementari
RISPARMIO COSTI: ~90% grazie a prompt caching
"""
import anthropic
from typing import List, Dict, Tuple
import json
from ..config import ANTHROPIC_API_KEY, MODEL_NAME, MAX_TOKENS, MODEL_TEMPERATURE


class ClaudeClient:
    """Client per interagire con Claude API con prompt caching"""
    
    def __init__(self):
        """Inizializza il client"""
        print("🔄 Inizializzazione Claude Client con Prompt Caching...")
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = MODEL_NAME
        
        # Carica catalogo completo per cache (lo fai solo 1 volta all'avvio)
        self._load_full_catalog()
        print("✅ Claude Client pronto con caching attivo!")
    
    def _load_full_catalog(self):
        """Carica catalogo completo per prompt caching"""
        from ..config import PRODUCTS_FILE
        
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            all_products = json.load(f)
        
        # Organizza per categoria per facilitare suggerimenti
        self.catalog_by_category = {}
        for product in all_products:
            cat = product.get('categoria', 'Altro')
            if cat not in self.catalog_by_category:
                self.catalog_by_category[cat] = []
            self.catalog_by_category[cat].append({
                'id': product.get('id'),
                'nome': product.get('nome'),
                'categoria': cat,
                'prezzo': product.get('prezzo')
            })
        
        # Crea rappresentazione testuale del catalogo (per cache)
        catalog_text = "CATALOGO COMPLETO STIGA (per suggerimenti complementari):\n\n"
        
        for categoria, prodotti in sorted(self.catalog_by_category.items()):
            catalog_text += f"### {categoria} ({len(prodotti)} prodotti)\n"
            for p in prodotti[:20]:  # Primi 20 per categoria per evitare troppo testo
                catalog_text += f"- {p['id']}: {p['nome']}"
                if p.get('prezzo'):
                    catalog_text += f" ({p['prezzo']})"
                catalog_text += "\n"
            catalog_text += "\n"
        
        self.full_catalog_text = catalog_text
        print(f"📚 Catalogo caricato: {len(all_products)} prodotti in {len(self.catalog_by_category)} categorie")
    
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
            # Handle sia tuple a 2 che a 3 elementi
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
        
        return json.dumps(products_for_context, ensure_ascii=False, indent=2)
    
    def chat(
        self,
        user_message: str,
        conversation_history: List[Dict] = None,
        products_context: str = None
    ) -> str:
        """
        Invia messaggio a Claude CON PROMPT CACHING
        
        Args:
            user_message: Messaggio utente
            conversation_history: Storia conversazione
            products_context: Contesto prodotti TOP-20 (JSON)
        
        Returns:
            Risposta di Claude
        """
        # ══════════════════════════════════════════════════════════════════════
        # SYSTEM PROMPT CON PROMPT CACHING
        # Il catalogo completo viene cachato per 5 minuti (cache ephemeral)
        # Costo: $3.75/M per write, poi $0.30/M per read (10x meno!)
        # ══════════════════════════════════════════════════════════════════════
        
        system_prompt_parts = [
            {
                "type": "text",
                "text": """Sei un esperto consulente STIGA, azienda italiana leader nel giardinaggio dal 1934.

Il tuo ruolo è CONSULTIVO: comprendi le esigenze del cliente attraverso domande mirate, poi consigli 2-3 prodotti adatti.

═══════════════════════════════════════════════════════════════════
⚠️ REGOLA ANTI-ALLUCINAZIONE - CRITICO
═══════════════════════════════════════════════════════════════════

🚨 NON INVENTARE MAI PRODOTTI O ACCESSORI CHE NON SONO NEI RISULTATI DI RICERCA!

REGOLE ASSOLUTE:
1. Se la ricerca restituisce prodotti NON RILEVANTI alla richiesta → DI CHIARAMENTE che non hai trovato quello che cerca
2. NON descrivere prodotti generici, ipotetici o non presenti nel catalogo
3. NON inventare accessori, caratteristiche o specifiche

ESEMPI:
❌ SBAGLIATO: Utente chiede "accessori neve" → ricevi "trattorini" → descrivi "spazzola spazzaneve, lama neve, catene"
✅ CORRETTO: Utente chiede "accessori neve" → ricevi "trattorini" → rispondi "Mi dispiace, non ho trovato accessori per la neve nel catalogo STIGA disponibile. Posso aiutarti con altri prodotti?"

═══════════════════════════════════════════════════════════════════
📋 GESTIONE RICHIESTE CONFRONTO
═══════════════════════════════════════════════════════════════════

Se l'utente chiede di confrontare prodotti che hai già mostrato (es: "confronta i due robot", "differenze tra questi"):
1. Usa il tag <confronto>true</confronto> nella risposta
2. Descrivi le differenze chiave tra i prodotti già mostrati
3. NON fare nuova ricerca, lavora su prodotti già presentati

═══════════════════════════════════════════════════════════════════
💡 SUGGERIMENTI COMPLEMENTARI
═══════════════════════════════════════════════════════════════════

DOPO aver risposto alla query principale con i prodotti rilevanti:
1. Suggerisci 1-2 prodotti COMPLEMENTARI dal catalogo completo sotto
2. Usa la frase: "💡 Potrebbe interessarti anche:"
3. Scegli prodotti che completano l'acquisto principale

ESEMPI DI COMPLEMENTARI:
- Rasaerba elettrico → Prolunga elettrica, sacchi raccolta
- Robot tagliaerba → Garage robot, filo perimetrale
- Decespugliatore → Occhiali protezione, filo ricambio
- Trattorino → Copertura protezione, kit mulching

REGOLE SUGGERIMENTI:
- Solo se hai trovato prodotti rilevanti alla query principale
- Max 2 suggerimenti complementari
- Scegli dalla categoria appropriata del catalogo sotto
- Menziona brevemente perché sono utili

═══════════════════════════════════════════════════════════════════
📝 FORMATO RISPOSTA
═══════════════════════════════════════════════════════════════════

<risposta>
[Testo conversazionale naturale con consigli]

💡 Potrebbe interessarti anche:
- [Prodotto complementare 1]: [breve spiegazione utilità]
- [Prodotto complementare 2]: [breve spiegazione utilità]
</risposta>

<prodotti>
[Lista ID prodotti consigliati, separati da virgola]
</prodotti>

<confronto>false</confronto>"""
            },
            {
                "type": "text",
                "text": self.full_catalog_text,
                "cache_control": {"type": "ephemeral"}  # ← QUESTO VIENE CACHATO! ✨
            }
        ]
        
        # ══════════════════════════════════════════════════════════════════════
        # MESSAGES (NON cachati - fresh ogni volta)
        # ══════════════════════════════════════════════════════════════════════
        
        messages = []
        
        # Aggiungi storia conversazione
        if conversation_history:
            messages.extend(conversation_history)
        
        # Aggiungi messaggio corrente con TOP-20 PRODOTTI
        if products_context:
            content = f"""Messaggio utente: {user_message}

TOP 20 PRODOTTI RILEVANTI ALLA QUERY (già ranked per rilevanza semantica):
{products_context}

ISTRUZIONI:
1. Analizza questi 20 prodotti
2. Scegli i migliori 2-3 per la richiesta specifica dell'utente
3. Rispondi in modo consultivo
4. Aggiungi 1-2 suggerimenti complementari dal catalogo completo sopra
5. Usa gli ID COMPLETI esatti dal JSON sopra nel tag <prodotti>"""
        else:
            content = user_message
        
        messages.append({
            'role': 'user',
            'content': content
        })
        
        # ══════════════════════════════════════════════════════════════════════
        # API CALL CON PROMPT CACHING
        # ══════════════════════════════════════════════════════════════════════
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=MAX_TOKENS,
            temperature=MODEL_TEMPERATURE,
            system=system_prompt_parts,  # ← Array con cache control!
            messages=messages
        )
        
        # Log usage per monitoraggio costi
        usage = response.usage
        print(f"📊 Token usage:")
        print(f"   Input (no cache): {usage.input_tokens}")
        print(f"   Input (cache write): {getattr(usage, 'cache_creation_input_tokens', 0)}")
        print(f"   Input (cache read): {getattr(usage, 'cache_read_input_tokens', 0)}")
        print(f"   Output: {usage.output_tokens}")
        
        # Calcola risparmio
        cache_read = getattr(usage, 'cache_read_input_tokens', 0)
        if cache_read > 0:
            saving = cache_read * 2.7 / 1000  # differenza tra $3 e $0.30 per 1k tokens
            print(f"   💰 Risparmio da cache: ~${saving:.4f}")
        
        # Estrai testo risposta
        return response.content[0].text
