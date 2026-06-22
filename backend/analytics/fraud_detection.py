import numpy as np
from sklearn.ensemble import IsolationForest
from collections import defaultdict

def detect_large_transactions(transactions):
    if len(transactions) < 2:
        return []
    
    amounts = [abs(t.amount) for t in transactions]
    mean = np.mean(amounts)
    std = np.std(amounts)
    
    if std < 1e-9:
        return []
        
    threshold = mean + 2 * std
    alerts = []
    for t in transactions:
        if abs(t.amount) > threshold:
            alerts.append({
                "transaction_id": t.id,
                "amount": round(t.amount, 2),
                "date": str(t.date),
                "description": t.description,
                "source": "large_transaction",
                "severity": "warning",
                "confidence": 0.80,
                "reason": "Transaction amount significantly exceeds normal spending."
            })
    return alerts

def detect_isolation_forest_anomalies(transactions):
    if len(transactions) < 5:
        return []
        
    X = np.array([[abs(t.amount), t.amount] for t in transactions])
    clf = IsolationForest(contamination=0.1, random_state=42)
    preds = clf.fit_predict(X)
    scores = clf.decision_function(X)
    
    alerts = []
    for i, t in enumerate(transactions):
        if preds[i] == -1:
            score_val = scores[i]
            # Normalize decision score to [0, 1] confidence range.
            # Decision scores for anomalies are negative (lower means more anomalous).
            confidence = round(min(1.0, max(0.0, 0.5 + abs(score_val))), 2)
            alerts.append({
                "transaction_id": t.id,
                "amount": round(t.amount, 2),
                "date": str(t.date),
                "description": t.description,
                "source": "isolation_forest",
                "severity": "critical",
                "confidence": confidence,
                "reason": "Isolation Forest flagged this transaction as statistically anomalous."
            })
    return alerts

def detect_rapid_transactions(transactions):
    by_date = defaultdict(list)
    for t in transactions:
        by_date[t.date].append(t)
        
    alerts = []
    for date, txs in by_date.items():
        if len(txs) < 2:
            continue
        
        flagged_ids = set()
        for i in range(len(txs)):
            for j in range(i + 1, len(txs)):
                t1, t2 = txs[i], txs[j]
                diff = abs(abs(t1.amount) - abs(t2.amount))
                avg_amt = (abs(t1.amount) + abs(t2.amount)) / 2.0
                
                # Check if difference is <= 2.00 or within 5% of their average
                if diff <= 2.00 or (avg_amt > 0 and (diff / avg_amt) <= 0.05):
                    flagged_ids.add(t1.id)
                    flagged_ids.add(t2.id)
                    
        for t in txs:
            if t.id in flagged_ids:
                alerts.append({
                    "transaction_id": t.id,
                    "amount": round(t.amount, 2),
                    "date": str(t.date),
                    "description": t.description,
                    "source": "rapid_transaction",
                    "severity": "medium",
                    "confidence": 0.70,
                    "reason": "Multiple transactions occurred on the same date with similar amounts."
                })
    return alerts
