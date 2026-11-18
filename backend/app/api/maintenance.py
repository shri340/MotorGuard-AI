"""
FastAPI Endpoints for Historical Analysis and Prescriptive Maintenance Recommendations.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import Dict, Any, List, Optional

from backend.app.database.db import (
    get_recent_monitoring_logs,
    clear_monitoring_logs,
    add_maintenance_record,
    get_all_maintenance_records,
    update_maintenance_status,
    get_db_connection
)
from backend.app.data.cwru_metadata import CLASS_NAMES

router = APIRouter(prefix="/api", tags=["History & Maintenance"])

# Prescriptive maintenance engineering playbook
PRESCRIPTIVE_PLAYBOOK = {
    "Healthy": {
        "status": "OPTIMAL",
        "action": "Routine Preventive Monitoring",
        "procedure": "Maintain standard 500-hour lubrication schedule. Inspect drive belt tension and verify motor grounding.",
        "urgency": "LOW",
        "component": "Drive-End Deep Groove Ball Bearing (SKF 6205-2RS)",
        "estimated_hours": 1.0,
        "recommendation": "Bearing is operating within baseline ISO 10816 vibration limits (RMS < 0.1 g). No corrective action required."
    },
    "Inner Race Fault": {
        "status": "WARNING",
        "action": "Schedule Bearing Replacement During Next Planned Outage",
        "procedure": "1. Verify shaft alignment and radial runout. 2. Lockout/tagout motor. 3. Remove drive pulley and DE bearing housing. 4. Inspect inner ring seat on shaft for fretting corrosion. 5. Heat new SKF 6205 bearing with induction heater (110°C) and press-fit onto shaft. 6. Regrease with Polyrex EM grease.",
        "urgency": "HIGH",
        "component": "Drive-End Bearing Inner Ring / Raceway",
        "estimated_hours": 4.5,
        "recommendation": "Inner race defect detected. Ball passes over defect generate periodic high-frequency impacts. Plan replacement within 14 days to prevent catastrophic cage failure."
    },
    "Ball Fault": {
        "status": "CAUTION",
        "action": "Perform Lubrication Flush and Secondary Ultrasound Verification",
        "procedure": "1. Collect lubricant sample for ferrographic wear particle analysis. 2. Purge old grease and inject synthetic polyurea lubricant. 3. Monitor for reduction in crest factor and high-frequency acoustic emission. 4. If vibration spikes persist after relubrication, order replacement bearing.",
        "urgency": "MEDIUM",
        "component": "Drive-End Rolling Elements (Balls & Retainer Cage)",
        "estimated_hours": 2.5,
        "recommendation": "Rolling element defect detected. Spalled ball surface causes randomized impacts as balls spin. Immediate relubrication can dampen friction and buy operational time."
    },
    "Outer Race Fault": {
        "status": "CRITICAL",
        "action": "Immediate Controlled Shutdown and Bearing Replacement",
        "procedure": "1. Initiate immediate controlled motor shutdown. 2. Disconnect drive coupling. 3. Inspect bearing housing bore for out-of-roundness or loose fit. 4. Replace damaged bearing assembly. 5. Perform laser shaft alignment before restarting.",
        "urgency": "IMMEDIATE",
        "component": "Drive-End Bearing Outer Ring (Stationary Housing)",
        "estimated_hours": 5.0,
        "recommendation": "Severe outer race defect detected. Vibration energy is highly elevated (RMS > 0.6 g). Direct load-zone impacts risk housing bore damage and catastrophic shaft seizure if operated continuously."
    }
}


@router.get("/history/logs")
def get_history_logs(
    limit: int = Query(50, ge=5, le=500),
    condition: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Retrieves recorded monitoring event logs from SQLite."""
    logs = get_recent_monitoring_logs(limit=limit, condition_filter=condition)
    return {
        "count": len(logs),
        "limit": limit,
        "condition_filter": condition,
        "logs": logs
    }


@router.delete("/history/clear")
def clear_history() -> Dict[str, Any]:
    """Clears all monitoring history from the database."""
    clear_monitoring_logs()
    return {"status": "success", "message": "Monitoring history cleared."}


@router.get("/history/stats")
def get_history_stats() -> Dict[str, Any]:
    """Aggregates summary statistics from SQLite monitoring logs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM monitoring_logs")
    total_events = cursor.fetchone()[0]
    
    condition_counts = {}
    cursor.execute("SELECT predicted_condition, COUNT(*) FROM monitoring_logs GROUP BY predicted_condition")
    for r in cursor.fetchall():
        condition_counts[r[0]] = r[1]
        
    cursor.execute("SELECT AVG(rms), AVG(kurtosis), AVG(severity_index) FROM monitoring_logs")
    avg_row = cursor.fetchone()
    avg_rms = round(float(avg_row[0] or 0.0), 4)
    avg_kurt = round(float(avg_row[1] or 0.0), 4)
    avg_sev = round(float(avg_row[2] or 0.0), 2)
    
    cursor.execute("SELECT COUNT(*) FROM monitoring_logs WHERE health_status IN ('WARNING', 'CRITICAL')")
    alert_count = cursor.fetchone()[0]
    
    conn.close()
    return {
        "total_events_logged": total_events,
        "condition_breakdown": condition_counts,
        "average_rms": avg_rms,
        "average_kurtosis": avg_kurt,
        "average_severity_index": avg_sev,
        "critical_alerts_count": alert_count
    }


@router.get("/maintenance/playbook")
def get_maintenance_playbook() -> Dict[str, Any]:
    """Returns prescriptive maintenance playbook for all bearing fault modes."""
    return {
        "playbook": PRESCRIPTIVE_PLAYBOOK,
        "standards": "ISO 10816-3 (Vibration Severity Standards for Industrial Machines)"
    }


@router.get("/maintenance/recommendations/{condition}")
def get_recommendation_for_condition(condition: str) -> Dict[str, Any]:
    """Returns prescriptive guidance for a specific condition."""
    if condition not in PRESCRIPTIVE_PLAYBOOK:
        raise HTTPException(status_code=404, detail=f"Condition '{condition}' not recognized.")
    return {
        "condition": condition,
        "guidance": PRESCRIPTIVE_PLAYBOOK[condition]
    }


@router.get("/maintenance/records")
def get_maintenance_work_orders() -> Dict[str, Any]:
    """Retrieves all maintenance work orders from the database."""
    records = get_all_maintenance_records()
    return {
        "count": len(records),
        "records": records
    }


@router.post("/maintenance/records")
def create_maintenance_work_order(
    record: Dict[str, Any] = Body(...)
) -> Dict[str, Any]:
    """Creates a new maintenance work order in SQLite."""
    required = ["bearing_condition", "severity_level", "component", "action_required", "recommended_procedure", "urgency"]
    for f in required:
        if f not in record:
            raise HTTPException(status_code=400, detail=f"Missing required field: {f}")
            
    rec_id = add_maintenance_record(record)
    return {
        "status": "success",
        "record_id": rec_id,
        "message": f"Maintenance work order #{rec_id} created successfully."
    }


@router.patch("/maintenance/records/{record_id}/status")
def update_status(
    record_id: int,
    status: str = Body(..., embed=True)
) -> Dict[str, Any]:
    """Updates work order status (PENDING -> IN_PROGRESS -> COMPLETED)."""
    valid_statuses = ["PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED"]
    if status.upper() not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid_statuses}")
        
    success = update_maintenance_status(record_id, status.upper())
    if not success:
        raise HTTPException(status_code=404, detail=f"Work order #{record_id} not found.")
        
    return {
        "status": "success",
        "record_id": record_id,
        "new_status": status.upper()
    }
