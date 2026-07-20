"""
Guardrail scope (F-33)
======================
Tiene l'assistente dentro l'universo STIGA (prodotti a catalogo, Magazine,
giardinaggio). Policy: BLOCCO TOTALE di tutto cio' che e' fuori tema.

Disegno a strati (difesa in profondita'):
1. Gate deterministico (qui, ~gratis): follow-up su prodotti gia' mostrati o
   categoria/modello riconosciuti -> DENTRO senza chiamate extra; marca
   concorrente -> deviazione a STIGA.
2. Classificatore LLM: decide solo i casi non risolti dal fast-path (incluso
   il fuori-tema). Cosi' non serve tarare soglie numeriche rischiose.
3. (Backstop, altrove) prompt blindato + anti-allucinazione + validazione ID.

Regola prudenziale: in caso di errore tecnico del classificatore -> FAIL-OPEN
(non blocca), perche' un falso-blocco su una domanda legittima e' l'incidente
peggiore in demo; il prompt blindato resta come rete.
"""

# Marche concorrenti note (garden equipment). Escluse le marche-motore che
# possono comparire nelle specifiche STIGA (es. Honda) per non generare falsi
# positivi su domande legittime tipo "che motore monta?".
COMPETITORS = [
    'husqvarna', 'gardena', 'einhell', 'john deere', 'stihl', 'worx',
    'ryobi', 'karcher', 'kärcher', 'flymo', 'ambrogio', 'mcculloch',
    'bosch', 'greenworks', 'cub cadet',
]

SCOPE_BLOCK_MSG = (
    "Mi occupo esclusivamente di giardinaggio e prodotti STIGA. "
    "Posso aiutarti a scegliere un attrezzo o darti consigli per il tuo giardino: dimmi pure!"
)

SCOPE_DEFLECT_MSG = (
    "Mi occupo solo di prodotti STIGA, non di altre marche. "
    "Se vuoi ti mostro la soluzione STIGA piu' adatta alle tue esigenze: dimmi cosa ti serve!"
)


def evaluate_scope(user_message, category_detected, use_previous, model_named, classify_fn):
    """Ritorna 'ok' | 'block' | 'deflect'.

    Args:
        user_message: testo utente
        category_detected: categoria estratta dal messaggio (o None)
        use_previous: True se e' un follow-up sui prodotti gia' mostrati
        model_named: True se il messaggio nomina un modello specifico
        classify_fn: funzione (str)->bool, True se in-scope (classificatore LLM)
    """
    msg = (user_message or '').lower()

    # 1) follow-up su prodotti gia' mostrati -> sempre dentro
    if use_previous:
        return 'ok'

    # 2) marca concorrente -> deviazione a STIGA
    if any(c in msg for c in COMPETITORS):
        return 'deflect'

    # 3) fast-path DENTRO: categoria riconosciuta o modello nominato -> nessuna chiamata extra
    if category_detected or model_named:
        return 'ok'

    # 4) resto -> classificatore LLM (fail-open in caso di errore tecnico)
    try:
        return 'ok' if classify_fn(user_message) else 'block'
    except Exception as e:
        print(f"⚠️ F-33 classify error (fail-open): {e}")
        return 'ok'
