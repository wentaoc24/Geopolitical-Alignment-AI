import json
import re
import time
import csv
from statistics import mean
from openai import OpenAI

# =========================================================
# CONFIG
# =========================================================
INPUT_PATH = "/Users/ankitpatro/Desktop/china_file/china.json"
OUTPUT_PATH = "/Users/ankitpatro/Desktop/china_file/china_scored.csv"

ORIGIN = "China"
MODEL = "gpt-5-nano"
SLEEP_BETWEEN_CALLS = 0.2
MAX_CHARS_PER_CHUNK = 2500

# PASTE YOUR API KEY HERE
API_KEY = "PASTE_YOUR_NEW_KEY_HERE"

client = OpenAI(api_key=API_KEY)

# =========================================================
# COUNTRY LIST
# =========================================================
COUNTRY_LIST = [
    "Afghanistan", "Albania", "Algeria", "Argentina", "Armenia", "Australia",
    "Austria", "Azerbaijan", "Bangladesh", "Belarus", "Belgium", "Bhutan",
    "Bolivia", "Bosnia", "Botswana", "Brazil", "Brunei", "Bulgaria",
    "Cambodia", "Cameroon", "Canada", "Chile", "China", "Colombia", "Congo",
    "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic", "Denmark",
    "Dominican Republic", "Ecuador", "Egypt", "Ethiopia", "Finland", "France",
    "Germany", "Ghana", "Greece", "Hungary", "Iceland", "India", "Indonesia",
    "Iran", "Iraq", "Ireland", "Israel", "Italy", "Japan", "Jordan",
    "Kazakhstan", "Kenya", "Kuwait", "Kyrgyzstan", "Laos", "Latvia",
    "Lebanon", "Libya", "Lithuania", "Luxembourg", "Malaysia", "Maldives",
    "Mexico", "Mongolia", "Morocco", "Myanmar", "Nepal", "Netherlands",
    "New Zealand", "Nigeria", "North Korea", "Norway", "Oman", "Pakistan",
    "Palestine", "Panama", "Peru", "Philippines", "Poland", "Portugal",
    "Qatar", "Romania", "Russia", "Saudi Arabia", "Senegal", "Serbia",
    "Seychelles", "Singapore", "Slovakia", "Slovenia", "Somalia",
    "South Africa", "South Korea", "Spain", "Sri Lanka", "Sudan", "Sweden",
    "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand",
    "Tunisia", "Turkey", "Turkmenistan", "Uganda", "Ukraine",
    "United Arab Emirates", "United Kingdom", "United States", "USA", "US",
    "Uruguay", "Uzbekistan", "Venezuela", "Vietnam", "Yemen", "Zimbabwe"
]

# =========================================================
# HELPERS
# =========================================================
def clean_text(text):
    if text is None:
        return ""
    text = str(text).replace("\r", "\n")
    text = re.sub(r"\n{2,}", "\n\n", text)
    return text.strip()

def extract_year(date_text):
    """
    Extract a 4-digit year from fields like:
    '2024-06-27', '2010-05-25', 'June 27, 2024', etc.
    """
    if not date_text:
        return ""
    match = re.search(r"\b(19|20)\d{2}\b", str(date_text))
    return match.group(0) if match else ""

def split_into_chunks(text, max_chars=2500):
    text = clean_text(text)
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    paras = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    current = ""

    for p in paras:
        if len(current) + len(p) + 2 <= max_chars:
            current = f"{current}\n{p}".strip()
        else:
            if current:
                chunks.append(current)
            current = p

            if len(current) > max_chars:
                sentences = re.split(r'(?<=[.!?])\s+', current)
                current = ""
                for s in sentences:
                    if len(current) + len(s) + 1 <= max_chars:
                        current = f"{current} {s}".strip()
                    else:
                        if current:
                            chunks.append(current)
                        current = s
                if current:
                    chunks.append(current)
                current = ""

    if current:
        chunks.append(current)

    return [c for c in chunks if c.strip()]

def infer_target(title, body):
    text = f"{clean_text(title)}\n{clean_text(body)}"
    matches = []

    for country in COUNTRY_LIST:
        pattern = r"\b" + re.escape(country) + r"\b"
        if re.search(pattern, text, flags=re.IGNORECASE):
            normalized = "United States" if country in {"USA", "US"} else country
            if normalized != ORIGIN:
                matches.append(normalized)

    seen = set()
    deduped = []
    for m in matches:
        if m not in seen:
            deduped.append(m)
            seen.add(m)

    return deduped[0] if deduped else "Unknown"

def build_prompt(origin, target, chunk):
    return f"""You are evaluating diplomatic language in an official Chinese foreign ministry document.

Does this text indicate cooperative alignment, neutral positioning, or adversarial positioning between {origin} and {target}?

IMPORTANT:
- Focus only on language relevant to the relationship between {origin} and {target}.
- This language is often found in meeting summaries, joint statements, press conferences, spokesperson remarks, or bilateral cooperation sections.
- If the document discusses {target} separately from other countries, evaluate ONLY the language about {target}.
- If {target} is grouped together with other countries or regions in a single statement and not separately identified, evaluate the grouped language.
- If the text refers only to {target}, treat it as a bilateral statement.

Assign a score from:
-1.0 = strongly adversarial
0 = neutral
+1.0 = strongly cooperative

Consider:
- tone
- commitments
- agreements
- strategic partnerships
- diplomatic support
- disputes
- military tensions
- sanctions
- accusations
- condemnations
- opposition to another state's actions
- references to sovereignty, territorial issues, or interference

Scoring guidance:
- Use positive scores for clear cooperation, partnership, support, or deepening ties.
- Use negative scores for condemnation, conflict, protest, or hostile positioning.
- Use 0 for procedural, factual, or ambiguous language with no clear directional alignment.
- If both positive and negative language appear, score the net diplomatic posture toward {target}.
- Do not over-weight generic diplomatic courtesy unless it clearly signals substantive cooperation.

Output only a numeric score.
Temperature = 0.

TEXT:
{chunk}"""

def parse_numeric_score(text):
    match = re.search(r"-?\d+(?:\.\d+)?", text.strip())
    if not match:
        raise ValueError(f"Could not parse numeric score from: {text}")
    score = float(match.group(0))
    return max(-1.0, min(1.0, score))

def get_score_from_model(prompt):
    response = client.responses.create(
        model=MODEL,
        input=prompt
    )
    output_text = response.output_text.strip()
    score = parse_numeric_score(output_text)
    return score, output_text

def load_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()

    if not raw:
        return []

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict):
            return [parsed]
        raise ValueError("Unsupported JSON structure.")
    except json.JSONDecodeError:
        docs = []
        for line in raw.splitlines():
            line = line.strip()
            if line:
                docs.append(json.loads(line))
        return docs

# =========================================================
# MAIN
# =========================================================
def main():
    if API_KEY == "PASTE_YOUR_NEW_KEY_HERE":
        raise ValueError("Please paste your OpenAI API key into the API_KEY variable.")

    docs = load_json_file(INPUT_PATH)
    print(f"Loaded {len(docs)} documents")

    rows = []

    for i, doc in enumerate(docs, start=1):
        title = doc.get("title", "") or ""
        body = doc.get("body", "") or doc.get("content", "") or ""
        body = clean_text(body)
        target = doc.get("target", "") or infer_target(title, body)

        year = (
            extract_year(doc.get("date", "")) or
            extract_year(doc.get("date_text", "")) or
            ""
        )

        if not body:
            rows.append({
                "origin": ORIGIN,
                "destination": target,
                "text": "",
                "year": year,
                "score": ""
            })
            continue

        chunks = split_into_chunks(body, MAX_CHARS_PER_CHUNK)
        chunk_scores = []

        for chunk in chunks:
            prompt = build_prompt(ORIGIN, target, chunk)
            try:
                score, _ = get_score_from_model(prompt)
                chunk_scores.append(score)
            except Exception as e:
                print(f"Error on document {i}: {e}")
            time.sleep(SLEEP_BETWEEN_CALLS)

        document_score = mean(chunk_scores) if chunk_scores else ""

        rows.append({
            "origin": ORIGIN,
            "destination": target,
            "text": body,
            "year": year,
            "score": document_score
        })

        if i % 50 == 0:
            print(f"Processed {i}/{len(docs)}")

    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["origin", "destination", "text", "year", "score"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved scored CSV to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
