import urllib.request
import json
import os
import datetime
import sys

# Configure python path to find modules in the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.transaction import Transaction


BASE_URL = "http://127.0.0.1:8000"

def get_endpoint(endpoint):
    import urllib.error
    url = f"{BASE_URL}{endpoint}"
    print(f"Querying GET {url}...")
    try:
        with urllib.request.urlopen(url) as response:
            status = response.getcode()
            body = response.read().decode('utf-8')
            return status, json.loads(body)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code} for {url}")
        return e.code, None
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return 500, None

def cleanup_db():
    db = SessionLocal()
    try:
        # Delete any pre-existing or test transactions containing [FraudTest]
        count = db.query(Transaction).filter(Transaction.description.like("%[FraudTest]%")).delete(synchronize_session=False)
        db.commit()
        if count > 0:
            print(f"Cleaned up {count} old [FraudTest] transactions from database.")
    except Exception as e:
        print(f"Cleanup error: {e}")
        db.rollback()
    finally:
        db.close()

def inject_baseline():
    db = SessionLocal()
    try:
        # Ingest 10 normal baseline transactions of small amounts
        baseline_amounts = [-100.0, -150.0, -200.0, -250.0, -300.0, -110.0, -120.0, -130.0, -140.0, -160.0]
        for i, amt in enumerate(baseline_amounts):
            tx = Transaction(
                date=datetime.date(2026, 6, 20),
                description=f"[FraudTest] Baseline {i}",
                amount=amt,
                category="Others",
                type="Expense"
            )
            db.add(tx)
        db.commit()
        print("Injected 10 normal baseline transactions.")
    except Exception as e:
        print(f"Injection error: {e}")
        db.rollback()
    finally:
        db.close()

def inject_anomalies():
    db = SessionLocal()
    try:
        # 1. Duplicate group (same date, desc, amount)
        tx_dup1 = Transaction(
            date=datetime.date(2026, 6, 21),
            description="[FraudTest] Duplicate Gas",
            amount=-80.00,
            category="Transport",
            type="Expense"
        )
        tx_dup2 = Transaction(
            date=datetime.date(2026, 6, 21),
            description="[FraudTest] Duplicate Gas",
            amount=-80.00,
            category="Transport",
            type="Expense"
        )
        db.add(tx_dup1)
        db.add(tx_dup2)
        
        # 2. Large transaction (amount = -100000.00, which will exceed 2 standard deviations and be an Isolation Forest anomaly)
        tx_large = Transaction(
            date=datetime.date(2026, 6, 22),
            description="[FraudTest] Large Purchase",
            amount=-100000.00,
            category="Shopping",
            type="Expense"
        )
        db.add(tx_large)
        
        # 3. Rapid same-date similar amount transactions
        tx_rapid1 = Transaction(
            date=datetime.date(2026, 6, 23),
            description="[FraudTest] Cab Ride 1",
            amount=-50.00,
            category="Transport",
            type="Expense"
        )
        tx_rapid2 = Transaction(
            date=datetime.date(2026, 6, 23),
            description="[FraudTest] Cab Ride 2",
            amount=-51.50,
            category="Transport",
            type="Expense"
        )
        db.add(tx_rapid1)
        db.add(tx_rapid2)
        
        db.commit()
        print("Injected anomalous test transactions.")
    except Exception as e:
        print(f"Anomaly injection error: {e}")
        db.rollback()
    finally:
        db.close()

def inject_few_transactions():
    db = SessionLocal()
    try:
        for i in range(3):
            tx = Transaction(
                date=datetime.date(2026, 6, 20),
                description=f"[FraudTest] Few {i}",
                amount=-100.0,
                category="Others",
                type="Expense"
            )
            db.add(tx)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

def run_tests():
    print("Starting Phase 7 Fraud Detection verification tests...\n")
    
    # --- Test 1: Empty database / safe defaults check ---
    cleanup_db()
    
    # If the user has other transactions in their DB, we temporarily save them,
    # but since this is our test suite, we check if GET /fraud-summary returns clean outputs when no alerts exist.
    # Note: to guarantee no alerts exist, we can check the return.
    status, summary = get_endpoint("/fraud-summary")
    assert status == 200
    assert "total_alerts" in summary
    assert "average_fraud_score" in summary
    assert "high_severity" in summary
    assert "medium_severity" in summary
    assert "low_severity" in summary
    print("[OK] Empty state safety checks passed.")
    
    # --- Test 2: Isolation Forest skip baseline check (< 5 transactions) ---
    from analytics.fraud_detection import detect_isolation_forest_anomalies
    class MockTransaction:
        def __init__(self, id, amount):
            self.id = id
            self.amount = amount
    mock_txs = [MockTransaction(i, -100.0) for i in range(3)]
    alerts_skip = detect_isolation_forest_anomalies(mock_txs)
    assert alerts_skip == [], "Isolation Forest should be skipped if count < 5"
    print("[OK] Isolation Forest skip check passed (skipped when count < 5).")

    
    # --- Test 3: Standard anomalies run ---
    cleanup_db()
    inject_baseline()
    inject_anomalies()
    
    # A: GET /fraud-alerts
    status, alerts = get_endpoint("/fraud-alerts")
    assert status == 200
    assert len(alerts) > 0, "No alerts triggered"
    
    # Find the large purchase transaction alert
    large_alert = None
    duplicate_alerts = []
    rapid_alerts = []
    
    for a in alerts:
        assert "transaction_id" in a
        assert "sources" in a
        assert "reasons" in a
        assert "severity" in a
        assert "confidence" in a
        assert "fraud_score" in a
        assert "generated_at" in a
        assert "fraud_level" in a
        assert "fraud_category" in a
        assert "transaction" in a
        
        # Verify transaction snapshot schema
        snap = a["transaction"]
        assert "date" in snap
        assert "description" in snap
        assert "amount" in snap
        assert "category" in snap
        assert isinstance(snap["amount"], (int, float))
        
        # Verify fraud level mapping values
        assert a["fraud_level"] in ("Low", "Medium", "High")
        
        # Verify fraud category mapping values
        assert a["fraud_category"] in ("anomaly", "abnormal_amount", "duplicate_payment", "repeated_payment")
        
        # Verify confidence range [0.0, 1.0]
        assert 0.0 <= a["confidence"] <= 1.0, f"Confidence {a['confidence']} out of bounds"
        # Verify fraud score bounds [0, 100]
        assert 0 <= a["fraud_score"] <= 100, f"Fraud score {a['fraud_score']} out of bounds"
        
        if "[FraudTest] Large Purchase" in a["description"]:
            large_alert = a
        if "[FraudTest] Duplicate Gas" in a["description"]:
            duplicate_alerts.append(a)
        if "[FraudTest] Cab Ride" in a["description"]:
            rapid_alerts.append(a)
            
    # B: Verify Deduplication / Merging on Large Purchase
    # It should be flagged by both large_transaction and isolation_forest!
    assert large_alert is not None, "Large purchase alert not found"
    assert "large_transaction" in large_alert["sources"]
    assert "isolation_forest" in large_alert["sources"]
    assert len(large_alert["sources"]) == 2, "Large purchase alert not deduplicated properly"
    assert large_alert["severity"] == "critical" # critical from isolation_forest > warning from large_transaction
    assert len(large_alert["reasons"]) == 2
    # Fraud score should be 50 (+20 for large +30 for Isolation Forest)
    assert large_alert["fraud_score"] == 50
    assert large_alert["fraud_level"] == "Medium" # 50 is between 31 and 60
    assert large_alert["fraud_category"] == "anomaly" # prioritized: isolation_forest (anomaly) > large_transaction (abnormal_amount)
    assert large_alert["transaction"]["category"] == "Shopping"
    print("[OK] Alert deduplication, merging, levels, categories, and fraud score bounds passed.")

    # C: GET /duplicate-transactions
    status, dup_groups = get_endpoint("/duplicate-transactions")
    assert status == 200
    assert len(dup_groups) >= 1
    found_dup_gas = False
    for group in dup_groups:
        assert isinstance(group, list)
        assert len(group) > 1
        if any("[FraudTest] Duplicate Gas" in tx["description"] for tx in group):
            found_dup_gas = True
    assert found_dup_gas, "Duplicate gas transactions not found in duplicate groups"
    print("[OK] Duplicate payment group detection passed.")

    # D: GET /suspicious-transactions
    status, suspicious = get_endpoint("/suspicious-transactions")
    assert status == 200
    for s in suspicious:
        assert "reason" in s or "reasons" in s
        assert "severity" in s
    print("[OK] GET /suspicious-transactions reasons and severities passed.")

    # E: GET /fraud-summary counts & average fraud score
    status, summary = get_endpoint("/fraud-summary")
    assert status == 200
    assert summary["total_alerts"] >= 5
    assert summary["high_severity"] >= 1 # Large purchase (critical)
    assert summary["medium_severity"] >= 4 # Duplicate gas (2) + Cab rides (2)
    assert summary["average_fraud_score"] > 0
    assert "highest_fraud_score" in summary
    assert "highest_risk_transaction_id" in summary
    assert summary["highest_fraud_score"] >= 50 # large_purchase has score 50
    assert summary["highest_risk_transaction_id"] is not None
    # Check rounding of average score
    assert abs(round(summary["average_fraud_score"], 2) - summary["average_fraud_score"]) < 1e-9
    print("[OK] GET /fraud-summary alert counts, highest score, highest risk ID, and average fraud score validation passed.")

    # Cleanup test run data
    cleanup_db()
    print("\nALL PHASE 7 FRAUD DETECTION TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
