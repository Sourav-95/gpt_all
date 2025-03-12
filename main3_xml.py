import xml.etree.ElementTree as ET
import re

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
            audit_trail_entry = {}

            for subchild in child:
                subchild_key = clean_key(subchild.tag)
                subchild_text = subchild.text.strip() if subchild.text else None

                if subchild_text is not None:
                    subchild_text = subchild_text.replace("\r", " ").replace("\n", " ")

                audit_trail_entry[subchild_key] = subchild_text

            audit_trail_entries.append(audit_trail_entry)

        elif len(list(child)) > 0:  # If element has child elements
            nested_dict = parse_element(child, key, {})

            for k, v in nested_dict.items():
                data_dict[f"{key}_{k}"] = v
        else:
            text_value = child.text.strip() if child.text else None

            if text_value is not None:
                text_value = text_value.replace("\r", " ").replace("\n", " ")

            data_dict[key] = text_value

    if audit_trail_entries:
        data_dict["AuditTrail"] = audit_trail_entries

    return data_dict

def xml_to_json(xml_file_path):
    """Parses the XML file and converts it into a structured list of dictionaries."""
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    data = [parse_element(record) for record in root]
    return data

def refine_key_unique(key):
    """Cleans redundant parent prefixes from keys."""
    parts = key.split("_")
    unique_parts = []
    
    for part in parts:
        if part not in unique_parts:
            unique_parts.append(part)

    return "_".join(unique_parts)

def clean_keys_in_data(data):
    """Iterates through the list of dictionaries and modifies the keys using refine_key_unique()."""
    cleaned_data = []
    
    for record in data:
        new_record = {}
        for key, value in record.items():
            cleaned_key = refine_key_unique(key)
            new_record[cleaned_key] = value
        cleaned_data.append(new_record)
    
    return cleaned_data

# 1. Parse XML into list of dictionaries
raw_data = xml_to_json("your_xml_file.xml")  # Replace with actual XML file path

# 2. Clean keys using refine_key_unique
final_data = clean_keys_in_data(raw_data)

# final_data now has the correct key structure without excessive nesting
