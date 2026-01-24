"""
Analytics Tracking Module
Gestisce il tracking di tutti gli eventi su PostgreSQL
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any


class AnalyticsTracker:
    """Tracker per eventi analytics su PostgreSQL"""
    
    def __init__(self):
        """Inizializza connessione DB"""
        self.db_url = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
        if not self.db_url:
            print("⚠️ DATABASE_URL not found - analytics disabled")
            self.enabled = False
        else:
            self.enabled = True
            print("✅ Analytics Tracker initialized")
    
    def _get_connection(self):
        """Ottieni connessione PostgreSQL"""
        if not self.enabled:
            return None
        try:
            return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
        except Exception as e:
            print(f"⚠️ DB connection error: {e}")
            return None
    
    def _log_event(self, event_type: str, session_id: str, data: Dict[str, Any]) -> bool:
        """Log generico di un evento"""
        if not self.enabled:
            return False
        
        conn = self._get_connection()
        if not conn:
            return False
        
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO analytics_events (timestamp, session_id, event_type, data)
                VALUES (NOW(), %s, %s, %s)
            """, (session_id, event_type, json.dumps(data)))
            
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Analytics log error: {e}")
            if conn:
                conn.close()
            return False
    
    def log_query(self, session_id: str, query: str, language: str = 'it', **extra_data) -> bool:
        """Log query utente"""
        data = {
            'query': query,
            'query_length': len(query),
            'language': language,
            **extra_data
        }
        success = self._log_event('query', session_id, data)
        if success:
            print(f"📝 Logged query: {query[:50]}...")
        return success
    
    def log_results(self, session_id: str, products_count: int, products_shown: list, 
                   categories: list, has_comparison: bool = False, **extra_data) -> bool:
        """Log risultati mostrati"""
        data = {
            'products_count': products_count,
            'top_products': products_shown[:10],
            'categories': list(set(categories)),
            'has_comparison': has_comparison,
            **extra_data
        }
        success = self._log_event('results', session_id, data)
        if success:
            print(f"📊 Logged results: {products_count} products, {len(categories)} categories")
        return success
    
    def log_product_click(self, session_id: str, product_name: str, product_id: str,
                         product_category: str, language: str = 'it', **extra_data) -> bool:
        """Log click su prodotto"""
        data = {
            'product_name': product_name,
            'product_id': product_id,
            'product_category': product_category,
            'language': language,
            **extra_data
        }
        success = self._log_event('product_click', session_id, data)
        if success:
            print(f"🖱️ Logged click: {product_name}")
        return success
    
    def log_session_start(self, session_id: str, language: str = 'it', 
                         user_agent: Optional[str] = None, **extra_data) -> bool:
        """Log inizio sessione"""
        data = {'language': language, 'user_agent': user_agent, **extra_data}
        return self._log_event('session_start', session_id, data)
    
    def log_error(self, session_id: str, error_message: str, 
                 error_type: Optional[str] = None, **extra_data) -> bool:
        """Log errore"""
        data = {'error_message': error_message, 'error_type': error_type, **extra_data}
        return self._log_event('error', session_id, data)


# Istanza globale
_tracker = None

def get_tracker() -> AnalyticsTracker:
    """Ottieni istanza tracker (singleton)"""
    global _tracker
    if _tracker is None:
        _tracker = AnalyticsTracker()
    return _tracker
