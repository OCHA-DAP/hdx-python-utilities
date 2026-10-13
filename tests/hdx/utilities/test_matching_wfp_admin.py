"""RapidFuzzMatcher on the match() calls hdx-python-country's AdminLevel made
for hdx-scraper-wfp-foodprices market admin names (prod vs stage world runs,
2026-10-12/13). Expected names are the candidates whose p-code is correct.
none_acceptable means returning no match is correct, eg. for pre-2020
Ukrainian raions or pre-2025 Burundian communes with no same-name successor.
"""

import json
from collections import Counter
from os.path import join

from hdx.utilities.matching import RapidFuzzMatcher


def al_transform_1(name: str) -> str | None:
    # As AdminLevel.fuzzy_pcode
    prefix = name[:3]
    if prefix == "al ":
        return f"ad {name[3:]}"
    if prefix == "ad ":
        return f"al {name[3:]}"
    return None


def al_transform_2(name: str) -> str | None:
    # As AdminLevel.fuzzy_pcode
    if name[:3] in ("al ", "ad "):
        return name[3:]
    return None


def score_calls(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        extract = json.load(f)
    matcher = RapidFuzzMatcher(RapidFuzzMatcher.place_name_scorer)
    results = []
    for call in extract["calls"]:
        possible_names = extract["candidate_sets"][call["candidate_set"]]
        index = matcher.match(
            possible_names,
            call["name"],
            alternative_name=call["alternative_name"],
            transform_possible_names=[al_transform_1, al_transform_2],
        )
        if index is None:
            outcome = "correct" if call["none_acceptable"] else "miss"
            matched = None
        else:
            matched = possible_names[index]
            outcome = "correct" if matched in call["expected_names"] else "wrong"
        results.append({**call, "matched": matched, "outcome": outcome})
    return results


class TestMatchingWFPAdmin:
    def test_wfp_admin_matcher_calls(self, fixturesfolder):
        results = score_calls(
            join(fixturesfolder, "matching", "wfp_admin_matcher_calls.json")
        )
        # 4.2.0: 205 correct, 27 miss, 68 wrong. Most remaining wrong
        # results are single-word near misses, eg. pre-2020 Ukrainian raions
        # matched to unrelated new raions ("novoazovskyi" -> "volnovaskyi").
        assert Counter(result["outcome"] for result in results) == {
            "correct": 210,
            "miss": 27,
            "wrong": 63,
        }
        matched = {
            (result["countryiso3"], result["name"]): result["matched"]
            for result in results
        }
        assert matched["ETH", "e shewa"] == "east shewa"
        assert matched["ETH", "s w shewa"] == "south west shewa"
        assert matched["ETH", "s gonder"] == "south gondar"
        assert matched["ETH", "b gumuz"] == "benishangul gumuz"
        assert matched["PHL", "region iv b"] is None
