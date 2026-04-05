# Geopolitical Alignment AI — Presentation Slides

> **Grant Showcase · 60-Second Video Script & Slide Deck**

---

## Slide 1 — Title

**Geopolitical Alignment AI**
*Measuring Diplomatic Relationships Through Foreign Ministry Language*

> Team: [Your Names]
> Date: 2024

---

## Slide 2 — The Problem

### Existing measures are limited

- **Bailey et al. (2017):** UN General Assembly voting → binary signal, annual frequency
- **Keyword counting (Caldara & Iacoviello, 2018):** rigid word lists, misses context

### What we're missing

> Foreign ministries speak volumes every day — in press releases that nobody is systematically reading at scale.

---

## Slide 3 — Our Solution

### Two Geopolitical Alignment Indices from Foreign Ministry Press Releases

| | Method 1 | Method 2 |
|---|---|---|
| **Name** | Usage-Weighted Alignment Score | LLM-Based Alignment Index |
| **Approach** | Rule-based NLP + sentiment lexicon | ChatGPT API + structured prompting |
| **Output** | pos/neg/net scores per country pair | Score in [−1, +1] with justification |
| **Strength** | Transparent, fast | Context-aware, nuanced |

---

## Slide 4 — Why LLMs?

> *"We express grave concern over destabilising activities"*
> → Score: **−0.72**

> *"We welcome the constructive role in multilateral dialogue"*
> → Score: **+0.68**

A keyword counter sees the same words. An LLM reads the room.

**LLMs can:**
- ✅ Understand context and implicit tone
- ✅ Disambiguate multi-country documents
- ✅ Detect subtle diplomatic signals
- ✅ Scale across languages

---

## Slide 5 — Sample Results: Canada

### Usage-Weighted Scores (Canada as origin country)

| Partner | Net Score | Signal |
|---------|-----------|--------|
| 🇺🇸 United States | +47.68 | Strong positive alliance |
| 🇺🇦 Ukraine | +94.00 | Solidarity in conflict |
| 🇻🇪 Venezuela | +26.27 | Mildly positive |
| 🇷🇺 Russia | −269.20 | Strong condemnation |
| 🇨🇳 China | −67.76 | Significant friction |

*Results are consistent with known geopolitical realities → validates our methodology.*

---

## Slide 6 — How AI Empowered Us

> We are economists — not software engineers.

### AI enabled us to:
1. **Write production-quality Python code** for NLP pipelines
2. **Access LLM APIs** to build a context-aware scoring engine
3. **Iterate rapidly** on prompt engineering and methodology
4. **Process hundreds of documents** in minutes, not months

**AI didn't replace our expertise — it amplified it.**

---

## Slide 7 — Applications

| Who | How They Benefit |
|-----|-----------------|
| 🏛️ **Policymakers** | Near-real-time early warning of relationship shifts |
| 🏦 **Financial institutions** | Country risk management & portfolio decisions |
| 📰 **Journalists** | Transparent, traceable measure of diplomatic tone |
| 🎓 **Researchers** | Reproducible alternative to UNGA voting measures |

---

## Slide 8 — Road Map

```
2024 Q1-Q2    →   Pilot: 3 countries (CAN, USA, CHN), English only
2024 Q3-Q4    →   Expand to 15 countries; add French & Spanish
2025          →   30+ countries; Arabic, Chinese, Russian; monthly index
2025+         →   Public dashboard; academic publication
```

---

## Slide 9 — Why This Matters

> "AI shouldn't be seen as a tool for replacing workers — rather as a means to
> empower them by expanding their capabilities and supporting their growth."

We are proof of that thesis.

**Two economists, with AI, built what would otherwise require a team of data scientists.**

---

## Slide 10 — Call to Action

### We are seeking grant support to:
- ✅ Scale data collection to 30+ countries
- ✅ Build a public-facing real-time dashboard
- ✅ Validate against existing measures and publish academically
- ✅ Make the full methodology open-source

**GitHub:** https://github.com/wentaoc24/Geopolitical-Alignment-AI

---

## 60-Second Video Script

> **[0–5 s]** *(Slide: world map with connection lines)*
> "Every day, governments around the world release statements about each other — revealing who they trust, who they criticise, and who they're aligned with."

> **[5–15 s]** *(Slide: existing methods — limitations)*
> "Existing measures rely on UN votes or newspaper keyword counts. They're coarse, slow, and miss the subtle language diplomats actually use."

> **[15–30 s]** *(Slide: our approach — dual method graphic)*
> "We built two AI-powered indices from foreign ministry press releases. The first uses rule-based NLP to score sentiment around country mentions. The second uses the ChatGPT API to read each passage in context and assign a bilateral alignment score from −1 to +1."

> **[30–45 s]** *(Slide: Canada results table)*
> "Testing on Canada, our methods correctly identify strong alignment with the US and UK, solidarity with Ukraine, and tension with Russia and China — consistent with known geopolitics."

> **[45–55 s]** *(Slide: AI empowers us)*
> "As economists, AI let us build a data pipeline we couldn't have coded alone. It's not replacing our expertise — it's amplifying it."

> **[55–60 s]** *(Slide: call to action)*
> "Help us scale this to 30 countries and build a public dashboard. This index belongs in the hands of policymakers, researchers, and the public."
