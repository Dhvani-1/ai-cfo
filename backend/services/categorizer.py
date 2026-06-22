def categorize(description):

    desc = description.lower()

    if "swiggy" in desc or "zomato" in desc:
        return "Food"

    elif "uber" in desc or "ola" in desc:
        return "Transport"

    elif "amazon" in desc or "flipkart" in desc:
        return "Shopping"

    elif "rent" in desc:
        return "Housing"

    elif "salary" in desc:
        return "Income"

    else:
        return "Others"