from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.transaction import Transaction
from models.user import User
from auth.dependencies import get_current_user
from analytics.fraud_detection import (
    detect_large_transactions,
    detect_isolation_forest_anomalies,
    detect_rapid_transactions
)
from analytics.duplicate_detection import detect_duplicates

router = APIRouter()

def get_merged_alerts_list(db: Session, current_user: User):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    if not transactions:
        return []
        
    # Gather raw alerts from all detectors
    large = detect_large_transactions(transactions)
    if_anom = detect_isolation_forest_anomalies(transactions)
    rapid = detect_rapid_transactions(transactions)
    _, duplicates = detect_duplicates(transactions)
    
    all_raw = large + if_anom + rapid + duplicates
    
    # Map tx_id to list of raw alerts
    from collections import defaultdict
    tx_alerts = defaultdict(list)
    for alert in all_raw:
        tx_alerts[alert["transaction_id"]].append(alert)
        
    tx_map = {t.id: t for t in transactions}
    
    sev_priority = {
        "critical": 3,
        "high": 3,
        "warning": 2,
        "medium": 2,
        "low": 1,
        "info": 1
    }
    
    merged_list = []
    for tx_id, alerts in tx_alerts.items():
        t = tx_map.get(tx_id)
        if not t:
            continue
            
        sources = list(dict.fromkeys([a["source"] for a in alerts]))
        reasons = list(dict.fromkeys([a["reason"] for a in alerts]))
        
        # Determine highest severity
        highest_sev = "low"
        highest_priority = 0
        for a in alerts:
            p = sev_priority.get(a["severity"].lower(), 0)
            if p > highest_priority:
                highest_priority = p
                highest_sev = a["severity"]
                 
        # Determine highest confidence
        max_confidence = max(a["confidence"] for a in alerts)
        
        # Calculate cumulative fraud score:
        # duplicate (+40), large_transaction (+20), rapid_transaction (+15), isolation_forest (+30)
        score = 0
        if "duplicate" in sources:
            score += 40
        if "large_transaction" in sources:
            score += 20
        if "rapid_transaction" in sources:
            score += 15
        if "isolation_forest" in sources:
            score += 30
        fraud_score = min(100, max(0, score))
        
        # Determine fraud level
        if fraud_score <= 30:
            fraud_level = "Low"
        elif fraud_score <= 60:
            fraud_level = "Medium"
        else:
            fraud_level = "High"
 
        # Determine fraud category based on prioritized sources
        if "isolation_forest" in sources:
            fraud_category = "anomaly"
        elif "large_transaction" in sources:
            fraud_category = "abnormal_amount"
        elif "duplicate" in sources:
            fraud_category = "duplicate_payment"
        elif "rapid_transaction" in sources:
            fraud_category = "repeated_payment"
        else:
            fraud_category = "anomaly"
 
        import datetime
        generated_at = datetime.datetime.utcnow().isoformat()
        
        merged_list.append({
            "transaction_id": tx_id,
            "transaction": {
                "date": str(t.date),
                "description": t.description,
                "amount": round(t.amount, 2),
                "category": t.category
            },
            "amount": round(t.amount, 2),
            "date": str(t.date),
            "description": t.description,
            "sources": sources,
            "reasons": reasons,
            "reason": "; ".join(reasons), # singular fallback for compatibility
            "severity": highest_sev,
            "confidence": round(max_confidence, 2),
            "fraud_score": fraud_score,
            "fraud_level": fraud_level,
            "fraud_category": fraud_category,
            "generated_at": generated_at
        })
        
    return merged_list

@router.get("/fraud-alerts")
def fraud_alerts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_merged_alerts_list(db, current_user)

@router.get("/duplicate-transactions")
def duplicate_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    dup_groups, _ = detect_duplicates(transactions)
    return dup_groups

@router.get("/suspicious-transactions")
def suspicious_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_merged_alerts_list(db, current_user)

@router.get("/fraud-summary")
def fraud_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    merged_alerts = get_merged_alerts_list(db, current_user)
    
    total_alerts = len(merged_alerts)
    if total_alerts == 0:
        return {
            "total_alerts": 0,
            "high_severity": 0,
            "medium_severity": 0,
            "low_severity": 0,
            "average_fraud_score": 0.0,
            "highest_fraud_score": 0,
            "highest_risk_transaction_id": None
        }
        
    high_count = 0
    medium_count = 0
    low_count = 0
    total_score = 0.0
    highest_score = 0
    highest_risk_id = None
    
    for alert in merged_alerts:
        sev = alert["severity"].lower()
        if sev in ("critical", "high"):
            high_count += 1
        elif sev in ("warning", "medium"):
            medium_count += 1
        else:
            low_count += 1
            
        score = alert["fraud_score"]
        total_score += score
        
        if score > highest_score:
            highest_score = score
            highest_risk_id = alert["transaction_id"]
        elif highest_risk_id is None:
            highest_risk_id = alert["transaction_id"]
        
    avg_score = round(total_score / total_alerts, 2)
    
    return {
        "total_alerts": total_alerts,
        "high_severity": high_count,
        "medium_severity": medium_count,
        "low_severity": low_count,
        "average_fraud_score": avg_score,
        "highest_fraud_score": highest_score,
        "highest_risk_transaction_id": highest_risk_id
    }

