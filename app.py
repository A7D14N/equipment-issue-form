import streamlit as st
from pathlib import Path
from PIL import Image

from ui.layout import render_form
from ui.pdf_export import save_form_as_pdf
from ui.passwords import render_passwords_form


st.set_page_config(layout="wide", page_title="Equipment Issue Form")

# ----------------------
# Load CSS
# ----------------------
css_path = Path(__file__).parent / "ui" / "styles.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ----------------------
# Layout
# ----------------------
col_left, col_right = st.columns([1, 3])

# ----------------------
# Left: checklist + export
# ----------------------
with col_left:
    st.markdown("## Checklist")

    equipment_filled = any(
        st.session_state.get(f"eq_desc_{i}", "").strip() != ""
        for i in range(10)
    )

    checklist_items = {
        "NAME": st.session_state.get("name", "").strip() != "",
        "DATE": st.session_state.get("date", None) is not None,
        "WORK LOCATION": st.session_state.get("work_location", "").strip() != "",
        "EQUIPMENT": equipment_filled,
        "ISSUER NAME": st.session_state.get("issuer_name", "").strip() != "",
        "RECEIVER NAME": st.session_state.get("receiver_name", "").strip() != "",
        "DATE OF RETURN": st.session_state.get("return_date", None) is not None,
    }

    for label, completed in checklist_items.items():
        st.markdown(f"✅ {label}" if completed else f"❗ {label}")

    st.markdown("---")
    save_form_as_pdf()

# ----------------------
# Right: logo + form
# ----------------------
with col_right:
    PROJECT_ROOT = Path(__file__).parent
    logos_path = PROJECT_ROOT / "assets" / "logos"

    if logos_path.exists() and logos_path.is_dir():
        logo_files = sorted(
            [f.name for f in logos_path.iterdir() if f.suffix.lower() == ".png"]
        )

        if logo_files:
            default_idx = (
                logo_files.index("demoforce_logo.png")
                if "demoforce_logo.png" in logo_files
                else 0
            )

            selected_logo = st.selectbox(
                "Select Company Logo",
                logo_files,
                index=default_idx,
                key="selected_logo",
            )

            # THIS MUST BE AT THIS INDENT LEVEL
            st.session_state["selected_logo_path"] = str(
                (logos_path / selected_logo).resolve()
            )

            # Preview logo
            try:
                logo_img = Image.open(st.session_state["selected_logo_path"])
                if logo_img.mode in ("RGBA", "P"):
                    logo_img = logo_img.convert("RGB")
                st.image(logo_img, width=200)
            except Exception as e:
                st.error(f"Failed to load logo '{selected_logo}': {e}")

    render_form()
    st.markdown("---")
    render_passwords_form()


