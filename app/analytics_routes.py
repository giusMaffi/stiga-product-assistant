"""
Analytics Dashboard Routes
Dashboard completo con metriche PostgreSQL native
"""
from flask import Blueprint, render_template, jsonify
from app.analytics_tracker import get_tracker
import psycopg2
import os
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__)

def get_db_connection():
    """Connessione PostgreSQL"""
    try:
        db_url = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
        if not db_url:
            return None
        return psycopg2.connect(db_url)
    except Exception as e:
        print(f"⚠️ DB connection error: {e}")
        return None

@analytics_bp.route('/analytics')
def analytics_dashboard():
    """Dashboard analytics principale"""
    try:
        conn = get_db_connection()
        tracker = get_tracker()
        
        if not conn:
            return "Database non disponibile", 503
        
        cur = conn.cursor()
        
        # ===== KPI PRINCIPALI =====
        
        # Conversazioni totali
        cur.execute("SELECT COUNT(DISTINCT session_id) FROM analytics_queries")
        total_conversations = cur.fetchone()[0] or 0
        
        # Query utenti totali
        cur.execute("SELECT COUNT(*) FROM analytics_queries")
        total_queries = cur.fetchone()[0] or 0
        
        # Risposte generate
        cur.execute("SELECT COUNT(*) FROM analytics_results")
        total_responses = cur.fetchone()[0] or 0
        
        # Click rate (usa la nuova formula)
        ctr = tracker.get_click_through_rate()
        
        # Engagement rate
        engagement_rate = tracker.get_engagement_rate()
        
        # Click per sessione attiva
        clicks_per_session = tracker.get_clicks_per_active_session()
        
        # ===== TOP QUERIES =====
        cur.execute("""
            SELECT query, COUNT(*) as count
            FROM analytics_queries
            GROUP BY query
            ORDER BY count DESC
            LIMIT 10
        """)
        top_queries = [{'query': row[0], 'count': row[1]} for row in cur.fetchall()]
        
        # ===== TOP PRODOTTI CLICCATI =====
        cur.execute("""
            SELECT product_name, COUNT(*) as clicks
            FROM analytics_clicks
            GROUP BY product_name
            ORDER BY clicks DESC
            LIMIT 10
        """)
        top_products = [{'name': row[0], 'clicks': row[1]} for row in cur.fetchall()]
        
        # ===== CATEGORIE RICERCATE =====
        cur.execute("""
            SELECT UNNEST(categories) as category, COUNT(*) as count
            FROM analytics_results
            WHERE categories IS NOT NULL AND array_length(categories, 1) > 0
            GROUP BY category
            ORDER BY count DESC
            LIMIT 10
        """)
        top_categories = [{'category': row[0], 'count': row[1]} for row in cur.fetchall()]
        
        # ===== CTR GIORNALIERO (ultimi 7 giorni) =====
        daily_ctr_data = tracker.get_daily_ctr(days=7)
        
        cur.close()
        conn.close()
        
        return render_template('analytics.html',
            total_conversations=total_conversations,
            total_queries=total_queries,
            total_responses=total_responses,
            ctr=ctr,
            engagement_rate=engagement_rate,
            clicks_per_session=clicks_per_session,
            top_queries=top_queries,
            top_products=top_products,
            top_categories=top_categories,
            daily_ctr_data=daily_ctr_data
        )
        
    except Exception as e:
        print(f"❌ Analytics dashboard error: {e}")
        import traceback
        traceback.print_exc()
        return f"Errore: {str(e)}", 500

@analytics_bp.route('/analytics/api/stats')
def get_stats():
    """API endpoint per statistiche real-time"""
    try:
        conn = get_db_connection()
        tracker = get_tracker()
        
        if not conn:
            return jsonify({'error': 'Database non disponibile'}), 503
        
        cur = conn.cursor()
        
        # Stats base
        cur.execute("SELECT COUNT(DISTINCT session_id) FROM analytics_queries")
        conversations = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COUNT(*) FROM analytics_queries")
        queries = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COUNT(*) FROM analytics_clicks")
        clicks = cur.fetchone()[0] or 0
        
        # Metriche avanzate
        ctr = tracker.get_click_through_rate()
        engagement = tracker.get_engagement_rate()
        clicks_per_session = tracker.get_clicks_per_active_session()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'conversations': conversations,
            'queries': queries,
            'clicks': clicks,
            'ctr': ctr,
            'engagement_rate': engagement,
            'clicks_per_session': clicks_per_session
        })
        
    except Exception as e:
        print(f"❌ Stats API error: {e}")
        return jsonify({'error': str(e)}), 500
