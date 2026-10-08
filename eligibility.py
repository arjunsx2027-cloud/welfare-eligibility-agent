from typing import Any, Dict


# =========================================================
# COMMON HELPERS
# =========================================================

def rule(status: str, reason: str) -> Dict[str, str]:
    return {
        "status": status,
        "reason": reason
    }


def verdict(rules: Dict[str, Dict[str, str]]) -> str:
    statuses = [r["status"] for r in rules.values()]

    if "FAIL" in statuses:
        return "NOT_ELIGIBLE"

    if "UNKNOWN" in statuses:
        return "POSSIBLY_ELIGIBLE"

    return "ELIGIBLE"


def result(scheme: str, rules: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    return {
        "scheme": scheme,
        "verdict": verdict(rules),
        "rules": rules
    }


# =========================================================
# 1. PM-KISAN
# =========================================================

def check_pm_kisan(p: Dict[str, Any]) -> Dict[str, Any]:

    rules = {}

    if p.get("landholding_farmer") is True:
        rules["landholding_farmer"] = rule(
            "PASS",
            "Profile indicates ownership of cultivable agricultural land."
        )
    elif p.get("landholding_farmer") is False:
        rules["landholding_farmer"] = rule(
            "FAIL",
            "Profile indicates no cultivable agricultural landholding."
        )
    else:
        rules["landholding_farmer"] = rule(
            "UNKNOWN",
            "Landholding status is not known."
        )

    if p.get("income_tax_payer") is True:
        rules["income_tax"] = rule(
            "FAIL",
            "Income-tax payer status is an exclusion criterion."
        )
    elif p.get("income_tax_payer") is False:
        rules["income_tax"] = rule(
            "PASS",
            "Applicant is not an income-tax payer."
        )
    else:
        rules["income_tax"] = rule(
            "UNKNOWN",
            "Income-tax payer status is not known."
        )

    return result("PM-KISAN", rules)


# =========================================================
# 2. AYUSHMAN BHARAT PM-JAY
# =========================================================

def check_pmjay(p: Dict[str, Any]) -> Dict[str, Any]:

    rules = {}

    age = p.get("age")

    if age is None:
        rules["age"] = rule(
            "UNKNOWN",
            "Age is not known."
        )
    elif age >= 70:
        rules["age"] = rule(
            "PASS",
            "Applicant is 70 years or older."
        )
    else:
        rules["age"] = rule(
            "PASS",
            "Applicant is below 70; beneficiary status must be checked."
        )

    if age is not None and age >= 70:
        rules["beneficiary_status"] = rule(
            "PASS",
            "Applicants aged 70 or above are eligible irrespective of income."
        )
    else:
        status = p.get("pmjay_database_status")

        if status is True:
            rules["beneficiary_status"] = rule(
                "PASS",
                "Applicant is indicated as an eligible PM-JAY beneficiary."
            )
        elif status is False:
            rules["beneficiary_status"] = rule(
                "FAIL",
                "Applicant is indicated as not being an eligible PM-JAY beneficiary."
            )
        else:
            rules["beneficiary_status"] = rule(
                "UNKNOWN",
                "PM-JAY beneficiary/database status is not known."
            )

    return result("Ayushman Bharat PM-JAY", rules)


# =========================================================
# 3. PM UJJWALA YOJANA
# =========================================================

def check_pmuy(p: Dict[str, Any]) -> Dict[str, Any]:

    rules = {}

    gender = p.get("gender")

    if gender == "female":
        rules["woman"] = rule(
            "PASS",
            "Applicant is a woman."
        )
    elif gender is None:
        rules["woman"] = rule(
            "UNKNOWN",
            "Gender is not known."
        )
    else:
        rules["woman"] = rule(
            "FAIL",
            "PMUY requires the applicant to be a woman."
        )

    age = p.get("age")

    if age is None:
        rules["age"] = rule(
            "UNKNOWN",
            "Age is not known."
        )
    elif age >= 18:
        rules["age"] = rule(
            "PASS",
            "Applicant is at least 18 years old."
        )
    else:
        rules["age"] = rule(
            "FAIL",
            "Applicant is below 18 years of age."
        )

    if p.get("lpg_connection") is True:
        rules["existing_lpg"] = rule(
            "FAIL",
            "Another LPG connection already exists in the household."
        )
    elif p.get("lpg_connection") is False:
        rules["existing_lpg"] = rule(
            "PASS",
            "No existing household LPG connection is indicated."
        )
    else:
        rules["existing_lpg"] = rule(
            "UNKNOWN",
            "Existing household LPG connection status is not known."
        )

    if p.get("poor_household") is True:
        rules["poor_household"] = rule(
            "PASS",
            "Household is indicated to meet the prescribed eligibility criteria."
        )
    elif p.get("poor_household") is False:
        rules["poor_household"] = rule(
            "FAIL",
            "Household is indicated not to meet the prescribed eligibility criteria."
        )
    else:
        rules["poor_household"] = rule(
            "UNKNOWN",
            "Household eligibility status is not known."
        )

    return result("PM Ujjwala Yojana", rules)


# =========================================================
# 4. ATAL PENSION YOJANA
# =========================================================

def check_apy(p: Dict[str, Any]) -> Dict[str, Any]:

    rules = {}

    age = p.get("age")

    if age is None:
        rules["age"] = rule("UNKNOWN", "Age is not known.")
    elif 18 <= age <= 40:
        rules["age"] = rule(
            "PASS",
            "Applicant is between 18 and 40 years old."
        )
    else:
        rules["age"] = rule(
            "FAIL",
            "Applicant is outside the 18–40 age range."
        )

    if p.get("bank_account") is True:
        rules["bank_account"] = rule(
            "PASS",
            "Applicant has a qualifying savings bank/post-office account."
        )
    elif p.get("bank_account") is False:
        rules["bank_account"] = rule(
            "FAIL",
            "A qualifying savings bank/post-office account is required."
        )
    else:
        rules["bank_account"] = rule(
            "UNKNOWN",
            "Bank/post-office account status is not known."
        )

    if p.get("income_tax_payer") is True:
        rules["income_tax"] = rule(
            "FAIL",
            "Income-tax payers cannot open a new APY account from 1 October 2022."
        )
    elif p.get("income_tax_payer") is False:
        rules["income_tax"] = rule(
            "PASS",
            "Applicant is not an income-tax payer."
        )
    else:
        rules["income_tax"] = rule(
            "UNKNOWN",
            "Income-tax payer status is not known."
        )

    return result("Atal Pension Yojana", rules)


# =========================================================
# 5. PM JEEVAN JYOTI BIMA YOJANA
# =========================================================

def check_pmjjby(p: Dict[str, Any]) -> Dict[str, Any]:

    rules = {}

    age = p.get("age")

    if age is None:
        rules["age"] = rule("UNKNOWN", "Age is not known.")
    elif 18 <= age <= 50:
        rules["age"] = rule(
            "PASS",
            "Applicant is within the 18–50 entry age range."
        )
    else:
        rules["age"] = rule(
            "FAIL",
            "Applicant is outside the 18–50 entry age range."
        )

    if p.get("bank_account") is True:
        rules["bank_account"] = rule(
            "PASS",
            "Applicant has a participating bank/post-office account."
        )
    elif p.get("bank_account") is False:
        rules["bank_account"] = rule(
            "FAIL",
            "A participating bank/post-office account is required."
        )
    else:
        rules["bank_account"] = rule(
            "UNKNOWN",
            "Bank/post-office account status is not known."
        )

    if p.get("auto_debit_consent") is True:
        rules["auto_debit"] = rule(
            "PASS",
            "Applicant has provided auto-debit consent."
        )
    elif p.get("auto_debit_consent") is False:
        rules["auto_debit"] = rule(
            "FAIL",
            "Auto-debit consent is required."
        )
    else:
        rules["auto_debit"] = rule(
            "UNKNOWN",
            "Auto-debit consent status is not known."
        )

    return result("PM Jeevan Jyoti Bima Yojana", rules)


# =========================================================
# 6. PM SURAKSHA BIMA YOJANA
# =========================================================

def check_pmsby(p: Dict[str, Any]) -> Dict[str, Any]:

    rules = {}

    age = p.get("age")

    if age is None:
        rules["age"] = rule("UNKNOWN", "Age is not known.")
    elif 18 <= age <= 70:
        rules["age"] = rule(
            "PASS",
            "Applicant is within the 18–70 age range."
        )
    else:
        rules["age"] = rule(
            "FAIL",
            "Applicant is outside the 18–70 age range."
        )

    if p.get("bank_account") is True:
        rules["bank_account"] = rule(
            "PASS",
            "Applicant has a participating bank/post-office account."
        )
    elif p.get("bank_account") is False:
        rules["bank_account"] = rule(
            "FAIL",
            "A participating bank/post-office account is required."
        )
    else:
        rules["bank_account"] = rule(
            "UNKNOWN",
            "Bank/post-office account status is not known."
        )

    if p.get("auto_debit_consent") is True:
        rules["auto_debit"] = rule(
            "PASS",
            "Applicant has provided auto-debit consent."
        )
    elif p.get("auto_debit_consent") is False:
        rules["auto_debit"] = rule(
            "FAIL",
            "Auto-debit consent is required."
        )
    else:
        rules["auto_debit"] = rule(
            "UNKNOWN",
            "Auto-debit consent status is not known."
        )

    return result("PM Suraksha Bima Yojana", rules)


# =========================================================
# 7. PM-SYM
# =========================================================

def check_pm_sym(p: Dict[str, Any]) -> Dict[str, Any]:

    rules = {}

    age = p.get("age")

    if age is None:
        rules["age"] = rule("UNKNOWN", "Age is not known.")
    elif 18 <= age <= 40:
        rules["age"] = rule(
            "PASS",
            "Applicant is between 18 and 40 years old."
        )
    else:
        rules["age"] = rule(
            "FAIL",
            "Applicant is outside the 18–40 age range."
        )

    income = p.get("monthly_income")

    if income is None:
        rules["income"] = rule(
            "UNKNOWN",
            "Monthly income is not known."
        )
    elif income <= 15000:
        rules["income"] = rule(
            "PASS",
            "Monthly income is ₹15,000 or less."
        )
    else:
        rules["income"] = rule(
            "FAIL",
            "Monthly income exceeds ₹15,000."
        )

    if p.get("unorganised_worker") is True:
        rules["worker_type"] = rule(
            "PASS",
            "Applicant is an unorganised worker."
        )
    elif p.get("unorganised_worker") is False:
        rules["worker_type"] = rule(
            "FAIL",
            "Applicant is not an unorganised worker."
        )
    else:
        rules["worker_type"] = rule(
            "UNKNOWN",
            "Worker classification is not known."
        )

    if p.get("nps_member") is True:
        rules["nps"] = rule(
            "FAIL",
            "Members of NPS are excluded."
        )
    elif p.get("nps_member") is False:
        rules["nps"] = rule(
            "PASS",
            "Applicant is not an NPS member."
        )
    else:
        rules["nps"] = rule(
            "UNKNOWN",
            "NPS membership is not known."
        )

    if p.get("epfo_member") is True:
        rules["epfo"] = rule(
            "FAIL",
            "Members of EPFO are excluded."
        )
    elif p.get("epfo_member") is False:
        rules["epfo"] = rule(
            "PASS",
            "Applicant is not an EPFO member."
        )
    else:
        rules["epfo"] = rule(
            "UNKNOWN",
            "EPFO membership is not known."
        )

    if p.get("esic_member") is True:
        rules["esic"] = rule(
            "FAIL",
            "Members covered by ESIC are excluded."
        )
    elif p.get("esic_member") is False:
        rules["esic"] = rule(
            "PASS",
            "Applicant is not covered by ESIC."
        )
    else:
        rules["esic"] = rule(
            "UNKNOWN",
            "ESIC coverage is not known."
        )

    if p.get("income_tax_payer") is True:
        rules["income_tax"] = rule(
            "FAIL",
            "Income-tax payers are excluded."
        )
    elif p.get("income_tax_payer") is False:
        rules["income_tax"] = rule(
            "PASS",
            "Applicant is not an income-tax payer."
        )
    else:
        rules["income_tax"] = rule(
            "UNKNOWN",
            "Income-tax payer status is not known."
        )

    return result("PM Shram Yogi Maandhan", rules)


# =========================================================
# 8. SUKANYA SAMRIDDHI
# =========================================================

def check_sukanya(p: Dict[str, Any]) -> Dict[str, Any]:

    rules = {}

    age = p.get("girl_child_age")

    if age is None:
        rules["girl_child_age"] = rule(
            "UNKNOWN",
            "Girl child's age is not known."
        )
    elif age < 10:
        rules["girl_child_age"] = rule(
            "PASS",
            "Girl child is below 10 years of age."
        )
    else:
        rules["girl_child_age"] = rule(
            "FAIL",
            "Girl child is 10 years or older."
        )

    if p.get("guardian_available") is True:
        rules["guardian"] = rule(
            "PASS",
            "A guardian is available to open the account."
        )
    elif p.get("guardian_available") is False:
        rules["guardian"] = rule(
            "FAIL",
            "A guardian is required to open the account."
        )
    else:
        rules["guardian"] = rule(
            "UNKNOWN",
            "Guardian status is not known."
        )

    return result("Sukanya Samriddhi Account", rules)


# =========================================================
# 9. PMAY-URBAN 2.0
# =========================================================

def check_pmay_urban(p: Dict[str, Any]) -> Dict[str, Any]:

    rules = {}

    if p.get("urban") is True:
        rules["urban"] = rule(
            "PASS",
            "Profile indicates an urban household."
        )
    elif p.get("urban") is False:
        rules["urban"] = rule(
            "FAIL",
            "PMAY-U 2.0 is for eligible urban households."
        )
    else:
        rules["urban"] = rule(
            "UNKNOWN",
            "Urban/rural status is not known."
        )

    income = p.get("annual_household_income")

    if income is None:
        rules["income"] = rule(
            "UNKNOWN",
            "Annual household income is not known."
        )
    elif income <= 900000:
        rules["income"] = rule(
            "PASS",
            "Annual household income is within the scheme's ₹9 lakh upper income band."
        )
    else:
        rules["income"] = rule(
            "FAIL",
            "Annual household income exceeds ₹9 lakh."
        )

    if p.get("pucca_house") is True:
        rules["pucca_house"] = rule(
            "FAIL",
            "Applicant or a family member owns a pucca house."
        )
    elif p.get("pucca_house") is False:
        rules["pucca_house"] = rule(
            "PASS",
            "Applicant/family is indicated not to own a pucca house."
        )
    else:
        rules["pucca_house"] = rule(
            "UNKNOWN",
            "Pucca-house ownership status is not known."
        )

    if p.get("housing_benefit_last_20_years") is True:
        rules["previous_housing_benefit"] = rule(
            "FAIL",
            "Applicant/family received a government housing-scheme benefit within the last 20 years."
        )
    elif p.get("housing_benefit_last_20_years") is False:
        rules["previous_housing_benefit"] = rule(
            "PASS",
            "No government housing-scheme benefit in the last 20 years is indicated."
        )
    else:
        rules["previous_housing_benefit"] = rule(
            "UNKNOWN",
            "Previous housing-scheme benefit status is not known."
        )

    return result("PMAY-Urban 2.0", rules)


# =========================================================
# 10. PM VISHWAKARMA
# =========================================================

def check_pm_vishwakarma(p: Dict[str, Any]) -> Dict[str, Any]:

    rules = {}

    age = p.get("age")

    if age is None:
        rules["age"] = rule(
            "UNKNOWN",
            "Age is not known."
        )
    elif age >= 18:
        rules["age"] = rule(
            "PASS",
            "Applicant is at least 18 years old."
        )
    else:
        rules["age"] = rule(
            "FAIL",
            "Applicant is below 18 years of age."
        )

    if p.get("traditional_trade") is True:
        rules["traditional_trade"] = rule(
            "PASS",
            "Applicant is engaged in one of the specified traditional trades."
        )
    elif p.get("traditional_trade") is False:
        rules["traditional_trade"] = rule(
            "FAIL",
            "Applicant is not engaged in a specified traditional trade."
        )
    else:
        rules["traditional_trade"] = rule(
            "UNKNOWN",
            "Traditional trade status is not known."
        )

    if p.get("self_employed") is True:
        rules["self_employed"] = rule(
            "PASS",
            "Applicant is self-employed/unorganised in the trade."
        )
    elif p.get("self_employed") is False:
        rules["self_employed"] = rule(
            "FAIL",
            "Applicant does not meet the self-employed/unorganised condition."
        )
    else:
        rules["self_employed"] = rule(
            "UNKNOWN",
            "Self-employed status is not known."
        )

    if p.get("government_employee") is True:
        rules["government_employee"] = rule(
            "FAIL",
            "Government employees are excluded."
        )
    elif p.get("government_employee") is False:
        rules["government_employee"] = rule(
            "PASS",
            "Applicant is not a government employee."
        )
    else:
        rules["government_employee"] = rule(
            "UNKNOWN",
            "Government employment status is not known."
        )

    if p.get("family_government_employee") is True:
        rules["family_government_employee"] = rule(
            "FAIL",
            "A family member is indicated to be a government employee."
        )
    elif p.get("family_government_employee") is False:
        rules["family_government_employee"] = rule(
            "PASS",
            "No family government employee is indicated."
        )
    else:
        rules["family_government_employee"] = rule(
            "UNKNOWN",
            "Family government-employment status is not known."
        )

    if p.get("government_loan_last_5_years") is True:
        rules["previous_credit"] = rule(
            "FAIL",
            "Applicant has availed credit support under a government scheme within the last 5 years."
        )
    elif p.get("government_loan_last_5_years") is False:
        rules["previous_credit"] = rule(
            "PASS",
            "No government-scheme credit support in the last 5 years is indicated."
        )
    else:
        rules["previous_credit"] = rule(
            "UNKNOWN",
            "Previous government-scheme credit status is not known."
        )

    if p.get("family_member_already_registered") is True:
        rules["family_registration"] = rule(
            "FAIL",
            "Another family member is already registered under PM Vishwakarma."
        )
    elif p.get("family_member_already_registered") is False:
        rules["family_registration"] = rule(
            "PASS",
            "No other family member is indicated as registered."
        )
    else:
        rules["family_registration"] = rule(
            "UNKNOWN",
            "Family registration status is not known."
        )

    return result("PM Vishwakarma", rules)


# =========================================================
# RUN ALL 10 SCHEMES
# =========================================================

def check_all_schemes(profile: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:

    return {
        "PM-KISAN": check_pm_kisan(profile),
        "PM-JAY": check_pmjay(profile),
        "PMUY": check_pmuy(profile),
        "APY": check_apy(profile),
        "PMJJBY": check_pmjjby(profile),
        "PMSBY": check_pmsby(profile),
        "PM-SYM": check_pm_sym(profile),
        "Sukanya Samriddhi": check_sukanya(profile),
        "PMAY-Urban 2.0": check_pmay_urban(profile),
        "PM Vishwakarma": check_pm_vishwakarma(profile),
    }