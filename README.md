# Geopolitical Alignment AI

A research project that constructs novel geopolitical alignment indices from foreign ministry press releases using natural language processing and large language models (LLMs).

## Overview

Traditional geopolitical alignment measures — such as Bailey et al. (2017), which relies on UN General Assembly voting patterns — capture formal diplomatic positions but miss the nuanced bilateral language used in official government communications. This project builds two complementary indices grounded in public foreign ministry press releases:

1. **Usage-Weighted Alignment Score** — A rule-based NLP measure using proximity-aware sentiment attribution and usage weighting to quantify how positively or negatively an origin country publicly characterises a target country.
2. **LLM-Based Geopolitical Alignment Index** — An LLM-assisted measure that sends each press release (or relevant excerpt) to a large language model, which returns a bilateral alignment score between **-1** (strongly negative) and **+1** (strongly positive) for every origin–target country pair mentioned.

## Repository Structure

```
.
├── README.md
├── data/
│   └── sample_canada_alignment.csv   # Sample usage-weighted results for Canada
├── scripts/
│   ├── llm_alignment_score.py        # LLM-based alignment scoring via OpenAI API
│   └── usage_weighted_alignment.py   # Rule-based usage-weighted alignment scoring
└── docs/
    ├── project_proposal.md           # Full project proposal
    └── presentation.md               # Short slide-deck outline
```

## Sample Results

The table below shows usage-weighted alignment scores where Canada is the origin country.

| Origin | Country | ISO3C | N Docs | Pos Total | Neg Total | Net Total |
|--------|---------|-------|--------|-----------|-----------|-----------|
| CAN | United States | USA | 17 | 73.44 | 25.76 | 47.68 |
| CAN | Ukraine | UKR | 32 | 392.03 | 298.03 | 94.00 |
| CAN | Venezuela | VEN | 5 | 26.27 | 0.00 | 26.27 |
| CAN | Hong Kong SAR China | HKG | 4 | 22.28 | 0.00 | 22.28 |
| CAN | Mexico | MEX | 6 | 19.07 | 0.00 | 19.07 |

A positive net score indicates net positive diplomatic sentiment; a negative score indicates net negative sentiment. Note that a country pair with high values in *both* `pos_total` and `neg_total` (e.g., Canada–Ukraine) reflects intense bilateral engagement: many documents contain strong solidarity language alongside frank acknowledgement of difficult circumstances (war, casualties, humanitarian need), driving up both columns simultaneously.

## Methodology

### Method 1 — Usage-Weighted Alignment Score

1. Collect official foreign ministry press releases for a set of origin countries.
2. For each document, identify all mentions of target countries (using named-entity recognition).
3. Within a configurable window around each mention, compute positive and negative sentiment scores using a financial/geopolitical sentiment lexicon.
4. Weight each document's score by the number of times the target country is mentioned relative to the total word count (usage weight).
5. Aggregate weighted scores across all documents to produce `pos_total`, `neg_total`, and `net_total` for each origin–target pair.

### Method 2 — LLM-Based Alignment Index

1. Split each press release into passages that reference a specific target country.
2. Submit each passage to an LLM (e.g., GPT-4o or GPT-4o-mini) with a structured prompt that asks it to:
   - Identify the origin country and target country.
   - Assign a bilateral alignment score in **[-1, +1]**.
   - Provide a one-sentence justification.
3. Aggregate scores per origin–target pair across all documents and time periods.

See `scripts/llm_alignment_score.py` for the full prompt and API integration.

## Why LLMs Beat Simple Keyword Counting

| Feature | Keyword Counting | LLM Approach |
|---------|-----------------|--------------|
| Context sensitivity | ✗ | ✓ |
| Implicit tone detection | ✗ | ✓ |
| Multi-country disambiguation | ✗ | ✓ |
| Scalable across languages | Limited | ✓ |
| Avoids rigid word lists | ✗ | ✓ |

Foreign ministry texts rarely say "we are allies" or "we are hostile." Instead they use phrases like *"mutual trust," "constructive role," "grave concern,"* or *"interference in internal affairs."* An LLM interprets these phrases in context in a way that keyword counts cannot.

## Applications

- **Policymakers** — Track geopolitical trends in near-real time.
- **Financial institutions** — Country risk management and portfolio allocation.
- **Journalists & researchers** — Transparent, reproducible measure of diplomatic tone.
- **Academics** — Alternative or complement to UNGA voting-based alignment indices.

## Setup

```bash
pip install openai pandas
```

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-key-here"
```

## Usage

### LLM-Based Scoring

```bash
python scripts/llm_alignment_score.py \
  --input data/press_releases.csv \
  --origin CAN \
  --output data/llm_scores_canada.csv
```

### Usage-Weighted Scoring

```bash
python scripts/usage_weighted_alignment.py \
  --input data/press_releases.csv \
  --origin CAN \
  --output data/weighted_scores_canada.csv
```

## References

- Bailey, M. A., Strezhnev, A., & Voeten, E. (2017). *Estimating Dynamic State Preferences from United Nations Voting Data.* Journal of Conflict Resolution, 61(2), 430–456.
- Caldara, D., & Iacoviello, M. (2018). *Measuring Geopolitical Risk.* American Economic Review, 112(4), 1194–1225.
