from google.cloud import storage
import json

def convert_json_to_ndjson(source_bucket_name, source_blob_name, target_bucket_name, target_blob_name):
    # Initialize client
    client = storage.Client()

    # Read from source GCS bucket
    source_bucket = client.bucket(source_bucket_name)
    blob = source_bucket.blob(source_blob_name)
    json_data = json.loads(blob.download_as_bytes())  # In-memory

    # Convert to NDJSON format
    ndjson_lines = []
    if isinstance(json_data, list):
        ndjson_lines = [json.dumps(record) for record in json_data]
    elif isinstance(json_data, dict):
        ndjson_lines = [json.dumps(json_data)]  # Single JSON object
    else:
        raise ValueError("Unsupported JSON format")

    ndjson_content = '\n'.join(ndjson_lines)

    # Write to target GCS bucket
    target_bucket = client.bucket(target_bucket_name)
    target_blob = target_bucket.blob(target_blob_name)
    target_blob.upload_from_string(ndjson_content, content_type='application/x-ndjson')

    print(f"Converted and uploaded NDJSON to gs://{target_bucket_name}/{target_blob_name}")
