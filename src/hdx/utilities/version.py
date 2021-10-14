from configparser import SafeConfigParser
from os.path import join
from typing import Optional


def get_version(projname: str) -> Optional[str]:
    """
    Get version

    Args:
        dirpath (str): Directory where setup.cfg is located

    Returns:
        Optional[str]: Version if available or None

    """
    config = SafeConfigParser()
    config.read(join(dirpath, "setup.cfg"))
    if not config.has_section("metadata"):
        return None
    return config["metadata"].get("version")
