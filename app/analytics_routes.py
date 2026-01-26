"""
Analytics Dashboard Routes - COMPLETO CON DRILL-DOWN
"""
from flask import Blueprint, render_template, request, jsonify
from app.analytics_tracker import get_tracker
from datetime import datetime, timedelta
from utils.statistics import chi_square_ctr_test, calculate_delta

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
def analytics_dashboard():
    """Dashboard analytics principale"""
    try:
        tracker = get_tracker()
        
        date_from_str = request.args.get('date_from')
        date_to_str = request.args.get('date_to')
        
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
        
        if date_from > date_to:
            date_from, date_to = date_to, date_from
        
        daily_stats = tracker.get_date_range_stats(date_from.isoformat(), date_to.isoformat())
        
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

        top_products = tracker.get_top_products_range(date_from.isoformat(), date_to.isoformat(), 10)
        
        for stat in daily_stats:
            if 'date' in stat and hasattr(stat['date'], 'isoformat'):
                stat['date'] = stat['date'].isoformat()
        
        return render_template('analytics.html',
            date_from=date_from.isoformat(),
            date_to=date_to.isoformat(),
            kpis=kpis,
            daily_stats=daily_stats,
            top_products=top_products
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return f"Errore: {str(e)}", 500


@analytics_bp.route('/analytics/daily')
def analytics_daily():
    """Drill-down: breakdown giornaliero"""
    try:
        tracker = get_tracker()
        metric = request.args.get('metric', 'sessions')
        date_from_str = request.args.get('date_from')
        date_to_str = request.args.get('date_to')
        
        if not date_from_str or not date_to_str:
            date_to = datetime.now().date()
            date_from = date_to - timedelta(days=7)
        else:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        
        daily_stats = tracker.get_date_range_stats(date_from.isoformat(), date_to.isoformat())
        
        for stat in daily_stats:
            if 'date' in stat and hasattr(stat['date'], 'isoformat'):
                stat['date'] = stat['date'].isoformat()
        
        return render_template('analytics_daily.html',
            metric=metric,
            date_from=date_from.isoformat(),
            date_to=date_to.isoformat(),
            daily_stats=daily_stats
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        return f"Errore: {str(e)}", 500


@analytics_bp.route('/analytics/sessions')
def analytics_sessions():
    """Drill-down: lista sessioni per giorno"""
    try:
        tracker = get_tracker()
        date_str = request.args.get('date')
        
        if not date_str:
            return "Data richiesta", 400
        
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        conversations = tracker.get_conversations_in_range(date.isoformat(), date.isoformat())
        
        return render_template('analytics_sessions.html',
            date=date.isoformat(),
            conversations=conversations
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        return f"Errore: {str(e)}", 500


@analytics_bp.route('/analytics/transcript/<session_id>')
def analytics_transcript(session_id):
    """Drill-down: transcript conversazione"""
    try:
        tracker = get_tracker()
        
        if not tracker.conn:
            return "Database non disponibile", 503
        
        cur = tracker.conn.cursor()
        cur.execute("""
            SELECT event_type, timestamp, data
            FROM analytics_events
            WHERE session_id = %s
            ORDER BY timestamp
        """, (session_id,))
        
        events = cur.fetchall()
        cur.close()
        
        transcript = []
        for event_type, timestamp, data in events:
            transcript.append({
                'event_type': event_type,
                'timestamp': timestamp.isoformat(),
                'data': data
            })
        
        queries = sum(1 for e in transcript if e['event_type'] == 'query')
        products = sum(e['data'].get('products_count', 0) for e in transcript if e['event_type'] == 'results')
        clicks = sum(1 for e in transcript if e['event_type'] == 'product_click')
        ctr = round((clicks / products * 100), 2) if products > 0 else 0.0
        
        return render_template('analytics_transcript.html',
            session_id=session_id,
            transcript=transcript,
            stats={'queries': queries, 'products': products, 'clicks': clicks, 'ctr': ctr}
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        return f"Errore: {str(e)}", 500


@analytics_bp.route('/api/analytics/compare', methods=['POST'])
def compare_periods():
    """Confronta due periodi analytics"""
    try:
        tracker = get_tracker()
        data = request.get_json()
        
        if not data or 'period_a' not in data or 'period_b' not in data:
            return jsonify({'error': 'Missing period_a or period_b'}), 400
        
        period_a = data['period_a']
        period_b = data['period_b']
        
        try:
            a_start = datetime.strptime(period_a['start'], '%Y-%m-%d').date()
            a_end = datetime.strptime(period_a['end'], '%Y-%m-%d').date()
            b_start = datetime.strptime(period_b['start'], '%Y-%m-%d').date()
            b_end = datetime.strptime(period_b['end'], '%Y-%m-%d').date()
        except (ValueError, KeyError) as e:
            return jsonify({'error': f'Invalid date format: {e}'}), 400
        
        def get_period_kpis(start_date, end_date):
            conn = tracker.conn
            if not conn:
                return None
            
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    COUNT(DISTINCT session_id) as sessions,
                    COUNT(*) FILTER (WHERE event_type = 'query') as queries,
                    SUM((data->>'products_count')::int) FILTER (WHERE event_type = 'results') as products_shown,
                    COUNT(*) FILTER (WHERE event_type = 'product_click') as clicks
                FROM analytics_events
                WHERE timestamp >= %s AND timestamp < %s + INTERVAL '1 day'
            """, (start_date, end_date))
            
            result = cur.fetchone()
            cur.close()
            
            sessions = result[0] or 0
            queries = result[1] or 0
            products_shown = result[2] or 0
            clicks = result[3] or 0
            ctr = round((clicks / products_shown * 100), 2) if products_shown > 0 else 0.0
            
            return {
                'sessions': sessions,
                'queries': queries,
                'products_shown': products_shown,
                'clicks': clicks,
                'ctr': ctr
            }
        
        kpis_a = get_period_kpis(a_start, a_end)
        kpis_b = get_period_kpis(b_start, b_end)
        
        if not kpis_a or not kpis_b:
            return jsonify({'error': 'Database connection failed'}), 503
        
        deltas = {
            'sessions': calculate_delta(kpis_a['sessions'], kpis_b['sessions']),
            'queries': calculate_delta(kpis_a['queries'], kpis_b['queries']),
            'clicks': calculate_delta(kpis_a['clicks'], kpis_b['clicks']),
            'ctr': calculate_delta(kpis_a['ctr'], kpis_b['ctr'], is_percentage=True)
        }
        
        significance = chi_square_ctr_test(
            {'clicks': kpis_a['clicks'], 'products_shown': kpis_a['products_shown']},
            {'clicks': kpis_b['clicks'], 'products_shown': kpis_b['products_shown']}
        )
        
        def get_daily_trend(start_date, end_date):
            conn = tracker.conn
            if not conn:
                return []
            
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(DISTINCT session_id) as sessions,
                    SUM((data->>'products_count')::int) FILTER (WHERE event_type = 'results') as products_shown,
                    COUNT(*) FILTER (WHERE event_type = 'product_click') as clicks
                FROM analytics_events
                WHERE timestamp >= %s AND timestamp < %s + INTERVAL '1 day'
                GROUP BY DATE(timestamp)
                ORDER BY date
            """, (start_date, end_date))
            
            results = cur.fetchall()
            cur.close()
            
            trend = []
            for row in results:
                date, sessions, products_shown, clicks = row
                ctr = round((clicks / products_shown * 100), 2) if products_shown and products_shown > 0 else 0.0
                trend.append({
                    'date': date.isoformat(),
                    'sessions': sessions or 0,
                    'clicks': clicks or 0,
                    'ctr': ctr
                })
            
            return trend
        
        daily_trends = {
            'period_a': get_daily_trend(a_start, a_end),
            'period_b': get_daily_trend(b_start, b_end)
        }
        
        def get_top_products_with_ctr(start_date, end_date):
            conn = tracker.conn
            if not conn:
                return []
            
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    product_name,
                    COUNT(*) as shown_count
                FROM analytics_events,
                    jsonb_array_elements_text(data->'product_names') as product_name
                WHERE event_type = 'results'
                    AND timestamp >= %s AND timestamp < %s + INTERVAL '1 day'
                GROUP BY product_name
            """, (start_date, end_date))
            
            shown = {row[0]: row[1] for row in cur.fetchall()}
            
            cur.execute("""
                SELECT 
                    data->>'product_name' as product_name,
                    COUNT(*) as click_count
                FROM analytics_events
                WHERE event_type = 'product_click'
                    AND timestamp >= %s AND timestamp < %s + INTERVAL '1 day'
                GROUP BY data->>'product_name'
            """, (start_date, end_date))
            
            clicked = {row[0]: row[1] for row in cur.fetchall()}
            cur.close()
            
            all_products = set(shown.keys()) | set(clicked.keys())
            products = []
            
            for product_name in all_products:
                shown_count = shown.get(product_name, 0)
                click_count = clicked.get(product_name, 0)
                ctr = round((click_count / shown_count * 100), 2) if shown_count > 0 else 0.0
                
                products.append({
                    'name': product_name,
                    'shown': shown_count,
                    'clicked': click_count,
                    'ctr': ctr
                })
            
            products.sort(key=lambda x: x['clicked'], reverse=True)
            return products[:20]
        
        products_a = get_top_products_with_ctr(a_start, a_end)
        products_b = get_top_products_with_ctr(b_start, b_end)
        
        products_map = {}
        
        for p in products_a:
            products_map[p['name']] = {
                'name': p['name'],
                'period_a': {'shown': p['shown'], 'clicked': p['clicked'], 'ctr': p['ctr']},
                'period_b': {'shown': 0, 'clicked': 0, 'ctr': 0.0}
            }
        
        for p in products_b:
            if p['name'] in products_map:
                products_map[p['name']]['period_b'] = {
                    'shown': p['shown'], 
                    'clicked': p['clicked'], 
                    'ctr': p['ctr']
                }
            else:
                products_map[p['name']] = {
                    'name': p['name'],
                    'period_a': {'shown': 0, 'clicked': 0, 'ctr': 0.0},
                    'period_b': {'shown': p['shown'], 'clicked': p['clicked'], 'ctr': p['ctr']}
                }
        
        products_comparison = []
        for product in products_map.values():
            ctr_a = product['period_a']['ctr']
            ctr_b = product['period_b']['ctr']
            delta_ctr = calculate_delta(ctr_a, ctr_b, is_percentage=True)
            
            products_comparison.append({
                'name': product['name'],
                'period_a': product['period_a'],
                'period_b': product['period_b'],
                'delta_ctr': delta_ctr
            })
        
        products_comparison.sort(key=lambda x: x['period_b']['clicked'], reverse=True)
        
        return jsonify({
            'period_a': {
                'start': a_start.isoformat(),
                'end': a_end.isoformat(),
                'kpis': kpis_a
            },
            'period_b': {
                'start': b_start.isoformat(),
                'end': b_end.isoformat(),
                'kpis': kpis_b
            },
            'deltas': deltas,
            'significance': significance,
            'daily_trends': daily_trends,
            'products_comparison': products_comparison
        })
        
    except Exception as e:
        print(f"❌ Compare API error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500