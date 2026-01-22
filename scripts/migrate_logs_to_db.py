#!/usr/bin/env python3
"""
Migra eventi da logs/user_queries.log a PostgreSQL
"""
import psycopg2
import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Carica .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

DATABASE_URL = os.getenv('DATABASE_PUBLIC_URL') or os.getenv('DATABASE_URL')
LOG_FILE = Path(__file__).parent.parent / 'logs' / 'user_queries.log'

print("="*70)
print("📦 MIGRAZIONE LOG → DATABASE")
print("="*70)
print()

if not LOG_FILE.exists():
    print(f"❌ File log non trovato: {LOG_FILE}")
    exit(1)

try:
    # Connessione
    print("📡 Connessione a PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    print("✅ Connesso!")
    print()
    
    # Leggi log file
    print(f"📂 Lettura {LOG_FILE}...")
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 Trovate {len(lines)} righe")
    print()
    
    # Parse e insert
    print("💾 Inserimento eventi...")
    
    inserted = 0
    skipped = 0
    
    for i, line in enumerate(lines, 1):
        try:
            # Parse: "2026-01-18 18:05:57,337 - {...json...}"
            parts = line.split(' - ', 1)
            if len(parts) != 2:
                print(f"⚠️  Riga {i}: formato invalido, skip")
                skipped += 1
                continue
            
            # Parse JSON
            event_data = json.loads(parts[1])
            
            # Estrai campi
            event_type = event_data.get('type')
            timestamp_str = event_data.get('timestamp')
            session_id = event_data.get('session')
            
            # Converti timestamp ISO a datetime
            timestamp = datetime.fromisoformat(timestamp_str)
            
            # Rimuovi campi già estratti dal JSON data
            data_json = {k: v for k, v in event_data.items() 
                        if k not in ['type', 'timestamp', 'session']}
            
            # Insert
            cur.execute("""
                INSERT INTO analytics_events 
                (session_id, event_type, timestamp, data)
                VALUES (%s, %s, %s, %s)
            """, (session_id, event_type, timestamp, json.dumps(data_json)))
            
            inserted += 1
            
            if inserted % 10 == 0:
                print(f"  ... {inserted} eventi inseriti")
            
        except Exception as e:
            print(f"⚠️  Riga {i}: errore - {e}")
            skipped += 1
            continue
    
    # Commit
    conn.commit()
    print()
    print("✅ Commit completato!")
    print()
    
    # Verifica
    cur.execute("SELECT COUNT(*) FROM analytics_events;")
    total = cur.fetchone()[0]
    
    cur.execute("SELECT event_type, COUNT(*) FROM analytics_events GROUP BY event_type;")
    by_type = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Report
    print("="*70)
    print("📊 REPORT MIGRAZIONE")
    print("="*70)
    print(f"Righe totali lette: {len(lines)}")
    print(f"Eventi inseriti: {inserted}")
    print(f"Righe skippate: {skipped}")
    print(f"Totale eventi in DB: {total}")
    print()
    print("Eventi per tipo:")
    for event_type, count in by_type:
        print(f"  - {event_type}: {count}")
    print()
    print("🎉 MIGRAZIONE COMPLETATA!")
    print("="*70)
    
except Exception as e:
    print(f"❌ Errore: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
