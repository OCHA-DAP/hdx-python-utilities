from configparser import SafeConfigParser
from os.path import join
from typing import Optional

from hdx.utilities.path import project_root_dir


def get_version() -> Optional[str]:
    """
    Get version

    Args:
        dirpath (str): Directory where setup.cfg is located

    Returns:
        Optional[str]: Version if available or None

    """
    config = SafeConfigParser()
    config.read(join(project_root_dir(2), "setup.cfg"))
    if not config.has_section("metadata"):
        return None
    return config["metadata"].get("version")
