import re
import datetime

def parse_date(date_str):
    if not date_str:
        return None
    date_str = date_str.strip()
    # Replace multiple spaces with a single space
    date_str = re.sub(r'\s+', ' ', date_str)
    # Try common formats
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%d %b %Y', '%d %B %Y', '%Y/%m/%d'):
        try:
            return datetime.datetime.strptime(date_str, fmt).date()
        except ValueError:
            pass
    # Try dateutil parser if available
    try:
        from dateutil import parser
        return parser.parse(date_str, fuzzy=True).date()
    except Exception:
        return None

def extract_invoice_fields(raw_text):
    if not raw_text:
        return {
            "vendor": None,
            "invoice_number": None,
            "invoice_date": None,
            "total_amount": None,
            "gst_number": None
        }

    # 1. Vendor
    vendor = None
    raw_text_lower = raw_text.lower()
    if "swiggy" in raw_text_lower:
        vendor = "Swiggy"
    elif "amazon" in raw_text_lower:
        vendor = "Amazon"
    elif "uber" in raw_text_lower:
        vendor = "Uber"
    else:
        # Search for vendor labels
        vendor_match = re.search(r'(?:vendor|seller|merchant|from|company\s+name)\s*[:\-]\s*([^\n\r]+)', raw_text, re.IGNORECASE)
        if vendor_match:
            vendor = vendor_match.group(1).strip()
        else:
            # Fallback to the first non-empty line if it is short
            lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
            if lines:
                candidate = lines[0]
                if len(candidate) < 60:
                    vendor = candidate

    # 2. Invoice Number
    invoice_number = None
    inv_match = re.search(r'(?:invoice|inv|bill|receipt)(?:\s+no|\s+number|\s*#|\s+id)?(?:[ \t]*[:#\-]+[ \t]*|[ \t]+)([a-z0-9/\-]+)', raw_text, re.IGNORECASE)
    if inv_match:
        invoice_number = inv_match.group(1).strip()
    else:
        inv_match_fallback = re.search(r'\binv-[a-z0-9/\-]+', raw_text, re.IGNORECASE)
        if inv_match_fallback:
            invoice_number = inv_match_fallback.group(0).strip()

    # 3. Date
    invoice_date = None
    # Look for labeled date using newline-resistant horizontal separator
    date_match = re.search(r'(?:date|dated)(?:[ \t]*[:\-]+[ \t]*|[ \t]+)(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4}|\d{1,2}\s+[a-zA-Z]{3,9}\s+\d{4}|\d{1,2}[-/][a-zA-Z]{3,9}[-/]\d{2,4})', raw_text, re.IGNORECASE)
    if date_match:
        invoice_date = parse_date(date_match.group(1))
    else:
        # Look for any date
        date_match_fallback = re.search(r'\b(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4}|\d{1,2}\s+[a-zA-Z]{3,9}\s+\d{4})\b', raw_text, re.IGNORECASE)
        if date_match_fallback:
            invoice_date = parse_date(date_match_fallback.group(1))

    # 4. GST Number
    gst_number = None
    gst_match = re.search(r'\b([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})\b', raw_text, re.IGNORECASE)
    if gst_match:
        gst_number = gst_match.group(1).upper()
    else:
        # Try a broader search near labels
        gst_label_match = re.search(r'gst(?:in)?\s*[:#\-]?\s*([0-9a-z]{15})', raw_text, re.IGNORECASE)
        if gst_label_match:
            gst_number = gst_label_match.group(1).upper()

    # 5. Total Amount
    total_amount = None
    # Look for labeled amount using newline-resistant horizontal separator and optional currency symbol
    amt_match = re.search(r'(?:total|grand\s+total|amount\s+due|net\s+amount)(?:[ \t]*[:\-#]+[ \t]*|[ \t]+)?(?:rs\.?|inr|usd|\$|₹)?[ \t]*([0-9,]+\.[0-9]{2})', raw_text, re.IGNORECASE)
    if amt_match:
        try:
            total_amount = round(float(amt_match.group(1).replace(',', '')), 2)
        except Exception:
            pass
    
    if total_amount is None:
        # Look for currency prefix pattern
        amt_match_currency = re.search(r'(?:rs\.?|inr|usd|\$|₹)[ \t]*([0-9,]+\.[0-9]{2})', raw_text, re.IGNORECASE)
        if amt_match_currency:
            try:
                total_amount = round(float(amt_match_currency.group(1).replace(',', '')), 2)
            except Exception:
                pass

    if total_amount is None:
        # Final fallback: find all numbers with 2 decimals and pick the largest one
        all_amts = re.findall(r'\b([0-9,]+\.[0-9]{2})\b', raw_text)
        floats = []
        for a in all_amts:
            try:
                floats.append(float(a.replace(',', '')))
            except Exception:
                pass
        if floats:
            total_amount = round(max(floats), 2)

    return {
        "vendor": vendor,
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "total_amount": total_amount,
        "gst_number": gst_number
    }
