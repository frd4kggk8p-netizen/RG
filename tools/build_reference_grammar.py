#!/usr/bin/env python3
"""
Reading Greek — Reference Grammar (§340+) Ingestion
Compiles canonical noun declension patterns (1a through 3h), pronouns,
and verb paradigm tables with morpheme analysis for Phase 5.
"""

import os
import json

REFERENCE_DATA = {
    "title": "Reference Grammar (§340–§375)",
    "description": "Systematic paradigms for noun declension codes, pronouns, and verb conjugations in Reading Greek.",
    "noun_declensions": {
        "1a": {
            "name": "First Declension: Feminines in -η",
            "example": "βο-ή, ἡ (‘shout’)",
            "stem": "βο-",
            "table": {
                "header": [["Case", "Singular", "Plural"]],
                "rows": [
                    ["Nom.", "βο-ή", "βο-αί"],
                    ["Acc.", "βο-ήν", "βο-άς"],
                    ["Gen.", "βο-ῆς", "βο-ῶν"],
                    ["Dat.", "βο-ῇ", "βο-αῖς"]
                ]
            }
        },
        "1b": {
            "name": "First Declension: Feminines in -ᾱ",
            "example": "χώρ-ᾱ, ἡ (‘land, country’)",
            "stem": "χωρ-",
            "table": {
                "header": [["Case", "Singular", "Plural"]],
                "rows": [
                    ["Nom.", "χώρ-ᾱ", "χῶρ-αι"],
                    ["Acc.", "χώρ-ᾱν", "χώρ-ᾱς"],
                    ["Gen.", "χώρ-ᾱς", "χωρ-ῶν"],
                    ["Dat.", "χώρ-ᾳ", "χώρ-αις"]
                ]
            }
        },
        "1c": {
            "name": "First Declension: Feminines in -ᾰ",
            "example": "θάλαττ-α, ἡ (‘sea’)",
            "stem": "θαλαττ-",
            "table": {
                "header": [["Case", "Singular", "Plural"]],
                "rows": [
                    ["Nom.", "θάλαττ-α", "θάλαττ-αι"],
                    ["Acc.", "θάλαττ-αν", "θαλάττ-ᾱς"],
                    ["Gen.", "θαλάττ-ης", "θαλαττ-ῶν"],
                    ["Dat.", "θαλάττ-ῃ", "θαλάττ-αις"]
                ]
            }
        },
        "1d": {
            "name": "First Declension: Masculines in -ης",
            "example": "ναύτ-ης, ὁ (‘sailor’)",
            "stem": "ναυτ-",
            "table": {
                "header": [["Case", "Singular", "Plural"]],
                "rows": [
                    ["Nom.", "ναύτ-ης", "ναῦτ-αι"],
                    ["Acc.", "ναύτ-ην", "ναύτ-ᾱς"],
                    ["Gen.", "ναύτ-ου", "ναυτ-ῶν"],
                    ["Dat.", "ναύτ-ῃ", "ναύτ-αις"],
                    ["Voc.", "ναῦτ-α", "ναῦτ-αι"]
                ]
            }
        },
        "2a": {
            "name": "Second Declension: Masculine/Feminine in -ος",
            "example": "λόγ-ος, ὁ (‘word, story, reason’)",
            "stem": "λογ-",
            "table": {
                "header": [["Case", "Singular", "Plural"]],
                "rows": [
                    ["Nom.", "λόγ-ος", "λόγ-οι"],
                    ["Acc.", "λόγ-ον", "λόγ-ους"],
                    ["Gen.", "λόγ-ου", "λόγ-ων"],
                    ["Dat.", "λόγ-ῳ", "λόγ-οις"],
                    ["Voc.", "λόγ-ε", "λόγ-οι"]
                ]
            }
        },
        "2b": {
            "name": "Second Declension: Neuter in -ον",
            "example": "παιδί-ον, τό (‘child, young slave’) / ἔργ-ον, τό (‘work’)",
            "stem": "παιδι- / ἐργ-",
            "table": {
                "header": [["Case", "Singular", "Plural"]],
                "rows": [
                    ["Nom.", "παιδί-ον / ἔργ-ον", "παιδί-α / ἔργ-α"],
                    ["Acc.", "παιδί-ον / ἔργ-ον", "παιδί-α / ἔργ-α"],
                    ["Gen.", "παιδί-ου / ἔργ-ου", "παιδί-ων / ἔργ-ων"],
                    ["Dat.", "παιδί-ῳ / ἔργ-ῳ", "παιδί-οις / ἔργ-οις"],
                    ["Voc.", "παιδί-ον / ἔργ-ον", "παιδί-α / ἔργ-α"]
                ]
            }
        },
        "3a": {
            "name": "Third Declension: Consonant Stems (Masc/Fem)",
            "example": "φύλαξ, ὁ (stem φυλακ-, ‘guard’) / νύξ, ἡ (stem νυκτ-, ‘night’)",
            "stem": "φυλακ- / νυκτ-",
            "table": {
                "header": [["Case", "Singular", "Plural"]],
                "rows": [
                    ["Nom.", "φύλαξ", "φύλακ-ες"],
                    ["Acc.", "φύλακ-α", "φύλακ-ας"],
                    ["Gen.", "φύλακ-ος", "φυλάκ-ων"],
                    ["Dat.", "φύλακ-ι", "φύλαξ-ι(ν)"]
                ]
            }
        },
        "3b": {
            "name": "Third Declension: Neuter Stems in -μα(τ)-",
            "example": "σῶμα, τό (stem σωματ-, ‘body’)",
            "stem": "σωματ-",
            "table": {
                "header": [["Case", "Singular", "Plural"]],
                "rows": [
                    ["Nom.", "σῶμα", "σώματ-α"],
                    ["Acc.", "σῶμα", "σώματ-α"],
                    ["Gen.", "σώματ-ος", "σωμάτ-ων"],
                    ["Dat.", "σώματ-ι", "σώμα-σι(ν)"]
                ]
            }
        },
        "3c": {
            "name": "Third Declension: Stems in -ντ-",
            "example": "γέρων, ὁ (stem γεροντ-, ‘old man’)",
            "stem": "γεροντ-",
            "table": {
                "header": [["Case", "Singular", "Plural"]],
                "rows": [
                    ["Nom.", "γέρων", "γέροντ-ες"],
                    ["Acc.", "γέροντ-α", "γέροντ-ας"],
                    ["Gen.", "γέροντ-ος", "γερόντ-ων"],
                    ["Dat.", "γέροντ-ι", "γέρου-σι(ν)"],
                    ["Voc.", "γέρον", "γέροντ-ες"]
                ]
            }
        },
        "3d": {
            "name": "Third Declension: Syncopated Stems in -ερ-/-ρ-",
            "example": "πατήρ, ὁ (stem πατερ-/πατρ-, ‘father’)",
            "stem": "πατερ- / πατρ-",
            "table": {
                "header": [["Case", "Singular", "Plural"]],
                "rows": [
                    ["Nom.", "πατήρ", "πατέρ-ες"],
                    ["Acc.", "πατέρ-α", "πατέρ-ας"],
                    ["Gen.", "πατρ-ός", "πατέρ-ων"],
                    ["Dat.", "πατρ-ί", "πατρ-άσι(ν)"],
                    ["Voc.", "πάτερ", "πατέρ-ες"]
                ]
            }
        },
        "3e": {
            "name": "Third Declension: Neuters in -ος (stem -ες-)",
            "example": "τεῖχ-ος, τό (stem τειχες-, ‘wall’)",
            "stem": "τειχεσ-",
            "table": {
                "header": [["Case", "Singular", "Plural"]],
                "rows": [
                    ["Nom.", "τεῖχ-ος", "τείχ-η (< -ε-α)"],
                    ["Acc.", "τεῖχ-ος", "τείχ-η (< -ε-α)"],
                    ["Gen.", "τείχ-ους (< -ε-ος)", "τειχ-ῶν (< -έ-ων)"],
                    ["Dat.", "τείχ-ει (< -ε-ϊ)", "τείχε-σι(ν)"]
                ]
            }
        },
        "3f": {
            "name": "Third Declension: Stems in -ι-/-ε- (Feminines in -ις)",
            "example": "πόλι-ς, ἡ (stem πολι-/πολε-, ‘city’)",
            "stem": "πολι- / πολε-",
            "table": {
                "header": [["Case", "Singular", "Plural"]],
                "rows": [
                    ["Nom.", "πόλι-ς", "πόλ-εις"],
                    ["Acc.", "πόλι-ν", "πόλ-εις"],
                    ["Gen.", "πόλε-ως", "πόλε-ων"],
                    ["Dat.", "πόλ-ει", "πόλε-σι(ν)"],
                    ["Voc.", "πόλι", "πόλ-εις"]
                ]
            }
        },
        "3g": {
            "name": "Third Declension: Stems in -ευ- (Masculines in -εύς)",
            "example": "βασιλεύ-ς, ὁ (stem βασιλευ-/βασιλε-, ‘king’)",
            "stem": "βασιλευ- / βασιλε-",
            "table": {
                "header": [["Case", "Singular", "Plural"]],
                "rows": [
                    ["Nom.", "βασιλεύ-ς", "βασιλ-ῆς / βασιλ-εῖς"],
                    ["Acc.", "βασιλέ-ᾱ", "βασιλέ-ᾱς"],
                    ["Gen.", "βασιλέ-ως", "βασιλέ-ων"],
                    ["Dat.", "βασιλ-εῖ", "βασιλεῦ-σι(ν)"],
                    ["Voc.", "βασιλεῦ", "βασιλ-ῆς / βασιλ-εῖς"]
                ]
            }
        },
        "3h": {
            "name": "Third Declension: Stems in -υ-",
            "example": "ὀφρύ-ς, ἡ (stem ὀφρυ-, ‘eyebrow’) / ὗ-ς, ὁ/ἡ (stem ὑ-, ‘pig, boar’)",
            "stem": "ὀφρυ- / ὑ-",
            "table": {
                "header": [["Case", "Singular", "Plural"]],
                "rows": [
                    ["Nom.", "ὀφρύ-ς / ὗ-ς", "ὀφρύ-ες / ὗ-ες"],
                    ["Acc.", "ὀφρύ-ν / ὗ-ν", "ὀφρῦ-ς / ὗ-ς"],
                    ["Gen.", "ὀφρύ-ος / ὑ-ός", "ὀφρύ-ων / ὑ-ῶν"],
                    ["Dat.", "ὀφρύ-ϊ / ὑ-ί", "ὀφρύ-σι(ν) / ὑ-σί(ν)"]
                ]
            }
        }
    },
    "pronouns": {
        "article": {
            "name": "Definite Article: ὁ, ἡ, τό (‘the’)",
            "table": {
                "header": [["Case", "Masc. Sing.", "Fem. Sing.", "Neut. Sing.", "Masc. Plur.", "Fem. Plur.", "Neut. Plur."]],
                "rows": [
                    ["Nom.", "ὁ", "ἡ", "τό", "οἱ", "αἱ", "τά"],
                    ["Acc.", "τόν", "τήν", "τό", "τούς", "τάς", "τά"],
                    ["Gen.", "τοῦ", "τῆς", "τοῦ", "τῶν", "τῶν", "τῶν"],
                    ["Dat.", "τῷ", "τῇ", "τῷ", "τοῖς", "ταῖς", "τοῖς"]
                ]
            }
        },
        "personal": {
            "name": "Personal Pronouns: 1st & 2nd Person",
            "table": {
                "header": [["Case", "1st Sing. (ἐγώ)", "2nd Sing. (σύ)", "1st Plur. (ἡμεῖς)", "2nd Plur. (ὑμεῖς)"]],
                "rows": [
                    ["Nom.", "ἐγώ", "σύ", "ἡμεῖς", "ὑμεῖς"],
                    ["Acc.", "(ἐ)μέ", "(σ)έ", "ἡμᾶς", "ὑμᾶς"],
                    ["Gen.", "(ἐ)μοῦ", "(σ)οῦ", "ἡμῶν", "ὑμῶν"],
                    ["Dat.", "(ἐ)μοί", "(σ)οί", "ἡμῖν", "ὑμῖν"]
                ]
            }
        },
        "relative": {
            "name": "Relative Pronoun: ὅς, ἥ, ὅ (‘who, which, that’)",
            "table": {
                "header": [["Case", "Masc. Sing.", "Fem. Sing.", "Neut. Sing.", "Masc. Plur.", "Fem. Plur.", "Neut. Plur."]],
                "rows": [
                    ["Nom.", "ὅς", "ἥ", "ὅ", "οἵ", "αἵ", "ἅ"],
                    ["Acc.", "ὅν", "ἥν", "ὅ", "οὕς", "ἅς", "ἅ"],
                    ["Gen.", "οὗ", "ἧς", "οὗ", "ὧν", "ὧν", "ὧν"],
                    ["Dat.", "ᾧ", "ᾗ", "ᾧ", "οἷς", "αἷς", "οἷς"]
                ]
            }
        }
    }
}

def main():
    print("=== Generating Reference Grammar Paradigms (Phase 5) ===")
    targets = ["data/reference_grammar.json", "site/data/reference_grammar.json"]
    for path in targets:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(REFERENCE_DATA, f, ensure_ascii=False, indent=2)
        print(f"Wrote reference grammar data to {path}")

if __name__ == "__main__":
    main()
