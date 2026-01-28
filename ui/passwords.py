import streamlit as st
import pandas as pd

def render_passwords_form():
    st.markdown("## Passwords (Page 2)")

    # ----------------------------
    # New starter details
    # ----------------------------
    st.text_input("New Starter Full Name", key="starter_full_name")
    st.text_input("Job Title", key="starter_role")

    st.text_area(
        "Instructions (shown on PDF)",
        key="starter_instructions",
        value='Please download the “Microsoft Authenticator App” from your Play Store or App Store',
        height=80,
    )

    # ----------------------------
    # Account details
    # ----------------------------
    st.markdown("### Account Details")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Laptop login")
        st.text_input("Laptop login username", key="laptop_username")
        st.text_input("Laptop login password", key="laptop_password", type="password")

        st.markdown("---")

        st.subheader("Microsoft 365")
        st.text_input(
            "Microsoft 365 username (without @domain)",
            key="m365_user_base",
            help="Example: dalif.toro",
        )
        st.selectbox(
            "Microsoft 365 domain",
            ["statom.co.uk", "demoforce.co.uk", "st-mep.co.uk", "frankifoundations.co.uk", "apexcoreengineering.co.uk"],
            key="m365_domain",
        )
        st.text_input("Microsoft 365 password", key="m365_password", type="password")
        st.checkbox("2 Factor Authentication setup required", key="m365_2fa", value=True)

    with col2:
        st.subheader("Useful Info")
        st.text_input("SharePoint URL", key="sharepoint_url", value="https://statom.sharepoint.com")
        st.text_input("IT Support Helpdesk Email", key="helpdesk_email", value="helpdesk@statom.co.uk")

    # ----------------------------
    # Extra accounts (AutoCAD etc.)
    # ----------------------------
    st.markdown("### Extra Accounts")
    st.caption("Add rows for anything extra (AutoCAD, Revit, Dropbox, etc).")

    if "extra_accounts" not in st.session_state:
        st.session_state["extra_accounts"] = [{"Software": "", "Account": "", "Password": ""}]

    df = pd.DataFrame(st.session_state["extra_accounts"])

    edited = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        key="extra_accounts_editor",
        column_config={
            "Software": st.column_config.TextColumn("Software"),
            "Account": st.column_config.TextColumn("Account"),
            "Password": st.column_config.TextColumn("Password"),
        },
    )

    st.session_state["extra_accounts"] = edited.fillna("").to_dict("records")

    # ----------------------------
    # Optional: show the final M365 email on-screen
    # ----------------------------
    base = (st.session_state.get("m365_user_base") or "").strip()
    dom = (st.session_state.get("m365_domain") or "").strip()
    if base and dom:
        st.info(f"Microsoft 365 email will be: {base}@{dom}")
