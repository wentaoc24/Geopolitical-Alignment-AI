"""
LLM-Based Geopolitical Alignment Scoring
=========================================
This script sends foreign ministry press release passages to an OpenAI model
and retrieves bilateral alignment scores in the range [-1, +1].

Usage
-----
    python scripts/llm_alignment_score.py \\
        --input  data/press_releases.csv \\
        --origin CAN \\
        --output data/llm_scores_canada.csv \\
        [--model gpt-4o-mini] \\
        [--batch-size 10]

Input CSV columns expected
--------------------------
    doc_id       : unique document identifier
    origin       : ISO3C code of the country that issued the press release
    text         : full text of the press release (or pre-split passage)
    year         : publication year (integer)

Output CSV columns
------------------
    doc_id, origin, target, iso3c_target, year, llm_score, justification
"""

import argparse
import json
import os
import sys
import time

import pandas as pd
from openai import OpenAI

# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert in geopolitical text analysis and diplomatic language.
Your task is to evaluate bilateral alignment scores from official foreign ministry press releases.

For each text passage you receive, you will:
1. Identify the ORIGIN country (the country that issued the statement).
2. Identify the TARGET country (the country being discussed or referenced).
3. Assign a bilateral ALIGNMENT SCORE between -1.0 and +1.0:
   - +1.0 = strongly positive / highly aligned (e.g., deep partnership, solidarity, strong praise)
   - 0.0  = neutral / procedural (e.g., mere acknowledgement of meeting, no evaluative language)
   - -1.0 = strongly negative / deeply misaligned (e.g., condemnation, sanctions, hostile rhetoric)
4. Provide a one-sentence JUSTIFICATION for the score, citing specific language from the text.

IMPORTANT GUIDELINES:
- Base the score ONLY on the origin country's characterisation of the target country in this passage.
- Detect IMPLICIT diplomatic tone: phrases like "mutual trust", "grave concern", "constructive role",
  "interference in internal affairs", or "strategic partnership" carry clear alignment signals.
- If the passage mentions several countries, focus only on the most prominent target country.
- Avoid being swayed by merely procedural language (e.g., "met with", "discussed") unless it is
  accompanied by clearly evaluative terms.

Respond ONLY with a valid JSON object matching this schema:
{
  "origin": "<ISO3C or country name>",
  "target": "<ISO3C or country name>",
  "alignment_score": <float between -1.0 and 1.0>,
  "justification": "<one sentence citing specific language from the text>"
}"""

USER_PROMPT_TEMPLATE = """Please analyse the following foreign ministry press release passage and
return the bilateral alignment score as a JSON object.

Origin country: {origin}
Year: {year}
Document ID: {doc_id}

--- BEGIN PASSAGE ---
{text}
--- END PASSAGE ---"""


# ---------------------------------------------------------------------------
# Core scoring function
# ---------------------------------------------------------------------------

def score_passage(client: OpenAI, model: str, doc_id: str, origin: str,
                  year: int, text: str, retries: int = 3) -> dict:
    """Call the LLM and return a parsed alignment score dict."""
    user_prompt = USER_PROMPT_TEMPLATE.format(
        origin=origin, year=year, doc_id=doc_id, text=text.strip()
    )
    for attempt in range(1, retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_prompt},
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content
            result = json.loads(raw)
            result["doc_id"] = doc_id
            result["year"] = year
            # Normalise score to [-1, +1]
            score = float(result.get("alignment_score", 0.0))
            result["alignment_score"] = max(-1.0, min(1.0, score))
            return result
        except Exception as exc:
            print(f"  [Attempt {attempt}/{retries}] Error scoring {doc_id}: {exc}",
                  file=sys.stderr)
            if attempt < retries:
                time.sleep(2 ** attempt)
    return {
        "doc_id": doc_id,
        "origin": origin,
        "target": None,
        "alignment_score": None,
        "justification": "ERROR: failed after retries",
        "year": year,
    }


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

def process_dataframe(df: pd.DataFrame, client: OpenAI, model: str,
                      batch_size: int = 10) -> pd.DataFrame:
    """Score all rows in the dataframe and return results as a DataFrame."""
    records = []
    total = len(df)
    for i, row in enumerate(df.itertuples(index=False), start=1):
        print(f"  Scoring document {i}/{total}: {row.doc_id} ...", end=" ")
        result = score_passage(
            client=client,
            model=model,
            doc_id=row.doc_id,
            origin=row.origin,
            year=int(row.year),
            text=row.text,
        )
        records.append(result)
        print(f"score={result.get('alignment_score')}")

        # Respect rate limits between batches
        if i % batch_size == 0 and i < total:
            print(f"  [Batch complete — sleeping 1 s to respect rate limits]")
            time.sleep(1)

    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score bilateral geopolitical alignment using an LLM."
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to input CSV with columns: doc_id, origin, text, year"
    )
    parser.add_argument(
        "--origin", required=False, default=None,
        help="Filter input to rows where origin == ORIGIN (e.g. CAN)"
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to write the output CSV of alignment scores"
    )
    parser.add_argument(
        "--model", default="gpt-4o-mini",
        help="OpenAI model name (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--batch-size", type=int, default=10,
        help="Number of documents per batch before a short sleep (default: 10)"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)

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

    print(f"Using model: {args.model}")
    results_df = process_dataframe(df, client, model=args.model,
                                   batch_size=args.batch_size)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    results_df.to_csv(args.output, index=False)
    print(f"\nDone. Results saved to: {args.output}")
    print(results_df.describe())


if __name__ == "__main__":
    main()
