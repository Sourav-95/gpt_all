import xml.etree.ElementTree as ET
import pandas as pd
import re
from pandas.io.json import json_normalize  # For older versions

def clean_key(keys):
    """Removes dynamic ID patterns from XML keys."""
    is_match = True
    while is_match:
        try:
            start_removal_index = keys.index('{')
            end_removal_index = keys.index('}')
            string_to_remove = keys[start_removal_index:end_removal_index+1]
            keys = re.sub(re.escape(string_to_remove), "", keys)
        except ValueError:
            is_match = False 
    return keys.strip("_")

def parse_element(element, parent_key="", data_dict=None):
    """Recursively parses an XML element into a structured dictionary."""
    if data_dict is None:
        data_dict = {}

    audit_trail_entries = []  # List to store AuditTrail entries

    for child in element:
        child_key = clean_key(child.tag)
        key = f"{parent_key}_{child_key}" if parent_key else child_key

        if child_key == "AuditTrailEntry":
            audit_trail_entry = {}  # Create a new audit trail dictionary

            # Parse each field inside AuditTrailEntry
            for subchild in child:
                subchild_key = clean_key(subchild.tag)
                subchild_text = subchild.text.strip() if subchild.text else None

                # Replace \r and \n with spaces
                if subchild_text is not None:
                    subchild_text = subchild_text.replace("\r", " ").replace("\n", " ")

                # Store raw XML in "notes" field if it exists
                if subchild_key == "Notes":
                    audit_trail_entry["notes"] = subchild_text
                else:
                    audit_trail_entry[subchild_key] = subchild_text

            # Ensure missing fields are set to None
            audit_trail_entry.setdefault("notes", None)

            audit_trail_entries.append(audit_trail_entry)
        
        elif len(list(child)) > 0:  # If element has child elements
            nested_dict = {}
            parse_element(child, key, nested_dict)
            data_dict.update(nested_dict)
        else:
            text_value = child.text.strip() if child.text else None

            # Replace \r and \n with spaces
            if text_value is not None:
                text_value = text_value.replace("\r", " ").replace("\n", " ")

            data_dict[child_key] = text_value

    # Attach the list of audit trail entries to the main dictionary
    if audit_trail_entries:
        data_dict["AuditTrail"] = audit_trail_entries

    return data_dict

def xml_to_json(xml_file_path):
    """Parses the XML file and converts it into a structured list of dictionaries."""
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    data = [parse_element(record) for record in root]
    return data

def convert_to_dataframe(data):
    """Converts structured JSON into a Pandas DataFrame."""
    df = pd.json_normalize(data, record_path=['AuditTrail'], meta=['pmt_id', 'state'])
    return df

# Example Usage
xml_file = "input.xml"  # Replace with your XML file path
data = xml_to_json(xml_file)

df = convert_to_dataframe(data)
print(df)
