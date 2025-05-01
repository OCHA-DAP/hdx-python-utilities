"""Text Processing Tests"""

from string import punctuation, whitespace

from pytest import approx

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
)


class TestText:
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
