import streamlit as st
from eligibility import check_all_schemes
from agent import ask_agent


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Welfare Eligibility Checker",
    page_icon="🇮🇳",
    layout="wide"
)


# =========================================================
# SESSION STATE
# =========================================================

if "last_profile" not in st.session_state:
    st.session_state["last_profile"] = None

if "last_results" not in st.session_state:
    st.session_state["last_results"] = None

if "ai_explanation" not in st.session_state:
    st.session_state["ai_explanation"] = None

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "question_text" not in st.session_state:
    st.session_state["question_text"] = ""

if "question_to_process" not in st.session_state:
    st.session_state["question_to_process"] = ""


# =========================================================
# CALLBACKS
# =========================================================

def select_question(question):
    st.session_state["question_text"] = question


def ask_ai_callback():

    question = st.session_state.get(
        "question_text",
        ""
    ).strip()

    if not question:
        return

    results = st.session_state.get("last_results")
    profile = st.session_state.get("last_profile")

    if results is None or profile is None:
        return

    st.session_state["question_to_process"] = question
    st.session_state["question_text"] = ""


# =========================================================
# PROCESS PENDING QUESTION
# =========================================================

def process_pending_question():

    question = st.session_state.get(
        "question_to_process",
        ""
    )

    if not question:
        return

    results = st.session_state.get("last_results")
    profile = st.session_state.get("last_profile")

    if results is None or profile is None:
        st.session_state["question_to_process"] = ""
        return

    with st.spinner("Thinking..."):

        answer, trace = ask_agent(
            question,
            profile=profile,
            results=results,
            return_trace=True
        )

    st.session_state["chat_history"].append(
        {
            "question": question,
            "answer": answer,
            "trace": trace
        }
    )

    st.session_state["question_to_process"] = ""


def show_trace(trace):
    """Show which tools the assistant called for this answer."""
    if not trace:
        return
    with st.expander(f"🔧 How the assistant got this answer ({len(trace)} tool call(s))"):
        for t in trace:
            if t["tool"] == "get_official_rules":
                st.markdown(f"**Step {t['step']}: looked up official rules** for "
                            f"*{t['args'].get('scheme', '')}*")
                res = t["result"]
                if res.get("found"):
                    for p in res["passages"]:
                        st.markdown(f"- {p['source']} ([link]({p['url']}))")
                else:
                    st.markdown("- No official rules found.")
            else:
                st.markdown(f"**Step {t['step']}: ran the eligibility engine** "
                            "(the engine decides; the AI only explains)")


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 19px;
        color: #555;
        margin-bottom: 25px;
    }

    .step-card {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e5e5e5;
        background-color: #fafafa;
        min-height: 130px;
    }

    .step-number {
        font-size: 26px;
        font-weight: 700;
    }

    .step-title {
        font-size: 18px;
        font-weight: 600;
        margin-top: 5px;
    }

    .step-text {
        font-size: 14px;
        color: #666;
        margin-top: 5px;
    }

    .section-note {
        color: #666;
        font-size: 15px;
        margin-bottom: 15px;
    }

    .summary-card {
        padding: 22px 18px;
        border-radius: 14px;
        text-align: center;
        border: 1px solid #e5e5e5;
        min-height: 145px;
    }

    .summary-number {
        font-size: 38px;
        font-weight: 700;
        margin: 5px 0;
    }

    .summary-label {
        font-size: 16px;
        font-weight: 600;
    }

    .summary-description {
        font-size: 13px;
        margin-top: 8px;
        color: #666;
    }

    .overall-result {
        padding: 18px 20px;
        border-radius: 12px;
        border: 1px solid #e5e5e5;
        background-color: #fafafa;
        margin-bottom: 20px;
        font-size: 17px;
    }

    .next-step-box {
        padding: 14px 16px;
        border-radius: 10px;
        border: 1px solid #e5e5e5;
        background-color: #fafafa;
        margin-top: 12px;
    }

    .unknown-box {
        padding: 14px 16px;
        border-radius: 10px;
        border: 1px solid #f0d98c;
        background-color: #fff9e6;
        margin-top: 12px;
        margin-bottom: 12px;
    }

    .unknown-title {
        font-weight: 600;
        margin-bottom: 5px;
    }

    /* =====================================================
       TEXT INPUT VISIBILITY FIX
       ===================================================== */

    div[data-baseweb="input"] {
        background-color: #ffffff !important;
    }

    div[data-baseweb="input"] input {
        color: #111111 !important;
        background-color: #ffffff !important;
        -webkit-text-fill-color: #111111 !important;
        caret-color: #111111 !important;
    }

    div[data-baseweb="input"] input::placeholder {
        color: #666666 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #666666 !important;
    }

    /* =====================================================
       TEXT AREA VISIBILITY FIX
       ===================================================== */

    div[data-baseweb="textarea"] {
        background-color: #ffffff !important;
    }

    div[data-baseweb="textarea"] textarea {
        color: #111111 !important;
        background-color: #ffffff !important;
        -webkit-text-fill-color: #111111 !important;
        caret-color: #111111 !important;
    }

    div[data-baseweb="textarea"] textarea::placeholder {
        color: #666666 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #666666 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🇮🇳 Welfare Eligibility Checker</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Find government welfare schemes you may be eligible for using '
    'your personal and household information.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# HOW IT WORKS
# =========================================================

st.markdown("### How it works")

step1, step2, step3 = st.columns(3)

with step1:

    st.markdown(
        """
        <div class="step-card">
            <div class="step-number">1️⃣</div>
            <div class="step-title">Tell us about yourself</div>
            <div class="step-text">
                Enter basic information about your age, income,
                employment and household situation.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with step2:

    st.markdown(
        """
        <div class="step-card">
            <div class="step-number">2️⃣</div>
            <div class="step-title">Check your eligibility</div>
            <div class="step-text">
                Our eligibility engine compares your information
                with the criteria of selected welfare schemes.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with step3:

    st.markdown(
        """
        <div class="step-card">
            <div class="step-number">3️⃣</div>
            <div class="step-title">Ask the AI assistant</div>
            <div class="step-text">
                Understand your results and ask follow-up
                questions in simple language.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


# =========================================================
# CITIZEN PROFILE
# =========================================================

st.header("1. Citizen Profile")

st.markdown(
    '<div class="section-note">'
    'Tell us about yourself. This information is used to screen '
    'your eligibility against the selected schemes.'
    '</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:

    age = st.number_input(
        "Age",
        min_value=1,
        max_value=120,
        value=35
    )

    gender = st.selectbox(
        "Gender",
        ["Male", "Female", "Other"]
    )

    monthly_income = st.number_input(
        "Monthly household income (₹)",
        min_value=0,
        value=12000,
        step=1000
    )

    unorganised_worker = st.checkbox(
        "I am an unorganised worker",
        value=True
    )

    income_tax_payer = st.checkbox(
        "I pay income tax",
        value=False
    )

with col2:

    bank_account = st.checkbox(
        "I have a bank account",
        value=True
    )

    post_office_account = st.checkbox(
        "I have a post office savings account",
        value=False
    )

    nps_member = st.checkbox(
        "I am already an NPS member",
        value=False
    )

    epfo_member = st.checkbox(
        "I am an EPFO member",
        value=False
    )

    esic_member = st.checkbox(
        "I am an ESIC member",
        value=False
    )


# =========================================================
# ADDITIONAL INFORMATION
# =========================================================

st.header("2. Additional Information")

st.markdown(
    '<div class="section-note">'
    'A few additional questions help us screen schemes with '
    'more specific eligibility requirements.'
    '</div>',
    unsafe_allow_html=True
)

col3, col4 = st.columns(2)

with col3:

    landholding_farmer = st.checkbox(
        "I am a landholding farmer",
        value=False
    )

    pmjay_status = st.selectbox(
        "PM-JAY beneficiary status",
        ["Unknown", "Yes", "No"]
    )

    existing_lpg = st.selectbox(
        "Do you already have an LPG connection?",
        ["Unknown", "Yes", "No"]
    )

with col4:

    poor_household = st.selectbox(
        "Would you describe your household as economically poor?",
        ["Unknown", "Yes", "No"]
    )


# =========================================================
# CREATE PROFILE
# =========================================================

profile = {
    "age": age,
    "gender": gender.lower(),
    "monthly_income": monthly_income,
    "unorganised_worker": unorganised_worker,
    "income_tax_payer": income_tax_payer,
    "bank_account": bank_account,
    "post_office_account": post_office_account,
    "nps_member": nps_member,
    "epfo_member": epfo_member,
    "esic_member": esic_member,
    "landholding_farmer": landholding_farmer,
    "pmjay_status": pmjay_status.lower(),
    "existing_lpg": existing_lpg.lower(),
    "poor_household": poor_household.lower()
}


# =========================================================
# CHECK ELIGIBILITY
# =========================================================

st.header("3. Check Eligibility")

if st.button(
    "🔍 Check Eligibility",
    type="primary",
    use_container_width=True
):

    with st.spinner("Checking your eligibility..."):

        results = check_all_schemes(profile)

    st.session_state["last_profile"] = profile
    st.session_state["last_results"] = results
    st.session_state["chat_history"] = []
    st.session_state["ai_explanation"] = None
    st.session_state["ai_trace"] = []
    st.session_state["question_text"] = ""
    st.session_state["question_to_process"] = ""

    with st.spinner("The AI is analysing your results..."):

        ai_response, ai_trace = ask_agent(
            """
            Review the citizen's profile and the eligibility engine
            results provided above.

            Explain the results in simple English.

            Start with the schemes where the citizen is ELIGIBLE.

            Then explain POSSIBLY ELIGIBLE schemes and what information
            still needs to be verified.

            Briefly explain why the citizen is NOT ELIGIBLE for the
            other schemes.

            Do not change any eligibility decision made by the
            eligibility engine.

            Do not invent eligibility criteria, benefits, or facts
            that are not present in the provided information.
            """,
            profile=profile,
            results=results,
            return_trace=True
        )

    st.session_state["ai_explanation"] = ai_response
    st.session_state["ai_trace"] = ai_trace


# =========================================================
# PROCESS AI QUESTION
# =========================================================

process_pending_question()


# =========================================================
# DISPLAY RESULTS
# =========================================================

if st.session_state["last_results"] is not None:

    results = st.session_state["last_results"]

    # =====================================================
    # SUMMARY
    # =====================================================

    st.header("4. Eligibility Summary")

    eligible_count = sum(
        1
        for r in results.values()
        if r.get("verdict") == "ELIGIBLE"
    )

    possible_count = sum(
        1
        for r in results.values()
        if r.get("verdict") == "POSSIBLY_ELIGIBLE"
    )

    not_eligible_count = sum(
        1
        for r in results.values()
        if r.get("verdict") == "NOT_ELIGIBLE"
    )

    total_schemes = len(results)

    # =====================================================
    # COUNT UNKNOWN INFORMATION
    # =====================================================

    total_unknown_rules = 0

    for result in results.values():

        rules = result.get("rules", {})

        for rule_result in rules.values():

            if rule_result.get("status", "UNKNOWN") not in [
                "PASS",
                "FAIL"
            ]:
                total_unknown_rules += 1

    # =====================================================
    # OVERALL MESSAGE
    # =====================================================

    if eligible_count > 0:

        overall_message = (
            f"Based on the information you provided, "
            f"you appear to meet the screening criteria for "
            f"<strong>{eligible_count}</strong> of the "
            f"{total_schemes} schemes screened."
        )

        if possible_count > 0:

            overall_message += (
                f" There are also <strong>{possible_count}</strong> "
                f"schemes where more information needs to be verified."
            )

    elif possible_count > 0:

        overall_message = (
            f"We could not confirm eligibility yet, but you may qualify "
            f"for <strong>{possible_count}</strong> schemes. "
            f"Some information needs to be verified."
        )

    else:

        overall_message = (
            f"Based on the information provided, you do not currently "
            f"appear to meet the screening criteria for the "
            f"{total_schemes} schemes checked."
        )

    # =====================================================
    # OVERALL RESULT
    # =====================================================

    st.markdown(
        f"""
        <div class="overall-result">
            <strong>Your screening result</strong><br>
            {overall_message}
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # UNKNOWN INFORMATION NOTICE
    # =====================================================

    if total_unknown_rules > 0:

        st.markdown(
            f"""
            <div class="unknown-box">
                <div class="unknown-title">
                    ❓ Some information still needs to be verified
                </div>
                Some of your answers are currently marked as unknown.
                This means certain scheme conditions could not be
                fully assessed.
                <br><br>
                We found <strong>{total_unknown_rules}</strong>
                condition(s) that could not be fully assessed.
                Look for <strong>❓ Information to verify</strong>
                inside the scheme results below.
            </div>
            """,
            unsafe_allow_html=True
        )

    # =====================================================
    # SUMMARY CARDS
    # =====================================================

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:

        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-number">
                    {eligible_count}
                </div>
                <div class="summary-label">
                    🟢 Eligible
                </div>
                <div class="summary-description">
                    You appear to meet the screening criteria.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with summary_col2:

        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-number">
                    {possible_count}
                </div>
                <div class="summary-label">
                    🟡 Possibly Eligible
                </div>
                <div class="summary-description">
                    More information needs to be verified.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with summary_col3:

        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-number">
                    {not_eligible_count}
                </div>
                <div class="summary-label">
                    🔴 Not Eligible
                </div>
                <div class="summary-description">
                    You do not appear to meet the screening criteria.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # =====================================================
    # SCHEME RESULTS
    # =====================================================

    st.divider()

    st.header("5. Scheme-wise Results")

    st.markdown(
        '<div class="section-note">'
        'Expand a scheme to see your status, the conditions you meet, '
        'the conditions you do not meet, and anything that may need '
        'further verification.'
        '</div>',
        unsafe_allow_html=True
    )

    for scheme_key, result in results.items():

        scheme = result.get(
            "scheme",
            scheme_key
        )

        verdict = result.get(
            "verdict",
            "UNKNOWN"
        )

        rules = result.get(
            "rules",
            {}
        )

        # -------------------------------------------------
        # SCHEME STATUS
        # -------------------------------------------------

        if verdict == "ELIGIBLE":

            icon = "🟢"
            status_text = "ELIGIBLE"

        elif verdict == "POSSIBLY_ELIGIBLE":

            icon = "🟡"
            status_text = "POSSIBLY ELIGIBLE"

        else:

            icon = "🔴"
            status_text = "NOT ELIGIBLE"

        # -------------------------------------------------
        # EXPANDER
        # -------------------------------------------------

        with st.expander(
            f"{icon} {scheme} — {status_text}",
            expanded=(verdict != "NOT_ELIGIBLE")
        ):

            if verdict == "ELIGIBLE":

                st.success(
                    "✅ You appear to meet the screening criteria "
                    "for this scheme based on the information provided."
                )

            elif verdict == "POSSIBLY_ELIGIBLE":

                st.warning(
                    "⚠️ You may be eligible, but the information "
                    "provided is not enough to confirm eligibility."
                )

            else:

                st.error(
                    "❌ You do not appear to meet the screening "
                    "criteria for this scheme."
                )

            # -------------------------------------------------
            # GROUP RULES
            # -------------------------------------------------

            passed_rules = []
            failed_rules = []
            unknown_rules = []

            for rule_name, rule_result in rules.items():

                rule_status = rule_result.get(
                    "status",
                    "UNKNOWN"
                )

                reason = rule_result.get(
                    "reason",
                    ""
                )

                rule_item = (
                    rule_name.replace("_", " ").title(),
                    reason
                )

                if rule_status == "PASS":

                    passed_rules.append(rule_item)

                elif rule_status == "FAIL":

                    failed_rules.append(rule_item)

                else:

                    unknown_rules.append(rule_item)

            # -------------------------------------------------
            # CONDITIONS MET
            # -------------------------------------------------

            if passed_rules:

                st.markdown("### ✅ Conditions met")

                for rule_name, reason in passed_rules:

                    st.markdown(
                        f"**{rule_name}**  \n"
                        f"{reason}"
                    )

            # -------------------------------------------------
            # CONDITIONS NOT MET
            # -------------------------------------------------

            if failed_rules:

                st.markdown("### ❌ Conditions not met")

                for rule_name, reason in failed_rules:

                    st.markdown(
                        f"**{rule_name}**  \n"
                        f"{reason}"
                    )

            # -------------------------------------------------
            # INFORMATION TO VERIFY
            # -------------------------------------------------

            if unknown_rules:

                st.markdown("### ❓ Information to verify")

                st.info(
                    "These conditions could not be fully assessed "
                    "because some information is unknown or missing."
                )

                for rule_name, reason in unknown_rules:

                    st.markdown(
                        f"**{rule_name}**  \n"
                        f"{reason}"
                    )

            # -------------------------------------------------
            # WHAT TO DO NEXT
            # -------------------------------------------------

            if verdict == "ELIGIBLE":

                st.markdown(
                    """
                    <div class="next-step-box">
                        <strong>➡️ What to do next</strong><br>
                        You appear to meet the screening criteria for
                        this scheme based on the information provided.
                        Check the official scheme requirements and
                        application process before applying.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif verdict == "POSSIBLY_ELIGIBLE":

                st.markdown(
                    """
                    <div class="next-step-box">
                        <strong>➡️ What to do next</strong><br>
                        Check the information listed under
                        <strong>❓ Information to verify</strong> above.
                        Confirming these details will help determine
                        whether you are eligible.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    """
                    <div class="next-step-box">
                        <strong>➡️ What to do next</strong><br>
                        Based on the information currently provided,
                        you do not appear to meet the screening criteria
                        for this scheme.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # =====================================================
    # AI EXPLANATION
    # =====================================================

    st.divider()

    st.header("6. 🤖 AI Welfare Assistant")

    st.write(
        "The AI assistant explains your screening results "
        "in simple language. It does not change the decisions "
        "made by the eligibility engine."
    )

    if st.session_state["ai_explanation"]:

        st.info(
            st.session_state["ai_explanation"]
        )
        show_trace(st.session_state.get("ai_trace"))

    # =====================================================
    # SUGGESTED QUESTIONS
    # =====================================================

    st.divider()

    st.header("7. 💬 Ask the AI Assistant")

    st.write(
        "Choose a suggested question or type your own question."
    )

    st.write("**💡 Suggested questions**")

    suggestion_col1, suggestion_col2 = st.columns(2)

    with suggestion_col1:

        st.button(
            "Why am I eligible for these schemes?",
            use_container_width=True,
            on_click=select_question,
            args=("Why am I eligible for these schemes?",)
        )

        st.button(
            "Why am I possibly eligible for some schemes?",
            use_container_width=True,
            on_click=select_question,
            args=("Why am I possibly eligible for some schemes?",)
        )

        st.button(
            "What should I do next?",
            use_container_width=True,
            on_click=select_question,
            args=("What should I do next?",)
        )

    with suggestion_col2:

        st.button(
            "Why am I not eligible for some schemes?",
            use_container_width=True,
            on_click=select_question,
            args=("Why am I not eligible for some schemes?",)
        )

        st.button(
            "What information do I need to verify?",
            use_container_width=True,
            on_click=select_question,
            args=("What information do I need to verify?",)
        )

        st.button(
            "Explain my results in simple terms.",
            use_container_width=True,
            on_click=select_question,
            args=("Explain my results in simple terms.",)
        )

    # =====================================================
    # CONVERSATION HISTORY
    # =====================================================

    if st.session_state["chat_history"]:

        st.write("### Conversation")

        for chat in st.session_state["chat_history"]:

            st.markdown(
                f"**👤 You:** {chat['question']}"
            )

            st.markdown(
                f"**🤖 AI:** {chat['answer']}"
            )
            show_trace(chat.get("trace"))

            st.divider()

    # =====================================================
    # QUESTION INPUT
    # =====================================================

    st.write("### Ask another question")

    st.text_input(
        "Your question",
        placeholder="Type your question here...",
        key="question_text"
    )

    st.button(
        "Ask AI",
        type="primary",
        on_click=ask_ai_callback
    )


# =========================================================
# DISCLAIMER
# =========================================================

st.divider()

st.caption(
    "⚠️ This tool provides preliminary screening only. "
    "It is not an official government eligibility determination. "
    "Eligibility should be verified through the official government "
    "scheme or relevant authority before taking any action."
)