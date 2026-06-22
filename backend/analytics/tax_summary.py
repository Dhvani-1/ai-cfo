import re

def get_gst_summary(invoices):
    if not invoices:
        return {
            "total_gst_paid": 0.0,
            "invoice_count": 0,
            "explicit_gst_invoices": 0,
            "estimated_gst_invoices": 0,
            "average_gst": 0.0
        }
        
    total_gst_paid = 0.0
    explicit_count = 0
    estimated_count = 0
    invoice_count = 0
    
    gst_pat = re.compile(r'(?:cgst|sgst|igst|gst|tax|service\s+tax)\s*[:$₹\s\-#]*\s*([0-9,]+\.[0-9]{2})', re.IGNORECASE)
    
    for inv in invoices:
        gst_amount = 0.0
        if inv.ocr_text:
            matches = gst_pat.findall(inv.ocr_text)
            for m in matches:
                try:
                    gst_amount += float(m.replace(',', ''))
                except ValueError:
                    pass
                    
        if gst_amount > 0.0:
            explicit_count += 1
            invoice_count += 1
            total_gst_paid += gst_amount
        elif inv.gst_number and inv.total_amount:
            # Estimate GST as 18% of total amount
            est_gst = round(inv.total_amount * 0.18, 2)
            estimated_count += 1
            invoice_count += 1
            total_gst_paid += est_gst
            
    average_gst = round(total_gst_paid / invoice_count, 2) if invoice_count > 0 else 0.0
    
    return {
        "total_gst_paid": round(total_gst_paid, 2),
        "invoice_count": invoice_count,
        "explicit_gst_invoices": explicit_count,
        "estimated_gst_invoices": estimated_count,
        "average_gst": average_gst
    }

def get_tax_deductible_categories(transactions):
    from collections import defaultdict
    summary = defaultdict(float)
    for t in transactions:
        if t.amount < 0:
            cat = t.category or "Others"
            summary[cat] += abs(t.amount)
            
    return {cat: round(val, 2) for cat, val in summary.items()}
