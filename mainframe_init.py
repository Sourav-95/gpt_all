import codecs
import os
from parser.unpacker import unpack_comp, unpack_comp3
from parser.edcdic_logger import logging as lg
import logging

logger = logging.getLogger(__name__)

class EBCDICDecoder:
    def __init__(self, file_path, schema):
        self.file_path = file_path
        self.schema = schema
        self.record_size = sum(field['length'] for field in schema)

    def parse(self):
        results = []
        with open(self.file_path, 'rb') as f:
            while True:
                record_bytes = f.read(self.record_size)
                if not record_bytes or len(record_bytes) < self.record_size:
                    break

                record = {}
                byte_pointer = 0

                for field in self.schema:
                    field_name = field['name']
                    field_type = field['type']
                    field_length = field['length']
                    field_data = record_bytes[byte_pointer : byte_pointer + field_length]
                    actual_length = len(field_data)
                    byte_pointer += field_length

                    lg.info(f'Starting Pointer: {byte_pointer - field_length}')
                    lg.info(f'End Pointer: {byte_pointer}')

                    try:
                        if field_type == 'CHAR':
                            if actual_length < field_length:
                                decoded_data = ' ' * (field_length - actual_length)
                            else:
                                decoded_data = codecs.decode(field_data, 'cp500')
                            record[field_name] = decoded_data

                        elif field_type == 'COMP':
                            decoded_data = unpack_comp(field_data, field_length)
                            record[field_name] = decoded_data

                        elif field_type == 'COMP-3':
                            decoded_data = unpack_comp3(field_data, field_length)
                            record[field_name] = decoded_data

                    except (ValueError, IndexError) as e:
                        record[field_name] = 0
                        lg.warning(f"Decoding failed for field {field_name}: {e}")

                results.append(record)
        return results

    def get_header_src_count(self):
        src_file_hdr_path = self.file_path.replace('.DAT', '') + '_hdr.DAT'
        if os.path.exists(src_file_hdr_path):
            with open(src_file_hdr_path, 'rb') as f:
                line = f.readline()
                decoded_data = codecs.decode(line, 'cp500')
                data_list = decoded_data.split()
                return int(data_list[1])
        else:
            lg.info('Header File does not exist')
            return None
