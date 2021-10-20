from uuid import UUID, uuid4


def get_uuid() -> str:
    """
    Get an UUID.

    Returns:
        str: A UUID
    """
    return str(uuid4())


def is_valid_uuid(uuid_to_test: str, version: int = 4) -> bool:
    """
    Check if uuid_to_test is a valid UUID.

    Args:
        uuid_to_test (str): UUID to test for validity
        version (int): UUID version. Defaults to 4.

    Returns:
        str: Current script's directory
    """
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except Exception:
        return False
    return str(uuid_obj) == uuid_to_test
