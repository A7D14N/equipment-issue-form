import streamlit as st
import re
from datetime import date, datetime
from io import BytesIO
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

from PIL import Image


# ---------- filename helpers ----------
def _safe_filename(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"[^\w\-. ]+", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s or "export"


def _fmt_date(v):
    if isinstance(v, (date, datetime)):
        return v.strftime("%Y-%m-%d")
    return "" if v is None else str(v)


def _first_asset_number() -> str:
    # Prefer first non-empty eq_asset_0..9 (what user types)
    for i in range(10):
        v = st.session_state.get(f"eq_asset_{i}", "")
        if str(v).strip():
            return str(v).strip()

    # fallback if you ever store equipment list dicts
    equipment = st.session_state.get("equipment", []) or []
    for r in equipment:
        v = (r or {}).get("ASSET No", "")
        if str(v).strip():
            return str(v).strip()

    return ""


def _get_m365_email() -> str:
    """
    Builds email from base + selected domain.
    If m365_username already contains '@', use it as-is.
    """
    existing = (st.session_state.get("m365_username") or "").strip()
    if "@" in existing:
        return existing

    base = (st.session_state.get("m365_user_base") or "").strip()
    domain = (st.session_state.get("m365_domain") or "statom.co.uk").strip()
    if not base:
        return ""
    return f"{base}@{domain}"


# ---------- drawing helpers ----------
def _txt(c, x, y, text, size=9, bold=False, color=colors.black):
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.setFillColor(color)
    c.drawString(x, y, "" if text is None else str(text))
    c.setFillColor(colors.black)


def _center(c, x, y, w, text, size=9, bold=True):
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.setFillColor(colors.black)
    c.drawCentredString(x + w / 2, y, "" if text is None else str(text))


def _rect(c, x, y, w, h, fill=None, stroke=1):
    if fill is None:
        c.setFillColor(colors.white)
        c.rect(x, y, w, h, stroke=stroke, fill=0)
    else:
        c.setFillColor(fill)
        c.rect(x, y, w, h, stroke=stroke, fill=1)
    c.setFillColor(colors.black)


def _hline(c, x1, x2, y):
    c.line(x1, y, x2, y)


def _vline(c, x, y1, y2):
    c.line(x, y1, x, y2)


def _get_logo_path() -> str:
    # always use the filename chosen in the selectbox
    selected_logo = st.session_state.get("selected_logo", "")
    if not selected_logo:
        return ""

    # ui/pdf_export.py -> parents[1] should be your project root
    project_root = Path(__file__).resolve().parents[1]
    candidate = project_root / "assets" / "logos" / selected_logo
    return str(candidate) if candidate.exists() else ""


def _draw_logo(c, x, y, box_w, box_h):
    """
    Draw logo reliably from PNGs:
    PIL open -> convert to RGB -> save to BytesIO -> ImageReader(BytesIO)
    """
    logo_path = _get_logo_path()
    if not logo_path:
        return

    try:
        pil_img = Image.open(logo_path)
        if pil_img.mode in ("RGBA", "LA", "P"):
            pil_img = pil_img.convert("RGB")

        tmp = BytesIO()
        pil_img.save(tmp, format="PNG")
        tmp.seek(0)

        img = ImageReader(tmp)

        pad = 6
        draw_w = box_w - 2 * pad
        draw_h = box_h - 2 * pad

        c.drawImage(
            img,
            x + pad,
            y + pad,
            width=draw_w,
            height=draw_h,
            preserveAspectRatio=True,
            anchor="sw",
        )
    except Exception as e:
        _txt(c, x + 6, y + 6, f"Logo error: {e}", size=6, bold=False)


# ---------- Page 2: passwords ----------
def _draw_passwords_page(c, margin, form_w, PAGE_H):
    YELLOW = colors.HexColor("#f4b400")

    x0 = margin
    y_top = PAGE_H - margin

    # Header area: logo left + title right
    header_h = 58
    y = y_top - header_h
    _rect(c, x0, y, form_w, header_h, fill=None, stroke=1)

    logo_box_w = form_w * 0.42
    _vline(c, x0 + logo_box_w, y, y + header_h)

    _draw_logo(c, x0, y, logo_box_w, header_h)
    _txt(c, x0 + logo_box_w + 10, y + header_h - 22, "NEW STARTER PASSWORDS", size=12, bold=True)

    y -= 18

    full_name = (st.session_state.get("starter_full_name", "") or "").strip()
    role = (st.session_state.get("starter_role", "") or "").strip()
    instructions = (st.session_state.get("starter_instructions", "") or "").strip()

    _txt(c, x0, y, "New Starter Details", size=10, bold=True)
    y -= 14
    _txt(c, x0, y, f"{full_name} – {role}".strip(" –"), size=9)
    y -= 18

    # Instructions box
    box_h = 44
    _rect(c, x0, y - box_h + 10, form_w, box_h, fill=None, stroke=1)

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.black)

    # simple wrap (max 3 lines)
    lines = []
    words = instructions.split()
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        if c.stringWidth(test, "Helvetica", 9) > (form_w - 16):
            lines.append(line)
            line = w
        else:
            line = test
    if line:
        lines.append(line)

    ty = y - 8
    for ln in lines[:3]:
        c.drawString(x0 + 8, ty, ln)
        ty -= 12

    y = y - box_h - 10

    # Section header
    bar_h = 16
    _rect(c, x0, y, form_w, bar_h, fill=YELLOW, stroke=1)
    _center(c, x0, y + 4, form_w, "ACCOUNT DETAILS", size=9, bold=True)
    y -= (bar_h + 10)

    def kv_row(label, value):
        nonlocal y
        row_h = 18
        label_w = form_w * 0.35
        _rect(c, x0, y - row_h, form_w, row_h, fill=None, stroke=1)
        _vline(c, x0 + label_w, y - row_h, y)
        _txt(c, x0 + 6, y - row_h + 5, label, size=8, bold=True)
        _txt(c, x0 + label_w + 6, y - row_h + 5, value, size=8)
        y -= row_h

    # ---- Laptop login (instead of Domain) ----
    kv_row("Laptop login username:", st.session_state.get("laptop_username", ""))
    kv_row("Laptop login password:", st.session_state.get("laptop_password", ""))

    # ---- Microsoft 365 ----
    kv_row("Microsoft 365 URL:", "https://www.office.com/")
    kv_row("Microsoft 365 Username:", _get_m365_email())
    kv_row("Microsoft 365 Password:", st.session_state.get("m365_password", ""))

    if st.session_state.get("m365_2fa", False):
        y -= 10
        _txt(c, x0 + 2, y, "2 Factor Authentication setup required", size=9, bold=True)
        y -= 16

    y -= 10

    # Useful info
    _rect(c, x0, y, form_w, bar_h, fill=YELLOW, stroke=1)
    _center(c, x0, y + 4, form_w, "USEFUL INFO", size=9, bold=True)
    y -= (bar_h + 10)

    kv_row("SharePoint:", st.session_state.get("sharepoint_url", "https://statom.sharepoint.com"))
    kv_row("IT Support Helpdesk:", st.session_state.get("helpdesk_email", "helpdesk@statom.co.uk"))

    y -= 10

    # Extra accounts table
    _txt(c, x0, y, "Extra Accounts", size=10, bold=True)
    y -= 12

    th = 18
    _rect(c, x0, y - th, form_w, th, fill=None, stroke=1)

    col1 = form_w * 0.33
    col2 = form_w * 0.34
    col3 = form_w - (col1 + col2)
    x1 = x0 + col1
    x2 = x1 + col2

    _vline(c, x1, y - th, y)
    _vline(c, x2, y - th, y)

    _center(c, x0, y - th + 6, col1, "Software", size=8, bold=True)
    _center(c, x1, y - th + 6, col2, "Account", size=8, bold=True)
    _center(c, x2, y - th + 6, col3, "Password", size=8, bold=True)

    y -= th

    rows = st.session_state.get("extra_accounts", []) or []
    row_h = 18

    for r in rows:
        software = str((r or {}).get("Software", "")).strip()
        account = str((r or {}).get("Account", "")).strip()
        password = str((r or {}).get("Password", "")).strip()

        if not (software or account or password):
            continue

        if (y - row_h) < (margin + 20):
            break

        _rect(c, x0, y - row_h, form_w, row_h, fill=None, stroke=1)
        _vline(c, x1, y - row_h, y)
        _vline(c, x2, y - row_h, y)

        _txt(c, x0 + 5, y - row_h + 5, software, size=8)
        _txt(c, x1 + 5, y - row_h + 5, account, size=8)
        _txt(c, x2 + 5, y - row_h + 5, password, size=8)

        y -= row_h


# ---------- main PDF generator ----------
def build_equipment_issue_pdf() -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    PAGE_W, PAGE_H = A4
    margin = 36
    x0 = margin
    y_top = PAGE_H - margin
    form_w = PAGE_W - 2 * margin

    YELLOW = colors.HexColor("#f4b400")
    BLUE = colors.HexColor("#cfe2f3")

    # Outer border
    form_h = PAGE_H - 2 * margin
    _rect(c, x0, margin, form_w, form_h, fill=None, stroke=1)

    # --- Top meta row ---
    meta_h = 16
    y = y_top - meta_h
    _rect(c, x0, y, form_w, meta_h, fill=None, stroke=1)

    cols = [0.18, 0.34, 0.20, 0.28]
    xs = [x0]
    for frac in cols[:-1]:
        xs.append(xs[-1] + form_w * frac)
    xs.append(x0 + form_w)

    for x in xs[1:-1]:
        _vline(c, x, y, y + meta_h)

    _center(c, xs[0], y + 4, xs[1] - xs[0], "D5.HRS.016", size=7, bold=False)
    _center(c, xs[1], y + 4, xs[2] - xs[1], "Equipment Issue Form", size=7, bold=False)
    _center(c, xs[2], y + 4, xs[3] - xs[2], "Version 1.2", size=7, bold=False)
    _center(c, xs[3], y + 4, xs[4] - xs[3], "2021-10-12", size=7, bold=False)

    # --- Header area: logo left + title right ---
    header_h = 58
    y = y - header_h
    _rect(c, x0, y, form_w, header_h, fill=None, stroke=1)

    logo_box_w = form_w * 0.42
    _vline(c, x0 + logo_box_w, y, y + header_h)

    _draw_logo(c, x0, y, logo_box_w, header_h)
    _txt(c, x0 + logo_box_w + 10, y + header_h - 22, "EQUIPMENT ISSUE RECORD", size=12, bold=True)

    # --- Notices box ---
    notice_h = 70
    y = y - notice_h
    _rect(c, x0, y, form_w, notice_h, fill=None, stroke=1)

    notice1 = (
        "This form must be completed upon issue of equipment / technology / software which is provided to you. "
        "This form will be kept on your personnel file and used to monitor the condition and return of any equipment "
        "should you depart the company."
    )
    notice2 = (
        "Be aware that damages or loss of issued items which are not rectified will result in a proportionate and "
        "reasonable charge for repair or replacement which will be deducted from your final salary."
    )

    c.setFont("Helvetica", 7)
    c.drawString(x0 + 8, y + notice_h - 18, notice1[:120])
    c.drawString(x0 + 8, y + notice_h - 30, notice1[120:240])
    c.drawString(x0 + 8, y + notice_h - 42, notice1[240:360])
    c.drawString(x0 + 8, y + 18, notice2[:120])
    c.drawString(x0 + 8, y + 6, notice2[120:240])

    # --- Yellow section ---
    bar_h = 16
    y = y - bar_h
    _rect(c, x0, y, form_w, bar_h, fill=YELLOW, stroke=1)
    _center(c, x0, y + 4, form_w, "EQUIPMENT ISSUED TO: PERSONNEL DETAIL", size=8, bold=True)

    # --- Name/Date row ---
    row_h = 20
    y = y - row_h
    _rect(c, x0, y, form_w, row_h, fill=None, stroke=1)

    w1 = form_w * 0.18
    w2 = form_w * 0.42
    w3 = form_w * 0.12
    w4 = form_w - (w1 + w2 + w3)
    x1 = x0
    x2 = x1 + w1
    x3 = x2 + w2
    x4 = x3 + w3

    for xx in [x2, x3, x4]:
        _vline(c, xx, y, y + row_h)

    _txt(c, x1 + 6, y + 6, "NAME:", size=8, bold=True)
    _txt(c, x2 + 6, y + 6, st.session_state.get("name", ""), size=8)

    _txt(c, x3 + 6, y + 6, "DATE", size=8, bold=True)
    _txt(c, x4 + 6, y + 6, _fmt_date(st.session_state.get("date", "")), size=8)

    # --- Work location row ---
    y = y - row_h
    _rect(c, x0, y, form_w, row_h, fill=None, stroke=1)
    _vline(c, x2, y, y + row_h)

    _txt(c, x1 + 6, y + 6, "WORK LOCATION:", size=8, bold=True)
    _txt(c, x2 + 6, y + 6, st.session_state.get("work_location", ""), size=8)

    # --- Yellow section: EQUIPMENT ---
    y = y - bar_h
    _rect(c, x0, y, form_w, bar_h, fill=YELLOW, stroke=1)
    _center(c, x0, y + 4, form_w, "EQUIPMENT", size=8, bold=True)

    # --- Equipment table header ---
    table_header_h = 18
    y = y - table_header_h
    _rect(c, x0, y, form_w, table_header_h, fill=None, stroke=1)

    col_desc = form_w * 0.36
    col_cond = form_w * 0.28
    col_serial = form_w * 0.18
    col_asset = form_w - (col_desc + col_cond + col_serial)

    xd1 = x0 + col_desc
    xd2 = xd1 + col_cond
    xd3 = xd2 + col_serial

    for xx in [xd1, xd2, xd3]:
        _vline(c, xx, y, y + table_header_h)

    _center(c, x0, y + 6, col_desc, "DESCRIPTION", size=7, bold=True)
    _center(c, xd1, y + 6, col_cond, "CONDITION AT ISSUE", size=7, bold=True)
    _center(c, xd2, y + 6, col_serial, "SERIAL No", size=7, bold=True)
    _center(c, xd3, y + 6, col_asset, "ASSET No", size=7, bold=True)

    eq_rows = 10
    row_h = 18
    for i in range(eq_rows):
        y = y - row_h
        _rect(c, x0, y, form_w, row_h, fill=None, stroke=1)
        for xx in [xd1, xd2, xd3]:
            _vline(c, xx, y, y + row_h)

        desc = st.session_state.get(f"eq_desc_{i}", "")
        cond = st.session_state.get(f"eq_condition_{i}", "")
        serial = st.session_state.get(f"eq_serial_{i}", "")
        asset = st.session_state.get(f"eq_asset_{i}", "")

        _txt(c, x0 + 4, y + 5, desc, size=7)
        _txt(c, xd1 + 4, y + 5, cond, size=7)
        _txt(c, xd2 + 4, y + 5, serial, size=7)
        _txt(c, xd3 + 4, y + 5, asset, size=7)

    # --- Yellow section: ISSUE SIGNOFF ---
    y = y - bar_h
    _rect(c, x0, y, form_w, bar_h, fill=YELLOW, stroke=1)
    _center(c, x0, y + 4, form_w, "ISSUE SIGNOFF", size=8, bold=True)

    sign_h = 44
    y = y - sign_h
    _rect(c, x0, y, form_w, sign_h, fill=None, stroke=1)

    mid = x0 + form_w * 0.5
    _vline(c, mid, y, y + sign_h)

    left_label_w = (mid - x0) * 0.35
    right_label_w = (x0 + form_w - mid) * 0.35
    ll = x0 + left_label_w
    rl = mid + right_label_w

    _vline(c, ll, y, y + sign_h)
    _vline(c, rl, y, y + sign_h)
    _hline(c, x0, x0 + form_w, y + sign_h / 2)

    _txt(c, x0 + 6, y + sign_h - 14, "ISSUER NAME", size=7, bold=True)
    _txt(c, ll + 6, y + sign_h - 14, st.session_state.get("issuer_name", ""), size=7)

    _txt(c, mid + 6, y + sign_h - 14, "ISSUER SIGN", size=7, bold=True)

    _txt(c, x0 + 6, y + 8, "RECEIVER NAME", size=7, bold=True)
    _txt(c, ll + 6, y + 8, st.session_state.get("receiver_name", ""), size=7)

    _txt(c, mid + 6, y + 8, "RECEIVER SIGN", size=7, bold=True)

    # (RETURNS DETAIL date removed — the UI no longer captures a return date)

    # --- Blue section: RETURNED EQUIPMENT ---
    y = y - bar_h
    _rect(c, x0, y, form_w, bar_h, fill=BLUE, stroke=1)
    _center(c, x0, y + 4, form_w, "RETURNED EQUIPMENT", size=8, bold=True)

    table_header_h = 18
    y = y - table_header_h
    _rect(c, x0, y, form_w, table_header_h, fill=None, stroke=1)

    col_desc2 = form_w * 0.36
    col_cond2 = form_w * 0.30
    col_serial2 = form_w * 0.12
    col_no2 = form_w * 0.08
    col_asset2 = form_w - (col_desc2 + col_cond2 + col_serial2 + col_no2)

    xr1 = x0 + col_desc2
    xr2 = xr1 + col_cond2
    xr3 = xr2 + col_serial2
    xr4 = xr3 + col_no2

    for xx in [xr1, xr2, xr3, xr4]:
        _vline(c, xx, y, y + table_header_h)

    _center(c, x0, y + 6, col_desc2, "DESCRIPTION", size=7, bold=True)
    _center(c, xr1, y + 6, col_cond2, "RETURNED CONDITION", size=7, bold=True)
    _center(c, xr2, y + 6, col_serial2, "SERIAL", size=7, bold=True)
    _center(c, xr3, y + 6, col_no2, "No", size=7, bold=True)
    _center(c, xr4, y + 6, col_asset2, "ASSET No", size=7, bold=True)

    ret_rows = 8
    row_h = 18
    for i in range(ret_rows):
        y = y - row_h
        _rect(c, x0, y, form_w, row_h, fill=None, stroke=1)
        for xx in [xr1, xr2, xr3, xr4]:
            _vline(c, xx, y, y + row_h)

        desc = st.session_state.get(f"ret_desc_{i}", "")
        cond = st.session_state.get(f"ret_condition_{i}", "")
        serial = st.session_state.get(f"ret_serial_{i}", "")
        asset = st.session_state.get(f"ret_asset_{i}", "")

        _txt(c, x0 + 4, y + 5, desc, size=7)
        _txt(c, xr1 + 4, y + 5, cond, size=7)
        _txt(c, xr2 + 4, y + 5, serial, size=7)
        _txt(c, xr4 + 4, y + 5, asset, size=7)

    # --- Blue section: EQUIPMENT RETURN SIGNOFF ---
    y = y - bar_h
    _rect(c, x0, y, form_w, bar_h, fill=BLUE, stroke=1)
    _center(c, x0, y + 4, form_w, "EQUIPMENT RETURN SIGNOFF", size=8, bold=True)

    sign_h = 40
    y = y - sign_h
    _rect(c, x0, y, form_w, sign_h, fill=None, stroke=1)

    mid = x0 + form_w * 0.5
    _vline(c, mid, y, y + sign_h)

    left_label_w = (mid - x0) * 0.35
    right_label_w = (x0 + form_w - mid) * 0.35
    ll = x0 + left_label_w
    rl = mid + right_label_w

    _vline(c, ll, y, y + sign_h)
    _vline(c, rl, y, y + sign_h)
    _hline(c, x0, x0 + form_w, y + sign_h / 2)

    _txt(c, x0 + 6, y + sign_h - 14, "ISSUER NAME", size=7, bold=True)
    _txt(c, ll + 6, y + sign_h - 14, st.session_state.get("return_issuer", ""), size=7)

    _txt(c, mid + 6, y + sign_h - 14, "ISSUER SIGN", size=7, bold=True)

    _txt(c, x0 + 6, y + 6, "RECEIVER NAME", size=7, bold=True)
    _txt(c, ll + 6, y + 6, st.session_state.get("return_receiver", ""), size=7)

    _txt(c, mid + 6, y + 6, "RECEIVER SIGN", size=7, bold=True)

    footer_text = "Please attach photographs on attached pages of any recorded defect or condition."
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.red)
    c.drawCentredString(x0 + form_w / 2, margin + 10, footer_text)
    c.setFillColor(colors.black)

    # --- end page 1 ---
    c.showPage()

    # --- page 2 ---
    _draw_passwords_page(c, margin=margin, form_w=form_w, PAGE_H=PAGE_H)

    c.showPage()
    c.save()

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def save_form_as_pdf():
    pdf_bytes = build_equipment_issue_pdf()

    person_name = _safe_filename(st.session_state.get("name", ""))
    asset_no = _safe_filename(_first_asset_number())

    if asset_no:
        filename = f"{person_name} - {asset_no}.pdf"
    else:
        filename = f"{person_name}.pdf"

    st.download_button(
        label="Export PDF",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
    )
