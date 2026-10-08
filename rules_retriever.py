from typing import List, Dict, Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# OFFICIAL RULES KNOWLEDGE BASE
# =========================================================

KNOWLEDGE_BASE = [

    {
        "scheme": "PM-KISAN",
        "text": """
        PM-KISAN provides income support to landholding farmer families.
        Eligibility is subject to specified exclusion categories.
        Exclusions include institutional land holders, certain constitutional
        office holders, specified serving or retired government employees,
        certain pensioners, persons who paid income tax in the last assessment
        year, and specified practicing professionals.
        """,
        "source": "PM-KISAN official website",
        "url": "https://www.pmkisan.gov.in/"
    },

    {
        "scheme": "Ayushman Bharat PM-JAY",
        "text": """
        All senior citizens aged 70 years or above are eligible for Ayushman
        Bharat PM-JAY irrespective of economic status or income. For people
        below 70, eligibility depends on the applicable beneficiary database
        and scheme eligibility criteria.
        """,
        "source": "National Health Authority official PM-JAY FAQ",
        "url": "https://nha.gov.in/img/resources/English_FAQs_related_to_the_benefits_for_senior_citizens.pdf"
    },

    {
        "scheme": "PM Ujjwala Yojana",
        "text": """
        PMUY eligibility requires an adult woman who has attained 18 years of
        age and belongs to an eligible category or poor household under the
        prescribed declaration. There should not be any other LPG connection
        in the same household.
        """,
        "source": "PM Ujjwala Yojana official website",
        "url": "https://www.pmuy.gov.in/about.html"
    },

    {
        "scheme": "Atal Pension Yojana",
        "text": """
        APY is available to Indian citizens with a savings bank account in a
        bank or Department of Posts. The minimum age of joining is 18 years
        and the maximum age is 40 years. From 1 October 2022, any Indian
        citizen who is or has been an income-tax payer on the date of
        application is not eligible to open a new APY account.
        """,
        "source": "PFRDA official APY page",
        "url": "https://pfrda.org.in/web/pfrda/schemes/atal-pension-yojana-apy"
    },

    {
        "scheme": "PM Jeevan Jyoti Bima Yojana",
        "text": """
        PMJJBY is available to individual account holders of participating
        banks or post offices in the age group of 18 to 50 years. A person
        with multiple bank or post office accounts can join through only one
        account. Enrolment involves payment through auto-debit from the
        designated bank or post office account.
        """,
        "source": "Jan Suraksha official PMJJBY rules",
        "url": "https://jansuraksha.gov.in/Files/PMJJBY/English/Rules.pdf"
    },

    {
        "scheme": "PM Suraksha Bima Yojana",
        "text": """
        PMSBY is available to individual bank or post office account holders
        in the age group of 18 to 70 years in participating institutions.
        Where a person has multiple accounts, the person can join through
        only one bank or post office account. Enrolment and premium payment
        use auto-debit from the designated account.
        """,
        "source": "Jan Suraksha official PMSBY rules",
        "url": "https://jansuraksha.gov.in/Files/PMSBY/English/Rules.pdf"
    },

    {
        "scheme": "PM Shram Yogi Maandhan",
        "text": """
        PM-SYM is a voluntary contributory pension scheme for unorganised
        workers aged 18 to 40 years with monthly income of Rs. 15,000 or less.
        The worker should not be covered under statutory social security
        schemes such as NPS, Employees' State Insurance Corporation or
        Employees' Provident Fund Organisation and should not be an
        income-tax payee.
        """,
        "source": "Ministry of Labour and Employment official FAQ",
        "url": "https://labour.gov.in/FAQ-0"
    },

    {
        "scheme": "Sukanya Samriddhi Account",
        "text": """
        A Sukanya Samriddhi Account can be opened by a natural or legal
        guardian in the name of a girl child who has not attained the age of
        ten years on the date of opening the account. The account is operated
        through a guardian subject to the applicable account rules.
        """,
        "source": "India Post official POSB material",
        "url": "https://www.indiapost.gov.in/"
    },

    {
        "scheme": "PMAY-Urban 2.0",
        "text": """
        PMAY-U 2.0 covers eligible families in urban areas belonging to EWS,
        LIG and MIG categories who do not own a pucca house anywhere in India.
        EWS households have annual income up to Rs. 3 lakh, LIG households
        have annual income from Rs. 3 lakh up to Rs. 6 lakh, and MIG households
        have annual income from Rs. 6 lakh up to Rs. 9 lakh. A beneficiary
        who has been allotted a house under a housing scheme of the Central
        Government, State or UT Government or Local Self Government in the
        previous 20 years is not eligible.
        """,
        "source": "PMAY-U 2.0 official website",
        "url": "https://pmaymis.gov.in/PMAYMIS2_2024/PmayFAQ.aspx"
    },

    {
        "scheme": "PM Vishwakarma",
        "text": """
        PM Vishwakarma is for artisans and craftspeople working with hands
        and tools in one of the 18 specified traditional trades in the
        unorganised sector on a self-employment basis. The applicant must be
        at least 18 years old and engaged in the concerned trade on the date
        of registration. The applicant should not have availed similar
        government credit-based self-employment or business-development loans
        during the previous five years. Registration and benefits are
        restricted to one member of a family. A person in government service
        and their family members are not eligible.
        """,
        "source": "Government of India MyScheme PM Vishwakarma",
        "url": "https://www.myscheme.gov.in/schemes/pmv"
    }
]


# =========================================================
# BUILD SEARCH INDEX
# =========================================================

DOCUMENTS = [
    item["scheme"] + " " + item["text"]
    for item in KNOWLEDGE_BASE
]

VECTORIZER = TfidfVectorizer(
    lowercase=True,
    stop_words="english"
)

DOCUMENT_MATRIX = VECTORIZER.fit_transform(DOCUMENTS)


# =========================================================
# RETRIEVAL FUNCTION
# =========================================================

def retrieve_official_rules(
    query: str,
    top_k: int = 3,
    scheme: str = None
) -> List[Dict[str, Any]]:

    """
    Retrieve relevant official rule chunks.

    If a specific scheme is supplied, retrieval is restricted
    to that scheme. This prevents rules from another scheme
    being treated as evidence for the requested scheme.
    """

    if not query or not query.strip():
        return []

    # -----------------------------------------------------
    # SCHEME-SPECIFIC SEARCH
    # -----------------------------------------------------

    if scheme:

        matching_documents = [
            item
            for item in KNOWLEDGE_BASE
            if item["scheme"].lower() == scheme.lower()
        ]

        if not matching_documents:
            return []

        documents = [
            item["scheme"] + " " + item["text"]
            for item in matching_documents
        ]

        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english"
        )

        document_matrix = vectorizer.fit_transform(documents)
        query_vector = vectorizer.transform([query])

        similarities = cosine_similarity(
            query_vector,
            document_matrix
        )[0]

        ranked_indices = similarities.argsort()[::-1][:top_k]

        results = []

        for index in ranked_indices:

            item = matching_documents[index].copy()
            item["score"] = round(
                float(similarities[index]),
                4
            )

            results.append(item)

        return results

    # -----------------------------------------------------
    # GENERAL SEARCH ACROSS ALL SCHEMES
    # -----------------------------------------------------

    query_vector = VECTORIZER.transform([query])

    similarities = cosine_similarity(
        query_vector,
        DOCUMENT_MATRIX
    )[0]

    ranked_indices = similarities.argsort()[::-1][:top_k]

    results = []

    for index in ranked_indices:

        score = float(similarities[index])

        if score <= 0:
            continue

        item = KNOWLEDGE_BASE[index].copy()
        item["score"] = round(score, 4)

        results.append(item)

    return results


# =========================================================
# SIMPLE TEST
# =========================================================

if __name__ == "__main__":

    tests = [
        {
            "query": "Can an income tax payer join?",
            "scheme": "Atal Pension Yojana"
        },
        {
            "query": "What are the age and income requirements?",
            "scheme": "PM Shram Yogi Maandhan"
        },
        {
            "query": "Who can get the scheme?",
            "scheme": "PMAY-Urban 2.0"
        },
        {
            "query": "Can a 70 year old person get this?",
            "scheme": "Ayushman Bharat PM-JAY"
        },
        {
            "query": "Who can apply?",
            "scheme": "PM Vishwakarma"
        }
    ]

    for test in tests:

        print("\n" + "=" * 70)
        print("QUERY:", test["query"])
        print("SCHEME:", test["scheme"])
        print("=" * 70)

        results = retrieve_official_rules(
            test["query"],
            top_k=2,
            scheme=test["scheme"]
        )

        for item in results:

            print(f"\nSCHEME: {item['scheme']}")
            print(f"SCORE: {item['score']}")
            print(f"SOURCE: {item['source']}")
            print(f"URL: {item['url']}")
            print(f"RULES: {item['text'].strip()}")