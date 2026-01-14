import streamlit as st

def render_form():
    # A4-like scale (keep if you want)
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

    st.markdown('<div class="section-yellow">EQUIPMENT ISSUED TO</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="label">NAME:</div>', unsafe_allow_html=True)
        st.text_input("Name", key="name", label_visibility="collapsed")

    with col2:
        st.markdown('<div class="label">DATE:</div>', unsafe_allow_html=True)
        st.date_input("Date", key="date", label_visibility="collapsed")

    st.markdown('<div class="label">WORK LOCATION:</div>', unsafe_allow_html=True)
    st.text_input("Work Location", key="work_location", value="Roaming", label_visibility="collapsed")

    st.markdown('<div class="section-yellow">EQUIPMENT</div>', unsafe_allow_html=True)

    equipment_data = st.session_state.get("equipment", [{} for _ in range(10)])

    for i in range(10):
        col_a, col_b, col_c, col_d = st.columns([3, 2, 2, 2])
        with col_a:
            equipment_data[i]["DESCRIPTION"] = st.text_input(
                "Description", key=f"eq_desc_{i}"
            )
        with col_b:
            equipment_data[i]["CONDITION AT ISSUE"] = st.text_input(
                "Condition at Issue", key=f"eq_condition_{i}"
            )
        with col_c:
            equipment_data[i]["SERIAL No"] = st.text_input(
                "Serial No", key=f"eq_serial_{i}"
            )
        with col_d:
            equipment_data[i]["ASSET No"] = st.text_input(
                "Asset No", key=f"eq_asset_{i}"
            )

    st.session_state["equipment"] = equipment_data

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

    st.markdown('<div class="section-blue">RETURNS DETAIL</div>', unsafe_allow_html=True)
    st.markdown('<div class="label">DATE OF RETURN</div>', unsafe_allow_html=True)
    st.date_input("Return Date", key="return_date", label_visibility="collapsed")

    st.markdown('<div class="section-blue">RETURNED EQUIPMENT</div>', unsafe_allow_html=True)

    returned_data = st.session_state.get("returned_equipment", [{} for _ in range(8)])

    for i in range(8):
        col_a, col_b, col_c, col_d = st.columns([3, 2, 2, 2])
        with col_a:
            returned_data[i]["DESCRIPTION"] = st.text_input(
                "Description", key=f"ret_desc_{i}"
            )
        with col_b:
            returned_data[i]["RETURNED CONDITION"] = st.text_input(
                "Returned Condition", key=f"ret_condition_{i}"
            )
        with col_c:
            returned_data[i]["SERIAL No"] = st.text_input(
                "Serial No", key=f"ret_serial_{i}"
            )
        with col_d:
            returned_data[i]["ASSET No"] = st.text_input(
                "Asset No", key=f"ret_asset_{i}"
            )

    st.session_state["returned_equipment"] = returned_data

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

    st.markdown('</div>', unsafe_allow_html=True)
