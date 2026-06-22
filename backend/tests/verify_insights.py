import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000"

def get_endpoint(endpoint):
    url = f"{BASE_URL}{endpoint}"
    print(f"Querying {url}...")
    try:
        with urllib.request.urlopen(url) as response:
            status = response.getcode()
            body = response.read().decode('utf-8')
            return status, json.loads(body)
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return 500, None

def verify_rounding(val):
    if isinstance(val, float):
        # Check if float has more than 2 decimal places in its actual value
        # by checking if rounding to 2 places matches the value within float precision tolerance.
        return abs(round(val, 2) - val) < 1e-9
    elif isinstance(val, dict):
        return all(verify_rounding(v) for v in val.values())
    elif isinstance(val, list):
        return all(verify_rounding(v) for v in val)
    return True

def run_tests():
    print("Starting Phase 4A verification tests...\n")

    # 1. Verify GET /monthly-summary
    status, body = get_endpoint("/monthly-summary")
    assert status == 200, f"Expected 200, got {status}"
    assert isinstance(body, dict), "Monthly summary should be a dictionary"
    for month, data in body.items():
        assert "income" in data, "income field missing"
        assert "expenses" in data, "expenses field missing"
        assert "profit" in data, "profit field missing"
        assert "largest_category" in data, "largest_category field missing"
        assert verify_rounding(data["income"]), f"income {data['income']} not rounded to 2 decimal places"
        assert verify_rounding(data["expenses"]), f"expenses {data['expenses']} not rounded to 2 decimal places"
        assert verify_rounding(data["profit"]), f"profit {data['profit']} not rounded to 2 decimal places"
        assert abs(data["income"] - data["expenses"] - data["profit"]) < 1e-9, "profit does not equal income - expenses"
    print("[OK] /monthly-summary verification passed.")

    # 2. Verify GET /top-expenses
    # Default limit=5
    status, body = get_endpoint("/top-expenses")
    assert status == 200
    assert len(body) == 5, f"Expected default limit 5, got {len(body)}"
    
    # Custom limit=3
    status, body_limit = get_endpoint("/top-expenses?limit=3")
    assert status == 200
    assert len(body_limit) == 3, f"Expected limit 3, got {len(body_limit)}"
    
    # Ordering verification (descending by abs(amount))
    amounts = [abs(item["amount"]) for item in body]
    assert amounts == sorted(amounts, reverse=True), f"Top expenses not sorted descending by absolute value: {amounts}"
    for item in body:
        assert verify_rounding(item["amount"]), f"amount {item['amount']} not rounded"
    print("[OK] /top-expenses verification passed.")

    # 3. Verify GET /top-income
    # Default limit=5
    status, body = get_endpoint("/top-income")
    assert status == 200
    assert len(body) == 5, f"Expected default limit 5, got {len(body)}"
    
    # Custom limit=2
    status, body_limit = get_endpoint("/top-income?limit=2")
    assert status == 200
    assert len(body_limit) == 2, f"Expected limit 2, got {len(body_limit)}"
    
    # Ordering verification (descending)
    amounts = [item["amount"] for item in body]
    assert amounts == sorted(amounts, reverse=True), f"Top income not sorted descending: {amounts}"
    for item in body:
        assert verify_rounding(item["amount"]), f"amount {item['amount']} not rounded"
    print("[OK] /top-income verification passed.")

    # 4. Verify GET /category-ranking
    status, body = get_endpoint("/category-ranking")
    assert status == 200
    assert "total_expenses" in body
    assert "categories" in body
    assert verify_rounding(body["total_expenses"])
    
    cats = body["categories"]
    assert len(cats) > 0, "No categories returned"
    amounts = [c["amount"] for c in cats]
    assert amounts == sorted(amounts, reverse=True), f"Category ranking not sorted descending: {amounts}"
    
    calc_sum = 0.0
    for c in cats:
        assert "category" in c
        assert "amount" in c
        assert "percentage" in c
        assert verify_rounding(c["amount"])
        assert verify_rounding(c["percentage"])
        calc_sum += c["amount"]
        
    assert abs(body["total_expenses"] - calc_sum) < 1e-9, f"Sum of category amounts ({calc_sum}) does not equal total_expenses ({body['total_expenses']})"
    total_pct = sum(c["percentage"] for c in cats)
    assert abs(total_pct - 100.0) < 1.0, f"Percentage sum is {total_pct}, expected approx 100%"
    print("[OK] /category-ranking verification passed.")

    # 5. Verify GET /anomalies
    status, body = get_endpoint("/anomalies")
    assert status == 200
    assert isinstance(body, list), "Anomalies should be a list"
    for anomaly in body:
        assert "description" in anomaly
        assert "amount" in anomaly
        assert "threshold" in anomaly
        assert "deviation" in anomaly
        assert verify_rounding(anomaly["amount"])
        assert verify_rounding(anomaly["threshold"])
        assert verify_rounding(anomaly["deviation"])
        # Check threshold math: deviation = abs(amount) - threshold
        assert abs(abs(anomaly["amount"]) - anomaly["threshold"] - anomaly["deviation"]) < 1e-9, "deviation math mismatch"
    print("[OK] /anomalies verification passed.")

    # 6. Verify GET /insights
    status, body = get_endpoint("/insights")
    assert status == 200
    assert "financial_status" in body
    assert "largest_category" in body
    assert "largest_category_percentage" in body
    assert "insights" in body
    assert isinstance(body["insights"], list)
    assert verify_rounding(body["largest_category_percentage"])
    print("[OK] /insights verification passed.")

    print("\nALL PHASE 4A TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
