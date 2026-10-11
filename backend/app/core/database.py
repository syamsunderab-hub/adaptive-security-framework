import sqlite3
import json
import time
from typing import List, Dict, Any, Optional
from .config import settings

def get_db_connection():
    conn = sqlite3.connect(settings.DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Nodes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nodes (
        node_id TEXT PRIMARY KEY,
        name TEXT,
        node_type TEXT,
        status TEXT,
        security_level TEXT,
        threat_score REAL,
        current_threat TEXT,
        cpu_usage REAL,
        network_traffic REAL,
        connections INTEGER,
        heartbeat_status TEXT,
        mape_k_stage TEXT,
        last_update REAL
    )
    """)

    # Security Events table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS security_events (
        id TEXT PRIMARY KEY,
        timestamp REAL,
        formatted_time TEXT,
        event_type TEXT,
        node_id TEXT,
        message TEXT,
        severity TEXT,
        details TEXT
    )
    """)

    # Threats table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS threats (
        threat_id TEXT PRIMARY KEY,
        node_id TEXT,
        threat_type TEXT,
        severity TEXT,
        confidence REAL,
        timestamp REAL,
        description TEXT,
        recommended_action TEXT,
        metrics_snapshot TEXT
    )
    """)

    # Adaptations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS adaptations (
        id TEXT PRIMARY KEY,
        timestamp REAL,
        node_id TEXT,
        previous_level TEXT,
        new_level TEXT,
        action_taken TEXT,
        trigger_threat TEXT,
        adaptation_mode TEXT,
        affected_nodes TEXT,
        details TEXT
    )
    """)

    # Heartbeats table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS heartbeats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        node_id TEXT,
        timestamp REAL,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

def log_event_db(event_id: str, timestamp: float, formatted_time: str, event_type: str, node_id: Optional[str], message: str, severity: str, details: Dict[str, Any]):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO security_events (id, timestamp, formatted_time, event_type, node_id, message, severity, details) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (event_id, timestamp, formatted_time, event_type, node_id, message, severity, json.dumps(details))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging event to DB: {e}")

def log_threat_db(threat_id: str, node_id: str, threat_type: str, severity: str, confidence: float, timestamp: float, description: str, recommended_action: str, metrics: Dict[str, Any]):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO threats (threat_id, node_id, threat_type, severity, confidence, timestamp, description, recommended_action, metrics_snapshot) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (threat_id, node_id, threat_type, severity, confidence, timestamp, description, recommended_action, json.dumps(metrics))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging threat to DB: {e}")

def log_adaptation_db(adapt_id: str, timestamp: float, node_id: str, prev_level: str, new_level: str, action: str, trigger: str, mode: str, affected: List[str], details: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO adaptations (id, timestamp, node_id, previous_level, new_level, action_taken, trigger_threat, adaptation_mode, affected_nodes, details) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (adapt_id, timestamp, node_id, prev_level, new_level, action, trigger, mode, json.dumps(affected), details)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging adaptation to DB: {e}")

def get_recent_events_db(limit: int = 50) -> List[Dict[str, Any]]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM security_events ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "timestamp": r["timestamp"],
                "formatted_time": r["formatted_time"],
                "event_type": r["event_type"],
                "node_id": r["node_id"],
                "message": r["message"],
                "severity": r["severity"],
                "details": json.loads(r["details"]) if r["details"] else {}
            })
        conn.close()
        return result
    except Exception as e:
        print(f"Error reading events from DB: {e}")
        return []
