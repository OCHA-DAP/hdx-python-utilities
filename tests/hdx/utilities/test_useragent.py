"""User Agent Tests"""
from os.path import join

import pytest

from hdx.utilities import __version__
from hdx.utilities.loader import LoadError
from hdx.utilities.useragent import UserAgent, UserAgentError


class TestUserAgent:
    @pytest.fixture(scope="class")
    def user_agent_config_yaml(self, configfolder):
        return join(configfolder, "user_agent_config.yml")

    @pytest.fixture(scope="class")
    def user_agent_config2_yaml(self, configfolder):
        return join(configfolder, "user_agent_config2.yml")

    @pytest.fixture(scope="class")
    def user_agent_config3_yaml(self, configfolder):
        return join(configfolder, "user_agent_config3.yml")

    @pytest.fixture(scope="class")
    def empty_yaml(self, configfolder):
        return join(configfolder, "empty.yml")

    @pytest.fixture(scope="class")
    def user_agent_config_wrong_yaml(self, configfolder):
        return join(configfolder, "user_agent_config_wrong.yml")

    def test_user_agent(
        self,
        monkeypatch,
        user_agent_config_yaml,
        user_agent_config2_yaml,
        user_agent_config3_yaml,
        empty_yaml,
        user_agent_config_wrong_yaml,
    ):
        assert (
            UserAgent.get(user_agent_config_yaml=user_agent_config_yaml)
            == f"lala:HDXPythonUtilities/{__version__}-myua"
        )
        assert (
            UserAgent.get(user_agent_config_yaml=user_agent_config2_yaml)
            == f"HDXPythonUtilities/{__version__}-myuseragent"
        )
        assert (
            UserAgent.get(
                user_agent_config_yaml=user_agent_config3_yaml,
                user_agent_lookup="lookup",
            )
            == f"HDXPythonUtilities/{__version__}-mylookupagent"
        )
        assert (
            UserAgent.get(user_agent="my_ua", preprefix="papa")
            == f"papa:HDXPythonUtilities/{__version__}-my_ua"
        )
        UserAgent.set_global(
            user_agent_config_yaml=user_agent_config3_yaml,
            user_agent_lookup="lookup2",
        )
        assert (
            UserAgent.get()
            == f"HDXPythonUtilities/{__version__}-mylookupagent2"
        )
        UserAgent.clear_global()
        with pytest.raises(UserAgentError):
            UserAgent.get(
                user_agent_config_yaml=user_agent_config3_yaml,
                user_agent_lookup="fail",
            )
        with pytest.raises(LoadError):
            UserAgent.get(user_agent_config_yaml=empty_yaml)
        with pytest.raises(UserAgentError):
            UserAgent.get(user_agent_config_yaml=user_agent_config_wrong_yaml)
        with pytest.raises(UserAgentError):
            UserAgent.get(user_agent_config_yaml="")
        with pytest.raises(UserAgentError):
            UserAgent.get()
        with pytest.raises(UserAgentError):
            UserAgent._load(prefix="", user_agent_config_yaml="")
        my_user_agent = "lala"
        monkeypatch.setenv("USER_AGENT", my_user_agent)
        assert (
            UserAgent.get()
            == f"HDXPythonUtilities/{__version__}-{my_user_agent}"
        )
        my_preprefix = "haha"
        monkeypatch.setenv("PREPREFIX", my_preprefix)
        assert (
            UserAgent.get()
            == f"{my_preprefix}:HDXPythonUtilities/{__version__}-{my_user_agent}"
        )
        my_prefix = f"HDXPythonLibrary/{__version__}"
        assert (
            UserAgent.get(prefix=my_prefix)
            == f"{my_preprefix}:{my_prefix}-{my_user_agent}"
        )
        UserAgent.clear_global()
