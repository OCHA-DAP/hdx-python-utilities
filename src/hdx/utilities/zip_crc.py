import struct
from io import IOBase
from os import fstat
from typing import Dict, Tuple

EOCD_MIN_SIZE = 22
MAX_COMMENT_SIZE = 65535
EOCD_SIGNATURE = b"PK\x05\x06"
CD_HEADER_SIGNATURE = b"PK\x01\x02"


def find_eocd_signature(tail_data: bytes) -> Tuple[int, int, int]:
    """Find EOCD Signature in zip file

    Args:
        tail_data (bytes): Data to search for EOCD

    Returns:
        Tuple[int, int, int]: (total_records, cd_offset, cd_end) or (-1, -1, -1) on failure
    """
    eocd_pos = tail_data.rfind(EOCD_SIGNATURE)
    if eocd_pos == -1:
        return -1, -1, -1

    # Unpack EOCD
    eocd = tail_data[eocd_pos : eocd_pos + 22]
    _, _, _, _, total_records, cd_size, cd_offset, _ = struct.unpack("<4sHHHHIIH", eocd)
    cd_end = cd_offset + cd_size
    return total_records, cd_offset, cd_end


def parse_central_directory(data: bytes, num_records: int) -> Dict[str, int]:
    """Parse zip file Central Directory and return dictionary with filepaths as keys
    and CRC32 as values.

    Args:
        data (bytes): Data to parse
        num_records (int): Number of files in zip

    Returns:
        Dict[str, int]: Dictionary of filepath to file CRC32
    """
    results = {}
    offset = 0
    for _ in range(num_records):
        if offset + 46 > len(data):
            break
        if data[offset : offset + 4] != CD_HEADER_SIGNATURE:
            break

        fields = struct.unpack("<4sHHHHHHIIIHHHHHII", data[offset : offset + 46])
        crc32 = fields[7]
        filepath_len = fields[10]
        extra_len = fields[11]
        comment_len = fields[12]

        filepath = data[offset + 46 : offset + 46 + filepath_len].decode(
            "utf-8", "replace"
        )
        if not filepath.endswith("/"):
            results[filepath] = crc32

        offset += 46 + filepath_len + extra_len + comment_len
    return results


def get_tail_start(size: int) -> int:
    """Get the starting offset of the tail of a zip.

    Args:
        size (int): File size

    Returns:
        int: Starting offset of the tail of a zip
    """
    read_size = min(size, MAX_COMMENT_SIZE + EOCD_MIN_SIZE)
    return size - read_size


def get_zip_tail_header(size: int) -> Dict[str, str]:
    """Get a header for a GET request with range from starting offset of the tail
    to the end of a zip.

    Args:
        size (int): File size

    Returns:
        Dict[str, str]: Header for GET request
    """
    return {"Range": f"bytes={get_tail_start(size)}-"}


def get_zip_cd_header(tail_data: bytes) -> Tuple[int, Dict]:
    """Get a header for a GET request with range for the Central Directory of a zip.

    Args:
        tail_data (bytes): Data to search for EOCD

    Returns:
        Tuple[int, Dict]: (total_records, CD range header) or (-1, {}) on failure
    """
    total_records, cd_offset, cd_end = find_eocd_signature(tail_data)
    if total_records == -1:
        return -1, {}
    return total_records, {"Range": f"bytes={cd_offset}-{cd_end - 1}"}


def get_zip_crcs_buffer(buffer: bytes) -> Dict[str, int]:
    """Get CRC32 for each file in a zip given a buffer

    Args:
        buffer (bytes): Zip in buffer

    Returns:
        Dict[str, int]: Dictionary of filepath to file CRC32
    """
    tail_data = buffer[get_tail_start(len(buffer)) :]
    num_records, cd_offset, cd_end = find_eocd_signature(tail_data)
    if num_records == -1:
        return {}
    cd_data = buffer[cd_offset:cd_end]
    return parse_central_directory(cd_data, num_records)


def get_zip_crcs_fp(fp: IOBase) -> Dict[str, int]:
    """Get CRC32 for each file in a zip given a file pointer

    Args:
        fp (IOBase): Zip file pointer

    Returns:
        Dict[str, int]: Dictionary of filepath to file CRC32
    """
    size = fstat(fp.fileno()).st_size
    tail_start = get_tail_start(size)
    fp.seek(tail_start, 0)
    tail_data = fp.read()
    num_records, cd_offset, cd_end = find_eocd_signature(tail_data)
    if num_records == -1:
        return {}
    fp.seek(cd_offset, 0)
    cd_data = fp.read(cd_end - cd_offset)
    return parse_central_directory(cd_data, num_records)


def get_crc_sum(file_crcs: Dict[str, int]) -> str:
    """Calculate the sum of the CRC32 for all files in a zip

    Args:
        file_crcs (Dict[str, int]): Dictionary of filepath to file CRC32

    Returns:
        str: Sum of the CRC32
    """
    crc_sum = 0
    for crc in file_crcs.values():
        crc_sum ^= crc
    if crc_sum:
        return f"{crc_sum:08x}"
    return ""
