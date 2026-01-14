import streamlit as st
import re


def _name_to_username(full_name: str) -> str:
    # "Jack Smith" -> "jack.smith"
    s = (full_name or "").strip().lower()
    s = re.sub(r"[^a-z0-9 ]+", "", s)  # keep letters/numbers/spaces only
    parts = [p for p in s.split() if p]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0]}.{parts[-1]}"


def _sync_from_name():
    """
    When NAME changes:
    - receiver_name = name
    - starter_full_name = name
    - return_receiver = name (prefill page 2)
    - domain_username = username
    - laptop_username = username
    - m365_user_base = username (for passwords form)
    - m365_username = username@domain
    """
    full_name = (st.session_state.get("name") or "").strip()
    if not full_name:
        return

    username = _name_to_username(full_name)

    # keep receiver name synced
    st.session_state["receiver_name"] = full_name

    # page 2 starter name
    st.session_state["starter_full_name"] = full_name

    # also pre-fill return receiver on page 2
    st.session_state["return_receiver"] = full_name

    # laptop and domain usernames
    st.session_state["laptop_username"] = username
    st.session_state["domain_username"] = username

    # m365 username/base
    st.session_state["m365_user_base"] = username
    domain = st.session_state.get("email_domain", "statom.co.uk")
    st.session_state["m365_username"] = f"{username}@{domain}" if username else ""


def render_form():
    st.markdown(
        """
        <style>
        .form-wrapper {
            transform: scale(0.9);
            transform-origin: top left;
            max-width: 1000px;
            margin: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="form-wrapper">', unsafe_allow_html=True)

    # Header meta
    st.markdown(
        """
        <div class="doc-meta">
            <div>D5.HRS.016</div>
            <div style="text-align:center;">Equipment Issue Form</div>
            <div style="text-align:right;">Version 1.2</div>
        </div>
        <div class="doc-meta">
            <div></div>
            <div></div>
            <div style="text-align:right;">2021-10-12</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="doc-title">EQUIPMENT ISSUE RECORD</div>', unsafe_allow_html=True)

    # Notices
    st.markdown(
        """
        <div class="notice-text">
        This form must be completed upon issue of equipment / technology / software which is provided to you.
        This form will be kept on your personnel file and used to monitor the condition and return of any equipment
        should you depart the company.
        </div>
        <div class="notice-text">
        Be aware that damages or loss of issued items which are not rectified will result in a proportionate and
        reasonable charge for repair or replacement which will be deducted from your final salary.
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------
    # Equipment issued to
    # ---------------------------
    st.markdown('<div class="section-yellow">EQUIPMENT ISSUED TO</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="label">NAME:</div>', unsafe_allow_html=True)
        st.text_input(
            "Name",
            key="name",
            label_visibility="collapsed",
            on_change=_sync_from_name,   # ✅ THIS is what you were missing
        )

    with col2:
        st.markdown('<div class="label">DATE:</div>', unsafe_allow_html=True)
        st.date_input("Date", key="date", label_visibility="collapsed")

    st.markdown('<div class="label">WORK LOCATION:</div>', unsafe_allow_html=True)
    st.text_input("Work Location", key="work_location", value="Roaming", label_visibility="collapsed")

    # ---------------------------
    # Equipment table
    # ---------------------------
    st.markdown('<div class="section-yellow">EQUIPMENT</div>', unsafe_allow_html=True)

    if "equipment" not in st.session_state:
        st.session_state["equipment"] = [{} for _ in range(10)]

    equipment_data = st.session_state["equipment"]

    for i in range(10):
        col_a, col_b, col_c, col_d = st.columns([3, 2, 2, 2])
        with col_a:
            equipment_data[i]["DESCRIPTION"] = st.text_input("Description", key=f"eq_desc_{i}")
        with col_b:
            equipment_data[i]["CONDITION AT ISSUE"] = st.text_input("Condition at Issue", key=f"eq_condition_{i}")
        with col_c:
            equipment_data[i]["SERIAL No"] = st.text_input("Serial No", key=f"eq_serial_{i}")
        with col_d:
            equipment_data[i]["ASSET No"] = st.text_input("Asset No", key=f"eq_asset_{i}")

    st.session_state["equipment"] = equipment_data

    # ---------------------------
    # Issue signoff
    # ---------------------------
    st.markdown('<div class="section-yellow">ISSUE SIGNOFF</div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="label">ISSUER NAME</div>', unsafe_allow_html=True)
        st.text_input("Issuer Name", key="issuer_name", label_visibility="collapsed")
        st.markdown('<div class="label">ISSUER SIGN</div>', unsafe_allow_html=True)
        st.text_input("Issuer Sign", key="issuer_sign", disabled=True, label_visibility="collapsed")

    with col4:
        st.markdown('<div class="label">RECEIVER NAME</div>', unsafe_allow_html=True)
        st.text_input("Receiver Name", key="receiver_name", label_visibility="collapsed")
        st.markdown('<div class="label">RECEIVER SIGN</div>', unsafe_allow_html=True)
        st.text_input("Receiver Sign", key="receiver_sign", disabled=True, label_visibility="collapsed")

    # ✅ REMOVED: RETURNS DETAIL + DATE OF RETURN (you said don’t include it)

    # ---------------------------
    # Returned equipment
    # ---------------------------
    st.markdown('<div class="section-blue">RETURNED EQUIPMENT</div>', unsafe_allow_html=True)

    if "returned_equipment" not in st.session_state:
        st.session_state["returned_equipment"] = [{} for _ in range(8)]

    returned_data = st.session_state["returned_equipment"]

    for i in range(8):
        col_a, col_b, col_c, col_d = st.columns([3, 2, 2, 2])
        with col_a:
            returned_data[i]["DESCRIPTION"] = st.text_input("Description", key=f"ret_desc_{i}")
        with col_b:
            returned_data[i]["RETURNED CONDITION"] = st.text_input("Returned Condition", key=f"ret_condition_{i}")
        with col_c:
            returned_data[i]["SERIAL No"] = st.text_input("Serial No", key=f"ret_serial_{i}")
        with col_d:
            returned_data[i]["ASSET No"] = st.text_input("Asset No", key=f"ret_asset_{i}")

    st.session_state["returned_equipment"] = returned_data

    # ---------------------------
    # Return signoff
    # ---------------------------
    st.markdown('<div class="section-blue">EQUIPMENT RETURN SIGNOFF</div>', unsafe_allow_html=True)

    col5, col6 = st.columns(2)
    with col5:
        st.markdown('<div class="label">ISSUER NAME</div>', unsafe_allow_html=True)
        st.text_input("Return Issuer", key="return_issuer", label_visibility="collapsed")
        st.markdown('<div class="label">ISSUER SIGN</div>', unsafe_allow_html=True)
        st.text_input("Return Issuer Sign", key="return_issuer_sign", disabled=True, label_visibility="collapsed")

    with col6:
        st.markdown('<div class="label">RECEIVER NAME</div>', unsafe_allow_html=True)
        st.text_input("Return Receiver", key="return_receiver", label_visibility="collapsed")
        st.markdown('<div class="label">RECEIVER SIGN</div>', unsafe_allow_html=True)
        st.text_input("Return Receiver Sign", key="return_receiver_sign", disabled=True, label_visibility="collapsed")

    st.markdown(
        '<div class="footer-note">Please attach photographs on attached pages of any recorded defect or condition.</div>',
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)
