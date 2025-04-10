# Becomes this in JSON format:

# json
# Copy
# Edit
[
    {"name": "ASSGN_ID", "type": "COMP", "length": 4},
    {"name": "ASSGN_TYP", "type": "CHAR", "length": 8},
    {"name": "ATTRB_CD", "type": "CHAR", "length": 8},
    {"name": "ATTR_VALU_CD", "type": "CHAR", "length": 8},
    {"name": "ASSGN_OWN_CD", "type": "CHAR", "length": 8},
    {"name": "UPDT_TS", "type": "CHAR", "length": 26},
    {"name": "UPDT_USER_ID", "type": "CHAR", "length": 8}
]
# Save this in a file, say schema.json.

# ✅ Step 2: Load JSON schema in Python
# Add this to your script before initializing the class:

# python
# Copy
# Edit
import json

with open("schema.json", "r") as f:
    schema = json.load(f)
# Now you can pass schema as usual:


decoder = EBCDICDecoder("your_file.DAT", schema)
parsed_data = decoder.parse()
