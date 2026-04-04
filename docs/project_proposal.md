# Geopolitical Alignment Index — Project Proposal

## Executive Summary

This project develops two novel **Geopolitical Alignment Indices** derived from official foreign ministry press releases. Unlike existing measures — most notably the UN General Assembly voting-based index by Bailey et al. (2017) — our approach draws on the actual diplomatic language that governments use when characterising other countries in public communications. The result is a more granular, real-time, and context-sensitive measure of bilateral geopolitical alignment that can be applied across countries, languages, and time periods.

---

## 1. Problem Statement

### 1.1 Motivation

Geopolitical alignment — the degree to which countries share or diverge in their international orientations — is a fundamental concept in international relations, global economics, and finance. Accurate alignment measures help:

- **Policymakers** anticipate shifts in diplomatic relationships.
- **Financial institutions** assess geopolitical risk and calibrate cross-border investment strategies.
- **Researchers and journalists** track the evolving structure of the international order with transparent, reproducible methods.

### 1.2 Limitation of Existing Indices

The most widely used academic measure, developed by **Bailey, Strezhnev, and Voeten (2017)**, derives alignment from co-voting patterns in the UN General Assembly. While valuable, this approach has well-known limitations:

| Limitation | Detail |
|---|---|
| **Binary signal** | A vote is either yes, no, or abstain — diplomatic nuance is lost. |
| **Annual frequency** | Voting sessions occur once per year; intra-year shifts are invisible. |
| **Strategic abstention** | Countries sometimes abstain for procedural reasons unrelated to their actual alignment. |
| **Limited coverage** | Only topics that reach the UNGA floor are captured. |

Caldara & Iacoviello's (2018) Geopolitical Risk index addresses some of these gaps but relies on keyword counting in newspaper articles, which suffers from false positives and lacks bilateral specificity.

### 1.3 Our Contribution

We develop two complementary measures grounded in **official foreign ministry press releases** — authoritative, publicly available, and rich in bilateral diplomatic language. These measures:

- Are **bilateral** (origin country → target country).
- Capture **implicit tone**, not just explicit statements.
- Can be produced at **monthly or even weekly frequency**.
- Are **scalable** across countries, languages, and time periods.

---

## 2. Methodology

### 2.1 Data Collection

Press releases are collected from the official websites of foreign ministries (or equivalent bodies) for a set of origin countries. Each document is tagged with:

- **Origin country** (the issuing ministry)
- **Publication date**
- **Document ID**

### 2.2 Method 1 — Usage-Weighted Alignment Score

**Conceptual framework:** How prominently and in what tone does a country mention another country in its official communications?

**Algorithm:**

1. **Named-entity recognition** — Identify mentions of target countries within each document.
2. **Proximity-aware sentiment** — Within a sliding character window around each mention, compute positive and negative sentiment scores using a geopolitical sentiment lexicon.
3. **Usage weighting** — Weight each document's sentiment contribution by the relative mention frequency of the target country (mentions ÷ total words), capturing how much attention the origin country devotes to each target.
4. **Aggregation** — Sum weighted scores across all documents for each origin–target pair to produce:
   - `pos_total` — Total positive sentiment (usage-weighted)
   - `neg_total` — Total negative sentiment (usage-weighted)
   - `net_total` — Net alignment score (`pos_total − neg_total`)

**Strengths:** Fully transparent and reproducible; no black-box components; fast to compute.

**Limitations:** Sensitive to lexicon quality; may miss implicit tone without multi-word phrase coverage.

### 2.3 Method 2 — LLM-Based Geopolitical Alignment Index

**Conceptual framework:** Can a large language model, primed with expert instructions, reliably extract bilateral alignment signals from diplomatic texts?

**Algorithm:**

1. **Passage extraction** — Each press release (or a relevant excerpt focused on a specific target country) is prepared as a prompt payload.
2. **Structured LLM scoring** — The passage is sent to an OpenAI model (e.g., GPT-4o or GPT-4o-mini) with a carefully engineered system prompt that instructs the model to:
   - Identify the origin and target countries.
   - Assign a bilateral alignment score in **[−1, +1]**.
   - Provide a one-sentence justification citing specific language.
3. **JSON output parsing** — The model returns a structured JSON object; scores are validated and clamped to [−1, +1].
4. **Aggregation** — Scores are averaged across documents for each origin–target pair, optionally weighted by document length or recency.

**Key advantages over keyword counting:**

| Feature | Keyword Counting | LLM Approach |
|---|---|---|
| Understands context | ✗ | ✓ |
| Detects implicit tone | ✗ | ✓ |
| Disambiguates multi-country documents | ✗ | ✓ |
| Handles linguistic variation | Limited | ✓ |
| Avoids rigid word lists | ✗ | ✓ |

**Example:** The phrase *"we express grave concern over China's destabilising activities"* and *"we welcome China's constructive engagement"* both contain the word "China," but only an LLM (or expert reader) correctly assigns −0.7 vs. +0.6.

---

## 3. Sample Results

### 3.1 Usage-Weighted Scores (Canada as Origin)

| Origin | Country | ISO3C | N Docs | Pos Total | Neg Total | Net Total |
|--------|---------|-------|--------|-----------|-----------|-----------|
| CAN | United States | USA | 17 | 73.44 | 25.76 | 47.68 |
| CAN | Ukraine | UKR | 32 | 392.03 | 298.03 | 94.00 |
| CAN | Venezuela | VEN | 5 | 26.27 | 0.00 | 26.27 |
| CAN | Hong Kong SAR China | HKG | 4 | 22.28 | 0.00 | 22.28 |
| CAN | Mexico | MEX | 6 | 19.07 | 0.00 | 19.07 |

*Interpretation:* Canada is most positively aligned with the United States and most negatively aligned with Russia and China, consistent with known geopolitical realities.

### 3.2 LLM-Based Scores (US–China Pair)

| Origin | Target | Year | Score | Justification (excerpt) |
|--------|--------|------|-------|------------------------|
| USA | CHN | 2023 | −0.62 | "expresses grave concern over China's trade practices" |
| USA | CHN | 2023 | −0.71 | "condemnation … violation of international law" |
| USA | CHN | 2022 | +0.15 | "cooperative dialogue on climate change" |
| CHN | USA | 2023 | −0.55 | "condemns US interference in internal affairs" |
| CHN | USA | 2023 | −0.67 | "sovereignty violation" regarding Taiwan Strait |

*Interpretation:* Both countries characterise each other predominantly negatively in recent years, with occasional positive signals around shared economic or environmental interests.

---

## 4. Applications and Impact

### 4.1 Policy Support
A quarterly or monthly alignment index provides diplomatic analysts with an early-warning signal of deteriorating bilateral relationships before they escalate to formal diplomatic incidents.

### 4.2 Financial Risk Management
Geopolitical alignment is increasingly correlated with trade patterns, supply-chain risk, and asset prices. Financial institutions can incorporate alignment scores into country-risk models.

### 4.3 Academic Research
Our indices offer a transparent, publicly replicable alternative or complement to existing measures, advancing research in international political economy, conflict studies, and global governance.

### 4.4 Media and Transparency
Because the method relies entirely on public government data and automated NLP, journalists can trace any score back to specific press releases and passages.

---

## 5. Role of AI in Our Work

This project illustrates how AI empowers non-computer-scientists to work at the cutting edge of data science. As economists, we know how to construct and validate empirical measures — but the algorithmic machinery for NLP and LLM integration was made accessible to us through AI tools (including GitHub Copilot and the ChatGPT API). Specifically:

- **Code generation:** AI assisted in writing the Python scripts for data collection, entity recognition, sentiment scoring, and API integration.
- **LLM-based measurement:** The ChatGPT API serves as the core scoring engine for Method 2, leveraging the model's contextual understanding of diplomatic language.
- **Iterative refinement:** We used AI to rapidly prototype and test different prompt formulations, window sizes, and aggregation methods.

AI did not replace our economic judgment — it amplified it, enabling us to implement methods that would otherwise have required a dedicated software engineering team.

---

## 6. Scalability and Future Work

| Dimension | Current | Planned |
|---|---|---|
| Countries (origin) | 3 (CAN, USA, CHN) | 30+ |
| Languages | English | + French, Spanish, Chinese, Russian, Arabic |
| Time span | 2020–2024 | 2000–present |
| Frequency | Annual | Monthly |
| Validation | Qualitative | Correlation with UNGA votes, trade data, conflict events |

---

## 7. References

- Bailey, M. A., Strezhnev, A., & Voeten, E. (2017). Estimating Dynamic State Preferences from United Nations Voting Data. *Journal of Conflict Resolution*, 61(2), 430–456.
- Caldara, D., & Iacoviello, M. (2018). Measuring Geopolitical Risk. *American Economic Review*, 112(4), 1194–1225.
- Brown, T. et al. (2020). Language Models are Few-Shot Learners. *NeurIPS*.
- Loughran, T., & McDonald, B. (2011). When Is a Liability Not a Liability? *Journal of Finance*, 66(1), 35–65.
