"""
Usage-Weighted Geopolitical Alignment Scoring
==============================================
This script constructs a rule-based measure of bilateral geopolitical alignment
using proximity-aware sentiment attribution and usage weighting.

For each foreign ministry press release, the algorithm:
1. Detects mentions of target countries via named-entity recognition (spaCy).
2. Within a sliding context window around each mention, scores positive and
   negative sentiment using a dual-polarity lexicon.
3. Weights each document's score by the relative mention frequency of the
   target country (usage weight).
4. Aggregates weighted scores across documents to produce
   pos_total, neg_total, and net_total per origin–target pair.

Usage
-----
    python scripts/usage_weighted_alignment.py \\
        --input  data/press_releases.csv \\
        --origin CAN \\
        --output data/weighted_scores_canada.csv \\
        [--window 50] \\
        [--lexicon data/geopolitical_lexicon.csv]

Input CSV columns expected
--------------------------
    doc_id  : unique document identifier
    origin  : ISO3C code of the country that issued the press release
    text    : full text of the press release
    year    : publication year (integer)

Output CSV columns
------------------
    origin, country, iso3c, n_docs, pos_total, neg_total, net_total
"""

import argparse
import os
import sys
from collections import defaultdict
from typing import Optional

import pandas as pd

# ---------------------------------------------------------------------------
# Built-in minimal geopolitical sentiment lexicon
# (Supplement or replace with a full lexicon via --lexicon)
# ---------------------------------------------------------------------------

DEFAULT_POSITIVE_TERMS = {
    "ally", "alliance", "partnership", "cooperate", "cooperation", "collaboration",
    "support", "solidarity", "trust", "friend", "friendly", "welcome", "congratulate",
    "commend", "appreciate", "mutual", "bilateral", "dialogue", "agreement", "accord",
    "constructive", "progress", "peaceful", "stability", "peace", "prosperity",
    "respect", "recognition", "commitment", "strengthen", "deepen", "enhance",
    "positive", "successful", "milestone", "historic", "strategic partnership",
}

DEFAULT_NEGATIVE_TERMS = {
    "condemn", "condemnation", "concern", "grave concern", "serious concern",
    "interference", "intervention", "aggression", "illegal", "unlawful", "violation",
    "sanction", "sanctions", "hostile", "threat", "threaten", "provocation",
    "escalate", "escalation", "denounce", "reject", "unacceptable", "destabilise",
    "destabilize", "coercion", "intimidation", "occupation", "invasion", "war crime",
    "disinformation", "manipulation", "restrict", "expel", "expulsion",
}

# Country name → ISO3C mapping (subset; extend as needed)
COUNTRY_ISO3C = {
    "united states": "USA", "us": "USA", "usa": "USA", "america": "USA",
    "china": "CHN", "prc": "CHN", "people's republic of china": "CHN",
    "russia": "RUS", "russian federation": "RUS",
    "ukraine": "UKR",
    "canada": "CAN",
    "united kingdom": "GBR", "uk": "GBR", "britain": "GBR",
    "france": "FRA",
    "germany": "DEU",
    "japan": "JPN",
    "india": "IND",
    "australia": "AUS",
    "mexico": "MEX",
    "brazil": "BRA",
    "venezuela": "VEN",
    "cuba": "CUB",
    "iran": "IRN",
    "north korea": "PRK", "dprk": "PRK",
    "south korea": "KOR", "korea": "KOR",
    "israel": "ISR",
    "saudi arabia": "SAU",
    "turkey": "TUR",
    "hong kong": "HKG", "hong kong sar china": "HKG",
    "taiwan": "TWN",
    "myanmar": "MMR", "burma": "MMR",
    "afghanistan": "AFG",
    "iraq": "IRQ",
    "syria": "SYR",
    "libya": "LBY",
    "sudan": "SDN",
    "ethiopia": "ETH",
    "pakistan": "PAK",
    "bangladesh": "BGD",
    "indonesia": "IDN",
    "vietnam": "VNM",
    "philippines": "PHL",
    "thailand": "THA",
    "malaysia": "MYS",
    "singapore": "SGP",
}


# ---------------------------------------------------------------------------
# Lexicon loading
# ---------------------------------------------------------------------------

def load_lexicon(path: Optional[str]) -> tuple[set[str], set[str]]:
    """Load sentiment lexicon from CSV or return built-in defaults."""
    if path and os.path.isfile(path):
        lex_df = pd.read_csv(path)
        pos = set(lex_df.loc[lex_df["polarity"] == "positive", "term"].str.lower())
        neg = set(lex_df.loc[lex_df["polarity"] == "negative", "term"].str.lower())
        print(f"Loaded lexicon: {len(pos)} positive, {len(neg)} negative terms")
        return pos, neg
    print("Using built-in default lexicon.")
    return DEFAULT_POSITIVE_TERMS, DEFAULT_NEGATIVE_TERMS


# ---------------------------------------------------------------------------
# Named-entity-style country detection (regex-based fallback)
# ---------------------------------------------------------------------------

def find_country_mentions(text: str, country_map: dict[str, str]) -> list[tuple[int, str, str]]:
    """
    Return list of (char_position, matched_phrase, iso3c) tuples.
    Searches for country names in descending length order to prefer longer matches.
    """
    text_lower = text.lower()
    mentions: list[tuple[int, str, str]] = []
    seen_positions: set[int] = set()
    for phrase in sorted(country_map, key=len, reverse=True):
        start = 0
        while True:
            idx = text_lower.find(phrase, start)
            if idx == -1:
                break
            # Avoid overlapping matches
            if not any(abs(idx - sp) < len(phrase) for sp in seen_positions):
                mentions.append((idx, phrase, country_map[phrase]))
                seen_positions.add(idx)
            start = idx + 1
    return sorted(mentions, key=lambda x: x[0])


# ---------------------------------------------------------------------------
# Proximity sentiment scoring
# ---------------------------------------------------------------------------

def score_window(text: str, char_pos: int, window: int,
                 pos_terms: set[str], neg_terms: set[str]) -> tuple[float, float]:
    """
    Score sentiment in a character window around char_pos.
    Returns (pos_score, neg_score).
    """
    start = max(0, char_pos - window)
    end = min(len(text), char_pos + window)
    snippet = text[start:end].lower()

    pos_score = sum(1.0 for term in pos_terms if term in snippet)
    neg_score = sum(1.0 for term in neg_terms if term in snippet)
    return pos_score, neg_score


# ---------------------------------------------------------------------------
# Per-document alignment scoring
# ---------------------------------------------------------------------------

def score_document(text: str, origin_iso: str, country_map: dict[str, str],
                   pos_terms: set[str], neg_terms: set[str],
                   window: int = 50) -> list[dict]:
    """
    Return a list of dicts with one entry per target country mentioned in `text`.
    Each entry contains: target, iso3c, pos_score, neg_score, mention_count, usage_weight.
    """
    mentions = find_country_mentions(text, country_map)
    word_count = max(len(text.split()), 1)

    # Group mentions by ISO3C
    by_country: dict[str, list[int]] = defaultdict(list)
    for char_pos, _phrase, iso3c in mentions:
        if iso3c != origin_iso:
            by_country[iso3c].append(char_pos)

    records = []
    for iso3c, positions in by_country.items():
        mention_count = len(positions)
        usage_weight = mention_count / word_count

        pos_total = 0.0
        neg_total = 0.0
        for char_pos in positions:
            p, n = score_window(text, char_pos, window, pos_terms, neg_terms)
            pos_total += p
            neg_total += n

        records.append({
            "iso3c": iso3c,
            "mention_count": mention_count,
            "usage_weight": usage_weight,
            "pos_score": pos_total * usage_weight,
            "neg_score": neg_total * usage_weight,
        })
    return records


# ---------------------------------------------------------------------------
# Aggregate across documents
# ---------------------------------------------------------------------------

def aggregate_scores(doc_records: list[dict]) -> pd.DataFrame:
    """
    Aggregate per-document per-target scores into a summary DataFrame.
    Returns columns: country, iso3c, n_docs, pos_total, neg_total, net_total
    """
    agg: dict[str, dict] = defaultdict(lambda: {"n_docs": 0, "pos": 0.0, "neg": 0.0})
    iso_to_name = {v: k.title() for k, v in COUNTRY_ISO3C.items()}

    for rec in doc_records:
        iso3c = rec["iso3c"]
        agg[iso3c]["n_docs"] += 1
        agg[iso3c]["pos"] += rec["pos_score"]
        agg[iso3c]["neg"] += rec["neg_score"]

    rows = []
    for iso3c, vals in agg.items():
        rows.append({
            "country": iso_to_name.get(iso3c, iso3c),
            "iso3c": iso3c,
            "n_docs": vals["n_docs"],
            "pos_total": round(vals["pos"], 4),
            "neg_total": round(vals["neg"], 4),
            "net_total": round(vals["pos"] - vals["neg"], 4),
        })
    return pd.DataFrame(rows).sort_values("net_total", ascending=False)


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute usage-weighted bilateral geopolitical alignment scores."
    )
    parser.add_argument("--input",   required=True,
                        help="Path to input CSV (columns: doc_id, origin, text, year)")
    parser.add_argument("--origin",  required=False, default=None,
                        help="Filter rows to a single origin ISO3C code (e.g. CAN)")
    parser.add_argument("--output",  required=True,
                        help="Path to write the output summary CSV")
    parser.add_argument("--window",  type=int, default=50,
                        help="Character window size for proximity scoring (default: 50)")
    parser.add_argument("--lexicon", default=None,
                        help="Optional CSV with columns: term, polarity (positive|negative)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print(f"Loading input data from: {args.input}")
    df = pd.read_csv(args.input)
    required_cols = {"doc_id", "origin", "text", "year"}
    missing = required_cols - set(df.columns)
    if missing:
        print(f"ERROR: Input CSV is missing columns: {missing}", file=sys.stderr)
        sys.exit(1)

    if args.origin:
        df = df[df["origin"] == args.origin].reset_index(drop=True)
        print(f"Filtered to origin='{args.origin}': {len(df)} documents")
    else:
        print(f"Processing all origins: {len(df)} documents")

    pos_terms, neg_terms = load_lexicon(args.lexicon)

    all_records: list[dict] = []
    for _, row in df.iterrows():
        doc_records = score_document(
            text=str(row["text"]),
            origin_iso=str(row["origin"]),
            country_map=COUNTRY_ISO3C,
            pos_terms=pos_terms,
            neg_terms=neg_terms,
            window=args.window,
        )
        all_records.extend(doc_records)

    results_df = aggregate_scores(all_records)
    results_df.insert(0, "origin", args.origin if args.origin else "ALL")

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    results_df.to_csv(args.output, index=False)
    print(f"\nDone. Results saved to: {args.output}")
    print(results_df.to_string(index=False))


if __name__ == "__main__":
    main()
