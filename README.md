# Welfare Eligibility Assistant

A tool-using assistant that screens a citizen against 10 Indian central government welfare schemes and explains the result with the official rule text and source.

**Live app:** https://welfare-eligibility-agent.streamlit.app/

## What it does

1. The citizen enters a profile (age, gender, income, accounts, memberships, household details).
2. A **deterministic rule engine** (`eligibility.py`) screens all 10 schemes and returns ELIGIBLE, POSSIBLY_ELIGIBLE or NOT_ELIGIBLE with a PASS / FAIL / UNKNOWN result for every rule.
3. A Gemini **assistant with two tools** explains the result and answers follow-up questions. It decides for itself which tool to call, reads what comes back, and can call again (up to 5 rounds):
   - `check_eligibility` runs the rule engine (re-check with different facts).
   - `get_official_rules` retrieves the official rule text, source name and URL for one scheme (`rules_retriever.py`, TF-IDF similarity over one passage per scheme).
4. The page shows which tools were called for each answer ("How the assistant got this answer").

The model never decides eligibility. The engine does. The model explains, and cites the retrieved source.

## Files

| File | Role |
|---|---|
| `app.py` | Streamlit page |
| `agent.py` | Gemini tool-calling loop and the two tool definitions |
| `eligibility.py` | Rule engine for the 10 schemes |
| `rules_retriever.py` | Official rule passages and the retrieval function |
| `evaluate.py` | Evaluation: retrieval, rule-engine tests, live tool-use test |
| `requirements.txt` | Dependencies |

## Run it

The easiest way is the live link above (no install, no key needed).

To run it yourself you need Python 3.10+ and a Google Gemini API key.

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="your key"        # Windows PowerShell: $env:GEMINI_API_KEY="your key"
streamlit run app.py
```

On Streamlit Community Cloud, add `GEMINI_API_KEY` under the app's Secrets. Never commit the key.

## Evaluate it

```bash
python evaluate.py          # offline: retrieval + rule-engine tests (no key)
python evaluate.py --live   # also runs the tool-use test and writes answers_for_grading.csv
```

## Limits

- Ten schemes and one rule passage per scheme. Not an official eligibility decision.
- Rules were encoded by hand from public sources and need a periodic check against the official pages.
- The retriever is keyword-based (TF-IDF), so it can rank the wrong scheme first on loosely worded questions. The assistant names the scheme when it calls the tool, which limits this.
- Questions and the profile are sent to the Gemini API. A real deployment would need consent, retention and access rules for citizen data.
