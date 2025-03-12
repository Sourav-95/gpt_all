import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def clean_key(key, separator="_"):
    """
    Cleans a key by removing redundant parent nesting.
    Example: "pmtid_pmtid_txtid" → "pmtid_txtid"
             "audittrialentry_audittrialentry_reftxf_audittrialentry_reftxf_pmtid" → "audittrialentry_reftxf_pmtid"
    
    Parameters:
        key (str): The dictionary key to clean.
        separator (str): The separator used in keys (default is "_").
    
    Returns:
        str: The cleaned key.
    """
    try:
        key_parts = key.split(separator)  # Split key by separator
        cleaned_parts = []
        
        for part in key_parts:
            if not cleaned_parts or cleaned_parts[-1] != part:  # Avoid duplicate adjacent parts
                cleaned_parts.append(part)
        
        return separator.join(cleaned_parts)  # Rejoin into a clean key
    except Exception as e:
        logging.error(f"Error while cleaning key '{key}': {e}")
        return key  # Return original key if error occurs

def clean_dict_keys(d, separator="_"):
    """
    Recursively cleans dictionary keys to remove duplicate parent-child nesting.

    Parameters:
        d (dict): The dictionary whose keys need to be cleaned.
        separator (str): The separator used in keys (default is "_").
    
    Returns:
        dict: A new dictionary with cleaned keys.
    """
    try:
        cleaned_dict = {}

        for key, value in d.items():
            new_key = clean_key(key, separator)  # Clean the key

            if isinstance(value, dict):
                cleaned_dict[new_key] = clean_dict_keys(value, separator)  # Recursively clean nested dict
            else:
                cleaned_dict[new_key] = value  # Assign cleaned key-value pair

        return cleaned_dict
    except Exception as e:
        logging.error(f"Error while cleaning dictionary keys: {e}")
        return d  # Return original dictionary if error occurs

def preprocess_data(data):
    """
    Cleans the keys of all dictionaries in a list before converting to a DataFrame.

    Parameters:
        data (list): List of dictionaries to preprocess.
    
    Returns:
        list: List of dictionaries with cleaned keys.
    """
    try:
        return [clean_dict_keys(item) for item in data]  # Apply cleaning to each dictionary
    except Exception as e:
        logging.error(f"Error while preprocessing data: {e}")
        return data  # Return original data if error occurs

def convert_to_dataframe(data):
    """
    Converts a structured JSON list into a Pandas DataFrame.

    Parameters:
        data (list): List of dictionaries to convert.
    
    Returns:
        pd.DataFrame: Pandas DataFrame with structured data.
    """
    try:
        cleaned_data = preprocess_data(data)  # Clean keys before conversion
        df = pd.DataFrame(cleaned_data)  # Convert to DataFrame
        return df
    except Exception as e:
        logging.error(f"Error while converting data to DataFrame: {e}")
        return pd.DataFrame()  # Return empty DataFrame if error occurs

# Example JSON data with nested and redundant keys
data = [
    {"pmtid_pmtid_txtid": "12345", "audittrialentry_audittrialentry_reftxf_audittrialentry_reftxf_pmtid": "67890"},
    {"pmtid_txtid": "abcde", "audittrialentry_reftxf_pmtid": "fghij"},
    {"CreDtTm": "2024-03-12T12:00:00", "NbOfTxs": "10"},  # No nested keys
    {"InstrId": "XYZ123", "EndToEndId": "78910", "TxId": "111213",
     "AuditTrailEntry": [{"timestamp": "2024-03-12T12:00:00", "user": "admin"}]},
]

# Convert to DataFrame
df = convert_to_dataframe(data)
print(df)
