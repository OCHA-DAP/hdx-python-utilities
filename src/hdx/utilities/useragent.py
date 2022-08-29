"""User agent utilities"""
import logging
import os
from os.path import expanduser, isfile, join
from typing import Any, Dict, Optional

from . import __version__
from .loader import load_yaml

logger = logging.getLogger(__name__)


class UserAgentError(Exception):
    pass


class UserAgent:
    default_user_agent_config_yaml = join(expanduser("~"), ".useragent.yml")
    user_agent = None

    @staticmethod
    def _environment_variables(**kwargs: Any) -> Any:
        """
        Overwrite keyword arguments with environment variables

        Args:
            **kwargs: See below
            user_agent (str): User agent string.

        Returns:
            kwargs: Changed keyword arguments

        """
        user_agent = os.getenv("USER_AGENT")
        if user_agent is not None:
            kwargs["user_agent"] = user_agent
        preprefix = os.getenv("PREPREFIX")
        if preprefix is not None:
            kwargs["preprefix"] = preprefix
        return kwargs

    @staticmethod
    def _construct(configdict: Dict, prefix: str, ua: str) -> str:
        """
        Construct user agent

        Args:
            configdict (str): Additional configuration for user agent
            prefix (str): Text to put at start of user agent
            ua (str): Custom user agent text

        Returns:
            str: Full user agent string

        """
        if not ua:
            raise UserAgentError(
                "User_agent parameter missing. It can be your project's name for example."
            )
        preprefix = configdict.get("preprefix")
        if preprefix:
            user_agent = f"{preprefix}:"
        else:
            user_agent = ""
        if prefix:
            user_agent = f"{user_agent}{prefix}-"
        user_agent = f"{user_agent}{ua}"
        return user_agent

    @classmethod
    def _load(
        cls,
        prefix: str,
        user_agent_config_yaml: str,
        user_agent_lookup: Optional[str] = None,
    ) -> str:
        """
        Load user agent YAML file

        Args:
            prefix (str): Text to put at start of user agent
            user_agent_config_yaml (str): Path to user agent YAML file
            user_agent_lookup (Optional[str]): Lookup key for YAML. Ignored if user_agent supplied.

        Returns:
            str: user agent

        """
        if not user_agent_config_yaml:
            user_agent_config_yaml = cls.default_user_agent_config_yaml
            logger.info(
                f"No user agent or user agent config file given. Using default user agent config file: {user_agent_config_yaml}."
            )
        if not isfile(user_agent_config_yaml):
            raise UserAgentError(
                "User_agent should be supplied in a YAML config file. It can be your project's name for example."
            )
        logger.info(
            f"Loading user agent config from: {user_agent_config_yaml}"
        )
        user_agent_config_dict = load_yaml(user_agent_config_yaml)
        if user_agent_lookup:
            user_agent_config_dict = user_agent_config_dict.get(
                user_agent_lookup
            )
        if not user_agent_config_dict:
            raise UserAgentError(
                f"No user agent information read from: {user_agent_config_yaml}"
            )
        ua = user_agent_config_dict.get("user_agent")
        return cls._construct(user_agent_config_dict, prefix, ua)

    @classmethod
    def _create(
        cls,
        user_agent: Optional[str] = None,
        user_agent_config_yaml: Optional[str] = None,
        user_agent_lookup: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        Get full user agent string

        Args:
            user_agent (Optional[str]): User agent string. HDXPythonLibrary/X.X.X- is prefixed.
            user_agent_config_yaml (Optional[str]): Path to YAML user agent configuration. Ignored if user_agent supplied. Defaults to ~/.useragent.yml.
            user_agent_lookup (Optional[str]): Lookup key for YAML. Ignored if user_agent supplied.

        Returns:
            str: Full user agent string

        """
        kwargs = UserAgent._environment_variables(**kwargs)
        user_agent = kwargs.pop("user_agent", user_agent)
        prefix = kwargs.pop("prefix", None)
        if not prefix:
            prefix = f"HDXPythonUtilities/{__version__}"
        if not user_agent:
            ua = cls._load(prefix, user_agent_config_yaml, user_agent_lookup)
        else:
            ua = cls._construct(kwargs, prefix, user_agent)
        return ua

    @classmethod
    def clear_global(cls) -> None:
        """
        Clear stored user agent string

        Returns:
            None

        """
        cls.user_agent = None

    @classmethod
    def set_global(
        cls,
        user_agent: Optional[str] = None,
        user_agent_config_yaml: Optional[str] = None,
        user_agent_lookup: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Set global user agent string

        Args:
            user_agent (Optional[str]): User agent string. HDXPythonLibrary/X.X.X- is prefixed.
            user_agent_config_yaml (Optional[str]): Path to YAML user agent configuration. Ignored if user_agent supplied. Defaults to ~/.useragent.yml.
            user_agent_lookup (Optional[str]): Lookup key for YAML. Ignored if user_agent supplied.

        Returns:
            None
        """
        cls.user_agent = cls._create(
            user_agent, user_agent_config_yaml, user_agent_lookup, **kwargs
        )

    @classmethod
    def get(
        cls,
        user_agent: Optional[str] = None,
        user_agent_config_yaml: Optional[str] = None,
        user_agent_lookup: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        Get full user agent string from parameters if supplied falling back on global user agent if set.

        Args:
            user_agent (Optional[str]): User agent string. HDXPythonLibrary/X.X.X- is prefixed.
            user_agent_config_yaml (Optional[str]): Path to YAML user agent configuration. Ignored if user_agent supplied. Defaults to ~/.useragent.yml.
            user_agent_lookup (Optional[str]): Lookup key for YAML. Ignored if user_agent supplied.

        Returns:
            str: Full user agent string

        """
        if (
            user_agent
            or user_agent_config_yaml
            or "user_agent" in UserAgent._environment_variables(**kwargs)
        ):
            return UserAgent._create(
                user_agent, user_agent_config_yaml, user_agent_lookup, **kwargs
            )
        if cls.user_agent:
            return cls.user_agent
        else:
            raise UserAgentError(
                "You must either set the global user agent: UserAgent.set_global(...) or pass in user agent parameters!"
            )
