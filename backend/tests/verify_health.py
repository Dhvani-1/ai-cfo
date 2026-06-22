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
    print("Starting updated Phase 5 health verification tests...\n")

    # 1. Verify GET /savings-ratio
    status, body = get_endpoint("/savings-ratio")
    assert status == 200, f"Expected 200, got {status}"
    assert isinstance(body, float), "Savings ratio must be a float"
    assert verify_rounding(body)
    print("[OK] /savings-ratio verification passed.")

    # 2. Verify GET /expense-ratio
    status, body = get_endpoint("/expense-ratio")
    assert status == 200
    assert isinstance(body, float), "Expense ratio must be a float"
    assert verify_rounding(body)
    print("[OK] /expense-ratio verification passed.")

    # 3. Verify GET /health-score
    status, body = get_endpoint("/health-score")
    assert status == 200
    assert "health_score" in body
    assert "components" in body
    assert "raw" in body["components"]
    assert "weighted" in body["components"]
    
    # Check raw component keys
    raw = body["components"]["raw"]
    assert "savings_ratio" in raw
    assert "expense_ratio" in raw
    assert "risk_level" in raw
    assert "cashflow_status" in raw
    
    # Check weighted component keys
    weighted = body["components"]["weighted"]
    assert "savings_ratio_score" in weighted
    assert "expense_ratio_score" in weighted
    assert "risk_component" in weighted
    assert "cashflow_component" in weighted
    
    # Check weighted components sum consistency
    calc_score = sum(weighted.values())
    assert abs(body["health_score"] - calc_score) < 0.05, f"Sum of components ({calc_score}) does not match health_score ({body['health_score']})"
    assert 0.0 <= body["health_score"] <= 100.0
    
    assert verify_rounding(body["health_score"])
    assert verify_rounding(weighted)
    print("[OK] /health-score verification passed.")

    # 4. Verify GET /financial-grade
    status, body = get_endpoint("/financial-grade")
    assert status == 200
    assert "score" in body
    assert "grade" in body
    assert "description" in body
    assert "color" in body
    assert verify_rounding(body["score"])
    
    # Verify grade boundary and colors
    grade = body["grade"]
    desc = body["description"]
    color = body["color"]
    
    expected_desc = {
        "A": "Excellent",
        "B": "Good",
        "C": "Average",
        "D": "Poor",
        "F": "Critical"
    }[grade]
    expected_color = {
        "A": "green",
        "B": "blue",
        "C": "yellow",
        "D": "orange",
        "F": "red"
    }[grade]
    
    assert desc == expected_desc, f"Expected desc {expected_desc}, got {desc}"
    assert color == expected_color, f"Expected color {expected_color}, got {color}"
    print("[OK] /financial-grade verification passed.")

    # 5. Verify GET /risk-analysis
    status, body = get_endpoint("/risk-analysis")
    assert status == 200
    assert "risk_level" in body
    assert "risk_score" in body
    assert "description" in body
    assert "reasons" in body
    
    # Verify risk score mappings and descriptions
    level = body["risk_level"]
    score = body["risk_score"]
    desc = body["description"]
    
    expected_score = {"low": 20, "medium": 50, "high": 80}[level]
    expected_desc = {"low": "Low financial risk", "medium": "Moderate financial risk", "high": "High financial risk"}[level]
    
    assert score == expected_score, f"Expected risk score {expected_score}, got {score}"
    assert desc == expected_desc, f"Expected risk description {expected_desc}, got {desc}"
    assert isinstance(body["reasons"], list)
    print("[OK] /risk-analysis verification passed.")

    # 6. Verify GET /recommendations
    status, body = get_endpoint("/recommendations")
    assert status == 200
    assert isinstance(body, list)
    assert len(body) > 0, "Recommendations list should not be empty"
    
    # Verify categories, severities, priority fields, and sorting
    last_priority = 0
    valid_categories = ["savings", "expenses", "cashflow", "risk", "housing", "forecast"]
    for rec in body:
        assert "severity" in rec
        assert "priority" in rec
        assert "category" in rec
        assert "message" in rec
        assert rec["severity"] in ["info", "warning", "critical"]
        assert rec["category"] in valid_categories
        
        expected_priority = {"critical": 1, "warning": 2, "info": 3}[rec["severity"]]
        assert rec["priority"] == expected_priority, f"Expected priority {expected_priority}, got {rec['priority']}"
        
        # Verify ordering is sorted ascending by priority (1 then 2 then 3)
        assert rec["priority"] >= last_priority, f"Recommendations not sorted correctly by priority: {rec['priority']} < {last_priority}"
        last_priority = rec["priority"]
    print("[OK] /recommendations verification passed.")

    # 7. Verify GET /financial-health (Nested consolidated schema)
    status, body = get_endpoint("/financial-health")
    assert status == 200
    assert "health_score" in body
    assert "grade" in body
    assert "risk" in body
    assert "ratios" in body
    assert "recommendations" in body
    
    # Check nested health_score layout
    assert "score" in body["health_score"]
    assert "components" in body["health_score"]
    assert "raw" in body["health_score"]["components"]
    assert "weighted" in body["health_score"]["components"]
    
    # Check nested grade layout
    assert "score" in body["grade"]
    assert "grade" in body["grade"]
    assert "description" in body["grade"]
    assert "color" in body["grade"]
    
    # Check nested risk layout
    assert "risk_level" in body["risk"]
    assert "risk_score" in body["risk"]
    assert "description" in body["risk"]
    assert "reasons" in body["risk"]
    
    # Check score consistency: low risk + positive cash flow should not produce poor grades (D or F)
    # Since our database has low risk and positive cash flow, check that the grade is C or higher (A, B, or C)
    if body["risk"]["risk_level"] == "low" and body["risk"]["risk_score"] == 20:
        assert body["grade"]["grade"] in ["A", "B", "C"], f"Expected healthy grade for low risk + positive cash flow, got {body['grade']['grade']}"
        
    print("[OK] /financial-health verification passed.")

    print("\nALL UPDATED PHASE 5 HEALTH TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
