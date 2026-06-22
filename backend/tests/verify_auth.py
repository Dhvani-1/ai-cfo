import urllib.request
import json
import os
import datetime
import sys
import time
from jose import jwt

# Configure python path to find modules in the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.user import User
from models.transaction import Transaction
from models.invoice import Invoice
from auth.security import SECRET_KEY, ALGORITHM

BASE_URL = "http://127.0.0.1:8000"

def make_request(method, endpoint, payload=None, token=None):
    import urllib.error
    url = f"{BASE_URL}{endpoint}"
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    if token is not None:
        headers['Authorization'] = f"Bearer {token}"
        
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            body = response.read().decode('utf-8')
            return status, json.loads(body) if body else None
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            parsed_body = json.loads(body)
        except Exception:
            parsed_body = body
        return e.code, parsed_body
    except Exception as e:
        return 500, str(e)

def cleanup_db():
    db = SessionLocal()
    try:
        # Delete test users
        test_emails = ["authtest_userA@example.com", "authtest_userB@example.com", "authtest_userC@example.com"]
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
    print("Starting Phase 9 Authentication & Multi-User Support verification tests...\n")
    
    # 0. Clean database
    cleanup_db()
    
    # 1. Weak Password Rejection (during register)
    print("Testing weak password rejection during registration...")
    
    # Short password (less than 8 chars)
    status, res = make_request("POST", "/register", {
        "name": "Weak User",
        "email": "authtest_userC@example.com",
        "password": "sh1t"
    })
    assert status == 400
    assert res.get("detail") == "Password does not meet minimum requirements."
    
    # No digit password
    status, res = make_request("POST", "/register", {
        "name": "Weak User",
        "email": "authtest_userC@example.com",
        "password": "plainpassword"
    })
    assert status == 400
    assert res.get("detail") == "Password does not meet minimum requirements."
    print("[OK] Weak password registration rejected correctly.")

    # 2. User Registration and Duplication Checks
    print("Registering User A...")
    status, res = make_request("POST", "/register", {
        "name": "User A",
        "email": "authtest_userA@example.com",
        "password": "validpass1"
    })
    assert status == 200
    assert res.get("email") == "authtest_userA@example.com"
    user_a_id = res.get("id")
    
    # Duplicate email registration check
    print("Testing duplicate email registration...")
    status, res = make_request("POST", "/register", {
        "name": "User A Duplicate",
        "email": "authtest_userA@example.com",
        "password": "anotherpass1"
    })
    assert status == 400
    assert res.get("detail") == "Email already registered"
    print("[OK] Duplicate email registration rejected correctly.")
    
    # 3. Login, Token Expiration Metadata, Claims (iat, exp), and payload checks
    print("Logging in User A...")
    status, login_res = make_request("POST", "/login", {
        "email": "authtest_userA@example.com",
        "password": "validpass1"
    })
    assert status == 200
    assert "access_token" in login_res
    assert login_res.get("token_type") == "bearer"
    assert login_res.get("expires_in_minutes") == 60
    
    token = login_res.get("access_token")
    
    # Decode token and verify claims
    print("Verifying JWT claims (iat, exp, sub, user_id)...")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") == "authtest_userA@example.com"
    assert payload.get("user_id") == user_a_id
    assert "iat" in payload
    assert "exp" in payload
    # exp must be iat + 3600 seconds (60 mins)
    assert payload["exp"] - payload["iat"] == 3600
    print("[OK] Token expiration metadata and claims verified successfully.")
    
    # Wrong password login rejection
    status, login_res_err = make_request("POST", "/login", {
        "email": "authtest_userA@example.com",
        "password": "wrongpassword1"
    })
    assert status == 401
    assert login_res_err.get("detail") == "Incorrect email or password"
    print("[OK] Login rejected for incorrect password.")
    
    # 4. GET /me statistics check (empty state: zero records)
    print("Checking GET /me stats for new user (empty state)...")
    status, me_res = make_request("GET", "/me", token=token)
    assert status == 200
    assert me_res.get("email") == "authtest_userA@example.com"
    assert "statistics" in me_res
    stats = me_res["statistics"]
    assert stats.get("transactions") == 0
    assert stats.get("invoices") == 0
    print("[OK] Empty state statistics avoided nulls correctly.")
    
    # 5. Ingesting records and validating statistics update
    print("Adding transaction and invoice for User A...")
    db = SessionLocal()
    tx1 = Transaction(
        date=datetime.date(2026, 6, 22),
        description="[AuthTest] Salary A",
        amount=5000.0,
        category="Salary",
        type="Income",
        user_id=user_a_id
    )
    tx2 = Transaction(
        date=datetime.date(2026, 6, 23),
        description="[AuthTest] Dinner A",
        amount=-50.0,
        category="Food",
        type="Expense",
        user_id=user_a_id
    )
    inv1 = Invoice(
        vendor="[AuthTest] Amazon",
        invoice_number="INV-A1",
        invoice_date=datetime.date(2026, 6, 22),
        total_amount=150.00,
        gst_number="07AWS1234A1Z1",
        category="Office Expenses",
        file_path="uploads/invoices/test_a.pdf",
        ocr_text="Amazon office invoice",
        user_id=user_a_id
    )
    db.add(tx1)
    db.add(tx2)
    db.add(inv1)
    db.commit()
    invoice_a_id = inv1.id
    db.close()
    
    print("Checking GET /me stats with active records...")
    status, me_res = make_request("GET", "/me", token=token)
    assert status == 200
    stats = me_res["statistics"]
    assert stats.get("transactions") == 2
    assert stats.get("invoices") == 1
    print("[OK] Active user statistics computed correctly.")
    
    # 6. Ownership boundary leakage returning 404
    print("Registering and logging in User B...")
    status, res = make_request("POST", "/register", {
        "name": "User B",
        "email": "authtest_userB@example.com",
        "password": "validpass2"
    })
    assert status == 200
    user_b_id = res.get("id")
    
    status, login_res_b = make_request("POST", "/login", {
        "email": "authtest_userB@example.com",
        "password": "validpass2"
    })
    assert status == 200
    token_b = login_res_b.get("access_token")
    
    print("Testing GET /invoice/{id} isolation...")
    # User B queries User A's invoice: must return 404, not 403
    status, res = make_request("GET", f"/invoice/{invoice_a_id}", token=token_b)
    assert status == 404
    assert res.get("detail") == "Invoice not found"
    
    print("Testing DELETE /invoice/{id} isolation...")
    # User B tries to delete User A's invoice: must return 404, not 403
    status, res = make_request("DELETE", f"/invoice/{invoice_a_id}", token=token_b)
    assert status == 404
    assert res.get("detail") == "Invoice not found"
    
    print("Testing invoice and transaction list isolation for User B...")
    # User B list invoices -> should be empty
    status, invoices_b = make_request("GET", "/invoices", token=token_b)
    assert status == 200
    assert len(invoices_b) == 0
    
    # User B list transactions -> should be empty
    status, txs_b = make_request("GET", "/transactions", token=token_b)
    assert status == 200
    assert len(txs_b) == 0
    print("[OK] Ownership isolation returning 404 and filtering list endpoints passed successfully.")

    # 7. Password change flow (including weak password rejection, invalid old pass, and login with new pass)
    print("Testing password change flow...")
    
    # Weak password change rejection
    status, res = make_request("POST", "/change-password", {
        "old_password": "validpass1",
        "new_password": "short"
    }, token=token)
    assert status == 400
    assert res.get("detail") == "Password does not meet minimum requirements."
    
    # Wrong old password rejection
    status, res = make_request("POST", "/change-password", {
        "old_password": "wrongoldpass",
        "new_password": "newvalidpass1"
    }, token=token)
    assert status == 400
    assert res.get("detail") == "Incorrect old password"
    
    # Successful password change
    status, res = make_request("POST", "/change-password", {
        "old_password": "validpass1",
        "new_password": "newvalidpass1"
    }, token=token)
    assert status == 200
    assert res.get("detail") == "Password updated successfully"
    
    # Try login with old password -> must fail
    status, res = make_request("POST", "/login", {
        "email": "authtest_userA@example.com",
        "password": "validpass1"
    })
    assert status == 401
    
    # Try login with new password -> must succeed
    status, login_res_new = make_request("POST", "/login", {
        "email": "authtest_userA@example.com",
        "password": "newvalidpass1"
    })
    assert status == 200
    assert "access_token" in login_res_new
    print("[OK] Password change flow, old password invalidation, and new login verified.")
    
    # 8. Clean up database
    print("Running self-cleaning database logic...")
    cleanup_db()
    
    print("\nALL PHASE 9 AUTHENTICATION & MULTI-USER TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
