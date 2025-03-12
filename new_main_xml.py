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

def refine_key(parent_key, child_key, separator="_"):
    """Ensures keys do not redundantly include parent names."""
    parent_parts = parent_key.split(separator) if parent_key else []
    
    # Avoid repetition if child_key is already the last part of parent_key
    if parent_parts and parent_parts[-1] == child_key:
        return child_key
    return f"{parent_key}{separator}{child_key}" if parent_key else child_key

def parse_element(element, parent_key="", data_dict=None):
    """Recursively parses an XML element into a structured dictionary."""
    if data_dict is None:
        data_dict = {}

    audit_trail_entries = []  # List to store AuditTrail entries

    for child in element:
        child_key = clean_key(child.tag)
        
        # Use refine_key to avoid redundant parent-child key repetition
        key = refine_key(parent_key, child_key)  

        if child_key == "AuditTrailEntry":
            audit_trail_entry = {}

            for subchild in child:
                subchild_key = clean_key(subchild.tag)
                subchild_text = subchild.text.strip() if subchild.text else None

                if subchild_text is not None:
                    subchild_text = subchild_text.replace("\r", " ").replace("\n", " ")

                if subchild_key == "Notes":
                    audit_trail_entry["notes"] = subchild_text
                else:
                    audit_trail_entry[subchild_key] = subchild_text

            audit_trail_entry.setdefault("notes", None)
            audit_trail_entries.append(audit_trail_entry)
        
        elif len(list(child)) > 0:  # If element has child elements
            nested_dict = parse_element(child, key, {})  # Ensure nested dictionary is correctly formed

            for k, v in nested_dict.items():
                refined_nested_key = refine_key(parent_key, k)  # Ensure correct key formatting
                data_dict[refined_nested_key] = v  
        else:
            text_value = child.text.strip() if child.text else None

            if text_value is not None:
                text_value = text_value.replace("\r", " ").replace("\n", " ")

            data_dict[key] = text_value  # Ensure hierarchical key structure

    if audit_trail_entries:
        data_dict["AuditTrail"] = audit_trail_entries

    return data_dict

def xml_to_json(xml_file_path):
    """Parses the XML file and converts it into a structured list of dictionaries."""
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        data = [parse_element(record) for record in root]
        return data
    except ET.ParseError as e:
        print(f"XML Parsing Error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return []

# Usage:
data_df = xml_to_json("your_xml_file.xml")  # Replace with actual file path
