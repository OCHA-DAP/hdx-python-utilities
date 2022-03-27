"""HTML Tests"""
from os.path import join

import pytest

from hdx.utilities.html import extract_table, get_soup
from hdx.utilities.loader import load_text


class TestHTML:
    url = "https://unstats.un.org/unsd/methodology/m49/overview/"

    @pytest.fixture(scope="function")
    def htmltext(self, fixturesfolder):
        return load_text(join(fixturesfolder, "html", "response.html"))

    @pytest.fixture(scope="function")
    def downloader(self, htmltext):
        class Response:
            pass

        class Download:
            @staticmethod
            def download(url):
                response = Response()
                if url == TestHTML.url:
                    response.text = htmltext
                return response

        return Download()

    def test_html(self, downloader):
        soup = get_soup(TestHTML.url, downloader=downloader)
        tabletag = soup.find(id="downloadTableEN")
        result = extract_table(tabletag)
        assert len(result) == 249
        assert result[10] == {
            "Intermediate Region Name": "Eastern Africa",
            "Global Code": "001",
            "Region Code": "002",
            "Land Locked Developing Countries (LLDC)": "",
            "Intermediate Region Code": "014",
            "Sub-region Name": "Sub-Saharan Africa",
            "Least Developed Countries (LDC)": "x",
            "Global Name": "World",
            "M49 Code": "262",
            "ISO-alpha3 Code": "DJI",
            "Small Island Developing States (SIDS)": "",
            "Developed / Developing Countries": "Developing",
            "Country or Area": "Djibouti",
            "Region Name": "Africa",
            "Sub-region Code": "202",
        }
        assert result[247] == {
            "Global Code": "001",
            "Sub-region Name": "Polynesia",
            "Intermediate Region Code": "",
            "Intermediate Region Name": "",
            "Region Code": "009",
            "Least Developed Countries (LDC)": "x",
            "ISO-alpha3 Code": "TUV",
            "Sub-region Code": "061",
            "Region Name": "Oceania",
            "Developed / Developing Countries": "Developing",
            "Small Island Developing States (SIDS)": "x",
            "Land Locked Developing Countries (LLDC)": "",
            "M49 Code": "798",
            "Global Name": "World",
            "Country or Area": "Tuvalu",
        }
