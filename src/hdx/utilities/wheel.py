import logging
from os import listdir, system
from typing import Optional

logger = logging.getLogger(__name__)


def get_version_from_whl(dirpath: str) -> Optional[str]:
    """
    Get version

    Args:
        dirpath (str): Path where wheel resides

    Returns:
        Optional[str]: Version if available or None

    """
    version = None
    for file in listdir(dirpath):
        if file.endswith(".whl"):
            version = file.split("-")[1]
            break
    return version


def git_tag_whl(dirpath: str) -> None:
    """
    Create git tag for whl given folder

    Args:
        dirpath (str): Path where wheel resides

    Returns:
        None

    """
    version = get_version_from_whl(dirpath)
    logger.info(f"Creating git tag {version}")
    system(f"git tag v{version}")
    system("git push --tags")
