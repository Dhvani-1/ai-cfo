import urllib.request
import json
import os
import datetime
import sys
import time
import re

# Configure python path to find modules in the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.user import User
from models.transaction import Transaction
from models.invoice import Invoice

BASE_URL = "http://127.0.0.1:8000"

def make_request(method, endpoint, payload=None, token=None, return_headers=False, is_multipart=False, multipart_data=None):
    import urllib.error
    url = f"{BASE_URL}{endpoint}"
    data = None
    headers = {}
    
    if token is not None:
        headers['Authorization'] = f"Bearer {token}"

    if is_multipart:
        # Construct multipart/form-data boundary
        boundary = "Boundary-AI-CFO-Final-Verification"
        headers['Content-Type'] = f"multipart/form-data; boundary={boundary}"
        
        body_parts = []
        for key, file_info in multipart_data.items():
            filename, file_content, content_type = file_info
            body_parts.append(f"--{boundary}".encode('utf-8'))
            body_parts.append(f'Content-Disposition: form-data; name="{key}"; filename="{filename}"'.encode('utf-8'))
            body_parts.append(f'Content-Type: {content_type}'.encode('utf-8'))
            body_parts.append(b"")
            body_parts.append(file_content if isinstance(file_content, bytes) else file_content.encode('utf-8'))
            
        body_parts.append(f"--{boundary}--".encode('utf-8'))
        body_parts.append(b"")
        data = b"\r\n".join(body_parts)
    elif payload is not None:
        data = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'
        
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            body = response.read()
            resp_headers = response.info()
            if return_headers:
                return status, body, resp_headers
            
            try:
                decoded_body = body.decode('utf-8')
                return status, json.loads(decoded_body)
            except Exception:
                return status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            parsed_body = json.loads(body)
        except Exception:
            parsed_body = body
        if return_headers:
            return e.code, parsed_body, e.headers
        return e.code, parsed_body
    except Exception as e:
        if return_headers:
            return 500, str(e), {}
        return 500, str(e)

def cleanup_db():
    db = SessionLocal()
    try:
        test_emails = ["verify_all_user_a@example.com", "verify_all_user_b@example.com"]
        users = db.query(User).filter(User.email.in_(test_emails)).all()
        user_ids = [u.id for u in users]
        
        if user_ids:
            # Delete transactions belonging to test users
            tx_count = db.query(Transaction).filter(Transaction.user_id.in_(user_ids)).delete(synchronize_session=False)
            # Delete invoices belonging to test users
            inv_count = db.query(Invoice).filter(Invoice.user_id.in_(user_ids)).delete(synchronize_session=False)
            # Delete test users
            user_count = db.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)
            db.commit()
            print(f"Cleaned up {user_count} test users, {tx_count} transactions, and {inv_count} invoices.")
        else:
            print("No test users to clean up.")
    except Exception as e:
        print(f"Cleanup error: {e}")
        db.rollback()
    finally:
        db.close()

def run_tests():
    print("=" * 60)
    print("STARTING FULL END-TO-END BACKEND INTEGRATION AUDIT")
    print("=" * 60)
    
    # 0. Clean database
    cleanup_db()
    
    # 1. Registration and Authentication checks
    print("\n--- 1. Testing Registration and Login ---")
    status, reg_res = make_request("POST", "/register", {
        "name": "Audit User A",
        "email": "verify_all_user_a@example.com",
        "password": "auditpassword12"
    })
    assert status == 200
    user_a_id = reg_res.get("id")
    print(f"[OK] Registration success for user_id={user_a_id}")
    
    # Duplicate email checks
    status, reg_dup = make_request("POST", "/register", {
        "name": "Audit User Duplicate",
        "email": "verify_all_user_a@example.com",
        "password": "auditpassword12"
    })
    assert status == 400
    print("[OK] Duplicate email rejected correctly.")
    
    # Weak password checks
    status, reg_weak = make_request("POST", "/register", {
        "name": "Audit User Weak",
        "email": "verify_all_user_weak@example.com",
        "password": "weak"
    })
    assert status == 400
    print("[OK] Weak password rejected correctly.")
    
    # Login and token retrieval
    status, login_res = make_request("POST", "/login", {
        "email": "verify_all_user_a@example.com",
        "password": "auditpassword12"
    })
    assert status == 200
    assert "access_token" in login_res
    assert login_res["token_type"] == "bearer"
    assert login_res["expires_in_minutes"] == 60
    token_a = login_res["access_token"]
    print("[OK] Login success, access token obtained and validated.")
    
    # GET /me endpoint check
    status, me_res = make_request("GET", "/me", token=token_a)
    assert status == 200
    assert me_res["email"] == "verify_all_user_a@example.com"
    assert me_res["statistics"]["transactions"] == 0
    assert me_res["statistics"]["invoices"] == 0
    print("[OK] GET /me stats returned 0 values for empty state (avoided nulls).")

    # 2. Empty-State Endpoint safety checks
    print("\n--- 2. Testing Empty-State Endpoint Safety (Returns 200, no crashes) ---")
    endpoints_to_test = [
        "/transactions",
        "/invoices",
        "/dashboard",
        "/cashflow",
        "/profit-loss",
        "/categories",
        "/monthly-summary",
        "/top-expenses",
        "/top-income",
        "/category-ranking",
        "/anomalies",
        "/insights",
        "/monthly-series",
        "/forecast",
        "/future-income",
        "/future-expenses",
        "/cash-runway",
        "/trend-analysis",
        "/health-score",
        "/financial-grade",
        "/risk-analysis",
        "/savings-ratio",
        "/expense-ratio",
        "/recommendations",
        "/financial-health",
        "/gst-summary",
        "/tax-estimate",
        "/tax-insights",
        "/tax-summary",
        "/fraud-alerts",
        "/duplicate-transactions",
        "/suspicious-transactions",
        "/fraud-summary",
        "/report-summary",
        "/export-pdf",
        "/export-excel"
    ]
    for ep in endpoints_to_test:
        status, res = make_request("GET", ep, token=token_a)
        assert status == 200, f"Endpoint {ep} failed with status {status}"
        print(f"[OK] Empty-state GET {ep} -> Status 200")
        
    # Chat empty-state
    status, chat_empty = make_request("POST", "/chat", {"question": "What was my salary?"}, token=token_a)
    assert status == 200
    assert "No financial records found" in chat_empty["answer"]
    print("[OK] Empty-state POST /chat -> Status 200 with fallback message")

    # 3. Data Ingestion (Transaction Upload & Invoice OCR)
    print("\n--- 3. Testing Data Ingestion (File upload and OCR) ---")
    
    # Upload CSV Transactions
    csv_content = (
        "Date,Description,Amount\n"
        "2026-06-01,Client Consulting Payment,3500.00\n"
        "2026-06-02,Office Rent Payment,-1200.00\n"
        "2026-06-03,Swiggy Restaurant,-150.00\n"
        "2026-06-03,Swiggy Restaurant Duplicate,-150.00\n"
        "2026-06-04,Hardware Depot Purchase,-800.00\n"
    )
    status, upload_tx_res = make_request(
        "POST", "/upload",
        token=token_a,
        is_multipart=True,
        multipart_data={
            "file": ("audit_transactions.csv", csv_content, "text/csv")
        }
    )
    assert status == 200
    print("[OK] Transaction CSV uploaded and categorized.")
    
    # Upload Invoice OCR (using mock ocr parser)
    invoice_ocr_text = (
        "Vendor: Swiggy food delivery\n"
        "Invoice Number: SW-9921\n"
        "Invoice Date: 2026-06-03\n"
        "GST Details: CGST 9.00 SGST 9.00\n"
        "Total: 150.00\n"
    )
    status, upload_inv_res = make_request(
        "POST", "/upload-invoice",
        token=token_a,
        is_multipart=True,
        multipart_data={
            "file": ("swiggy_invoice.txt", invoice_ocr_text, "text/plain")
        }
    )
    assert status == 200
    invoice_a_id = upload_inv_res.get("id")
    print(f"[OK] Invoice uploaded and parsed. Assigned invoice_id={invoice_a_id}")
    
    # Duplicate Invoice Prevention check
    status, upload_inv_dup = make_request(
        "POST", "/upload-invoice",
        token=token_a,
        is_multipart=True,
        multipart_data={
            "file": ("swiggy_invoice_copy.txt", invoice_ocr_text, "text/plain")
        }
    )
    assert status == 200
    assert upload_inv_dup.get("duplicate") is True
    print("[OK] Duplicate Invoice Ingestion rejected correctly.")

    # 4. Endpoints & Modules Data Integrations
    print("\n--- 4. Testing Populated Modules Integration ---")
    
    # A. Analytics dashboard
    status, dash = make_request("GET", "/dashboard", token=token_a)
    assert status == 200
    # Net cashflow should match (3500 - 1200 - 150 - 150 - 800) = 1200.00
    assert dash["profit_loss"]["net_profit"] == 1200.00
    print(f"[OK] Analytics Cross-check: Net Profit matches expected ${dash['profit_loss']['net_profit']}")
    
    # B. Forecasting
    status, fc = make_request("GET", "/forecast", token=token_a)
    assert status == 200
    assert fc["predicted_income"] > 0
    assert fc["runway_status"] == "cashflow_positive"
    print(f"[OK] Forecasting: Predicted Monthly Income computed.")
    
    # C. Health score
    status, health = make_request("GET", "/financial-health", token=token_a)
    assert status == 200
    assert "health_score" in health
    assert "grade" in health
    print(f"[OK] Health score computed correctly: {health['health_score']['score']} / Grade: {health['grade']['grade']}")
    
    # D. Fraud detection
    status, fraud = make_request("GET", "/fraud-summary", token=token_a)
    assert status == 200
    assert fraud["total_alerts"] > 0
    print(f"[OK] Fraud Detection alert merging verified. Alerts flagged: {fraud['total_alerts']}")
    
    # E. Tax Summary
    status, tax = make_request("GET", "/tax-summary", token=token_a)
    assert status == 200
    # GST paid from Swiggy invoice: 9.00 + 9.00 = 18.00 CGST+SGST
    assert tax["gst"]["total_gst_paid"] == 18.00
    assert "estimates only and should not be considered" in tax["disclaimer"]
    print(f"[OK] Tax Assistant: Total GST matches invoice: {tax['gst']['total_gst_paid']}. Disclaimer present.")

    # 5. RAG AI Chat grounded response test
    print("\n--- 5. Testing Grounded RAG Chat Answers ---")
    status, chat_ans1 = make_request("POST", "/chat", {"question": "What was my salary income or consulting fee?"}, token=token_a)
    assert status == 200
    ans1 = chat_ans1["answer"].lower()
    print(f"Chat response: {chat_ans1['answer']}")
    # Verify response contains relevant transaction text/digits
    assert "3500" in ans1 or "consulting" in ans1 or "3,500" in ans1
    print("[OK] Chat answers successfully grounded in retrieved transactions.")

    # 6. Multi-User Isolation Boundary Check
    print("\n--- 6. Testing Multi-User Isolation Boundary ---")
    
    # Register & Login User B
    status, reg_b = make_request("POST", "/register", {
        "name": "Audit User B",
        "email": "verify_all_user_b@example.com",
        "password": "auditpassword22"
    })
    assert status == 200
    user_b_id = reg_b.get("id")
    
    status, login_b = make_request("POST", "/login", {
        "email": "verify_all_user_b@example.com",
        "password": "auditpassword22"
    })
    assert status == 200
    token_b = login_b["access_token"]
    
    # Check that User B sees zero records
    status, txs_b = make_request("GET", "/transactions", token=token_b)
    assert len(txs_b) == 0
    
    status, invs_b = make_request("GET", "/invoices", token=token_b)
    assert len(invs_b) == 0
    print("[OK] User B records lists are clean (0 items). Data isolated.")
    
    # User B tries to query User A's invoice: must return 404
    status, detail_inv = make_request("GET", f"/invoice/{invoice_a_id}", token=token_b)
    assert status == 404
    
    # User B tries to delete User A's invoice: must return 404
    status, del_inv = make_request("DELETE", f"/invoice/{invoice_a_id}", token=token_b)
    assert status == 404
    print("[OK] User B attempting to view/delete User A's invoice gets 404 Not Found.")

    # 7. Password change validity check
    print("\n--- 7. Testing Password Change Flow ---")
    status, chg_res = make_request("POST", "/change-password", {
        "old_password": "auditpassword12",
        "new_password": "newauditpassword12"
    }, token=token_a)
    assert status == 200
    
    # Login with old password -> must fail
    status, login_old = make_request("POST", "/login", {
        "email": "verify_all_user_a@example.com",
        "password": "auditpassword12"
    })
    assert status == 401
    
    # Login with new password -> must succeed
    status, login_new = make_request("POST", "/login", {
        "email": "verify_all_user_a@example.com",
        "password": "newauditpassword12"
    })
    assert status == 200
    print("[OK] Password change invalidates old password immediately and accepts new credentials.")

    # 8. Database Cleanups
    print("\n--- 8. Database Cleanups ---")
    cleanup_db()
    
    print("\n" + "=" * 60)
    print("E2E INTEGRATION AUDIT COMPLETED SUCCESSFULLY - ALL TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
