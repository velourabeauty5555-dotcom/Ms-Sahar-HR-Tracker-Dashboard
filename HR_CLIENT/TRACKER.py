import streamlit as st
import pandas as pd
import sqlite3
import io
from datetime import date, timedelta
from pathlib import Path
from uuid import uuid4

# ---------------- DATABASE ----------------

conn = sqlite3.connect("hr_clients.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    company TEXT,
    email TEXT,
    cc_email TEXT,
    phone TEXT,
    position TEXT,
    contact_date TEXT,
    status TEXT,
    follow_up TEXT,
    notes TEXT
)
""")

# Add the CC field to databases created by earlier versions of the tracker.
columns = {
    row[1] for row in conn.execute("PRAGMA table_info(clients)")
}
if "cc_email" not in columns:
    conn.execute("ALTER TABLE clients ADD COLUMN cc_email TEXT")

conn.commit()
conn.execute("""
CREATE TABLE IF NOT EXISTS client_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    original_name TEXT NOT NULL,
    stored_name TEXT NOT NULL,
    uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients (id)
)
""")
conn.commit()

DOCUMENTS_DIR = Path("client_documents")
DOCUMENTS_DIR.mkdir(exist_ok=True)
# ---------------- SETTINGS ----------------

st.set_page_config(
    page_title="Ms Sahar - HR Tracker Dashboard",
    page_icon="🤝",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --ink:#1d322d; --muted:#71817a; --green:#16745d; --line:#e5ece7; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:linear-gradient(135deg,#f4f8f5 0%,#f7f8f4 55%,#eff6f2 100%); color:var(--ink); }
.block-container { max-width:1320px; padding-top:2.1rem; padding-bottom:3rem; }
header[data-testid="stHeader"] { background:transparent; }
h1,h2,h3 { font-family:'Manrope',sans-serif!important; color:var(--ink)!important; letter-spacing:-.035em; }
.hero { position:relative; overflow:hidden; padding:30px 34px; margin-bottom:22px; border-radius:22px; color:#fff; background:linear-gradient(115deg,#123c32,#176b56 62%,#24836b); box-shadow:0 14px 35px #164d3c22; }
.hero:after { content:' '; position:absolute; right:-30px; top:-100px; width:290px; height:290px; border:1px solid #ffffff22; border-radius:50%; box-shadow:0 0 0 32px #ffffff0c,0 0 0 68px #ffffff08; }
.hero-kicker { margin:0 0 8px; color:#bfe5d3; text-transform:uppercase; letter-spacing:.15em; font-size:.72rem; font-weight:700; }
.hero h1 { margin:0!important; color:white!important; font-size:clamp(2rem,4vw,2.8rem)!important; }
.hero p:last-child { margin:8px 0 0; color:#d5e9df; font-size:1rem; }
[data-testid="stMetric"] { padding:18px 20px; background:#fff; border:1px solid var(--line); border-radius:16px; box-shadow:0 5px 18px #1b42300a; }
[data-testid="stMetricLabel"] p { color:var(--muted); font-weight:600; }
[data-testid="stMetricValue"] { color:var(--green); font-family:'Manrope',sans-serif; }
[data-testid="stForm"] { padding:20px; background:#fff; border:1px solid var(--line); border-radius:16px; }
[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] { background:#f0f7f2!important; border:1px dashed #9fc9b3!important; border-radius:12px!important; }
[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] * { color:#264b3f!important; }
[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] button { background:#16745d!important; border:1px solid #16745d!important; border-radius:8px!important; }
[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] button, [data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] button * { color:#ffffff!important; }
[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] small { color:#71817a!important; }
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-testid="stDateInput"] input { border-radius:10px; }
[data-testid="stWidgetLabel"] *, [data-testid="stForm"] label { color:#264b3f!important; }
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-testid="stDateInput"] input, [data-baseweb="select"] input { background-color:#ffffff!important; color:#203b32!important; border-color:#c6dfd0!important; }
[data-baseweb="input"] > div, [data-baseweb="textarea"] > div, [data-baseweb="select"] > div { background-color:#ffffff!important; border-color:#c6dfd0!important; }
[data-testid="stTextInput"] input::placeholder, [data-testid="stTextArea"] textarea::placeholder { color:#73857b!important; opacity:1; }
.stButton button, [data-testid="stFormSubmitButton"] button, [data-testid="stDownloadButton"] button { border-radius:10px; font-weight:700; }
.stButton button[kind="primary"], [data-testid="stFormSubmitButton"] button { background:#16745d; border-color:#16745d; }
hr { border-color:var(--line); }
@media (max-width:700px) { .block-container{padding:1.2rem 1rem 2rem}.hero{padding:24px 22px;border-radius:17px} }
</style>
<div class="hero">
  <p class="hero-kicker">Created by Aamir</p>
  <h1>Ms Sahar - HR Tracker Dashboard</h1>
  <p>Keep every conversation, client, and follow-up moving forward.</p>
</div>
""", unsafe_allow_html=True)

today = date.today()
def style_table(frame):
    return frame.style.set_properties(**{
        "color": "#245b49",
        "background-color": "#fbfdfb",
        "border-color": "#e2eee7"
    }).set_table_styles([
        {"selector": "th", "props": [
            ("background-color", "#dcefe4"),
            ("color", "#176b56"),
            ("font-weight", "700"),
            ("border-color", "#c6dfd0")
        ]},
        {"selector": "tbody tr:nth-child(even) td", "props": [
            ("background-color", "#f0f7f2")
        ]}
    ])

# ---------------- LOAD DATA ----------------

def load_clients():
    return pd.read_sql_query(
        """
        SELECT id, name, company, email, cc_email, phone,
               position, contact_date, status, follow_up, notes
        FROM clients
        ORDER BY contact_date DESC
        """,
        conn
    )

df = load_clients()

# ---------------- DASHBOARD ----------------

total = len(df)

pending = len(
    df[df["status"] == "Waiting for Reply"]
)

replied = len(
    df[df["status"] == "Replied"]
)

if not df.empty:
    overdue = len(
        df[
            (df["follow_up"] < str(today))
            & (df["status"] != "Replied")
        ]
    )
else:
    overdue = 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Clients", total)
col2.metric("Waiting for Reply", pending)
col3.metric("Clients Replied", replied)
col4.metric("Overdue Follow-ups", overdue)

st.divider()

# ---------------- ADD CLIENT ----------------

st.subheader("➕ Add New Client")

with st.form("client_form"):

    name = st.text_input("Client Name")
    company = st.text_input("Company Name")

    email = st.text_input("Email Address")
    cc_email = st.text_input("CC Email Address (optional)")
    phone = st.text_input("Phone Number")

    position = st.text_input("Job Position")

    contact_date = st.date_input(
        "Date Contacted",
        value=today
    )

    status = st.selectbox(
        "Client Status",
        [
            "Waiting for Reply",
            "Replied",
            "Interested",
            "Not Interested",
            "Meeting Scheduled",
            "Closed"
        ]
    )

    follow_up = st.date_input(
        "Next Follow-up Date",
        value=today + timedelta(days=60)
    )

    notes = st.text_area(
        "Notes / Communication Details"
    )

    client_documents = st.file_uploader(
        "Attach PDF documents (optional)",
        type=["pdf"],
        accept_multiple_files=True,
        key="new_client_documents"
    )

    submitted = st.form_submit_button(
        "Save Client"
    )

    if submitted:

        if not name.strip():
            st.error("Please enter the client name.")

        elif any(not pdf_file.getvalue().startswith(b"%PDF-") for pdf_file in client_documents):
            st.error("One or more selected files are not valid PDFs. Please choose PDF files and try again.")

        else:

            client_cursor = conn.execute("""
                INSERT INTO clients (
                    name, company, email, cc_email, phone,
                    position, contact_date,
                    status, follow_up, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                company,
                email,
                cc_email,
                phone,
                position,
                str(contact_date),
                status,
                str(follow_up),
                notes
            ))

            client_id = client_cursor.lastrowid
            for pdf_file in client_documents:
                original_name = Path(pdf_file.name).name
                stored_name = f"{uuid4().hex}.pdf"
                (DOCUMENTS_DIR / stored_name).write_bytes(pdf_file.getvalue())
                conn.execute(
                    "INSERT INTO client_documents (client_id, original_name, stored_name) VALUES (?, ?, ?)",
                    (client_id, original_name, stored_name)
                )
            conn.commit()

            st.success("Client and documents saved successfully!" if client_documents else "Client saved successfully!")

            st.rerun()

# ---------------- IMPORT EXCEL ----------------

st.divider()
st.subheader("📤 Import Clients from Excel")
st.caption("Upload an .xlsx file with a name column. Existing client records will stay in place.")

uploaded_file = st.file_uploader(
    "Choose an Excel workbook",
    type=["xlsx"],
    help="Accepted columns: name, company, email, cc_email, phone, position, contact_date, status, follow_up, notes.",
    key="client_excel_upload"
)

if uploaded_file is not None:
    try:
        imported_df = pd.read_excel(uploaded_file)
    except Exception as exc:
        st.error(f"Could not read this workbook. Please check that it is a valid .xlsx file. Details: {exc}")
    else:
        aliases = {
            "name": "name", "client name": "name", "full name": "name",
            "company": "company", "company name": "company",
            "email": "email", "email address": "email",
            "cc email": "cc_email", "cc_email": "cc_email", "cc email address": "cc_email",
            "phone": "phone", "phone number": "phone",
            "position": "position", "job position": "position",
            "contact date": "contact_date", "contact_date": "contact_date", "date contacted": "contact_date",
            "status": "status", "client status": "status",
            "follow up": "follow_up", "follow-up": "follow_up", "follow_up": "follow_up", "next follow-up date": "follow_up",
            "notes": "notes", "notes / communication details": "notes"
        }
        rename_columns = {}
        for column in imported_df.columns:
            normalized = " ".join(str(column).strip().lower().replace("_", " ").split())
            target = aliases.get(normalized, aliases.get(str(column).strip().lower()))
            if target:
                rename_columns[column] = target

        imported_df = imported_df.rename(columns=rename_columns)
        imported_df = imported_df.loc[:, ~imported_df.columns.duplicated()]

        if "name" not in imported_df.columns:
            st.error("I couldn’t find a client name column. Add a column named name or Client Name, then upload again.")
        else:
            import_columns = [
                "name", "company", "email", "cc_email", "phone", "position",
                "contact_date", "status", "follow_up", "notes"
            ]
            for column in import_columns:
                if column not in imported_df.columns:
                    imported_df[column] = ""

            for column in ["contact_date", "follow_up"]:
                parsed_dates = pd.to_datetime(imported_df[column], errors="coerce")
                imported_df[column] = parsed_dates.dt.strftime("%Y-%m-%d").fillna("")

            for column in [c for c in import_columns if c not in ["contact_date", "follow_up"]]:
                imported_df[column] = imported_df[column].fillna("").astype(str).str.strip()

            imported_df = imported_df[import_columns]
            imported_df = imported_df[imported_df["name"].str.strip() != ""]
            imported_df = imported_df.drop_duplicates()

            if imported_df.empty:
                st.warning("No rows with a client name were found in this workbook.")
            else:
                st.write(f"Found **{len(imported_df)}** client record(s). Review the preview, then import.")
                st.dataframe(style_table(imported_df), width="stretch", hide_index=True)
                if st.button("Import client records", type="primary", key="import_excel_clients"):
                    existing_by_email = {
                        str(email).strip().casefold(): {"name": name or "", "phone": phone or ""}
                        for name, email, phone in conn.execute(
                            "SELECT name, email, phone FROM clients WHERE email IS NOT NULL AND email != ''"
                        )
                    }
                    rows_to_add = []
                    skipped_duplicates = []
                    for row in imported_df.itertuples(index=False, name=None):
                        values = list(row)
                        email_key = str(values[2]).strip().casefold()
                        if email_key and email_key in existing_by_email:
                            existing_client = existing_by_email[email_key]
                            skipped_duplicates.append({
                                "Uploaded Name": values[0],
                                "Uploaded Phone": values[4] or "-",
                                "Existing Client": existing_client["name"] or "-",
                                "Existing Phone": existing_client["phone"] or "-"
                            })
                            continue
                        if not values[7]:
                            values[7] = "Waiting for Reply"
                        rows_to_add.append(tuple(values))
                        if email_key:
                            existing_by_email[email_key] = {"name": values[0], "phone": values[4]}

                    if rows_to_add:
                        conn.executemany("""
                            INSERT INTO clients (
                                name, company, email, cc_email, phone, position,
                                contact_date, status, follow_up, notes
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, rows_to_add)
                        conn.commit()
                    st.success(f"Imported {len(rows_to_add)} client record(s). {len(skipped_duplicates)} duplicate email record(s) skipped.")
                    if skipped_duplicates:
                        st.caption("Phone numbers for skipped duplicate entries:")
                        duplicate_df = pd.DataFrame(skipped_duplicates)
                        st.dataframe(style_table(duplicate_df), width="stretch", hide_index=True)
# ---------------- SEARCH CLIENTS ----------------

st.divider()

st.subheader("🔎 Search Client")

search = st.text_input(
    "Search by client, company, email/CC, or phone"
)

df = load_clients()

if search:

    df = df[
        df.astype(str)
        .apply(
            lambda row: row.str.contains(
                search,
                case=False,
                na=False
            ).any(),
            axis=1
        )
    ]

st.dataframe(
    style_table(df),
    width="stretch",
    hide_index=True
)

# ---------------- CLIENT PDF DOCUMENTS ----------------

st.divider()
st.subheader("📄 Client Documents")
st.caption("Upload PDF files for a client. Files are saved in the client_documents folder beside the tracker database.")

all_clients = load_clients()
if all_clients.empty:
    st.info("Add a client before uploading documents.")
else:
    client_records = all_clients.to_dict("records")
    client_by_id = {int(client["id"]): client for client in client_records}
    selected_client_id = st.selectbox(
        "Choose a client",
        options=list(client_by_id),
        format_func=lambda client_id: (
            f"{client_by_id[client_id]['name']}"
            + (f" — {client_by_id[client_id]['company']}" if client_by_id[client_id]["company"] else "")
        ),
        key="document_client_id"
    )
    pdf_files = st.file_uploader(
        "Select PDF documents",
        type=["pdf"],
        accept_multiple_files=True,
        key=f"client_pdfs_{selected_client_id}"
    )
    if st.button("📤 Upload PDF", type="primary", key=f"save_client_pdfs_{selected_client_id}"):
        if not pdf_files:
            st.warning("Choose at least one PDF first.")
        else:
            saved_count = 0
            invalid_files = []
            for pdf_file in pdf_files:
                file_bytes = pdf_file.getvalue()
                if not file_bytes.startswith(b"%PDF-"):
                    invalid_files.append(Path(pdf_file.name).name)
                    continue
                original_name = Path(pdf_file.name).name
                stored_name = f"{uuid4().hex}.pdf"
                (DOCUMENTS_DIR / stored_name).write_bytes(file_bytes)
                conn.execute(
                    "INSERT INTO client_documents (client_id, original_name, stored_name) VALUES (?, ?, ?)",
                    (selected_client_id, original_name, stored_name)
                )
                saved_count += 1
            conn.commit()
            if saved_count:
                st.success(f"Saved {saved_count} PDF document(s) for {client_by_id[selected_client_id]['name']}.")
            if invalid_files:
                st.error("These files were not valid PDFs: " + ", ".join(invalid_files))

    documents = conn.execute(
        "SELECT id, original_name, stored_name, uploaded_at FROM client_documents WHERE client_id = ? ORDER BY uploaded_at DESC, id DESC",
        (selected_client_id,)
    ).fetchall()
    if documents:
        st.markdown("**Saved documents**")
        for document_id, original_name, stored_name, uploaded_at in documents:
            document_path = DOCUMENTS_DIR / stored_name
            if document_path.is_file():
                st.download_button(
                    label=f"Download {original_name}",
                    data=document_path.read_bytes(),
                    file_name=original_name,
                    mime="application/pdf",
                    key=f"download_client_document_{document_id}"
                )
                st.caption(f"Uploaded {uploaded_at}")
            else:
                st.warning(f"The saved file {original_name} could not be found in the client_documents folder.")
    else:
        st.caption("No PDF documents have been saved for this client yet.")
# ---------------- FOLLOW-UP REMINDERS ----------------

st.divider()

st.subheader("⏰ Follow-up Reminders")

if not df.empty:

    reminders = df[
        (df["follow_up"] <= str(today))
        & (~df["status"].isin(["Replied", "Closed"]))
    ]

    if not reminders.empty:

        st.warning(
            f"{len(reminders)} client(s) need follow-up."
        )

        st.dataframe(
            style_table(reminders[
                [
                    "name",
                    "company",
                    "phone",
                    "status",
                    "follow_up"
                ]
            ]),
            width="stretch",
            hide_index=True
        )

    else:

        st.success("No overdue follow-ups.")

# ---------------- PDF REPORT AND EXPORT ----------------

st.divider()

st.subheader("📊 Reports and Export")

df = load_clients()

if not df.empty:

    report_df = df.copy()
    document_rows = conn.execute("""
        SELECT d.client_id, c.name, c.company, d.original_name, d.uploaded_at
        FROM client_documents d
        JOIN clients c ON c.id = d.client_id
        ORDER BY c.name, d.uploaded_at DESC
    """).fetchall()
    documents_by_client = {}
    for client_id, client_name, company, file_name, uploaded_at in document_rows:
        documents_by_client.setdefault(client_id, []).append(file_name)

    def get_follow_up_status(row):
        if row["status"] in ["Replied", "Closed"]:
            return "Complete"
        if not row["follow_up"]:
            return "No date set"
        if row["follow_up"] < str(today):
            return "Overdue"
        if row["follow_up"] == str(today):
            return "Due today"
        return "Upcoming"

    report_df["Follow-up Status"] = report_df.apply(get_follow_up_status, axis=1)
    report_df["PDF Count"] = report_df["id"].map(
        lambda client_id: len(documents_by_client.get(client_id, []))
    )
    report_df["PDF Documents"] = report_df["id"].map(
        lambda client_id: ", ".join(documents_by_client.get(client_id, []))
    )
    follow_up_report = report_df[
        report_df["Follow-up Status"].isin(["Overdue", "Due today", "Upcoming"])
    ].copy()

    from html import escape
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

    report_buffer = io.BytesIO()
    page_width, page_height = landscape(A4)
    pdf_doc = SimpleDocTemplate(
        report_buffer,
        pagesize=landscape(A4),
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="HR Client Report"
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], textColor=colors.HexColor("#176b56"),
        fontName="Helvetica-Bold", fontSize=22, leading=27, alignment=0, spaceAfter=5
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle", parent=styles["Normal"], textColor=colors.HexColor("#60776d"),
        fontName="Helvetica", fontSize=9, leading=13, spaceAfter=14
    )
    section_style = ParagraphStyle(
        "ReportSection", parent=styles["Heading2"], textColor=colors.HexColor("#176b56"),
        fontName="Helvetica-Bold", fontSize=14, leading=18, spaceBefore=3, spaceAfter=9
    )
    cell_style = ParagraphStyle(
        "ReportCell", parent=styles["BodyText"], textColor=colors.HexColor("#243d34"),
        fontName="Helvetica", fontSize=7, leading=9, wordWrap="CJK"
    )
    header_style = ParagraphStyle(
        "ReportHeader", parent=cell_style, textColor=colors.white,
        fontName="Helvetica-Bold", fontSize=7, leading=9
    )

    def report_cell(value, style=cell_style):
        if value is None or pd.isna(value):
            value = ""
        return Paragraph(escape(str(value)).replace("\n", "<br/>"), style)

    def report_table(headers, rows, widths):
        table_data = [[report_cell(value, header_style) for value in headers]]
        table_data.extend([[report_cell(value) for value in row] for row in rows])
        table = Table(table_data, colWidths=widths, repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#176b56")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f7f2")]),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d7e7dd")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        return table

    story = [
        Paragraph("HR Client Report", title_style),
        Paragraph(f"Prepared {today.strftime('%d %B %Y')} - Client details, follow-ups, and linked PDF documents", subtitle_style),
        Paragraph("Overview", section_style)
    ]
    overdue_count = int((report_df["Follow-up Status"] == "Overdue").sum())
    due_today_count = int((report_df["Follow-up Status"] == "Due today").sum())
    overview_rows = [
        ["Total clients", len(report_df), "Overdue follow-ups", overdue_count],
        ["Due today", due_today_count, "Attached PDFs", len(document_rows)]
    ]
    overview_table = Table(overview_rows, colWidths=[125, 90, 145, 90], hAlign="LEFT")
    overview_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e5f2e9")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#e5f2e9")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#21483b")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d7e7dd")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.extend([overview_table, Spacer(1, 14), Paragraph("Client Details", section_style)])

    client_headers = ["Client", "Company", "Email", "CC Email", "Phone", "Position", "Status", "Contacted"]
    client_rows = report_df[["name", "company", "email", "cc_email", "phone", "position", "status", "contact_date"]].values.tolist()
    story.append(report_table(client_headers, client_rows, [80, 78, 112, 100, 75, 100, 85, 67]))

    story.extend([PageBreak(), Paragraph("Follow-ups and Documents", section_style)])
    follow_headers = ["Client", "Company", "Follow-up Date", "Status", "PDF Documents"]
    follow_rows = follow_up_report[["name", "company", "follow_up", "Follow-up Status", "PDF Documents"]].values.tolist()
    if follow_rows:
        story.append(report_table(follow_headers, follow_rows, [105, 105, 100, 100, 302]))
    else:
        story.append(Paragraph("No upcoming or overdue follow-ups.", subtitle_style))

    story.extend([PageBreak(), Paragraph("Client Notes", section_style)])
    notes_headers = ["Client", "Company", "Notes"]
    notes_rows = report_df[["name", "company", "notes"]].values.tolist()
    story.append(report_table(notes_headers, notes_rows, [100, 95, 545]))

    story.extend([Spacer(1, 16), Paragraph("Attached PDF Files", section_style)])
    document_headers = ["Client", "Company", "PDF File", "Uploaded At"]
    document_report_rows = [[row[1], row[2], row[3], row[4]] for row in document_rows]
    if document_report_rows:
        story.append(report_table(document_headers, document_report_rows, [135, 130, 300, 147]))
    else:
        story.append(Paragraph("No PDF documents have been attached yet.", subtitle_style))

    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#d7e7dd"))
        canvas.line(18 * mm, 13 * mm, page_width - 18 * mm, 13 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#60776d"))
        canvas.drawString(18 * mm, 8 * mm, "HR Client Tracker")
        canvas.drawRightString(page_width - 18 * mm, 8 * mm, f"Page {doc.page}")
        canvas.restoreState()

    pdf_doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    report_buffer.seek(0)
    st.download_button(
        label="📄 Download PDF Report",
        data=report_buffer.getvalue(),
        file_name="HR_Client_Report.pdf",
        mime="application/pdf"
    )

    csv_file = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Client Records CSV",
        data=csv_file,
        file_name="HR_Client_Records.csv",
        mime="text/csv"
    )
# ---------------- CLOSE DATABASE ----------------

conn.close()


















