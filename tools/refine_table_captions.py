#!/usr/bin/env python3
"""
tools/refine_table_captions.py
Updates table captions in data/grammar/s06.json through s10.json
with exact, descriptive grammatical paradigm titles.
"""

import json

SECTION_TABLE_CAPTIONS = {
    "s06": {
        43: "First aorist of contract verbs (τιμάω, ποιέω, δηλόω)",
        122: "Third declension noun: ὀφρύς, ἡ (eyebrow, 3h)",
        129: "Principal parts: regular verbs (present, imperfect, future, aorist)",
        131: "Principal parts: liquid and contract verbs",
        146: "Second aorist indicative middle: ἐ-γεν-όμην (‘I became’)",
        151: "Second aorist overview: λαμβάνω, γίγνομαι",
        154: "Common second aorist stems (γίγνομαι, εὑρίσκω, ἔχω)",
        157: "Second aorists from suppletive stems (ἔρχομαι, λέγω, ὁράω)"
    },
    "s07": {
        30: "Adjective comparison: regular (-ότερος / -ότατος)",
        44: "Adjective comparison: irregular (ἀγαθός, κακός, etc.)",
        108: "Pluperfect of οἶδα: ᾔδη (‘I knew’)",
        110: "Present indicative of φημί (‘I say’)",
        196: "Reflexive pronouns: overview",
        211: "Reflexive pronouns: ἐμαυτόν, σεαυτόν, ἑαυτόν",
        251: "Noun declension patterns summary"
    },
    "s08": {
        0: "Personal pronouns: ἐγώ, σύ, ἡμεῖς, ὑμεῖς",
        27: "Irregular adjective comparison (ἀγαθός, etc.)",
        39: "Adjectives in -ων, -ον (εὔφρων)",
        56: "Present optative active of contract verbs (τιμάω, ποιέω, δηλόω)",
        58: "Present optative middle of contract verbs (θεάομαι, ποιέομαι, δουλόομαι)"
    },
    "s09": {
        5: "First & second declension nouns review",
        7: "Personal pronouns review",
        67: "Present optative of -μι verbs (δύναμαι, ἀνίστημι)",
        75: "Principal parts review",
        228: "Third declension adjective: πᾶς, πᾶσα, πᾶν (all, whole, every)",
        251: "Present imperative active & middle (παῦε, παυέσθω)",
        253: "Contract verb imperatives (τίμα, ποίει, δήλου)",
        255: "First aorist imperative active & middle (παῦσον, παῦσαι)",
        257: "Second aorist imperative active & middle (λαβέ, λαβοῦ)",
        272: "Imperatives of irregular verbs (εἰμί, εἶμι, οἶδα)",
        302: "Principal parts: irregular verbs (αἱρέω, ἐρωτάω, etc.)"
    },
    "s10": {
        17: "Second aorist optative active & middle (λάβοιμι, λαβοίμην)",
        40: "Third declension adjectives in -ης, -ες (ἀμελής, singular)",
        41: "Third declension adjectives in -ης, -ες (ἀμελεῖς, plural)",
        43: "Third declension adjectives in -υς, -εια, -υ (γλυκύς, singular)",
        44: "Third declension adjectives in -υς, -εια, -υ (γλυκεῖς, plural)",
        54: "Relative pronoun: ὅς, ἥ, ὅ (‘who, which, that’)",
        86: "Indefinite relative pronoun: ὅστις, ἥτις, ὅτι (‘whoever, whatever’)"
    }
}

def main():
    for sec, cap_map in SECTION_TABLE_CAPTIONS.items():
        file_path = f"data/grammar/{sec}.json"
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        updated = 0
        for i, b in enumerate(data.get("blocks", [])):
            if b.get("t") == "table" and i in cap_map:
                b["caption"] = cap_map[i]
                updated += 1
                
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"Updated {updated} table captions in {file_path}")

if __name__ == "__main__":
    main()
