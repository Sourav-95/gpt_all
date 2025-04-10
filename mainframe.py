import codecs
import os
from parser.unpacker import unpack_comp, unpack_comp3
from parser.edcdic_logger import logging as lg
import logging

logger = logging.getLogger(__name__)

class EBCDIC_Decoder:

    @classmethod
    def parse_dat_file(cls, file_path, schema):
        results = []

        # Calculate total size of one record
        record_size = sum(field["length"] for field in schema)

        with open(file_path, 'rb') as f:
            while True:
                record_bytes = f.read(record_size)
                if not record_bytes or len(record_bytes) < record_size:
                    break  # End of file or incomplete record

                record = {}
                byte_pointer = 0  # Reset for each record

                lg.info(f'Reading record of length: {len(record_bytes)}')
                lg.info(f'Record bytes: {record_bytes}')

                for field in schema:
                    field_name = field['name']
                    field_type = field['type']
                    field_length = field['length']
                    field_data = record_bytes[byte_pointer:byte_pointer+field_length]
                    actual_length = len(field_data)

                    lg.info(f'Starting Pointer: {byte_pointer}')
                    byte_pointer += field_length
                    lg.info(f'End Pointer: {byte_pointer}')

                    try:
                        if field_type == 'CHAR':
                            if actual_length < field_length:
                                decoded_data = ' ' * (field_length - actual_length)
                                record[field_name] = decoded_data
                            else:
                                decoded_data = codecs.decode(field_data, 'cp500').strip()
                                record[field_name] = decoded_data

                        elif field_type == 'COMP':
                            decoded_data = unpack_comp(field_data, field_length)
                            record[field_name] = decoded_data

                        elif field_type == 'COMP-3':
                            decoded_data = unpack_comp3(field_data, field_length)
                            record[field_name] = decoded_data

                        lg.info(f'Raw data: {field_data} || Decoded: {decoded_data}')
                        lg.info(f"Actual Length: {actual_length}, Expected Length: {field_length}\n")

                    except Exception as e:
                        lg.error(f"Error decoding {field_name} of type {field_type}: {e}")
                        record[field_name] = None  # or a default value like 0

                results.append(record)

        return results

    @classmethod
    def _get_header_src_count(cls, file_path):
        src_file_dump = file_path.replace('.DAT', '')
        src_file_hdr_path = src_file_dump + '_hdr.DAT'
        if os.path.exists(src_file_hdr_path):
            with open(src_file_hdr_path, 'rb') as f:
                line = f.readline()
                decoded_data = codecs.decode(line, 'cp500')
                data_list = decoded_data.split()
                new_src_count = int(data_list[1])
                return new_src_count
        else:
            lg.info('Header File doesn’t exist')
            return None
