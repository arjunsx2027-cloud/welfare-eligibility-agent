import os

from google import genai
from google.genai import types

from eligibility import check_all_schemes
from rules_retriever import retrieve_official_rules, KNOWLEDGE_BASE


client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)

MODEL = "gemini-3.5-flash-lite"


SYSTEM_PROMPT = """
You are an AI assistant for an Indian government welfare-scheme eligibility system.

Your job is to:
1. Understand the citizen's situation.
2. Identify information needed to check eligibility.
3. Use the check_eligibility tool when enough information is available.
4. Use the get_official_rules tool to look up the official wording of a scheme's
   rules, and quote its source name when you explain a result or answer a question
   about what a scheme requires.
5. Explain the results in simple English.

GROUNDING RULES:
- State only facts that appear in the tool results, the engine output or the citizen profile.
  Never describe a scheme's benefits, amounts, loan sizes or features from memory.
- If none of the covered schemes fits what the citizen asks for (for example a loan of a
  stated size), say clearly that these schemes do not cover it. Do not name a scheme just
  to have an answer.
- For a "what if" question (a changed age, a new family member, a different income), run
  check_eligibility again with the changed facts. Never state a new verdict yourself.

TOOLS:
- check_eligibility: the deterministic Python engine. It decides eligibility.
- get_official_rules: retrieves the official rule text and source URL for one scheme.
  Use it for "why", "what does the scheme require" and "what would change this" questions.
  If it returns nothing, say the rules were not found. Do not answer from memory.

IMPORTANT:
- The Python eligibility engine is the source of truth.
- Never invent eligibility rules.
- Never change or override an eligibility decision made by the Python engine.
- If information is unknown, treat it as unknown.
- Clearly distinguish ELIGIBLE, POSSIBLY_ELIGIBLE and NOT_ELIGIBLE.
- If important information is missing, ask the citizen for it.

The Python eligibility engine uses these fields:

age
gender
monthly_income
annual_household_income
unorganised_worker
income_tax_payer
bank_account
post_office_account
nps_member
epfo_member
esic_member
landholding_farmer
pmjay_database_status
lpg_connection
poor_household
auto_debit_consent
girl_child_age
guardian_available
urban
pucca_house
housing_benefit_last_20_years
traditional_trade
self_employed
government_employee
family_government_employee
government_loan_last_5_years
family_member_already_registered
"""


def check_eligibility(
    age=0,
    gender="unknown",
    monthly_income=0,
    annual_household_income=0,
    unorganised_worker=False,
    income_tax_payer=False,
    bank_account=False,
    post_office_account=False,
    nps_member=False,
    epfo_member=False,
    esic_member=False,
    landholding_farmer=False,
    pmjay_database_status="unknown",
    lpg_connection="unknown",
    poor_household="unknown",
    auto_debit_consent="unknown",
    girl_child_age=0,
    guardian_available="unknown",
    urban="unknown",
    pucca_house="unknown",
    housing_benefit_last_20_years="unknown",
    traditional_trade="unknown",
    self_employed="unknown",
    government_employee="unknown",
    family_government_employee="unknown",
    government_loan_last_5_years="unknown",
    family_member_already_registered="unknown"
):
    """
    Run the deterministic Python eligibility engine.
    """

    profile = {
        "age": age,
        "gender": gender,
        "monthly_income": monthly_income,
        "annual_household_income": annual_household_income,
        "unorganised_worker": unorganised_worker,
        "income_tax_payer": income_tax_payer,
        "bank_account": bank_account,
        "post_office_account": post_office_account,
        "nps_member": nps_member,
        "epfo_member": epfo_member,
        "esic_member": esic_member,
        "landholding_farmer": landholding_farmer,
        "pmjay_database_status": pmjay_database_status,
        "lpg_connection": lpg_connection,
        "poor_household": poor_household,
        "auto_debit_consent": auto_debit_consent,
        "girl_child_age": girl_child_age,
        "guardian_available": guardian_available,
        "urban": urban,
        "pucca_house": pucca_house,
        "housing_benefit_last_20_years": housing_benefit_last_20_years,
        "traditional_trade": traditional_trade,
        "self_employed": self_employed,
        "government_employee": government_employee,
        "family_government_employee": family_government_employee,
        "government_loan_last_5_years": government_loan_last_5_years,
        "family_member_already_registered": family_member_already_registered
    }

    return check_all_schemes(profile)


TOOL_DECLARATION = {
    "name": "check_eligibility",
    "description": (
        "Check the citizen's eligibility for Indian government "
        "welfare schemes using the deterministic Python eligibility engine."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "age": {
                "type": "number",
                "description": "Citizen age in years. Use 0 if unknown."
            },
            "gender": {
                "type": "string",
                "description": "Gender such as male, female, or unknown."
            },
            "monthly_income": {
                "type": "number",
                "description": "Monthly income in rupees. Use 0 if unknown."
            },
            "annual_household_income": {
                "type": "number",
                "description": "Annual household income in rupees. Use 0 if unknown."
            },
            "unorganised_worker": {
                "type": "boolean",
                "description": "Whether the citizen is an unorganised worker."
            },
            "income_tax_payer": {
                "type": "boolean",
                "description": "Whether the citizen pays income tax."
            },
            "bank_account": {
                "type": "boolean",
                "description": "Whether the citizen has a bank account."
            },
            "post_office_account": {
                "type": "boolean",
                "description": "Whether the citizen has a post office account."
            },
            "nps_member": {
                "type": "boolean",
                "description": "Whether the citizen is an NPS member."
            },
            "epfo_member": {
                "type": "boolean",
                "description": "Whether the citizen is an EPFO member."
            },
            "esic_member": {
                "type": "boolean",
                "description": "Whether the citizen is an ESIC member."
            },
            "landholding_farmer": {
                "type": "boolean",
                "description": "Whether the citizen is a landholding farmer."
            },
            "pmjay_database_status": {
                "type": "string",
                "description": "PM-JAY database status: true, false, or unknown."
            },
            "lpg_connection": {
                "type": "string",
                "description": "Whether the citizen already has an LPG connection: true, false, or unknown."
            },
            "poor_household": {
                "type": "string",
                "description": "Whether the household qualifies as poor: true, false, or unknown."
            },
            "auto_debit_consent": {
                "type": "string",
                "description": "Whether the citizen agrees to auto-debit: true, false, or unknown."
            },
            "girl_child_age": {
                "type": "number",
                "description": "Age of the girl child for Sukanya Samriddhi. Use 0 if unknown."
            },
            "guardian_available": {
                "type": "string",
                "description": "Whether a guardian is available: true, false, or unknown."
            },
            "urban": {
                "type": "string",
                "description": "Whether the household is in an urban area: true, false, or unknown."
            },
            "pucca_house": {
                "type": "string",
                "description": "Whether the household has a pucca house: true, false, or unknown."
            },
            "housing_benefit_last_20_years": {
                "type": "string",
                "description": "Whether the household received a housing benefit in the last 20 years: true, false, or unknown."
            },
            "traditional_trade": {
                "type": "string",
                "description": "Whether the citizen works in a traditional trade covered by PM Vishwakarma: true, false, or unknown."
            },
            "self_employed": {
                "type": "string",
                "description": "Whether the citizen is self-employed: true, false, or unknown."
            },
            "government_employee": {
                "type": "string",
                "description": "Whether the citizen is a government employee: true, false, or unknown."
            },
            "family_government_employee": {
                "type": "string",
                "description": "Whether a family member is a government employee: true, false, or unknown."
            },
            "government_loan_last_5_years": {
                "type": "string",
                "description": "Whether the citizen received a government loan in the last 5 years: true, false, or unknown."
            },
            "family_member_already_registered": {
                "type": "string",
                "description": "Whether another family member is already registered under PM Vishwakarma: true, false, or unknown."
            }
        },
        "required": [
            "age",
            "gender",
            "monthly_income",
            "annual_household_income",
            "unorganised_worker",
            "income_tax_payer",
            "bank_account",
            "post_office_account",
            "nps_member",
            "epfo_member",
            "esic_member",
            "landholding_farmer",
            "pmjay_database_status",
            "lpg_connection",
            "poor_household",
            "auto_debit_consent",
            "girl_child_age",
            "guardian_available",
            "urban",
            "pucca_house",
            "housing_benefit_last_20_years",
            "traditional_trade",
            "self_employed",
            "government_employee",
            "family_government_employee",
            "government_loan_last_5_years",
            "family_member_already_registered"
        ]
    }
}



SCHEME_NAMES = [item["scheme"] for item in KNOWLEDGE_BASE]

RULES_TOOL_DECLARATION = {
    "name": "get_official_rules",
    "description": (
        "Retrieve the official eligibility rules and source URL for one welfare "
        "scheme, to explain or verify a result. Returns the rule text, the source "
        "name and the URL."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "scheme": {
                "type": "string",
                "description": "Scheme name. One of: " + "; ".join(SCHEME_NAMES)
            },
            "question": {
                "type": "string",
                "description": "What you want to know about the scheme's rules."
            }
        },
        "required": ["scheme", "question"]
    }
}

MAX_STEPS = 5      # cap on tool-calling rounds per question


def get_official_rules(scheme="", question=""):
    """Tool: retrieve official rule passages for a scheme."""
    hits = retrieve_official_rules(query=question or scheme, top_k=2, scheme=scheme or None)
    if not hits and scheme:      # scheme name not matched exactly: search all schemes
        hits = retrieve_official_rules(query=f"{scheme} {question}", top_k=2)
    if not hits:
        return {"found": False, "message": "No official rules found for this scheme."}
    return {
        "found": True,
        "passages": [
            {"scheme": h["scheme"], "rules": " ".join(h["text"].split()),
             "source": h["source"], "url": h["url"], "score": h["score"]}
            for h in hits
        ],
    }


TOOLS = {"check_eligibility": check_eligibility, "get_official_rules": get_official_rules}


def _tool_config():
    return types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[types.Tool(function_declarations=[
            types.FunctionDeclaration(name=d["name"], description=d["description"],
                                      parameters=d["parameters"])
            for d in (TOOL_DECLARATION, RULES_TOOL_DECLARATION)
        ])],
    )


def ask_agent(user_question, profile=None, results=None, return_trace=False):
    """Run the tool-calling loop: the model decides which tool to call, reads the
    result, and decides again, up to MAX_STEPS rounds. Returns the answer text
    (and the list of tool calls when return_trace=True)."""

    contents = []
    if profile is not None or results is not None:
        contents.append(types.Content(role="user", parts=[types.Part.from_text(
            text=f"Current citizen profile:\n\n{profile}\n\nCurrent Python eligibility results:\n\n{results}\n")]))
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_question)]))

    trace = []
    config = _tool_config()
    text = ""

    for step in range(MAX_STEPS + 1):
        # On the last round tools are withdrawn so the model must answer.
        cfg = config if step < MAX_STEPS else types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
        response = client.models.generate_content(model=MODEL, contents=contents, config=cfg)
        parts = response.candidates[0].content.parts or []
        calls = [p.function_call for p in parts if p.function_call]
        if not calls:
            text = response.text or ""
            break

        contents.append(response.candidates[0].content)
        reply_parts = []
        for call in calls:
            args = dict(call.args or {})
            fn = TOOLS.get(call.name)
            try:
                out = fn(**args) if fn else {"error": f"unknown tool {call.name}"}
            except Exception as e:
                out = {"error": str(e)[:200]}
            trace.append({"step": step + 1, "tool": call.name,
                          "args": {k: v for k, v in args.items() if call.name != "check_eligibility"} or "profile fields",
                          "result": out})
            reply_parts.append(types.Part.from_function_response(
                name=call.name, response={"results": out}))
        contents.append(types.Content(role="user", parts=reply_parts))

    return (text, trace) if return_trace else text
