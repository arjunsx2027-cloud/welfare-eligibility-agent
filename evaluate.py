"""Evaluation for the Welfare Eligibility Assistant.

Run offline parts (no API key needed):   python evaluate.py
Run the live tool-use test (needs key):  python evaluate.py --live

A. Retrieval quality  - does the retriever return the right scheme's official rules?
B. Rule-engine tests  - boundary cases taken from the official rule text.
C. Tool use (live)    - does the model call the right tool(s)? Answer quality is
                        graded by hand from answers_for_grading.csv.
"""
import csv, sys
from eligibility import check_all_schemes
from rules_retriever import retrieve_official_rules

# ---------------- A. retrieval ----------------
RETRIEVAL = [   # (question, gold scheme)
 ("Can an income tax payer open an APY account?", "Atal Pension Yojana"),
 ("What is the maximum age to join the pension scheme for bank account holders?", "Atal Pension Yojana"),
 ("Is a 70 year old eligible for Ayushman Bharat?", "Ayushman Bharat PM-JAY"),
 ("Do senior citizens get health cover regardless of income?", "Ayushman Bharat PM-JAY"),
 ("Who can get a free LPG connection?", "PM Ujjwala Yojana"),
 ("Can a household with an existing LPG connection get Ujjwala?", "PM Ujjwala Yojana"),
 ("Are serving government employees excluded from farmer income support?", "PM-KISAN"),
 ("Which land holders are excluded from the farmer income support scheme?", "PM-KISAN"),
 ("What is the age band for the life insurance scheme through bank accounts?", "PM Jeevan Jyoti Bima Yojana"),
 ("What is the age limit for accident insurance through a bank account?", "PM Suraksha Bima Yojana"),
 ("Is the unorganised worker pension open if I have an EPFO account?", "PM Shram Yogi Maandhan"),
 ("What is the income limit for the unorganised worker pension scheme?", "PM Shram Yogi Maandhan"),
 ("How old can a girl be for a Sukanya account?", "Sukanya Samriddhi Account"),
 ("Who can open a girl child savings account?", "Sukanya Samriddhi Account"),
 ("What is the income limit for EWS housing in urban areas?", "PMAY-Urban 2.0"),
 ("Can I get an urban housing subsidy if I own a pucca house?", "PMAY-Urban 2.0"),
 ("Which traditional trades does the artisan scheme cover?", "PM Vishwakarma"),
 ("Can two members of one family register as artisans?", "PM Vishwakarma"),
 ("Who is not eligible for the craftsperson scheme?", "PM Vishwakarma"),
 ("Do I need auto-debit for the accident insurance scheme?", "PM Suraksha Bima Yojana"),
]

def run_retrieval():
    a1 = a3 = 0
    print("A. RETRIEVAL (all schemes searched, no scheme filter)")
    for q, gold in RETRIEVAL:
        hits = retrieve_official_rules(q, top_k=3)
        names = [h["scheme"] for h in hits]
        ok1 = bool(names) and names[0] == gold
        ok3 = gold in names
        a1 += ok1; a3 += ok3
        if not ok1:
            print(f"   miss@1  {q!r}  gold={gold}  got={names}")
    n = len(RETRIEVAL)
    print(f"   right scheme first: {a1}/{n}   right scheme in top 3: {a3}/{n}\n")
    return a1, a3, n

# ---------------- B. rule-engine tests ----------------
BASE = dict(age=35, gender="male", monthly_income=12000, annual_household_income=144000,
            unorganised_worker=True, income_tax_payer=False, bank_account=True,
            post_office_account=False, nps_member=False, epfo_member=False, esic_member=False,
            landholding_farmer=False)
ENGINE = [  # (description, profile changes, scheme key contains, expected verdict)
 ("APY: income-tax payer is excluded", dict(income_tax_payer=True), "Atal", "NOT_ELIGIBLE"),
 ("APY: age 41 is above the maximum", dict(age=41), "Atal", "NOT_ELIGIBLE"),
 ("APY: age 17 is below the minimum", dict(age=17), "Atal", "NOT_ELIGIBLE"),
 ("APY: age 40 is within the limit", dict(age=40), "Atal", "not NOT_ELIGIBLE"),
 ("APY: age 18 is within the limit", dict(age=18), "Atal", "not NOT_ELIGIBLE"),
 ("PMJJBY: age 51 is above the maximum", dict(age=51), "Jeevan", "NOT_ELIGIBLE"),
 ("PMJJBY: age 50 is within the limit", dict(age=50), "Jeevan", "not NOT_ELIGIBLE"),
 ("PMSBY: age 71 is above the maximum", dict(age=71), "Suraksha", "NOT_ELIGIBLE"),
 ("PMSBY: age 70 is within the limit", dict(age=70), "Suraksha", "not NOT_ELIGIBLE"),
 ("PM-SYM: income Rs 15,001 is above the limit", dict(monthly_income=15001), "Shram", "NOT_ELIGIBLE"),
 ("PM-SYM: income Rs 15,000 is within the limit", dict(monthly_income=15000), "Shram", "not NOT_ELIGIBLE"),
 ("PM-SYM: EPFO member is excluded", dict(epfo_member=True), "Shram", "NOT_ELIGIBLE"),
 ("PM-SYM: age 41 is above the maximum", dict(age=41), "Shram", "NOT_ELIGIBLE"),
 ("PM-KISAN: not a landholding farmer", dict(landholding_farmer=False), "KISAN", "NOT_ELIGIBLE"),
 ("PM-KISAN: income-tax payer is excluded", dict(landholding_farmer=True, income_tax_payer=True), "KISAN", "NOT_ELIGIBLE"),
 ("PM-JAY: age 70 is eligible whatever the income", dict(age=70, monthly_income=500000), "JAY", "ELIGIBLE"),
 ("PM Ujjwala: a man is not eligible", dict(gender="male"), "Ujjwala", "NOT_ELIGIBLE"),
 ("PM Ujjwala: existing LPG connection excludes", dict(gender="female", lpg_connection=True), "Ujjwala", "NOT_ELIGIBLE"),
 ("Sukanya: girl aged 10 is not eligible", dict(girl_child_age=10), "Sukanya", "NOT_ELIGIBLE"),
 ("Sukanya: girl aged 9 is not ruled out", dict(girl_child_age=9), "Sukanya", "not NOT_ELIGIBLE"),
]

def _find(results, key):
    for name, r in results.items():
        if key.lower() in name.lower() or key.lower() in str(r.get("scheme", "")).lower():
            return r
    raise KeyError(key)

def run_engine():
    print("B. RULE-ENGINE TESTS (expected result taken from the official rule text)")
    passed = 0
    for desc, change, key, exp in ENGINE:
        p = dict(BASE); p.update(change)
        v = _find(check_all_schemes(p), key)["verdict"]
        ok = (v == exp) if not exp.startswith("not ") else (v != exp[4:])
        passed += ok
        if not ok:
            print(f"   FAIL  {desc}: expected {exp}, engine said {v}")
    print(f"   passed {passed}/{len(ENGINE)}\n")
    return passed, len(ENGINE)

# ---------------- C. live tool-use test ----------------
LIVE = [  # (question, tools the model should call)
 ("Why am I not eligible for the farmer income support scheme?", {"get_official_rules"}),
 ("What does Atal Pension Yojana require, and does it apply to me?", {"get_official_rules"}),
 ("Where does the rule about income tax payers for APY come from?", {"get_official_rules"}),
 ("Re-check my eligibility if I were 45 years old.", {"check_eligibility"}),
 ("What would change for me if I had a girl child aged 6?", {"check_eligibility"}),
 ("Am I eligible for PM-SYM and what exactly is the rule?", {"check_eligibility", "get_official_rules"}),
 ("What is the weather in Kolkata today?", set()),          # should call no tool
 ("Which scheme will give me a loan of 10 lakh?", set()),   # not covered: should refuse
]

def run_live():
    from agent import ask_agent
    print("C. LIVE TOOL-USE TEST")
    rows, ok_n = [], 0
    for q, expected in LIVE:
        text, trace = ask_agent(q, profile=BASE, results=check_all_schemes(BASE), return_trace=True)
        used = {t["tool"] for t in trace}
        ok = used == expected if not expected else expected.issubset(used)
        ok_n += ok
        print(f"   {'ok ' if ok else 'MISS'} {q}  tools={sorted(used)}")
        rows.append({"question": q, "expected_tools": sorted(expected), "tools_used": sorted(used),
                     "tool_ok": ok, "answer": text, "human_correct": "", "human_notes": ""})
    with open("answers_for_grading.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f"   right tools called: {ok_n}/{len(LIVE)}   (answers saved to answers_for_grading.csv for hand-grading)\n")

if __name__ == "__main__":
    run_retrieval()
    run_engine()
    if "--live" in sys.argv:
        run_live()
