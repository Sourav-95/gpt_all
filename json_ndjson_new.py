def copy_file_to_gcs(self, capture_file: FileLookupDc, checksum_metd) -> FileLookupDc:
    """
    Method to copy file(s) from Source bucket+folder to target bucket+folder.
    If JSON, transforms to NDJSON in-memory and writes to target GCS.
    Args:
        checksum_metd:
        capture_file:

    Returns:
        Updated capture_file with target checksum
    """
    logger.debug(f'Source Bucket: {self.job_params.gcs_src_bckt_nm}')
    logger.debug(f'Target Bucket: {self.job_params.gcs_tgt_bckt_nm}')

    _, src_folder_path = capture_file.src_file_path.split('/', 1)
    src_folder_file_path = os.path.join(src_folder_path, capture_file.file_name)
    tgt_folder_file_path = os.path.join(self.job_params.gcs_tgt_folder_nm, capture_file.file_name)
    logger.debug(f'Source file Blob / folder: {src_folder_file_path}')
    logger.debug(f'Target  file Blob / folder: {tgt_folder_file_path}')

    try:
        src_bucket = self.gcs_client_instance.get_bucket(self.job_params.gcs_src_bckt_nm, retry=self.retry_strategy)
        dst_bucket = self.gcs_client_instance.get_bucket(self.job_params.gcs_tgt_bckt_nm, retry=self.retry_strategy)

        src_blob = src_bucket.blob(src_folder_file_path)
        dst_blob = dst_bucket.blob(tgt_folder_file_path)

        # Handle JSON to NDJSON transformation if needed
        if src_blob.exists() and capture_file.file_name.endswith(".json"):
            logger.debug(f"Transforming JSON to NDJSON for file: {capture_file.file_name}")
            json_data = json.loads(src_blob.download_as_text())
            # Open GCS write stream to write NDJSON
            with dst_blob.open(mode="w", content_type="application/x-ndjson") as f:
                if isinstance(json_data, list):
                    for obj in json_data:
                        f.write(json.dumps(obj) + "\n")
                elif isinstance(json_data, dict):
                    f.write(json.dumps(json_data) + "\n")
                else:
                    raise ValueError("Unsupported JSON format for NDJSON conversion")
        elif src_blob.exists():
            # Binary copy for non-JSON files
            token = None
            while True:
                token, bytes_rewritten, total_bytes = dst_blob.rewrite(src_blob,
                                                                       token=token,
                                                                       retry=self.retry_strategy)
                if not token:
                    break

        # Post-copy validations
        if dst_blob.exists():
            logger.debug(f"File `{src_blob.name}` from bucket `{self.job_params.gcs_src_bckt_nm}` "
                         f"copied to file `{dst_blob.name}` to bucket `{self.job_params.gcs_tgt_bckt_nm}`")

            gcs_file_integrity_operations = GCSFileIntegrityOperations(env_params_dc=self.env_params,
                                                                       job_params_dc=self.job_params,
                                                                       global_rt_params=self.global_rt_params,
                                                                       arg_params_dc=self.arg_params)

            _, _, _, dst_file_checksum = gcs_file_integrity_operations.get_data_file_integrity_values(
                checksum_method=checksum_metd,
                file_full_path=os.path.join(self.job_params.gcs_tgt_bckt_nm, tgt_folder_file_path),
                rowcount_require=False)
        else:
            logger.error(f"Error Blob `{src_blob.name}` in bucket `{self.job_params.gcs_src_bckt_nm}` "
                         f"unable to copy blob `{dst_blob.name}` in bucket `{self.job_params.gcs_tgt_bckt_nm}`")
            dst_file_checksum = None

        logger.debug(f"file {dst_blob.name}: checksum `{dst_file_checksum}`")
        return capture_file.set_tgt_dq(tgt_file_path=self.job_params.gcs_tgt_folder_nm, tgt_dq=dst_file_checksum)

    except Exception as exp:
        logger.error(exp)
        e = GcsFileOperationException(env_params_dc=self.env_params,
                                      global_rt_params_dc=self.global_rt_params,
                                      arg_params_dc=self.arg_params,
                                      job_params_dc=self.job_params)
        e.logged_exception_in_bq(message=str(exp),
                                 session_id=generate_session_id(),
                                 session_name="Copy file")
