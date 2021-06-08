# -*- coding: UTF-8 -*-
"""Text Processing Tests"""
from string import punctuation, whitespace

from pytest import approx

from hdx.utilities.text import get_matching_text_in_strs, get_matching_then_nonmatching_text, get_matching_text, \
    get_words_in_sentence, multiple_replace, remove_from_end, remove_end_characters, remove_string, \
    PUNCTUATION_MINUS_BRACKETS, get_fraction_str, number_format, only_allowed_in_str, get_numeric_if_possible


class TestText:
    a = 'The quick brown fox jumped over the lazy dog. It was so fast!'
    b = 'The quicker brown fox leapt over the slower fox. It was so fast!'
    c = 'The quick brown fox climbed over the lazy dog. It was so fast!'

    def test_remove_end_characters(self):
        assert remove_end_characters('lalala,.,"') == 'lalala'
        assert remove_end_characters('lalala, .\t/,"', '%s%s' % (punctuation, whitespace)) == 'lalala'

    def test_remove_from_end(self):
        result = remove_from_end(TestText.a, ['fast!', 'so', 'hello', 'as'], 'Transforming %s -> %s')
        assert result == 'The quick brown fox jumped over the lazy dog. It was'
        result = remove_from_end(TestText.a, ['fast!', 'so', 'hello', 'as'], 'Transforming %s -> %s', False)
        assert result == 'The quick brown fox jumped over the lazy dog. It w'

    def test_remove_string(self):
        assert remove_string('lala, 01/02/2020 ', '01/02/2020') == 'lala '
        assert remove_string('lala,(01/02/2020) ', '01/02/2020') == 'lala) '
        assert remove_string('lala, 01/02/2020 ', '01/02/2020', PUNCTUATION_MINUS_BRACKETS) == 'lala '
        assert remove_string('lala,(01/02/2020) ', '01/02/2020', PUNCTUATION_MINUS_BRACKETS) == 'lala,() '

    def test_multiple_replace(self):
        result = multiple_replace(TestText.a, {'quick': 'slow', 'fast': 'slow', 'lazy': 'busy'})
        assert result == 'The slow brown fox jumped over the busy dog. It was so slow!'

    def test_get_words_in_sentence(self):
        result = get_words_in_sentence("Korea (Democratic People's Republic of)")
        assert result == ['Korea', 'Democratic', "People's", 'Republic', 'of']
        result = get_words_in_sentence('Serbia and Kosovo: S/RES/1244 (1999)')
        assert result == ['Serbia', 'and', 'Kosovo', 'S', 'RES', '1244', '1999']

    def test_get_matching_text_in_strs(self):
        result = get_matching_text_in_strs(TestText.a, TestText.b)
        assert result == []
        result = get_matching_text_in_strs(TestText.a, TestText.b, match_min_size=10)
        assert result == [' brown fox ', ' over the ', '. It was so fast!']
        result = get_matching_text_in_strs(TestText.a, TestText.b, match_min_size=9, end_characters='.!\r\n')
        assert result == ['The quick', ' brown fox ', ' over the ', ' It was so fast!']
        result = get_matching_text_in_strs(TestText.a, TestText.c, match_min_size=5)
        assert result == ['The quick brown fox ', 'ed over the lazy dog. It was so fast!']
        result = get_matching_text_in_strs(TestText.a, TestText.c, match_min_size=5, end_characters='.\r\n')
        assert result == ['The quick brown fox ', 'ed over the lazy dog.']
        result = get_matching_text_in_strs(TestText.a, TestText.c, match_min_size=5, end_characters='.!\r\n')
        assert result == ['The quick brown fox ', 'ed over the lazy dog. It was so fast!']

    def test_get_matching_text(self):
        l = [TestText.a, TestText.b, TestText.c]
        result = get_matching_text(l, match_min_size=10)
        assert result == ' brown fox  over the  It was so fast!'
        description = ['Internally displaced persons are defined according to the 1998 Guiding Principles (http://www.internal-displacement.org/publications/1998/ocha-guiding-principles-on-internal-displacement) as people or groups of people who have been forced or obliged to flee or to leave their homes or places of habitual residence, in particular as a result of armed conflict, or to avoid the effects of armed conflict, situations of generalized violence, violations of human rights, or natural or human-made disasters and who have not crossed an international border.\n\n"People Displaced" refers to the number of people living in displacement as of the end of each year.\n\nContains data from IDMC\'s [data portal](https://github.com/idmc-labs/IDMC-Platform-API/wiki).', 'Internally displaced persons are defined according to the 1998 Guiding Principles (http://www.internal-displacement.org/publications/1998/ocha-guiding-principles-on-internal-displacement) as people or groups of people who have been forced or obliged to flee or to leave their homes or places of habitual residence, in particular as a result of armed conflict, or to avoid the effects of armed conflict, situations of generalized violence, violations of human rights, or natural or human-made disasters and who have not crossed an international border.\n\n"New Displacement" refers to the number of new cases or incidents of displacement recorded, rather than the number of people displaced. This is done because people may have been displaced more than once.\n\nContains data from IDMC\'s [data portal](https://github.com/idmc-labs/IDMC-Platform-API/wiki).', 'Internally displaced persons are defined according to the 1998 Guiding Principles (http://www.internal-displacement.org/publications/1998/ocha-guiding-principles-on-internal-displacement) as people or groups of people who have been forced or obliged to flee or to leave their homes or places of habitual residence, in particular as a result of armed conflict, or to avoid the effects of armed conflict, situations of generalized violence, violations of human rights, or natural or human-made disasters and who have not crossed an international border.\n\n"New Displacement" refers to the number of new cases or incidents of displacement recorded, rather than the number of people displaced. This is done because people may have been displaced more than once.\n\nContains data from IDMC\'s [data portal](https://github.com/idmc-labs/IDMC-Platform-API/wiki).']
        result = get_matching_text(description, ignore='\n', end_characters='.!')
        assert result == '''Internally displaced persons are defined according to the 1998 Guiding Principles (http://www.internal-displacement.org/publications/1998/ocha-guiding-principles-on-internal-displacement) as people or groups of people who have been forced or obliged to flee or to leave their homes or places of habitual residence, in particular as a result of armed conflict, or to avoid the effects of armed conflict, situations of generalized violence, violations of human rights, or natural or human-made disasters and who have not crossed an international border.

Contains data from IDMC's [data portal](https://github.com/idmc-labs/IDMC-Platform-API/wiki).'''

    def test_get_matching_then_nonmatching_text(self):
        l = [TestText.a, TestText.b, TestText.c]
        result = get_matching_then_nonmatching_text(l, match_min_size=10)
        assert result == ' brown fox  over the  It was so fast!The quickjumpedlazy dog.The quickerleaptslower fox.The quickclimbedlazy dog.'
        description = ['Internally displaced persons are defined according to the 1998 Guiding Principles (http://www.internal-displacement.org/publications/1998/ocha-guiding-principles-on-internal-displacement) as people or groups of people who have been forced or obliged to flee or to leave their homes or places of habitual residence, in particular as a result of armed conflict, or to avoid the effects of armed conflict, situations of generalized violence, violations of human rights, or natural or human-made disasters and who have not crossed an international border.\n\n"People Displaced" refers to the number of people living in displacement as of the end of each year.\n\nContains data from IDMC\'s [data portal](https://github.com/idmc-labs/IDMC-Platform-API/wiki).', 'Internally displaced persons are defined according to the 1998 Guiding Principles (http://www.internal-displacement.org/publications/1998/ocha-guiding-principles-on-internal-displacement) as people or groups of people who have been forced or obliged to flee or to leave their homes or places of habitual residence, in particular as a result of armed conflict, or to avoid the effects of armed conflict, situations of generalized violence, violations of human rights, or natural or human-made disasters and who have not crossed an international border.\n\n"New Displacement" refers to the number of new cases or incidents of displacement recorded, rather than the number of people displaced. This is done because people may have been displaced more than once.\n\nContains data from IDMC\'s [data portal](https://github.com/idmc-labs/IDMC-Platform-API/wiki).', 'Internally displaced persons are defined according to the 1998 Guiding Principles (http://www.internal-displacement.org/publications/1998/ocha-guiding-principles-on-internal-displacement) as people or groups of people who have been forced or obliged to flee or to leave their homes or places of habitual residence, in particular as a result of armed conflict, or to avoid the effects of armed conflict, situations of generalized violence, violations of human rights, or natural or human-made disasters and who have not crossed an international border.\n\n"New Displacement" refers to the number of new cases or incidents of displacement recorded, rather than the number of people displaced. This is done because people may have been displaced more than once.\n\nContains data from IDMC\'s [data portal](https://github.com/idmc-labs/IDMC-Platform-API/wiki).']
        result = get_matching_then_nonmatching_text(description, separator='\n\n', ignore='\n')
        print(result)
        assert result == '''Internally displaced persons are defined according to the 1998 Guiding Principles (http://www.internal-displacement.org/publications/1998/ocha-guiding-principles-on-internal-displacement) as people or groups of people who have been forced or obliged to flee or to leave their homes or places of habitual residence, in particular as a result of armed conflict, or to avoid the effects of armed conflict, situations of generalized violence, violations of human rights, or natural or human-made disasters and who have not crossed an international border.

"People Displaced" refers to the number of people living in displacement as of the end of each year.

"New Displacement" refers to the number of new cases or incidents of displacement recorded, rather than the number of people displaced. This is done because people may have been displaced more than once.

Contains data from IDMC's [data portal](https://github.com/idmc-labs/IDMC-Platform-API/wiki).'''

    def test_number_format(self):
        assert number_format(1234.56789) == '1234.5679'
        assert number_format('') == ''
        assert number_format(None) == ''
        assert number_format(1234.5, '%.4f') == '1234.5000'
        assert number_format(1234.5, '%.4f', False) == '1234.5'
        assert number_format(1234, '%.4f', False) == '1234'

    def test_get_fraction_str(self):
        assert get_fraction_str('abc', 345) == ''
        assert get_fraction_str(123, 345) == '0.3565'
        assert get_fraction_str(123, 0) == ''

    def test_only_allowed_in_str(self):
        assert only_allowed_in_str('1234a', {'1', '2', '3', 'a'}) is False
        assert only_allowed_in_str('1234a', {'1', '2', '3', '4', 'a'}) is True

    def test_get_numeric_if_possible(self):
        assert get_numeric_if_possible(123) == 123
        assert get_numeric_if_possible(-123) == -123
        assert get_numeric_if_possible(123.45) == 123.45
        assert get_numeric_if_possible(-123.45) == -123.45
        assert get_numeric_if_possible('') == ''
        assert get_numeric_if_possible('hello') == 'hello'
        assert get_numeric_if_possible('123') == 123
        assert get_numeric_if_possible('-123') == -123
        assert get_numeric_if_possible('123.45') == 123.45
        assert get_numeric_if_possible('-123.45') == -123.45
        assert get_numeric_if_possible('123,123,123.45') == 123123123.45
        assert get_numeric_if_possible('123.123.123,45') == 123123123.45
        assert get_numeric_if_possible('123,123,123') == 123123123
        assert get_numeric_if_possible('123.123.123') == 123123123
        assert get_numeric_if_possible('12.3%') == approx(0.123)
        assert get_numeric_if_possible('10%') == 0.1
        assert get_numeric_if_possible('-10%') == -0.1
        assert get_numeric_if_possible('10-') == '10-'
        assert get_numeric_if_possible('123,123.45%') == 1231.2345
        assert get_numeric_if_possible('-123,123.45%') == -1231.2345
        assert get_numeric_if_possible('123.123,45%') == 1231.2345
