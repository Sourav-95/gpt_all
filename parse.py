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

                if subchild_key == "Notes":
                    audit_trail_entry["notes"] = subchild_text
                else:
                    audit_trail_entry[subchild_key] = subchild_text

            audit_trail_entry.setdefault("notes", None)
            audit_trail_entries.append(audit_trail_entry)
        
        elif len(list(child)) > 0:  # If element has child elements
            nested_dict = parse_element(child, key, {})  # Ensure nested dictionary is correctly formed

            for k, v in nested_dict.items():
                data_dict[f"{key}_{k}"] = v  # Maintain parent_child structure
        else:
            text_value = child.text.strip() if child.text else None

            if text_value is not None:
                text_value = text_value.replace("\r", " ").replace("\n", " ")

            data_dict[key] = text_value  # Ensure hierarchical key structure

    if audit_trail_entries:
        data_dict["AuditTrail"] = audit_trail_entries

    return data_dict
