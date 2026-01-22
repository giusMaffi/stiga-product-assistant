#!/usr/bin/env python3
"""
Inizializza database PostgreSQL per analytics
Crea tabella events e indici necessari
"""
import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv

# Carica .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Usa PUBLIC_URL per testing locale, altrimenti internal URL
DATABASE_URL = os.getenv('DATABASE_PUBLIC_URL') or os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL o DATABASE_PUBLIC_URL non trovato in .env")
    exit(1)

print(f"📡 Usando database: {DATABASE_URL.split('@')[1].split('/')[0]}")

print("="*70)
print("🗄️  INIZIALIZZAZIONE DATABASE ANALYTICS")
print("="*70)
print()

try:
    # Connessione
    print("📡 Connessione a PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    print("✅ Connesso!")
    print()
    
    # Crea tabella analytics_events
    print("📋 Creazione tabella analytics_events...")
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS analytics_events (
        id SERIAL PRIMARY KEY,
        session_id VARCHAR(64) NOT NULL,
        event_type VARCHAR(32) NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        data JSONB,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    cur.execute(create_table_query)
    conn.commit()
    print("✅ Tabella analytics_events creata!")
    print()
    
    # Crea indici per performance
    print("⚡ Creazione indici...")
    
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_session_id ON analytics_events(session_id);",
        "CREATE INDEX IF NOT EXISTS idx_event_type ON analytics_events(event_type);",
        "CREATE INDEX IF NOT EXISTS idx_timestamp ON analytics_events(timestamp);",
        "CREATE INDEX IF NOT EXISTS idx_created_at ON analytics_events(created_at DESC);"
    ]
    
    for idx_query in indices:
        cur.execute(idx_query)
    
    conn.commit()
    print("✅ Indici creati!")
    print()
    
    # Verifica
    print("🔍 Verifica tabella...")
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'analytics_events'
        ORDER BY ordinal_position;
    """)
    
    columns = cur.fetchall()
    print("Colonne:")
    for col_name, col_type in columns:
        print(f"  - {col_name}: {col_type}")
    print()
    
    # Conta eventi esistenti
    cur.execute("SELECT COUNT(*) FROM analytics_events;")
    count = cur.fetchone()[0]
    print(f"📊 Eventi attuali nel database: {count}")
    print()
    
    cur.close()
    conn.close()
    
    print("="*70)
    print("🎉 DATABASE PRONTO!")
    print("="*70)
    print()
    print("Prossimo passo: Migrare eventi da logs/user_queries.log")
    print("Comando: python scripts/migrate_logs_to_db.py")
    print()
    
except Exception as e:
    print(f"❌ Errore: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
