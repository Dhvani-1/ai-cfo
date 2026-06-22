import urllib.request
import json
import os
import datetime
import sys

# Configure python path to find modules in the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.transaction import Transaction
from models.invoice import Invoice

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
        # Delete any test transactions containing [TaxTest]
        tx_count = db.query(Transaction).filter(Transaction.description.like("%[TaxTest]%")).delete(synchronize_session=False)
        # Delete any test invoices containing [TaxTest]
        inv_count = db.query(Invoice).filter(Invoice.vendor.like("%[TaxTest]%")).delete(synchronize_session=False)
        db.commit()
        if tx_count > 0 or inv_count > 0:
            print(f"Cleaned up {tx_count} old [TaxTest] transactions and {inv_count} old invoices from database.")
    except Exception as e:
        print(f"Cleanup error: {e}")
        db.rollback()
    finally:
        db.close()

def inject_test_data():
    db = SessionLocal()
    try:
        # 1. Ingest transactions
        # 1 Income: description [TaxTest] Client Payment, amount 10000.0
        # 1 Expense: description [TaxTest] Office Rent, amount -3000.0, category "Housing"
        # 1 Expense: description [TaxTest] Gas fill, amount -500.0, category "Transport"
        tx1 = Transaction(
            date=datetime.date(2026, 6, 20),
            description="[TaxTest] Client Payment",
            amount=10000.0,
            category="Income",
            type="Income"
        )
        tx2 = Transaction(
            date=datetime.date(2026, 6, 21),
            description="[TaxTest] Office Rent",
            amount=-3000.00,
            category="Housing",
            type="Expense"
        )
        tx3 = Transaction(
            date=datetime.date(2026, 6, 22),
            description="[TaxTest] Gas fill",
            amount=-500.00,
            category="Transport",
            type="Expense"
        )
        db.add(tx1)
        db.add(tx2)
        db.add(tx3)

        # 2. Ingest invoices
        # 1 Invoice (Explicit GST): GST found in text
        inv1 = Invoice(
            vendor="[TaxTest] Vendor A",
            invoice_number="INV-T1",
            invoice_date=datetime.date(2026, 6, 20),
            total_amount=1180.00,
            gst_number="07AAAAA1111A1Z1",
            category="Others",
            file_path="uploads/invoices/tax_test_a.pdf",
            ocr_text="Vendor: [TaxTest] Vendor A\nGST: 180.00\nTotal: 1180.00\n"
        )
        # 1 Invoice (Estimated GST - gst_number present, no explicit GST in text)
        inv2 = Invoice(
            vendor="[TaxTest] Vendor B",
            invoice_number="INV-T2",
            invoice_date=datetime.date(2026, 6, 21),
            total_amount=1000.00,
            gst_number="07BBBBB2222B2Z2",
            category="Others",
            file_path="uploads/invoices/tax_test_b.pdf",
            ocr_text="Vendor: [TaxTest] Vendor B\nTotal: 1000.00\n"
        )
        db.add(inv1)
        db.add(inv2)

        db.commit()
        print("Injected test transactions and invoices.")
    except Exception as e:
        print(f"Injection error: {e}")
        db.rollback()
    finally:
        db.close()

def run_tests():
    print("Starting Phase 8 Tax Assistant verification tests...\n")

    # --- Test 1: Empty database / safe defaults check ---
    cleanup_db()

    # Query estimate endpoint
    # Since other user transactions might exist, we check that if no test data exists, 
    # the endpoints still run and return rounded schemas. We will verify empty-state logic specifically.
    db = SessionLocal()
    # Find pre-existing counts to do accurate delta assertions if needed, 
    # but the safest unit test is to ensure calculations do not throw exceptions.
    pre_existing_txs = db.query(Transaction).count()
    pre_existing_invs = db.query(Invoice).count()
    db.close()

    if pre_existing_txs == 0:
        status, est = get_endpoint("/tax-estimate")
        assert status == 200
        assert est["income"] == 0.0
        assert est["expenses"] == 0.0
        assert est["taxable_income"] == 0.0
        assert est["expense_ratio"] == 0.0

    if pre_existing_invs == 0:
        status, gst = get_endpoint("/gst-summary")
        assert status == 200
        assert gst["total_gst_paid"] == 0.0
        assert gst["invoice_count"] == 0
        assert gst["explicit_gst_invoices"] == 0
        assert gst["estimated_gst_invoices"] == 0
        assert gst["average_gst"] == 0.0

    print("[OK] Safe empty-state default checks passed.")

    # --- Test 2: Standard calculations with test data ---
    inject_test_data()

    # A: GET /gst-summary
    status, gst = get_endpoint("/gst-summary")
    assert status == 200
    # Vendor A explicit GST = 180.00. Vendor B estimated GST = 18% of 1000.00 = 180.00.
    # Total GST should increase by 360.00, count by 2, explicit by 1, estimated by 1.
    # If the database was empty, these are exact. Otherwise we check relative offsets.
    if pre_existing_invs == 0:
        assert gst["total_gst_paid"] == 360.00
        assert gst["invoice_count"] == 2
        assert gst["explicit_gst_invoices"] == 1
        assert gst["estimated_gst_invoices"] == 1
        assert gst["average_gst"] == 180.00
    else:
        assert gst["explicit_gst_invoices"] >= 1
        assert gst["estimated_gst_invoices"] >= 1
    
    # Check rounding of float outputs
    assert abs(round(gst["total_gst_paid"], 2) - gst["total_gst_paid"]) < 1e-9
    assert abs(round(gst["average_gst"], 2) - gst["average_gst"]) < 1e-9
    print("[OK] GET /gst-summary verification passed.")

    # B: GET /tax-estimate
    status, est = get_endpoint("/tax-estimate")
    assert status == 200
    if pre_existing_txs == 0:
        assert est["income"] == 10000.00
        assert est["expenses"] == 3500.00
        assert est["taxable_income"] == 6500.00
        assert est["expense_ratio"] == 35.00
    else:
        assert est["income"] >= 10000.00
        assert est["expenses"] >= 3500.00
    
    assert abs(round(est["income"], 2) - est["income"]) < 1e-9
    assert abs(round(est["expenses"], 2) - est["expenses"]) < 1e-9
    assert abs(round(est["taxable_income"], 2) - est["taxable_income"]) < 1e-9
    assert abs(round(est["expense_ratio"], 2) - est["expense_ratio"]) < 1e-9
    print("[OK] GET /tax-estimate verification passed.")

    # C: GET /tax-insights
    status, ins = get_endpoint("/tax-insights")
    assert status == 200
    assert "tax_status" in ins
    assert "insights" in ins
    assert "largest_expense_category" in ins
    
    # Large expense category should be "Housing" because Housing = 3000.00 and Transport = 500.00
    if pre_existing_txs == 0:
        assert ins["tax_status"] == "positive_income"
        assert ins["largest_expense_category"] == "Housing"
        assert any("Housing represents the largest expense category" in text for text in ins["insights"])
        assert any("Taxable income is positive" in text for text in ins["insights"])
    print("[OK] GET /tax-insights verification passed.")

    # D: GET /tax-summary (consolidated endpoint)
    status, summ = get_endpoint("/tax-summary")
    assert status == 200
    assert "gst" in summ
    assert "estimate" in summ
    assert "insights" in summ
    assert "generated_at" in summ
    assert "disclaimer" in summ
    
    # Check disclaimer text matches
    assert "estimates only and should not be considered professional or legal advice" in summ["disclaimer"]
    
    # Check generated_at timestamp existence
    assert len(summ["generated_at"]) > 0
    print("[OK] GET /tax-summary consolidated endpoint verification passed.")

    # Clean up test data
    cleanup_db()
    print("\nALL PHASE 8 TAX ASSISTANT TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
