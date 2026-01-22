"""
Analytics Dashboard Routes
Modulo separato per analytics - zero impatto su app principale
"""
from flask import Blueprint, render_template, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from collections import defaultdict
import json

analytics_bp = Blueprint('analytics', __name__)

def get_db_connection():
    """Connessione PostgreSQL con fallback"""
    try:
        db_url = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
        if not db_url:
            return None
        return psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    except Exception as e:
        print(f"⚠️ DB connection error: {e}")
        return None

@analytics_bp.route('/analytics')
def analytics_dashboard():
    """Dashboard analytics principale"""
    try:
        conn = get_db_connection()
        if not conn:
            return "Database non disponibile", 503
        
        cur = conn.cursor()
        
        # Parametri periodo - date range selector
        days = int(request.args.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        
        # ===== KPI PRINCIPALI =====
        cur.execute("""
            SELECT 
                COUNT(DISTINCT session_id) as total_sessions,
                COUNT(*) FILTER (WHERE event_type = 'query') as total_queries,
                COUNT(*) FILTER (WHERE event_type = 'results') as total_results,
                COUNT(*) FILTER (WHERE event_type = 'product_click') as total_clicks
            FROM analytics_events
            WHERE timestamp >= %s
        """, (start_date,))
        
        kpis = cur.fetchone()
        
        # ===== TREND GIORNALIERO =====
        cur.execute("""
            SELECT 
                DATE(timestamp) as date,
                COUNT(DISTINCT session_id) as sessions,
                COUNT(*) FILTER (WHERE event_type = 'query') as queries
            FROM analytics_events
            WHERE timestamp >= %s
            GROUP BY DATE(timestamp)
            ORDER BY date
        """, (start_date,))
        
        daily_data = cur.fetchall()
        
        # Grafico trend
        if daily_data:
            dates = [row['date'].strftime('%Y-%m-%d') for row in daily_data]
            sessions = [row['sessions'] for row in daily_data]
            
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=dates, 
                y=sessions,
                mode='lines+markers',
                name='Conversazioni',
                line=dict(color='#00C853', width=3),
                marker=dict(size=8)
            ))
            
            fig_trend.update_layout(
                template='plotly_dark',
                height=350,
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis_title="Data",
                yaxis_title="Conversazioni",
                hovermode='x unified'
            )
            
            trend_chart = fig_trend.to_html(include_plotlyjs='cdn', div_id='trend-chart')
        else:
            trend_chart = "<p>Nessun dato disponibile</p>"
        
        # ===== TOP QUERIES =====
        cur.execute("""
            SELECT 
                data->>'query' as query,
                COUNT(*) as count
            FROM analytics_events
            WHERE event_type = 'query' 
                AND timestamp >= %s
                AND data->>'query' IS NOT NULL
            GROUP BY query
            ORDER BY count DESC
            LIMIT 10
        """, (start_date,))
        
        top_queries = cur.fetchall()
        
        # Grafico queries
        if top_queries:
            queries = [row['query'][:50] + '...' if len(row['query']) > 50 else row['query'] for row in top_queries]
            counts = [row['count'] for row in top_queries]
            
            fig_queries = go.Figure(go.Bar(
                x=counts,
                y=queries,
                orientation='h',
                marker=dict(
                    color=counts,
                    colorscale='Greens',
                    showscale=False
                ),
                text=counts,
                textposition='auto'
            ))
            
            fig_queries.update_layout(
                template='plotly_dark',
                height=400,
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis_title="Numero ricerche",
                yaxis_title="",
                yaxis={'categoryorder': 'total ascending'}
            )
            
            queries_chart = fig_queries.to_html(include_plotlyjs=False, div_id='queries-chart')
        else:
            queries_chart = "<p>Nessuna query registrata</p>"
        
        # ===== TOP PRODOTTI MOSTRATI =====
        cur.execute("""
            SELECT 
                product,
                COUNT(*) as shown_count
            FROM analytics_events,
                jsonb_array_elements_text(data->'top_products') as product
            WHERE event_type = 'results'
                AND timestamp >= %s
            GROUP BY product
            ORDER BY shown_count DESC
            LIMIT 10
        """, (start_date,))
        
        top_products = cur.fetchall()
        
        # Grafico prodotti
        if top_products:
            products = [row['product'] for row in top_products]
            counts = [row['shown_count'] for row in top_products]
            
            fig_products = go.Figure(go.Bar(
                x=counts,
                y=products,
                orientation='h',
                marker=dict(
                    color=counts,
                    colorscale='Viridis',
                    showscale=False
                ),
                text=counts,
                textposition='auto'
            ))
            
            fig_products.update_layout(
                template='plotly_dark',
                height=400,
                margin=dict(l=0, r=0, t=20, b=0),
                xaxis_title="Volte mostrato",
                yaxis_title="",
                yaxis={'categoryorder': 'total ascending'}
            )
            
            products_chart = fig_products.to_html(include_plotlyjs=False, div_id='products-chart')
        else:
            products_chart = "<p>Nessun prodotto mostrato</p>"
        
        # ===== CATEGORIE =====
        cur.execute("""
            SELECT 
                category,
                COUNT(*) as count
            FROM analytics_events,
                jsonb_array_elements_text(data->'categories') as category
            WHERE event_type = 'results'
                AND timestamp >= %s
            GROUP BY category
            ORDER BY count DESC
        """, (start_date,))
        
        categories = cur.fetchall()
        
        # ===== TOP PRODOTTI CLICCATI =====
        cur.execute("""
            SELECT 
                data->>'product_name' as product_name,
                COUNT(*) as click_count
            FROM analytics_events
            WHERE event_type = 'product_click'
                AND timestamp >= %s
                AND data->>'product_name' IS NOT NULL
            GROUP BY product_name
            ORDER BY click_count DESC
            LIMIT 10
        """, (start_date,))
        
        top_clicked = cur.fetchall()
        
        # ===== TOP PRODOTTI CLICCATI =====
        cur.execute("""
            SELECT 
                data->>'product_name' as product_name,
                COUNT(*) as click_count
            FROM analytics_events
            WHERE event_type = 'product_click'
                AND timestamp >= %s
                AND data->>'product_name' IS NOT NULL
            GROUP BY product_name
            ORDER BY click_count DESC
            LIMIT 10
        """, (start_date,))
        
        top_clicked = cur.fetchall()
        
        # ===== TOP PRODOTTI CLICCATI =====
        cur.execute("""
            SELECT 
                data->>'product_name' as product_name,
                COUNT(*) as click_count
            FROM analytics_events
            WHERE event_type = 'product_click'
                AND timestamp >= %s
                AND data->>'product_name' IS NOT NULL
            GROUP BY product_name
            ORDER BY click_count DESC
            LIMIT 10
        """, (start_date,))
        
        top_clicked = cur.fetchall()
        
        # ===== TOP PRODOTTI CLICCATI =====
        cur.execute("""
            SELECT 
                data->>'product_name' as product_name,
                COUNT(*) as click_count
            FROM analytics_events
            WHERE event_type = 'product_click'
                AND timestamp >= %s
                AND data->>'product_name' IS NOT NULL
            GROUP BY product_name
            ORDER BY click_count DESC
            LIMIT 10
        """, (start_date,))
        
        top_clicked = cur.fetchall()
        
        # ===== TOP PRODOTTI CLICCATI =====
        cur.execute("""
            SELECT 
                data->>'product_name' as product_name,
                COUNT(*) as click_count
            FROM analytics_events
            WHERE event_type = 'product_click'
                AND timestamp >= %s
                AND data->>'product_name' IS NOT NULL
            GROUP BY product_name
            ORDER BY click_count DESC
            LIMIT 10
        """, (start_date,))
        
        top_clicked = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Render template
        return render_template('analytics.html',
            kpis=kpis,
            trend_chart=trend_chart,
            queries_chart=queries_chart,
            products_chart=products_chart,
            categories=categories,
            top_clicked=top_clicked,
            days=days
        )
        
    except Exception as e:
        print(f"❌ Analytics error: {e}")
        import traceback
        traceback.print_exc()
        return f"Errore analytics: {e}", 500

@analytics_bp.route('/api/analytics/conversations')
def get_conversations():
    """Ottieni conversazioni recenti raggruppate per session"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'DB not available'}), 503
        
        cur = conn.cursor()
        
        # Parametri
        days = int(request.args.get('days', 30))
        limit = int(request.args.get('limit', 20))
        start_date = datetime.now() - timedelta(days=days)
        
        # Ottieni tutte le sessioni con eventi
        cur.execute("""
            SELECT 
                session_id,
                MIN(timestamp) as first_seen,
                MAX(timestamp) as last_seen,
                COUNT(*) as event_count,
                json_agg(
                    json_build_object(
                        'type', event_type,
                        'timestamp', timestamp,
                        'data', data
                    ) ORDER BY timestamp
                ) as events
            FROM analytics_events
            WHERE timestamp >= %s
            GROUP BY session_id
            ORDER BY last_seen DESC
            LIMIT %s
        """, (start_date, limit))
        
        sessions = cur.fetchall()
        
        # Formatta conversazioni
        conversations = []
        for session in sessions:
            # Estrai query e results
            messages = []
            for event in session['events']:
                if event['type'] == 'query':
                    messages.append({
                        'role': 'user',
                        'content': event['data'].get('query', ''),
                        'timestamp': event['timestamp']
                    })
                elif event['type'] == 'results':
                    messages.append({
                        'role': 'assistant',
                        'products_count': event['data'].get('products_count', 0),
                        'products': event['data'].get('top_products', [])[:3],  # Top 3
                        'timestamp': event['timestamp']
                    })
            
            conversations.append({
                'session_id': session['session_id'][:8],  # Short ID
                'first_seen': session['first_seen'].isoformat(),
                'last_seen': session['last_seen'].isoformat(),
                'message_count': len(messages),
                'messages': messages
            })
        
        cur.close()
        conn.close()
        
        return jsonify({'conversations': conversations})
        
    except Exception as e:
        print(f"❌ Conversations API error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/analytics/health')
def analytics_health():
    """Health check per analytics"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'status': 'error', 'message': 'DB not available'}), 503
        
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as count FROM analytics_events")
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        return jsonify({
            'status': 'ok',
            'total_events': result['count']
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
