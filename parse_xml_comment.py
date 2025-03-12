import logging
import xml.etree.ElementTree as ET

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def clean_key(key):
    """
    Cleans an XML tag to use as a dictionary key.
    Removes redundant nesting and ensures a clean structure.

    Parameters:
        key (str): The XML tag to clean.

    Returns:
        str: A cleaned version of the key.
    """
    try:
        return key.strip().replace(" ", "_") if key else key
    except Exception as e:
        logging.error(f"Error cleaning key '{key}': {e}")
        return key  # Return original key if error occurs

def parse_element(element, parent_key="", data_dict=None):
    """
    Recursively parses an XML element into a structured dictionary.
    
    Parameters:
        element (xml.etree.ElementTree.Element): XML element to parse.
        parent_key (str, optional): Parent key to maintain hierarchy (default: "").
        data_dict (dict, optional): Dictionary to store parsed data (default: None).

    Returns:
        dict: Parsed dictionary with structured XML data.
    """
    try:
        if data_dict is None:
            data_dict = {}

        audit_trail_entries = []  # List to store AuditTrail entries

        for child in element:
            child_key = clean_key(child.tag)
            key = f"{parent_key}_{child_key}" if parent_key else child_key

            if child_key == "AuditTrailEntry":
                # Handle AuditTrailEntry separately as a list of dictionaries
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

                audit_trail_entry.setdefault("notes", None)  # Ensure 'notes' key exists
                audit_trail_entries.append(audit_trail_entry)

            elif len(list(child)) > 0:  # If element has child elements, recurse
                nested_dict = parse_element(child, key, {})  # Ensure proper nesting

                for k, v in nested_dict.items():
                    data_dict[f"{key}_{k}"] = v  # Maintain hierarchy with parent_child structure
            else:
                # Extract text value if it's a leaf node
                text_value = child.text.strip() if child.text else None

                if text_value is not None:
                    text_value = text_value.replace("\r", " ").replace("\n", " ")

                data_dict[key] = text_value  # Store key-value pair in dictionary

        if audit_trail_entries:
            data_dict["AuditTrail"] = audit_trail_entries  # Add AuditTrail list to dictionary

        return data_dict

    except Exception as e:
        logging.error(f"Error while parsing XML element '{element.tag}': {e}")
        return data_dict if data_dict else {}  # Return partial data if an error occurs

# Example XML for testing
xml_string = """
<Root>
    <pmtid_pmtid_txtid>12345</pmtid_pmtid_txtid>
    <audittrialentry_audittrialentry_reftxf_audittrialentry_reftxf_pmtid>67890</audittrialentry_audittrialentry_reftxf_audittrialentry_reftxf_pmtid>
    <AuditTrailEntry>
        <timestamp>2024-03-12T12:00:00</timestamp>
        <user>admin</user>
        <Notes>This is a test note</Notes>
    </AuditTrailEntry>
</Root>
"""

# Parse XML string into an ElementTree
try:
    root = ET.fromstring(xml_string)
    parsed_data = parse_element(root)
    print(parsed_data)
except Exception as e:
    logging.error(f"Error parsing XML string: {e}")
