"""
Analytics Tracker - PostgreSQL Native (FIXED)
Gestisce tracking analytics su database PostgreSQL usando UNIFIED analytics_events table
"""
import psycopg2
from psycopg2.extras import RealDictCursor, Json
import os
from typing import Optional, List
from datetime import datetime

class AnalyticsTracker:
    """Tracker per analytics su PostgreSQL - UNIFIED EVENTS TABLE"""
    
    def __init__(self):
        """Inizializza connessione DB"""
        self.db_url = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
        
        if not self.db_url:
            print("⚠️ DATABASE_URL not found - analytics disabled")
            self.conn = None
            return
        
        try:
            self.conn = psycopg2.connect(self.db_url)
            print("✅ Analytics Tracker initialized")
        except Exception as e:
            print(f"❌ DB connection error: {e}")
            self.conn = None
    
    def log_query(self, session_id: str, query: str, language: str = 'it', query_index: int = None) -> bool:
        """Log query utente"""
        if not self.conn:
            return False
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO analytics_events (session_id, event_type, timestamp, data)
                VALUES (%s, %s, %s, %s)
            """, (
                session_id,
                'query',
                datetime.utcnow(),
                Json({
                    'query': query,
                    'language': language,
                    'query_index': query_index
                })
            ))
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"❌ Query log error: {e}")
            self.conn.rollback()
            return False
    
    def log_results(self, session_id: str, products_count: int, products_shown: list, 
                   product_names: list, categories: list, has_comparison: bool = False,
                   query_index: int = None) -> bool:
        """Log risultati mostrati"""
        if not self.conn:
            return False
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO analytics_events (session_id, event_type, timestamp, data)
                VALUES (%s, %s, %s, %s)
            """, (
                session_id,
                'results',
                datetime.utcnow(),
                Json({
                    'products_count': products_count,
                    'products_shown': products_shown,
                    'product_names': product_names,
                    'categories': categories,
                    'has_comparison': has_comparison,
                    'query_index': query_index
                })
            ))
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"❌ Results log error: {e}")
            self.conn.rollback()
            return False
    
    def log_product_click(self, session_id: str, product_name: str, 
                         product_id: str = '', product_category: str = '', 
                         language: str = 'it', query_index: int = None) -> bool:
        """Log click su prodotto"""
        if not self.conn:
            return False
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO analytics_events (session_id, event_type, timestamp, data)
                VALUES (%s, %s, %s, %s)
            """, (
                session_id,
                'product_click',
                datetime.utcnow(),
                Json({
                    'product_id': product_id,
                    'product_name': product_name,
                    'product_category': product_category,
                    'language': language,
                    'query_index': query_index
                })
            ))
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"❌ Click log error: {e}")
            self.conn.rollback()
            return False
    
    def log_session_start(self, session_id: str, language: str = 'it', user_agent: Optional[str] = None) -> bool:
        """Log inizio sessione"""
        if not self.conn:
            return False
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO analytics_events (session_id, event_type, timestamp, data)
                VALUES (%s, %s, %s, %s)
            """, (
                session_id,
                'session_start',
                datetime.utcnow(),
                Json({
                    'language': language,
                    'user_agent': user_agent
                })
            ))
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"❌ Session log error: {e}")
            self.conn.rollback()
            return False
    
    def log_error(self, session_id: str, error_message: str, error_type: Optional[str] = None) -> bool:
        """Log errore"""
        if not self.conn:
            return False
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO analytics_events (session_id, event_type, timestamp, data)
                VALUES (%s, %s, %s, %s)
            """, (
                session_id,
                'error',
                datetime.utcnow(),
                Json({
                    'error_message': error_message,
                    'error_type': error_type
                })
            ))
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"❌ Error log error: {e}")
            self.conn.rollback()
            return False
    
    def get_click_through_rate(self, start_date: str = None, end_date: str = None) -> float:
        """Calcola CTR totale"""
        if not self.conn:
            return 0.0
        try:
            cur = self.conn.cursor()
            
            where_clause = ""
            params = []
            
            if start_date and end_date:
                where_clause = "WHERE timestamp >= %s AND timestamp < %s"
                params = [start_date, end_date]
            
            query = f"""
                SELECT 
                    COUNT(*) FILTER (WHERE event_type = 'product_click') as clicks,
                    SUM((data->>'products_count')::int) FILTER (WHERE event_type = 'results') as products_shown
                FROM analytics_events
                {where_clause}
            """
            
            cur.execute(query, params)
            result = cur.fetchone()
            cur.close()
            
            clicks = result[0] or 0
            products_shown = result[1] or 0
            
            if products_shown == 0:
                return 0.0
            
            return round((clicks / products_shown) * 100, 2)
            
        except Exception as e:
            print(f"❌ CTR calculation error: {e}")
            return 0.0
    
    def get_session_ctr(self, session_id: str) -> dict:
        """Calcola CTR per una specifica sessione"""
        if not self.conn:
            return {'clicks': 0, 'products_shown': 0, 'ctr': 0.0}
        
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE event_type = 'product_click') as clicks,
                    SUM((data->>'products_count')::int) FILTER (WHERE event_type = 'results') as products_shown
                FROM analytics_events
                WHERE session_id = %s
            """, (session_id,))
            
            result = cur.fetchone()
            cur.close()
            
            clicks = result[0] or 0
            products_shown = result[1] or 0
            ctr = round((clicks / products_shown) * 100, 2) if products_shown > 0 else 0.0
            
            return {
                'clicks': clicks,
                'products_shown': products_shown,
                'ctr': ctr
            }
            
        except Exception as e:
            print(f"❌ Session CTR error: {e}")
            return {'clicks': 0, 'products_shown': 0, 'ctr': 0.0}
    
    def __del__(self):
        """Chiudi connessione"""
        if self.conn:
            self.conn.close()

_tracker = None

def get_tracker() -> AnalyticsTracker:
    """Ottieni istanza tracker (singleton)"""
    global _tracker
    if _tracker is None:
        _tracker = AnalyticsTracker()
    return _tracker
