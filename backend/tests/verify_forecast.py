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
    if val is None:
        return True
    if isinstance(val, float):
        return abs(round(val, 2) - val) < 1e-9
    elif isinstance(val, dict):
        return all(verify_rounding(v) for v in val.values())
    elif isinstance(val, list):
        return all(verify_rounding(v) for v in val)
    return True

def run_tests():
    print("Starting Phase 4B forecasting verification tests...\n")

    # 1. Verify GET /monthly-series
    status, body = get_endpoint("/monthly-series")
    assert status == 200, f"Expected 200, got {status}"
    assert isinstance(body, list), "Monthly series must be a list"
    assert len(body) > 0, "Monthly series should not be empty"
    for item in body:
        assert "month" in item
        assert "income" in item
        assert "expenses" in item
        assert verify_rounding(item["income"])
        assert verify_rounding(item["expenses"])
    print("[OK] /monthly-series verification passed.")

    # 2. Verify GET /future-income
    status, body = get_endpoint("/future-income")
    assert status == 200
    assert "predicted_income" in body
    assert "method" in body
    assert "months_used" in body
    assert body["method"] == "moving_average"
    assert verify_rounding(body["predicted_income"])
    print("[OK] /future-income verification passed.")

    # 3. Verify GET /future-expenses
    status, body = get_endpoint("/future-expenses")
    assert status == 200
    assert "predicted_expenses" in body
    assert "method" in body
    assert "months_used" in body
    assert body["method"] == "moving_average"
    assert verify_rounding(body["predicted_expenses"])
    print("[OK] /future-expenses verification passed.")

    # 4. Verify GET /cash-runway
    status, body = get_endpoint("/cash-runway")
    assert status == 200
    assert "current_balance" in body
    assert "average_monthly_expenses" in body
    assert "average_monthly_income" in body
    assert "net_burn" in body
    assert "months_remaining" in body
    assert "status" in body
    
    assert verify_rounding(body["current_balance"])
    assert verify_rounding(body["average_monthly_expenses"])
    assert verify_rounding(body["average_monthly_income"])
    assert verify_rounding(body["net_burn"])
    assert verify_rounding(body["months_remaining"])

    # Cashflow positive checks since total income > expenses in current database state
    assert body["average_monthly_income"] > body["average_monthly_expenses"]
    assert body["net_burn"] == 0.0
    assert body["months_remaining"] is None
    assert body["status"] == "cashflow_positive"
    print("[OK] /cash-runway verification passed.")

    # 5. Verify GET /trend-analysis
    status, body = get_endpoint("/trend-analysis")
    assert status == 200
    assert "income" in body
    assert "expenses" in body
    
    for key in ["income", "expenses"]:
        trend_info = body[key]
        assert "slope" in trend_info
        assert "trend" in trend_info
        assert trend_info["trend"] in ["increasing", "decreasing", "stable"]
        assert verify_rounding(trend_info["slope"])
        
        # Verify slope tolerance classification logic (epsilon = 0.05)
        slope = trend_info["slope"]
        expected_trend = "stable"
        if slope > 0.05:
            expected_trend = "increasing"
        elif slope < -0.05:
            expected_trend = "decreasing"
        assert trend_info["trend"] == expected_trend, f"Expected trend {expected_trend} for slope {slope}, got {trend_info['trend']}"
    print("[OK] /trend-analysis verification passed.")

    # 6. Verify GET /forecast
    status, body = get_endpoint("/forecast")
    assert status == 200
    assert "predicted_income" in body
    assert "predicted_expenses" in body
    assert "income_trend" in body
    assert "expenses_trend" in body
    assert "months_remaining" in body
    assert "runway_status" in body
    assert "confidence" in body
    
    assert body["confidence"] in ["high", "medium", "low"]
    assert body["months_remaining"] is None
    assert body["runway_status"] == "cashflow_positive"
    # Confidence must be "low" because we only have 1 month of historical data (< 6 months)
    assert body["confidence"] == "low"
    
    assert verify_rounding(body["predicted_income"])
    assert verify_rounding(body["predicted_expenses"])
    print("[OK] /forecast verification passed.")

    print("\nALL PHASE 4B FORECAST TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
