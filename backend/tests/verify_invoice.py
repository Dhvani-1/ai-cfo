import urllib.request
import json
import os
import uuid
from PIL import Image
from reportlab.pdfgen import canvas

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
        try:
            body_content = e.read().decode('utf-8')
            return e.code, json.loads(body_content)
        except Exception:
            return e.code, None
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return 500, None

def post_file(endpoint, file_path):
    import urllib.error
    url = f"{BASE_URL}{endpoint}"
    filename = os.path.basename(file_path)
    print(f"Querying POST {url} with file {filename}...")
    
    # Read file content
    with open(file_path, "rb") as f:
        file_content = f.read()
        
    # Multi-part encoding
    boundary = uuid.uuid4().hex
    data = []
    data.append(f'--{boundary}'.encode('utf-8'))
    data.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode('utf-8'))
    # Determine Content-Type
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.pdf':
        data.append(b'Content-Type: application/pdf')
    elif ext == '.png':
        data.append(b'Content-Type: image/png')
    else:
        data.append(b'Content-Type: application/octet-stream')
    data.append(b'')
    data.append(file_content)
    data.append(f'--{boundary}--'.encode('utf-8'))
    data.append(b'')
    
    body = b'\r\n'.join(data)
    
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Length': str(len(body))
    }
    
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            res_body = response.read().decode('utf-8')
            return status, json.loads(res_body)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code} for {url}")
        try:
            body_content = e.read().decode('utf-8')
            return e.code, json.loads(body_content)
        except Exception:
            return e.code, None
    except Exception as e:
        print(f"Failed to post to {url}: {e}")
        return 500, None

def delete_endpoint(endpoint):
    import urllib.error
    url = f"{BASE_URL}{endpoint}"
    print(f"Querying DELETE {url}...")
    req = urllib.request.Request(url, method="DELETE")
    try:
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            body = response.read().decode('utf-8')
            return status, json.loads(body)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code} for {url}")
        try:
            body_content = e.read().decode('utf-8')
            return e.code, json.loads(body_content)
        except Exception:
            return e.code, None
    except Exception as e:
        print(f"Failed to delete {url}: {e}")
        return 500, None

def run_tests():
    print("Starting Phase 6 Invoice OCR verification tests...\n")
    
    # Ensure temporary workspace is clean
    temp_files = []
    
    # Self-healing database cleanup of previous test runs
    status, invoices = get_endpoint("/invoices")
    if status == 200 and invoices:
        for inv in invoices:
            if inv.get("vendor") in ["Swiggy", "Amazon", "Some unknown company text"]:
                print(f"Cleaning up old test invoice ID {inv['id']} from DB...")
                delete_endpoint(f"/invoice/{inv['id']}")

    
    # 1. OCR Fallback test (.txt file next to dummy image)
    img_filename = "test_invoice_swiggy.png"
    # Ensure uploads/invoices directory exists
    os.makedirs(os.path.join("uploads", "invoices"), exist_ok=True)
    txt_filename = os.path.join("uploads", "invoices", img_filename + ".txt")
    
    # Create image
    img = Image.new('RGB', (100, 100), color='blue')
    img.save(img_filename)
    temp_files.append(img_filename)
    
    # Create matching txt file
    swiggy_text = """Swiggy Receipt
Invoice No: SW-88371
Date: 2026-06-18
GSTIN: 07AAAAA1111A1Z1
Total: 450.25
"""
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(swiggy_text)
    temp_files.append(txt_filename)
    
    status, body = post_file("/upload-invoice", img_filename)
    assert status == 200, f"Expected 200, got {status}"
    assert body["vendor"] == "Swiggy"
    assert body["invoice_number"] == "SW-88371"
    assert body["total_amount"] == 450.25
    assert body["gst_number"] == "07AAAAA1111A1Z1"
    assert body["category"] == "Food"
    assert body["ocr_text"] == swiggy_text
    
    swiggy_id = body["id"]
    saved_file_path = body["file_path"]
    
    print("[OK] OCR Fallback and field extraction test passed.")

    # 2. Duplicate invoice prevention test
    status, body_dup = post_file("/upload-invoice", img_filename)
    assert status == 200
    assert body_dup["duplicate"] is True
    assert "Invoice already exists" in body_dup["message"]
    print("[OK] Duplicate invoice prevention test passed.")

    # 3. Missing optional fields test
    missing_img = "test_invoice_missing.png"
    missing_txt = os.path.join("uploads", "invoices", missing_img + ".txt")
    
    img2 = Image.new('RGB', (100, 100), color='green')
    img2.save(missing_img)
    temp_files.append(missing_img)
    
    missing_text = """Some unknown company text
GSTIN: 07BBBBB2222B2Z2
"""
    with open(missing_txt, "w", encoding="utf-8") as f:
        f.write(missing_text)
    temp_files.append(missing_txt)
    
    status, body_missing = post_file("/upload-invoice", missing_img)
    assert status == 200
    assert body_missing["vendor"] == "Some unknown company text"
    assert body_missing["invoice_number"] is None
    assert body_missing["invoice_date"] is None
    assert body_missing["total_amount"] is None
    assert body_missing["gst_number"] == "07BBBBB2222B2Z2"
    assert body_missing["category"] == "Others"
    print("[OK] Missing optional fields parsing and storage test passed.")

    # 4. PDF parsing using pdfplumber test & Vendor Categorization
    pdf_filename = "test_invoice_amazon.pdf"
    c = canvas.Canvas(pdf_filename)
    c.drawString(100, 750, "Vendor: Amazon")
    c.drawString(100, 730, "Invoice Number: AMZ-901")
    c.drawString(100, 710, "Date: 2026-06-19")
    c.drawString(100, 690, "Total: 1550.50")
    c.save()
    temp_files.append(pdf_filename)
    
    status, body_pdf = post_file("/upload-invoice", pdf_filename)
    assert status == 200
    assert body_pdf["vendor"] == "Amazon"
    assert body_pdf["invoice_number"] == "AMZ-901"
    assert body_pdf["invoice_date"] == "2026-06-19"
    assert body_pdf["total_amount"] == 1550.50
    assert body_pdf["category"] == "Shopping"
    print("[OK] PDF text extraction and categorization test passed.")

    # 5. GET /invoices verification
    status, invoices = get_endpoint("/invoices")
    assert status == 200
    assert len(invoices) >= 3
    # Check that our invoices are in the list
    ids = [inv["id"] for inv in invoices]
    assert swiggy_id in ids
    print("[OK] GET /invoices validation passed.")

    # 6. GET /invoice/{id} verification
    status, inv_detail = get_endpoint(f"/invoice/{swiggy_id}")
    assert status == 200
    assert inv_detail["invoice_number"] == "SW-88371"
    
    # Verify 404
    status_404, _ = get_endpoint("/invoice/999999")
    assert status_404 == 404
    print("[OK] GET /invoice/{id} validation passed.")

    # 7. GET /invoice-summary verification (Top category/vendor and rounded total amounts)
    status, summary = get_endpoint("/invoice-summary")
    assert status == 200
    # swiggy total is 450.25 (Food), amazon is 1550.50 (Shopping). Total should be at least 2000.75.
    assert summary["total_invoices"] >= 3
    assert summary["total_spend"] >= 2000.75
    # Verify top vendor and category grouping logic
    assert summary["top_vendor"] == "Amazon"
    assert summary["top_category"] == "Shopping"
    
    # Check rounding of summary spend
    assert abs(round(summary["total_spend"], 2) - summary["total_spend"]) < 1e-9
    print("[OK] GET /invoice-summary validation passed.")

    # 8. DELETE /invoice/{id} and file deletion on disk
    # Confirm file exists before deletion
    assert os.path.exists(saved_file_path), f"Expected file to exist at {saved_file_path}"
    
    status_del, res_del = delete_endpoint(f"/invoice/{swiggy_id}")
    assert status_del == 200
    assert "Invoice deleted successfully" in res_del["message"]
    
    # Verify file is deleted on disk
    assert not os.path.exists(saved_file_path), f"Expected file to be deleted from disk at {saved_file_path}"
    
    # Verify database record deleted (returns 404)
    status_get, _ = get_endpoint(f"/invoice/{swiggy_id}")
    assert status_get == 404
    print("[OK] DELETE /invoice/{id} and file deletion test passed.")

    # Clean up local test files
    for temp in temp_files:
        try:
            if os.path.exists(temp):
                os.remove(temp)
        except Exception:
            pass
            
    print("\nALL PHASE 6 INVOICE OCR TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
