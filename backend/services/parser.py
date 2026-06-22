import pandas as pd
import numpy as np

def parse_file(filepath):
    if filepath.endswith(".csv"):
        df = pd.read_csv(filepath)
    elif filepath.endswith(".xlsx"):
        df = pd.read_excel(filepath)
    else:
        return []

    # Clean/normalize column names: strip spaces and convert to lower case
    df.columns = [str(col).strip().lower() for col in df.columns]

    # Map columns to expected keys: "Date", "Description", "Amount"
    col_mapping = {}
    for col in df.columns:
        if "date" in col:
            col_mapping[col] = "Date"
        elif "desc" in col:
            col_mapping[col] = "Description"
        elif "amt" in col or "amount" in col:
            col_mapping[col] = "Amount"

    df = df.rename(columns=col_mapping)

    # Ensure required columns exist
    for required in ["Date", "Description", "Amount"]:
        if required not in df.columns:
            df[required] = None

    # Parse dates safely
    try:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    except Exception:
        pass

    # Ensure amount is numeric, handle currency symbols if present
    if df["Amount"].dtype == object:
        df["Amount"] = df["Amount"].astype(str).str.replace(r'[^\d.-]', '', regex=True)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)

    # Convert pandas NaN/NaT to None for SQLite storage compatibility
    df = df.replace({np.nan: None})

    records = []
    for record in df.to_dict(orient="records"):
        dt_val = record.get("Date")
        if pd.isnull(dt_val) or dt_val is None:
            record["Date"] = None
        elif isinstance(dt_val, pd.Timestamp):
            record["Date"] = dt_val.date()
        elif hasattr(dt_val, "date"):
            record["Date"] = dt_val.date()
        else:
            record["Date"] = None
        records.append(record)

    return records