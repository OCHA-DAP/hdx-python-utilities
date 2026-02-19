"""Text Processing Tests"""

from string import punctuation, whitespace

import pytest
from pytest import approx

from hdx.utilities.downloader import Download
from hdx.utilities.text import (
    PUNCTUATION_MINUS_BRACKETS,
    get_fraction_str,
    get_numeric_if_possible,
    get_words_in_sentence,
    normalise,
    number_format,
    only_allowed_in_str,
    remove_end_characters,
    remove_from_end,
    remove_string,
    smart_split,
)


class TestText:
    @pytest.fixture(scope="function")
    def text1(self, fixturesfolder):
        with Download() as downloader:
            return downloader.download_text(fixturesfolder / "text" / "text1.txt")

    @pytest.fixture(scope="function")
    def text2(self, fixturesfolder):
        with Download() as downloader:
            return downloader.download_text(fixturesfolder / "text" / "text2.txt")

    def test_normalise(self):
        assert (
            normalise("£^*& ()+-[]<>?|\ Al DhaleZ'eÉ / الضالع,,..1234''#~~### ")
            == "al dhalezee 1234"
        )

    def test_remove_end_characters(self):
        assert remove_end_characters('lalala,.,"') == "lalala"
        assert (
            remove_end_characters('lalala, .\t/,"', f"{punctuation}{whitespace}")
            == "lalala"
        )

    def test_remove_from_end(self):
        a = "The quick brown fox jumped over the lazy dog. It was so fast!"
        result = remove_from_end(
            a, ["fast!", "so", "hello", "as"], "Transforming %s -> %s"
        )
        assert result == "The quick brown fox jumped over the lazy dog. It was"
        result = remove_from_end(
            a,
            ["fast!", "so", "hello", "as"],
            "Transforming %s -> %s",
            False,
        )
        assert result == "The quick brown fox jumped over the lazy dog. It w"

    def test_remove_string(self):
        assert remove_string("lala, 01/02/2020 ", "01/02/2020") == "lala "
        assert remove_string("lala,(01/02/2020) ", "01/02/2020") == "lala) "
        assert (
            remove_string("lala, 01/02/2020 ", "01/02/2020", PUNCTUATION_MINUS_BRACKETS)
            == "lala "
        )
        assert (
            remove_string(
                "lala,(01/02/2020) ", "01/02/2020", PUNCTUATION_MINUS_BRACKETS
            )
            == "lala,() "
        )

    def test_get_words_in_sentence(self):
        result = get_words_in_sentence("Korea (Democratic People's Republic of)")
        assert result == ["Korea", "Democratic", "People's", "Republic", "of"]
        result = get_words_in_sentence("Serbia and Kosovo: S/RES/1244 (1999)")
        assert result == [
            "Serbia",
            "and",
            "Kosovo",
            "S",
            "RES",
            "1244",
            "1999",
        ]

    def test_number_format(self):
        assert number_format(1234.56789) == "1234.5679"
        assert number_format("") == ""
        assert number_format(None) == ""
        assert number_format(1234.5, "%.4f") == "1234.5000"
        assert number_format(1234.5, "%.4f", False) == "1234.5"
        assert number_format(1234, "%.4f", False) == "1234"

    def test_get_fraction_str(self):
        assert get_fraction_str("abc", 345) == ""
        assert get_fraction_str(123, 345) == "0.3565"
        assert get_fraction_str(123, 0) == ""

    def test_only_allowed_in_str(self):
        assert only_allowed_in_str("1234a", {"1", "2", "3", "a"}) is False
        assert only_allowed_in_str("1234a", {"1", "2", "3", "4", "a"}) is True

    def test_get_numeric_if_possible(self):
        assert get_numeric_if_possible(123) == 123
        assert get_numeric_if_possible(-123) == -123
        assert get_numeric_if_possible(123.45) == 123.45
        assert get_numeric_if_possible(-123.45) == -123.45
        assert get_numeric_if_possible("") == ""
        assert get_numeric_if_possible("hello") == "hello"
        assert get_numeric_if_possible("123") == 123
        assert get_numeric_if_possible("-123") == -123
        assert get_numeric_if_possible("123.45") == 123.45
        assert get_numeric_if_possible("-123.45") == -123.45
        assert get_numeric_if_possible("123,123,123.45") == 123123123.45
        assert get_numeric_if_possible("123.123.123,45") == 123123123.45
        assert get_numeric_if_possible("123,123,123") == 123123123
        assert get_numeric_if_possible("123.123.123") == 123123123
        assert get_numeric_if_possible("12.3%") == approx(0.123)
        assert get_numeric_if_possible("10%") == 0.1
        assert get_numeric_if_possible("-10%") == -0.1
        assert get_numeric_if_possible("10-") == "10-"
        assert get_numeric_if_possible("123,123.45%") == 1231.2345
        assert get_numeric_if_possible("-123,123.45%") == -1231.2345
        assert get_numeric_if_possible("123.123,45%") == 1231.2345

    def test_smart_split(self, text1, text2):
        result = smart_split(text1)
        assert result == (
            "The World Database on Protected and Conserved Areas (WDPCA) combines the "
            "formerly separate World Database on Protected Areas (WDPA) and World "
            "Database on Other Effective Area-based Conservation Measures (WD-OECM). The "
            "WDPCA is the most comprehensive global database of marine and terrestrial "
            "protected areas and other effective area-based conservation measures, "
            "updated on a monthly basis, and is one of the key global biodiversity "
            "datasets being widely used by scientists, businesses, governments, "
            "international secretariats, and others to inform planning, policy decisions, "
            "and management.\n"
            "\n"
            "The WDPCA is part of the Protected Planet Initiative, a joint product of the "
            "UN Environment Programme and the International Union for Conservation of "
            "Nature (IUCN). The compilation and management of the WDPCA is carried out by "
            "the UN Environment Programme World Conservation Monitoring Centre "
            "(UNEP-WCMC), in collaboration with governments and other stakeholders. Data "
            "and information on the world's protected and conserved areas compiled in the "
            "WDPCA is used for reporting on progress towards reaching Target 3 of the "
            "Kunming-Montreal Global Biodiversity Framework, which calls for 30% of the "
            "worldâ€™s land and waters to be effectively conserved by 2030.\n"
            "\n"
            "Additionally, the WDPCA is used for reporting to the UN to track progress "
            "towards the 2030 Sustainable Development Goals, tracking of core indicators "
            "of the Intergovernmental Science-Policy Platform on Biodiversity and "
            "Ecosystem Services (IPBES), and providing information for other "
            "international assessments and reports including the Global Biodiversity "
            "Outlook. UNEP-WCMC and IUCN periodically release the Protected Planet Report "
            "on the status of the world's protected and conserved areas.\n"
            "\n"
            "Many platforms are incorporating the WDPCA to provide integrated information "
            "to diverse users, including businesses and governments, in a range of "
            "sectors. For example, the WDPCA is included in the Integrated Biodiversity "
            "Assessment Tool (IBAT), an innovative decision support tool that gives "
            "commercial users easy access to up-to-date information that allows them to "
            "identify biodiversity risks and opportunities within a project boundary.\n"
            "\n"
            "The reach of the WDPCA is further enhanced by the UN Biodiversity Lab as "
            "well as services developed by other parties, such as the Global Forest Watch "
            "and the Digital Observatory for Protected Areas, which provide decision "
            "makers with access to monitoring and alert systems that allow whole "
            "landscapes to be managed better. Together, these applications of the WDPCA "
            "demonstrate the growing value and significance of the Protected Planet "
            "initiative."
        )
        result = smart_split(text2)
        assert result == (
            "UNHCR, the UN Refugee Agency, is a global organization dedicated to saving "
            "lives, protecting rights and building a better future for people forced to "
            "flee their homes because of conflict and persecution. We lead international "
            "action to protect refugees, forcibly displaced communities and stateless "
            "people. Our vision is a world where every person forced to flee can build a "
            "better future. Formally known as the Office of the High Commissioner for "
            "Refugees, UNHCR was established by the General Assembly of the United "
            "Nations in 1950 in the aftermath of the Second World War to help the "
            "millions of people who had lost their homes.\n"
            "\n"
            "Today, UNHCR works in 128 countries. We provide life-saving assistance, "
            "including shelter, food, water and medical care for people forced to flee "
            "conflict and persecution, many of whom have nobody left to turn to. We "
            "defend their right to reach safety and help them find a place to call home "
            "so they can rebuild their lives. Long term, we work with countries to "
            "improve and monitor refugee and asylum laws and policies, ensuring human "
            "rights are upheld.\n"
            "\n"
            "In everything we do UNHCR considers refugees and those forced to flee as "
            "partners, putting those most affected at the centre of planning and "
            "decision-making."
        )
