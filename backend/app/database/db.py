"""
SQLite Database Layer for MotorGuard AI.
Manages persistent storage for:
  - Monitoring history logs (vibration readings, features, ML predictions, ISO severity)
  - Maintenance records (work orders, prescriptive recommendations, status)
  - System configuration & alarm thresholds
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data"))
DB_PATH = os.path.join(DB_DIR, "motorguard.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database with row factory enabled."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initializes SQLite database schema and creates necessary indexes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Monitoring history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monitoring_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        recording_id TEXT NOT NULL,
        file_id INTEGER NOT NULL,
        window_idx INTEGER NOT NULL,
        predicted_condition TEXT NOT NULL,
        confidence REAL NOT NULL,
        rms REAL NOT NULL,
        kurtosis REAL NOT NULL,
        peak_to_peak REAL NOT NULL,
        crest_factor REAL NOT NULL,
        variance REAL NOT NULL,
        health_status TEXT NOT NULL,
        urgency TEXT NOT NULL,
        severity_index REAL NOT NULL,
        model_used TEXT NOT NULL,
        probabilities_json TEXT NOT NULL
    )
    """)
    
    # 2. Maintenance recommendations and work orders
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maintenance_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        bearing_condition TEXT NOT NULL,
        severity_level TEXT NOT NULL,
        component TEXT NOT NULL,
        action_required TEXT NOT NULL,
        recommended_procedure TEXT NOT NULL,
        urgency TEXT NOT NULL,
        estimated_hours REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'PENDING',
        completed_at DATETIME
    )
    """)
    
    # 3. System configuration table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create indexes for high-performance querying
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON monitoring_logs(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_condition ON monitoring_logs(predicted_condition)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_maint_status ON maintenance_records(status)")
    
    # Populate default settings if not exists
    default_settings = {
        "active_model": "Random Forest",
        "rms_alarm_threshold": "0.25",
        "kurtosis_alarm_threshold": "4.5",
        "playback_step_delay_ms": "300",
        "persistence_filter_windows": "3"
    }
    for k, v in default_settings.items():
        cursor.execute("INSERT OR IGNORE INTO system_settings (key, value) VALUES (?, ?)", (k, v))
        
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


def log_monitoring_event(event_data: Dict[str, Any]) -> int:
    """Inserts a monitoring event log into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    prob_str = json.dumps(event_data.get("probabilities", {}))
    features = event_data.get("features", {})
    
    cursor.execute("""
    INSERT INTO monitoring_logs (
        recording_id, file_id, window_idx, predicted_condition, confidence,
        rms, kurtosis, peak_to_peak, crest_factor, variance,
        health_status, urgency, severity_index, model_used, probabilities_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event_data.get("recording_id", "UNKNOWN"),
        event_data.get("file_id", 0),
        event_data.get("window_idx", 0),
        event_data.get("predicted_condition", "UNKNOWN"),
        event_data.get("confidence", 0.0),
        features.get("rms", 0.0),
        features.get("kurtosis", 3.0),
        features.get("peak_to_peak", 0.0),
        features.get("crest_factor", 1.0),
        features.get("variance", 0.0),
        event_data.get("health_status", "OPTIMAL"),
        event_data.get("urgency", "LOW"),
        event_data.get("severity_index", 0.0),
        event_data.get("model_used", "Random Forest"),
        prob_str
    ))
    
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id


def get_recent_monitoring_logs(limit: int = 50, condition_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves recent monitoring logs ordered chronologically descending."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if condition_filter:
        cursor.execute("""
        SELECT * FROM monitoring_logs WHERE predicted_condition = ? ORDER BY id DESC LIMIT ?
        """, (condition_filter, limit))
    else:
        cursor.execute("""
        SELECT * FROM monitoring_logs ORDER BY id DESC LIMIT ?
        """, (limit,))
        
    rows = cursor.fetchall()
    results = []
    for r in rows:
        d = dict(r)
        d["probabilities"] = json.loads(d["probabilities_json"])
        results.append(d)
        
    conn.close()
    return results


def clear_monitoring_logs():
    """Clears all monitoring history logs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM monitoring_logs")
    conn.commit()
    conn.close()


def add_maintenance_record(record: Dict[str, Any]) -> int:
    """Inserts a new maintenance recommendation / work order."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO maintenance_records (
        bearing_condition, severity_level, component, action_required,
        recommended_procedure, urgency, estimated_hours, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record["bearing_condition"],
        record["severity_level"],
        record["component"],
        record["action_required"],
        record["recommended_procedure"],
        record["urgency"],
        record.get("estimated_hours", 2.0),
        record.get("status", "PENDING")
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id


def get_all_maintenance_records() -> List[Dict[str, Any]]:
    """Fetches all maintenance work orders."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM maintenance_records ORDER BY id DESC")
    rows = cursor.fetchall()
    results = [dict(r) for r in rows]
    conn.close()
    return results


def update_maintenance_status(record_id: int, new_status: str) -> bool:
    """Updates the status of a maintenance work order (e.g. PENDING -> IN_PROGRESS -> COMPLETED)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    completed_at = datetime.utcnow().isoformat() if new_status == "COMPLETED" else None
    cursor.execute("""
    UPDATE maintenance_records SET status = ?, completed_at = ? WHERE id = ?
    """, (new_status, completed_at, record_id))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


# Initialize automatically on module load
init_database()
