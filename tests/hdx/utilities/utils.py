def assert_downloaders(downloader1, downloader2, params):
    user_agent, custom_user_agent, extra_params_dict = params
    test_url = "http://www.lalala.com/lala"
    assert downloader1.session.headers["User-Agent"].endswith(user_agent)
    assert downloader1.session.auth is None
    assert downloader1.get_full_url(test_url) == test_url
    assert downloader2.session.headers["User-Agent"].endswith(
        custom_user_agent
    )
    assert downloader2.session.auth == ("user", "pass")
    key, value = next(iter(extra_params_dict.items()))
    assert downloader2.get_full_url(test_url) == f"{test_url}?{key}={value}"
