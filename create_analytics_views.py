#!/usr/bin/env python3
"""
Crea VIEWS PostgreSQL per analytics giornalieri
"""
import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL')

if not DATABASE_URL:
    print("❌ DATABASE_PUBLIC_URL non trovato!")
    exit(1)

print("🔌 Connessione a PostgreSQL...")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("📊 Creazione VIEWS...")

# VIEW 1: Daily Stats (KPI giornalieri)
print("  → analytics_daily_stats")
cur.execute("""
DROP VIEW IF EXISTS analytics_daily_stats CASCADE;

CREATE VIEW analytics_daily_stats AS
SELECT 
    d.date,
    COALESCE(sessions_count, 0) as total_sessions,
    COALESCE(queries_count, 0) as total_queries,
    COALESCE(products_shown, 0) as total_products_shown,
    COALESCE(clicks_count, 0) as total_clicks,
    CASE 
        WHEN COALESCE(products_shown, 0) > 0 
        THEN ROUND((COALESCE(clicks_count, 0)::numeric / products_shown) * 100, 2)
        ELSE 0 
    END as ctr_percent,
    CASE
        WHEN COALESCE(sessions_count, 0) > 0
        THEN ROUND((COALESCE(sessions_with_clicks, 0)::numeric / sessions_count) * 100, 2)
        ELSE 0
    END as engagement_rate,
    CASE
        WHEN COALESCE(sessions_count, 0) > 0
        THEN ROUND(COALESCE(products_shown, 0)::numeric / sessions_count, 2)
        ELSE 0
    END as avg_products_per_session
FROM (
    SELECT DISTINCT DATE(timestamp) as date 
    FROM analytics_queries
) d
LEFT JOIN (
    SELECT DATE(created_at) as date, COUNT(DISTINCT session_id) as sessions_count
    FROM analytics_sessions
    GROUP BY DATE(created_at)
) s ON d.date = s.date
LEFT JOIN (
    SELECT DATE(timestamp) as date, COUNT(*) as queries_count
    FROM analytics_queries
    GROUP BY DATE(timestamp)
) q ON d.date = q.date
LEFT JOIN (
    SELECT DATE(timestamp) as date, SUM(products_count) as products_shown
    FROM analytics_results
    WHERE products_count > 0
    GROUP BY DATE(timestamp)
) r ON d.date = r.date
LEFT JOIN (
    SELECT DATE(timestamp) as date, COUNT(*) as clicks_count, COUNT(DISTINCT session_id) as sessions_with_clicks
    FROM analytics_clicks
    GROUP BY DATE(timestamp)
) c ON d.date = c.date
ORDER BY d.date DESC;
""")

# VIEW 2: Top Queries Daily
print("  → analytics_top_queries_daily")
cur.execute("""
DROP VIEW IF EXISTS analytics_top_queries_daily CASCADE;

CREATE VIEW analytics_top_queries_daily AS
SELECT 
    DATE(timestamp) as date,
    query,
    COUNT(*) as count
FROM analytics_queries
GROUP BY DATE(timestamp), query
ORDER BY DATE(timestamp) DESC, count DESC;
""")

# VIEW 3: Top Products Daily
print("  → analytics_top_products_daily")
cur.execute("""
DROP VIEW IF EXISTS analytics_top_products_daily CASCADE;

CREATE VIEW analytics_top_products_daily AS
SELECT 
    DATE(timestamp) as date,
    product_name,
    product_category,
    COUNT(*) as clicks
FROM analytics_clicks
GROUP BY DATE(timestamp), product_name, product_category
ORDER BY DATE(timestamp) DESC, clicks DESC;
""")

# VIEW 4: Top Categories Daily
print("  → analytics_top_categories_daily")
cur.execute("""
DROP VIEW IF EXISTS analytics_top_categories_daily CASCADE;

CREATE VIEW analytics_top_categories_daily AS
SELECT 
    DATE(timestamp) as date,
    UNNEST(categories) as category,
    COUNT(*) as count
FROM analytics_results
WHERE categories IS NOT NULL AND array_length(categories, 1) > 0
GROUP BY DATE(timestamp), category
ORDER BY DATE(timestamp) DESC, count DESC;
""")

# Aggiungi indici per performance
print("📈 Creazione indici...")
cur.execute("""
CREATE INDEX IF NOT EXISTS idx_queries_date ON analytics_queries(DATE(timestamp));
CREATE INDEX IF NOT EXISTS idx_results_date ON analytics_results(DATE(timestamp));
CREATE INDEX IF NOT EXISTS idx_clicks_date ON analytics_clicks(DATE(timestamp));
CREATE INDEX IF NOT EXISTS idx_sessions_date ON analytics_sessions(DATE(created_at));
""")

conn.commit()
cur.close()
conn.close()

print("✅ VIEWS create con successo!")
print("📊 Views disponibili:")
print("   - analytics_daily_stats")
print("   - analytics_top_queries_daily")
print("   - analytics_top_products_daily")
print("   - analytics_top_categories_daily")
