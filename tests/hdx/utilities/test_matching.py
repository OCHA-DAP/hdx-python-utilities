"""Matching Tests"""

from hdx.utilities.matching import (
    Phonetics,
    earliest_index,
    get_code_from_name,
    get_matching_text,
    get_matching_text_in_strs,
    get_matching_then_nonmatching_text,
    match_template_variables,
    multiple_replace,
)
from hdx.utilities.text import normalise


class TestMatching:
    a = "The quick brown fox jumped over the lazy dog. It was so fast!"
    b = "The quicker brown fox leapt over the slower fox. It was so fast!"
    c = "The quick brown fox climbed over the lazy dog. It was so fast!"

    def test_phonetics(self):
        possible_names = ["Al Maharah", "Ad Dali", "Dhamar"]
        phonetics = Phonetics()
        assert phonetics.match(possible_names, "al dali") == 1
        assert phonetics.match(possible_names, "xxx", "Damar") == 2
        transform_possible_names = [lambda x: None]
        assert (
            phonetics.match(possible_names, "xxx", "yyy", transform_possible_names)
            is None
        )

    def test_get_code_from_name_org_type(self):
        org_type_lookup = {
            "Academic / Research": "431",
            "Donor": "433",
            "Embassy": "434",
            "Government": "435",
            "International NGO": "437",
            "International Organization": "438",
            "Media": "439",
            "Military": "440",
            "National NGO": "441",
            "Other": "443",
            "Private sector": "444",
            "Red Cross / Red Crescent": "445",
            "Religious": "446",
            "United Nations": "447",
        }
        org_type_map = {
            "agence un": "447",
            "govt": "435",
            "ingo": "437",
            "mouv. cr": "445",
            "nngo": "441",
            "ong int": "437",
            "ong nat": "441",
            "un agency": "447",
        }
        actual_org_type_lookup = {normalise(k): v for k, v in org_type_lookup.items()}
        actual_org_type_lookup.update(org_type_map)
        assert (
            get_code_from_name(
                "NATIONAL_NGO",
                actual_org_type_lookup,
                [],
                fuzzy_match=False,
            )
            == "441"
        )
        assert (
            get_code_from_name(
                "COOPÉRATION_INTERNATIONALE",
                actual_org_type_lookup,
                [],
                fuzzy_match=False,
            )
            is None
        )
        unmatched = []
        assert (
            get_code_from_name(
                "COOPÉRATION_INTERNATIONALE",
                actual_org_type_lookup,
                unmatched,
                fuzzy_match=True,
            )
            is None
        )
        assert (
            get_code_from_name(
                "COOPÉRATION_INTERNATIONALE",
                actual_org_type_lookup,
                unmatched,
                fuzzy_match=True,
            )
            is None
        )
        assert (
            get_code_from_name("NGO", actual_org_type_lookup, [], fuzzy_match=False)
            is None
        )
        assert (
            get_code_from_name(
                "International",
                actual_org_type_lookup,
                [],
                fuzzy_match=False,
            )
            is None
        )

    def test_get_code_from_name_sector(self):
        sector_lookup = {
            "Emergency Shelter and NFI": "SHL",
            "Camp Coordination / Management": "CCM",
            "Mine Action": "PRO - MIN",
            "Food Security": "FSC",
            "Water Sanitation Hygiene": "WSH",
            "Logistics": "LOG",
            "Child Protection": "PRO - CPN",
            "Protection": "PRO",
            "Education": "EDU",
            "Nutrition": "NUT",
            "Health": "HEA",
            "Early Recovery": "ERY",
            "Emergency Telecommunications": "TEL",
            "Gender Based Violence": "PRO - GBV",
            "Housing, Land and Property": "PRO - HLP",
        }
        sector_map = {
            "abris": "SHL",
            "cccm": "CCM",
            "coordination": "CCM",
            "education": "EDU",
            "eha": "WSH",
            "erl": "ERY",
            "nutrition": "NUT",
            "operatioanl presence: water, sanitation & hygiene": "WSH",
            "operational presence: education in emergencies": "EDU",
            "operational presence: emergency shelter & non-food items": "SHL",
            "operational presence: food security & agriculture": "FSC",
            "operational presence: health": "HEA",
            "operational presence: nutrition": "NUT",
            "operational presence: protection": "PRO",
            "protection": "PRO",
            "sa": "FSC",
            "sante": "HEA",
            "wash": "WSH",
        }

        actual_sector_lookup = {normalise(k): v for k, v in sector_lookup.items()}
        actual_sector_lookup.update(sector_map)
        assert (
            get_code_from_name("education", actual_sector_lookup, [], fuzzy_match=True)
            == "EDU"
        )
        assert (
            get_code_from_name("LOGISTIQUE", actual_sector_lookup, [], fuzzy_match=True)
            == "LOG"
        )
        assert (
            get_code_from_name("CCCM", actual_sector_lookup, [], fuzzy_match=False)
            == "CCM"
        )
        assert (
            get_code_from_name("Santé", actual_sector_lookup, [], fuzzy_match=False)
            == "HEA"
        )
        actual_sector_lookup["cccm"] = "CCM"
        assert (
            get_code_from_name("CCS", actual_sector_lookup, [], fuzzy_match=False)
            is None
        )

    def test_multiple_replace(self):
        result = multiple_replace(
            self.a, {"quick": "slow", "fast": "slow", "lazy": "busy"}
        )
        assert result == "The slow brown fox jumped over the busy dog. It was so slow!"

    def test_match_template_variables(self):
        assert match_template_variables("dasdda") == (None, None)
        assert match_template_variables("dasdda{{abc}}gff") == (
            "{{abc}}",
            "abc",
        )

    def test_earliest_index(self):
        assert earliest_index(self.a, ["fox"]) == 16
        assert earliest_index(self.a, ["lala"]) is None
        assert earliest_index(self.a, ["lala", "fox", "haha", "dog"]) == 16
        assert earliest_index(self.a, ["dog", "lala", "fox", "haha"]) == 16
        assert earliest_index(self.a, ["dog", "lala", "fox", "haha", "quick"]) == 4

    def test_get_matching_text_in_strs(self):
        result = get_matching_text_in_strs(self.a, self.b)
        assert result == []
        result = get_matching_text_in_strs(self.a, self.b, match_min_size=10)
        assert result == [" brown fox ", " over the ", ". It was so fast!"]
        result = get_matching_text_in_strs(
            self.a, self.b, match_min_size=9, end_characters=".!\r\n"
        )
        assert result == [
            "The quick",
            " brown fox ",
            " over the ",
            " It was so fast!",
        ]
        result = get_matching_text_in_strs(self.a, self.c, match_min_size=5)
        assert result == [
            "The quick brown fox ",
            "ed over the lazy dog. It was so fast!",
        ]
        result = get_matching_text_in_strs(
            self.a, self.c, match_min_size=5, end_characters=".\r\n"
        )
        assert result == ["The quick brown fox ", "ed over the lazy dog."]
        result = get_matching_text_in_strs(
            self.a, self.c, match_min_size=5, end_characters=".!\r\n"
        )
        assert result == [
            "The quick brown fox ",
            "ed over the lazy dog. It was so fast!",
        ]

    def test_get_matching_text(self):
        list_of_text = [self.a, self.b, self.c]
        result = get_matching_text(list_of_text, match_min_size=10)
        assert result == " brown fox  over the  It was so fast!"
        description = [
            'Internally displaced persons are defined according to the 1998 Guiding Principles (http://www.internal-displacement.org/publications/1998/ocha-guiding-principles-on-internal-displacement) as people or groups of people who have been forced or obliged to flee or to leave their homes or places of habitual residence, in particular as a result of armed conflict, or to avoid the effects of armed conflict, situations of generalized violence, violations of human rights, or natural or human-made disasters and who have not crossed an international border.\n\n"People Displaced" refers to the number of people living in displacement as of the end of each year.\n\nContains data from IDMC\'s [data portal](https://github.com/idmc-labs/IDMC-Platform-API/wiki).',
            'Internally displaced persons are defined according to the 1998 Guiding Principles (http://www.internal-displacement.org/publications/1998/ocha-guiding-principles-on-internal-displacement) as people or groups of people who have been forced or obliged to flee or to leave their homes or places of habitual residence, in particular as a result of armed conflict, or to avoid the effects of armed conflict, situations of generalized violence, violations of human rights, or natural or human-made disasters and who have not crossed an international border.\n\n"New Displacement" refers to the number of new cases or incidents of displacement recorded, rather than the number of people displaced. This is done because people may have been displaced more than once.\n\nContains data from IDMC\'s [data portal](https://github.com/idmc-labs/IDMC-Platform-API/wiki).',
            'Internally displaced persons are defined according to the 1998 Guiding Principles (http://www.internal-displacement.org/publications/1998/ocha-guiding-principles-on-internal-displacement) as people or groups of people who have been forced or obliged to flee or to leave their homes or places of habitual residence, in particular as a result of armed conflict, or to avoid the effects of armed conflict, situations of generalized violence, violations of human rights, or natural or human-made disasters and who have not crossed an international border.\n\n"New Displacement" refers to the number of new cases or incidents of displacement recorded, rather than the number of people displaced. This is done because people may have been displaced more than once.\n\nContains data from IDMC\'s [data portal](https://github.com/idmc-labs/IDMC-Platform-API/wiki).',
        ]
        result = get_matching_text(description, ignore="\n", end_characters=".!")
        assert (
            result
            == """Internally displaced persons are defined according to the 1998 Guiding Principles (http://www.internal-displacement.org/publications/1998/ocha-guiding-principles-on-internal-displacement) as people or groups of people who have been forced or obliged to flee or to leave their homes or places of habitual residence, in particular as a result of armed conflict, or to avoid the effects of armed conflict, situations of generalized violence, violations of human rights, or natural or human-made disasters and who have not crossed an international border.

Contains data from IDMC's [data portal](https://github.com/idmc-labs/IDMC-Platform-API/wiki)."""
        )

    def test_get_matching_then_nonmatching_text(self):
        list_of_str = [self.a, self.b, self.c]
        result = get_matching_then_nonmatching_text(list_of_str, match_min_size=10)
        assert (
            result
            == " brown fox  over the  It was so fast!The quickjumpedlazy dog.The quickerleaptslower fox.The quickclimbedlazy dog."
        )
        description = [
            'Internally displaced persons are defined according to the 1998 Guiding Principles (http://www.internal-displacement.org/publications/1998/ocha-guiding-principles-on-internal-displacement) as people or groups of people who have been forced or obliged to flee or to leave their homes or places of habitual residence, in particular as a result of armed conflict, or to avoid the effects of armed conflict, situations of generalized violence, violations of human rights, or natural or human-made disasters and who have not crossed an international border.\n\n"People Displaced" refers to the number of people living in displacement as of the end of each year.\n\nContains data from IDMC\'s [data portal](https://github.com/idmc-labs/IDMC-Platform-API/wiki).',
            'Internally displaced persons are defined according to the 1998 Guiding Principles (http://www.internal-displacement.org/publications/1998/ocha-guiding-principles-on-internal-displacement) as people or groups of people who have been forced or obliged to flee or to leave their homes or places of habitual residence, in particular as a result of armed conflict, or to avoid the effects of armed conflict, situations of generalized violence, violations of human rights, or natural or human-made disasters and who have not crossed an international border.\n\n"New Displacement" refers to the number of new cases or incidents of displacement recorded, rather than the number of people displaced. This is done because people may have been displaced more than once.\n\nContains data from IDMC\'s [data portal](https://github.com/idmc-labs/IDMC-Platform-API/wiki).',
            'Internally displaced persons are defined according to the 1998 Guiding Principles (http://www.internal-displacement.org/publications/1998/ocha-guiding-principles-on-internal-displacement) as people or groups of people who have been forced or obliged to flee or to leave their homes or places of habitual residence, in particular as a result of armed conflict, or to avoid the effects of armed conflict, situations of generalized violence, violations of human rights, or natural or human-made disasters and who have not crossed an international border.\n\n"New Displacement" refers to the number of new cases or incidents of displacement recorded, rather than the number of people displaced. This is done because people may have been displaced more than once.\n\nContains data from IDMC\'s [data portal](https://github.com/idmc-labs/IDMC-Platform-API/wiki).',
        ]
        result = get_matching_then_nonmatching_text(
            description, separator="\n\n", ignore="\n"
        )
        print(result)
        assert (
            result
            == """Internally displaced persons are defined according to the 1998 Guiding Principles (http://www.internal-displacement.org/publications/1998/ocha-guiding-principles-on-internal-displacement) as people or groups of people who have been forced or obliged to flee or to leave their homes or places of habitual residence, in particular as a result of armed conflict, or to avoid the effects of armed conflict, situations of generalized violence, violations of human rights, or natural or human-made disasters and who have not crossed an international border.

"People Displaced" refers to the number of people living in displacement as of the end of each year.

"New Displacement" refers to the number of new cases or incidents of displacement recorded, rather than the number of people displaced. This is done because people may have been displaced more than once.

Contains data from IDMC's [data portal](https://github.com/idmc-labs/IDMC-Platform-API/wiki)."""
        )
