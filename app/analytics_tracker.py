"""
Analytics Tracker - Sistema unificato con analytics_events
"""
import psycopg2
from psycopg2.extras import Json
import os
from datetime import datetime

class AnalyticsTracker:
    def __init__(self):
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Connessione al database PostgreSQL"""
        try:
            database_url = os.getenv('DATABASE_URL')
            if database_url:
                self.conn = psycopg2.connect(database_url)
                print("✅ Analytics tracker connected to PostgreSQL")
            else:
                print("⚠️ DATABASE_URL not found")
        except Exception as e:
            print(f"❌ Analytics DB connection failed: {e}")
            self.conn = None
    
    def log_session_start(self, session_id, language='it', user_agent=None):
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
                datetime.now(),
                Json({'language': language, 'user_agent': user_agent})
            ))
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"❌ Log session error: {e}")
            self.conn.rollback()
            return False
    
    def log_query(self, session_id, query, language='it', query_index=None):
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
                datetime.now(),
                Json({
                    'query': query,
                    'query_length': len(query),
                    'language': language,
                    'query_index': query_index
                })
            ))
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"❌ Log query error: {e}")
            self.conn.rollback()
            return False
    
    def log_results(self, session_id, products_count, products_shown, product_names, 
                   categories, has_comparison, query_index=None):
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
                datetime.now(),
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
            print(f"❌ Log results error: {e}")
            self.conn.rollback()
            return False
    
    def log_product_click(self, session_id, product_name, product_id='', 
                         product_category='', language='it', query_index=None):
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
                datetime.now(),
                Json({
                    'product_name': product_name,
                    'product_id': product_id,
                    'product_category': product_category,
                    'language': language,
                    'query_index': query_index
                })
            ))
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"❌ Log click error: {e}")
            self.conn.rollback()
            return False
    
    def log_error(self, session_id, error_message, error_type='Exception'):
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
                datetime.now(),
                Json({
                    'error_message': error_message,
                    'error_type': error_type
                })
            ))
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"❌ Log error failed: {e}")
            self.conn.rollback()
            return False
    
    def get_date_range_stats(self, start_date, end_date):
        """Statistiche aggregate per range di date"""
        if not self.conn:
            return []
        
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(DISTINCT session_id) as total_sessions,
                    COUNT(*) FILTER (WHERE event_type = 'query') as total_queries,
                    SUM((data->>'products_count')::int) FILTER (WHERE event_type = 'results') as total_products_shown,
                    COUNT(*) FILTER (WHERE event_type = 'product_click') as total_clicks
                FROM analytics_events
                WHERE timestamp >= %s AND timestamp < %s::date + INTERVAL '1 day'
                GROUP BY DATE(timestamp)
                ORDER BY date
            """, (start_date, end_date))
            
            results = cur.fetchall()
            cur.close()
            
            stats = []
            for row in results:
                stats.append({
                    'date': row[0],
                    'total_sessions': row[1] or 0,
                    'total_queries': row[2] or 0,
                    'total_products_shown': row[3] or 0,
                    'total_clicks': row[4] or 0
                })
            return stats
        except Exception as e:
            print(f"❌ Get date range stats error: {e}")
            return []
    
    def get_top_queries_range(self, start_date, end_date, limit=10):
        """Top queries per range di date"""
        if not self.conn:
            return []
        
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT 
                    data->>'query' as query,
                    COUNT(*) as count
                FROM analytics_events
                WHERE event_type = 'query'
                    AND timestamp >= %s 
                    AND timestamp < %s::date + INTERVAL '1 day'
                    AND data->>'query' IS NOT NULL
                GROUP BY data->>'query'
                ORDER BY count DESC
                LIMIT %s
            """, (start_date, end_date, limit))
            
            results = cur.fetchall()
            cur.close()
            
            return [{'query': row[0], 'count': row[1]} for row in results]
        except Exception as e:
            print(f"❌ Get top queries error: {e}")
            return []
    
    def get_top_products_range(self, start_date, end_date, limit=10):
        """Top prodotti cliccati per range di date"""
        if not self.conn:
            return []
        
        try:
            cur = self.conn.cursor()
            
            # Products shown
            cur.execute("""
                SELECT 
                    product_name,
                    COUNT(*) as shown_count
                FROM analytics_events,
                    jsonb_array_elements_text(data->'product_names') as product_name
                WHERE event_type = 'results'
                    AND timestamp >= %s 
                    AND timestamp < %s::date + INTERVAL '1 day'
                GROUP BY product_name
            """, (start_date, end_date))
            
            shown = {row[0]: row[1] for row in cur.fetchall()}
            
            # Products clicked
            cur.execute("""
                SELECT 
                    data->>'product_name' as product_name,
                    COUNT(*) as click_count
                FROM analytics_events
                WHERE event_type = 'product_click'
                    AND timestamp >= %s 
                    AND timestamp < %s::date + INTERVAL '1 day'
                    AND data->>'product_name' IS NOT NULL
                GROUP BY data->>'product_name'
                ORDER BY click_count DESC
                LIMIT %s
            """, (start_date, end_date, limit))
            
            clicked = cur.fetchall()
            cur.close()
            
            # Combine
            products = []
            for product_name, click_count in clicked:
                shown_count = shown.get(product_name, 0)
                ctr = round((click_count / shown_count * 100), 2) if shown_count > 0 else 0.0
                products.append({
                    'product_name': product_name,
                    'shown_count': shown_count,
                    'click_count': click_count,
                    'ctr': ctr
                })
            
            return products
        except Exception as e:
            print(f"❌ Get top products error: {e}")
            return []
    
    def get_top_categories_range(self, start_date, end_date, limit=10):
        """Top categorie per range di date"""
        if not self.conn:
            return []
        
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT 
                    category,
                    COUNT(*) as count
                FROM analytics_events,
                    jsonb_array_elements_text(data->'categories') as category
                WHERE event_type = 'results'
                    AND timestamp >= %s 
                    AND timestamp < %s::date + INTERVAL '1 day'
                GROUP BY category
                ORDER BY count DESC
                LIMIT %s
            """, (start_date, end_date, limit))
            
            results = cur.fetchall()
            cur.close()
            
            return [{'category': row[0], 'count': row[1]} for row in results]
        except Exception as e:
            print(f"❌ Get top categories error: {e}")
            return []
    
    def get_conversations_in_range(self, start_date, end_date):
        """Conversazioni complete per range di date"""
        if not self.conn:
            return []
        
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT DISTINCT session_id
                FROM analytics_events
                WHERE timestamp >= %s AND timestamp < %s::date + INTERVAL '1 day'
                ORDER BY session_id
            """, (start_date, end_date))
            
            session_ids = [row[0] for row in cur.fetchall()]
            
            conversations = []
            for session_id in session_ids:
                cur.execute("""
                    SELECT 
                        MIN(timestamp) as first_event,
                        COUNT(*) FILTER (WHERE event_type = 'query') as queries,
                        SUM((data->>'products_count')::int) FILTER (WHERE event_type = 'results') as products,
                        COUNT(*) FILTER (WHERE event_type = 'product_click') as clicks
                    FROM analytics_events
                    WHERE session_id = %s
                """, (session_id,))
                
                row = cur.fetchone()
                if row:
                    conversations.append({
                        'session_id': session_id,
                        'timestamp': row[0],
                        'queries': row[1] or 0,
                        'products': row[2] or 0,
                        'clicks': row[3] or 0
                    })
            
            cur.close()
            return conversations
        except Exception as e:
            print(f"❌ Get conversations error: {e}")
            return []
    
    def get_session_ctr(self, session_id):
        """CTR per singola sessione"""
        if not self.conn:
            return 0.0
        
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT 
                    SUM((data->>'products_count')::int) FILTER (WHERE event_type = 'results') as products,
                    COUNT(*) FILTER (WHERE event_type = 'product_click') as clicks
                FROM analytics_events
                WHERE session_id = %s
            """, (session_id,))
            
            row = cur.fetchone()
            cur.close()
            
            if row:
                products = row[0] or 0
                clicks = row[1] or 0
                return round((clicks / products * 100), 2) if products > 0 else 0.0
            return 0.0
        except Exception as e:
            print(f"❌ Get session CTR error: {e}")
            return 0.0
    
    def get_click_through_rate(self, start_date, end_date):
        """CTR globale per range di date"""
        if not self.conn:
            return 0.0
        
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT 
                    SUM((data->>'products_count')::int) FILTER (WHERE event_type = 'results') as products,
                    COUNT(*) FILTER (WHERE event_type = 'product_click') as clicks
                FROM analytics_events
                WHERE timestamp >= %s AND timestamp < %s::date + INTERVAL '1 day'
            """, (start_date, end_date))
            
            row = cur.fetchone()
            cur.close()
            
            if row:
                products = row[0] or 0
                clicks = row[1] or 0
                return round((clicks / products * 100), 2) if products > 0 else 0.0
            return 0.0
        except Exception as e:
            print(f"❌ Get CTR error: {e}")
            return 0.0

# Singleton instance
_tracker_instance = None

def get_tracker():
    """Ottieni istanza singleton del tracker"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = AnalyticsTracker()
    return _tracker_instance