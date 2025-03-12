def convert_to_dataframe(data):
    """Converts structured JSON into a Pandas DataFrame."""
    
    # Ensure 'AuditTrailEntry' exists in every record
    for item in data:
        if "AuditTrailEntry" not in item:
            item["AuditTrailEntry"] = [{}]  # Use [{}] instead of []

    df = pd.json_normalize(data, record_path=['AuditTrailEntry'], meta=['CreDtTm', 'NbOfTxs', 'TxId', 'State'], errors='ignore')
    
    return df
