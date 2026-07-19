"""
Session store (F-02 + F-07)
===========================
Stato conversazioni su PostgreSQL con TTL e fallback graceful in memoria.

Perche':
- F-02: prima lo stato viveva in un dizionario di processo -> memory leak nel
  tempo e stato NON condiviso tra worker/replica. Qui va su una tabella Postgres
  (condivisa) con scadenza (TTL) che risolve entrambe le cose.
- F-07: l'accesso al DB usa un pool di connessioni (psycopg2 ThreadedConnectionPool)
  con reconnect implicito: una connessione caduta viene scartata e ne viene creata
  una nuova, invece di fallire in silenzio.

Regola d'oro (path caldo della chat): qualunque problema col DB NON deve rompere
la conversazione. Ogni funzione, se il DB non risponde, ricade su un dizionario
in memoria -> nel caso peggiore ci si comporta come prima, senza errori all'utente.
"""

import os
import json
import threading
from contextlib import contextmanager

# --- Config ---------------------------------------------------------------
TTL_SECONDS = int(os.getenv('SESSION_TTL_SECONDS', 6 * 60 * 60))  # default 6 ore
_POOL_MIN = 1
_POOL_MAX = int(os.getenv('SESSION_POOL_MAX', 5))
_CLEANUP_EVERY = 50  # ogni N salvataggi elimina le righe scadute

# --- Stato modulo ---------------------------------------------------------
_pool = None
_pool_lock = threading.Lock()
_pool_failed = False          # se l'init del pool fallisce, non ritentiamo a raffica
_table_ready = False
_save_count = 0

_mem = {}                     # fallback in memoria
_mem_lock = threading.Lock()


def _default_session():
    return {'history': [], 'last_products': [], 'last_products_data': []}


# --- Pool / connessioni (F-07) -------------------------------------------
def _get_pool():
    """Ritorna il pool, creandolo una volta. None se DATABASE_URL manca o l'init fallisce."""
    global _pool, _pool_failed
    if _pool is not None:
        return _pool
    if _pool_failed:
        return None
    with _pool_lock:
        if _pool is not None:
            return _pool
        if _pool_failed:
            return None
        dsn = os.getenv('DATABASE_URL')
        if not dsn:
            _pool_failed = True
            print("⚠️ F-02 session_store: DATABASE_URL assente -> uso fallback in memoria")
            return None
        try:
            from psycopg2.pool import ThreadedConnectionPool
            _pool = ThreadedConnectionPool(_POOL_MIN, _POOL_MAX, dsn)
            print("✅ F-02 session_store: pool Postgres pronto")
        except Exception as e:
            _pool_failed = True
            print(f"❌ F-02 session_store: init pool fallito ({e}) -> fallback in memoria")
            return None
    return _pool


@contextmanager
def _cursor():
    """Context manager: connessione dal pool, commit/rollback, restituzione al pool.
    Su errore la connessione viene scartata (close=True) cosi' il pool ne ricrea una
    sana al giro dopo -> reconnect implicito (F-07)."""
    pool = _get_pool()
    if pool is None:
        raise RuntimeError('no pool')
    conn = pool.getconn()
    cur = None
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        # connessione potenzialmente compromessa: scartala
        try:
            if cur is not None:
                cur.close()
        except Exception:
            pass
        try:
            pool.putconn(conn, close=True)
        except Exception:
            pass
        conn = None
        raise
    finally:
        if conn is not None:
            try:
                if cur is not None:
                    cur.close()
            except Exception:
                pass
            try:
                pool.putconn(conn)
            except Exception:
                pass


def _ensure_table():
    global _table_ready
    if _table_ready:
        return
    with _cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                session_id  TEXT PRIMARY KEY,
                data        JSONB NOT NULL,
                updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
            )
        """)
    _table_ready = True


# --- API pubblica ---------------------------------------------------------
def get_session(session_id):
    """Ritorna il dict di sessione (history / last_products / last_products_data).
    Se manca o e' scaduto ritorna un default nuovo. Mai solleva: su errore DB
    ricade sulla copia in memoria."""
    try:
        _ensure_table()
        with _cursor() as cur:
            cur.execute(
                "SELECT data FROM conversation_sessions "
                "WHERE session_id = %s AND updated_at > now() - make_interval(secs => %s)",
                (session_id, TTL_SECONDS)
            )
            row = cur.fetchone()
        base = _default_session()
        if row and row[0]:
            data = row[0]
            if isinstance(data, str):
                data = json.loads(data)
            if isinstance(data, dict):
                base.update(data)
        return base
    except Exception as e:
        print(f"⚠️ F-02 session_store.get fallback memoria: {e}")
        with _mem_lock:
            existing = _mem.get(session_id)
            if existing is not None:
                base = _default_session()
                base.update(existing)
                return base
            return _default_session()


def save_session(session_id, data):
    """Salva/aggiorna la sessione con updated_at=now(). Occasionalmente ripulisce
    le righe scadute (TTL). Su errore DB salva in memoria e ritorna False."""
    global _save_count
    try:
        _ensure_table()
        payload = json.dumps(data, ensure_ascii=False)
        with _cursor() as cur:
            cur.execute(
                "INSERT INTO conversation_sessions (session_id, data, updated_at) "
                "VALUES (%s, %s::jsonb, now()) "
                "ON CONFLICT (session_id) DO UPDATE "
                "SET data = EXCLUDED.data, updated_at = now()",
                (session_id, payload)
            )
            _save_count += 1
            if _save_count % _CLEANUP_EVERY == 0:
                cur.execute(
                    "DELETE FROM conversation_sessions "
                    "WHERE updated_at < now() - make_interval(secs => %s)",
                    (TTL_SECONDS,)
                )
        # mirror in memoria: se piu' avanti il DB cade, non perdiamo del tutto lo stato caldo
        with _mem_lock:
            _mem[session_id] = data
        return True
    except Exception as e:
        print(f"⚠️ F-02 session_store.save fallback memoria: {e}")
        with _mem_lock:
            _mem[session_id] = data
        return False
