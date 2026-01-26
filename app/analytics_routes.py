"""
Analytics Dashboard Routes - COMPLETO CON DATE RANGE
"""
from flask import Blueprint, render_template, request, jsonify
from app.analytics_tracker import get_tracker
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
def analytics_dashboard():
    """Dashboard analytics con date range selector"""
    try:
        tracker = get_tracker()
        
        # Ottieni date range da query params
        date_from_str = request.args.get('date_from')
        date_to_str = request.args.get('date_to')
        
        # Default: ultimi 7 giorni
        if not date_from_str or not date_to_str:
            date_to = datetime.now().date()
            date_from = date_to - timedelta(days=7)
        else:
            try:
                date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
                date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
            except ValueError:
                date_to = datetime.now().date()
                date_from = date_to - timedelta(days=7)
        
        # Valida range
        if date_from > date_to:
            date_from, date_to = date_to, date_from
        
        # Query stats giornalieri
        daily_stats = tracker.get_date_range_stats(date_from.isoformat(), date_to.isoformat())
        
        # KPI aggregate
        total_sessions = sum(d.get('total_sessions', 0) for d in daily_stats)
        total_queries = sum(d.get('total_queries', 0) for d in daily_stats)
        total_products = sum(d.get('total_products_shown', 0) for d in daily_stats)
        total_clicks = sum(d.get('total_clicks', 0) for d in daily_stats)
        avg_ctr = round((total_clicks / total_products * 100), 2) if total_products > 0 else 0
        
        kpis = {
            'total_sessions': total_sessions,
            'total_queries': total_queries,
            'total_products': total_products,
            'total_clicks': total_clicks,
            'ctr_percent': avg_ctr
        }

        # Conversazioni del periodo
        conversations = tracker.get_conversations_in_range(
            date_from.isoformat(),
            date_to.isoformat()
        )
        
        top_queries = tracker.get_top_queries_range(date_from.isoformat(), date_to.isoformat(), 10)
        top_products = tracker.get_top_products_range(date_from.isoformat(), date_to.isoformat(), 10)
        top_categories = tracker.get_top_categories_range(date_from.isoformat(), date_to.isoformat(), 10)
        
        # Converti date
        for stat in daily_stats:
            if 'date' in stat and hasattr(stat['date'], 'isoformat'):
                stat['date'] = stat['date'].isoformat()
        
        return render_template('analytics.html',
            date_from=date_from.isoformat(),
            date_to=date_to.isoformat(),
            kpis=kpis,
            daily_stats=daily_stats,
            top_queries=top_queries,
            top_products=top_products,
            top_categories=top_categories,
            conversations=conversations
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return f"Errore: {str(e)}", 500


@analytics_bp.route('/api/analytics/compare', methods=['POST'])
def compare_periods():
    """Confronta due periodi analytics"""
    from flask import jsonify
    try:
        from utils.statistics import chi_square_ctr_test, calculate_delta
    except ImportError:
        return jsonify({'error': 'scipy not installed'}), 500
    
    try:
        tracker = get_tracker()
        data = request.get_json()
        
        if not data or 'period_a' not in data or 'period_b' not in data:
            return jsonify({'error': 'Missing period_a or period_b'}), 400
        
        period_a = data['period_a']
        period_b = data['period_b']
        
        # Parse dates
        a_start = datetime.strptime(period_a['start'], '%Y-%m-%d').date()
        a_end = datetime.strptime(period_a['end'], '%Y-%m-%d').date()
        b_start = datetime.strptime(period_b['start'], '%Y-%m-%d').date()
        b_end = datetime.strptime(period_b['end'], '%Y-%m-%d').date()
        
        # Get KPIs helper
        def get_kpis(start, end):
            conn = tracker.conn
            if not conn:
                return None
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    COUNT(DISTINCT session_id),
                    COUNT(*) FILTER (WHERE event_type = 'query'),
                    SUM((data->>'products_count')::int) FILTER (WHERE event_type = 'results'),
                    COUNT(*) FILTER (WHERE event_type = 'product_click')
                FROM analytics_events
                WHERE timestamp >= %s AND timestamp < %s + INTERVAL '1 day'
            """, (start, end))
            r = cur.fetchone()
            cur.close()
            sessions, queries, products, clicks = r[0] or 0, r[1] or 0, r[2] or 0, r[3] or 0
            ctr = round((clicks / products * 100), 2) if products > 0 else 0.0
            return {'sessions': sessions, 'queries': queries, 'products_shown': products, 'clicks': clicks, 'ctr': ctr}
        
        kpis_a = get_kpis(a_start, a_end)
        kpis_b = get_kpis(b_start, b_end)
        
        if not kpis_a or not kpis_b:
            return jsonify({'error': 'Database error'}), 503
        
        # Deltas
        deltas = {
            'sessions': calculate_delta(kpis_a['sessions'], kpis_b['sessions']),
            'ctr': calculate_delta(kpis_a['ctr'], kpis_b['ctr'], is_percentage=True)
        }
        
        # Significance
        significance = chi_square_ctr_test(
            {'clicks': kpis_a['clicks'], 'products_shown': kpis_a['products_shown']},
            {'clicks': kpis_b['clicks'], 'products_shown': kpis_b['products_shown']}
        )
        
        return jsonify({
            'period_a': {'start': a_start.isoformat(), 'end': a_end.isoformat(), 'kpis': kpis_a},
            'period_b': {'start': b_start.isoformat(), 'end': b_end.isoformat(), 'kpis': kpis_b},
            'deltas': deltas,
            'significance': significance
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
