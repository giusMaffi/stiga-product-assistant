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
            top_categories=top_categories
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return f"Errore: {str(e)}", 500
