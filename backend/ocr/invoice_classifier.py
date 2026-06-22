def categorize_vendor(vendor):
    if not vendor:
        return "Others"
    
    vendor_lower = vendor.lower()
    if "swiggy" in vendor_lower:
        return "Food"
    elif "amazon" in vendor_lower:
        return "Shopping"
    elif "uber" in vendor_lower:
        return "Transport"
    else:
        return "Others"
