from collections import defaultdict

def detect_duplicates(transactions):
    groups = defaultdict(list)
    for t in transactions:
        key = (t.date, t.description, t.amount)
        groups[key].append(t)
        
    duplicate_groups = []
    duplicate_alerts = []
    
    for key, txs in groups.items():
        if len(txs) > 1:
            duplicate_groups.append(txs)
            for t in txs:
                duplicate_alerts.append({
                    "transaction_id": t.id,
                    "amount": round(t.amount, 2),
                    "date": str(t.date),
                    "description": t.description,
                    "source": "duplicate",
                    "severity": "medium",
                    "confidence": 0.95,
                    "reason": "Duplicate payment detected."
                })
                
    return duplicate_groups, duplicate_alerts
