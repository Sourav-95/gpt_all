""" Replace this block of Code"""

# Copy Source to Destination
if src_blob.exists():
    token = None
    while True:
        token, bytes_rewritten, total_bytes = dst_blob.rewrite(src_blob,
                                                               token=token,
                                                               retry=self.retry_strategy)
        if not token:
            break


""" With this logic:
Download JSON in memory

Parse it

Transform it into NDJSON

Upload transformed NDJSON to target"""

if src_blob.exists():
    # Step 1: Download JSON data as bytes
    json_bytes = src_blob.download_as_bytes(retry=self.retry_strategy)
    json_obj = json.loads(json_bytes)

    # Step 2: Transform to NDJSON
    if isinstance(json_obj, list):
        ndjson_lines = [json.dumps(item) for item in json_obj]
    elif isinstance(json_obj, dict):
        ndjson_lines = [json.dumps(json_obj)]
    else:
        logger.error(f"Unexpected JSON format in file `{src_blob.name}`")
        raise ValueError("Invalid JSON format")

    ndjson_data = "\n".join(ndjson_lines)

    # Step 3: Upload NDJSON to target
    dst_blob.upload_from_string(ndjson_data, content_type='application/x-ndjson')

    logger.debug(f"NDJSON transformed file `{src_blob.name}` uploaded to `{dst_blob.name}` in bucket `{self.job_params.gcs_tgt_bckt_nm}`")
