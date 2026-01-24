"""
Analytics Tracker - PostgreSQL Native
Gestisce tracking analytics su database PostgreSQL
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import Optional

class AnalyticsTracker:
    """Tracker per analytics su PostgreSQL"""
    
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
    
    def log_session_start(self, session_id: str, language: str = 'it', user_agent: Optional[str] = None) -> bool:
        """Log inizio sessione"""
        if not self.conn:
            return False
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO analytics_sessions (session_id, language, user_agent)
                VALUES (%s, %s, %s)
                ON CONFLICT (session_id) DO NOTHING
            """, (session_id, language, user_agent))
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"❌ Session log error: {e}")
            return False
    
    def log_query(self, session_id: str, query: str, language: str = 'it') -> bool:
        """Log query utente"""
        if not self.conn:
            return False
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO analytics_queries (session_id, query, language)
                VALUES (%s, %s, %s)
            """, (session_id, query, language))
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"❌ Query log error: {e}")
            return False
    
    def log_results(self, session_id: str, products_count: int, products_shown: list, 
                   categories: list, has_comparison: bool = False) -> bool:
        """Log risultati mostrati"""
        if not self.conn:
            return False
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO analytics_results 
                (session_id, products_count, products_shown, categories, has_comparison)
                VALUES (%s, %s, %s, %s, %s)
            """, (session_id, products_count, products_shown, categories, has_comparison))
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"❌ Results log error: {e}")
            return False
    
    def log_product_click(self, session_id: str, product_name: str, 
                         product_id: str = '', product_category: str = '', 
                         language: str = 'it') -> bool:
        """Log click su prodotto"""
        if not self.conn:
            return False
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO analytics_clicks 
                (session_id, product_id, product_name, product_category, language)
                VALUES (%s, %s, %s, %s, %s)
            """, (session_id, product_id, product_name, product_category, language))
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"❌ Click log error: {e}")
            return False
    
    def log_error(self, session_id: str, error_message: str, error_type: Optional[str] = None) -> bool:
        """Log errore"""
        if not self.conn:
            return False
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO analytics_errors (session_id, error_message, error_type)
                VALUES (%s, %s, %s)
            """, (session_id, error_message, error_type))
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"❌ Error log error: {e}")
            return False
    
    def get_click_through_rate(self) -> float:
        """Calcola CTR basato su prodotti mostrati (click / prodotti_mostrati × 100)"""
        if not self.conn:
            return 0.0
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT COUNT(*) FROM analytics_clicks")
            clicks = cur.fetchone()[0] or 0
            cur.execute("SELECT SUM(products_count) FROM analytics_results WHERE products_count > 0")
            products_shown = cur.fetchone()[0] or 0
            cur.close()
            if products_shown == 0:
                return 0.0
            return round((clicks / products_shown) * 100, 2)
        except Exception as e:
            print(f"❌ CTR error: {e}")
            return 0.0
    
    def get_engagement_rate(self) -> float:
        """Calcola engagement rate (sessioni con click / sessioni con prodotti × 100)"""
        if not self.conn:
            return 0.0
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT COUNT(DISTINCT session_id) FROM analytics_clicks")
            sessions_with_clicks = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(DISTINCT session_id) FROM analytics_results WHERE products_count > 0")
            sessions_with_products = cur.fetchone()[0] or 0
            cur.close()
            if sessions_with_products == 0:
                return 0.0
            return round((sessions_with_clicks / sessions_with_products) * 100, 2)
        except Exception as e:
            print(f"❌ Engagement rate error: {e}")
            return 0.0
    
    def get_clicks_per_active_session(self) -> float:
        """Calcola media click per sessione attiva"""
        if not self.conn:
            return 0.0
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT COUNT(*) FROM analytics_clicks")
            clicks = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(DISTINCT session_id) FROM analytics_results WHERE products_count > 0")
            active_sessions = cur.fetchone()[0] or 0
            cur.close()
            if active_sessions == 0:
                return 0.0
            return round(clicks / active_sessions, 2)
        except Exception as e:
            print(f"❌ Clicks per session error: {e}")
            return 0.0
    
    def get_daily_ctr(self, days: int = 7) -> list:
        """Calcola CTR per ogni giorno degli ultimi N giorni"""
        if not self.conn:
            return []
        try:
            cur = self.conn.cursor()
            query = """
                WITH daily_products AS (
                    SELECT 
                        DATE(timestamp) as date,
                        SUM(products_count) as products_shown
                    FROM analytics_results
                    WHERE products_count > 0 AND timestamp >= CURRENT_DATE - INTERVAL '%s days'
                    GROUP BY DATE(timestamp)
                ),
                daily_clicks AS (
                    SELECT 
                        DATE(timestamp) as date,
                        COUNT(*) as clicks
                    FROM analytics_clicks
                    WHERE timestamp >= CURRENT_DATE - INTERVAL '%s days'
                    GROUP BY DATE(timestamp)
                )
                SELECT 
                    COALESCE(dp.date, dc.date) as date,
                    COALESCE(dc.clicks, 0) as clicks,
                    COALESCE(dp.products_shown, 0) as products_shown,
                    CASE 
                        WHEN COALESCE(dp.products_shown, 0) > 0 
                        THEN ROUND((COALESCE(dc.clicks, 0)::numeric / dp.products_shown) * 100, 2)
                        ELSE 0
                    END as ctr
                FROM daily_products dp
                FULL OUTER JOIN daily_clicks dc ON dp.date = dc.date
                ORDER BY date DESC
            """
            cur.execute(query, (days, days))
            results = []
            for row in cur.fetchall():
                results.append({
                    'date': row[0].strftime('%Y-%m-%d') if row[0] else None,
                    'clicks': row[1],
                    'products_shown': row[2],
                    'ctr': float(row[3])
                })
            cur.close()
            return results
        except Exception as e:
            print(f"❌ Daily CTR error: {e}")
            return []
    

    def get_date_range_stats(self, start_date: str, end_date: str) -> list:
        """Ottieni statistiche giornaliere per un range di date"""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT 
                    date, total_sessions, total_queries, total_products_shown,
                    total_clicks, ctr_percent, engagement_rate, avg_products_per_session
                FROM analytics_daily_stats
                WHERE date BETWEEN %s AND %s
                ORDER BY date DESC
            """, (start_date, end_date))
            
            columns = ['date', 'total_sessions', 'total_queries', 'total_products_shown', 
                      'total_clicks', 'ctr_percent', 'engagement_rate', 'avg_products_per_session']
            return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            print(f"❌ Error getting date range stats: {e}")
            return []
    
    def get_top_queries_range(self, start_date: str, end_date: str, limit: int = 10) -> list:
        """Top queries aggregate per un range di date"""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT query, SUM(count) as total_count
                FROM analytics_top_queries_daily
                WHERE date BETWEEN %s AND %s
                GROUP BY query
                ORDER BY total_count DESC
                LIMIT %s
            """, (start_date, end_date, limit))
            return [{'query': row[0], 'count': row[1]} for row in cur.fetchall()]
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def get_top_products_range(self, start_date: str, end_date: str, limit: int = 10) -> list:
        """Top products aggregate per un range di date"""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT product_name, product_category, SUM(clicks) as total_clicks
                FROM analytics_top_products_daily
                WHERE date BETWEEN %s AND %s
                GROUP BY product_name, product_category
                ORDER BY total_clicks DESC
                LIMIT %s
            """, (start_date, end_date, limit))
            return [{'product_name': row[0], 'category': row[1], 'clicks': row[2]} 
                    for row in cur.fetchall()]
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def get_top_categories_range(self, start_date: str, end_date: str, limit: int = 10) -> list:
        """Top categories aggregate per un range di date"""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT category, SUM(count) as total_count
                FROM analytics_top_categories_daily
                WHERE date BETWEEN %s AND %s
                GROUP BY category
                ORDER BY total_count DESC
                LIMIT %s
            """, (start_date, end_date, limit))
            return [{'category': row[0], 'count': row[1]} for row in cur.fetchall()]
        except Exception as e:
            print(f"❌ Error: {e}")
            return []

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
