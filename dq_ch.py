class NasFileOperations:
    """Class is to validate provided Source file data quality
    Calculate file row count
    """

    global_rt_param = None  # Class attribute
    job_param = None  # Class attribute

    def __init__(self, job_params_dc: JobLookupDc, global_rt_params_dc: GlobalRtLookupDc):
        NasFileOperations.job_param = job_params_dc  # Assign to class attribute
        NasFileOperations.global_rt_param = global_rt_params_dc  # Assign to class attribute

    @classmethod
    def _read_file_in_byte_chunks(cls, file_path, binary, chunk_size=8192):
        """
        Generator to read a file in chunks.
        """
        if binary:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    yield chunk
        else:
            with open(file_path, 'r', encoding=cls.job_param.char_set_cd) as f:
                while chunk := f.read(chunk_size):
                    yield chunk

    @staticmethod
    def calculate_sha256(file, chunk_size=8192):
        """
        Calculate sha256 hash of a file.
        """
        if NasFileOperations.global_rt_param is None:
            raise ValueError("global_rt_param is not set. Make sure to instantiate NasFileOperations first.")

        data_file_ext = file.rsplit('.', 1)[-1].lower()
        if data_file_ext in NasFileOperations.global_rt_param.NON_BINARY_FILE_EXT.enum:
            binary = False
        else:
            binary = True

        hashlib_sha256 = hashlib.sha256()

        for chunk in NasFileOperations._read_file_in_byte_chunks(file, binary, chunk_size):
            if not chunk:
                break
            if not binary:
                chunk = chunk.encode(NasFileOperations.job_param.char_set_cd)
            hashlib_sha256.update(chunk)

        return hashlib_sha256.hexdigest() if binary else "checksumprocess_disabled_for_delimited_files"
