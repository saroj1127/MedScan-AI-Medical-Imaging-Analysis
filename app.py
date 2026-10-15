import os
import re
from PIL import Image as PILImage
from google import genai
from google.genai import types
import streamlit as st
import requests
from datetime import datetime
import mysql.connector
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
st.set_page_config(
    page_title="AI Medical Imaging Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
# Google Login Check
if not st.user.is_logged_in:
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("""
        <div style='background:white; border-radius:16px; border:1px solid #e2e8f0; 
        padding:48px 40px; margin-top:60px; text-align:center; box-shadow:0 4px 24px rgba(0,0,0,0.08);'>
            <h2 style='font-size:26px; font-weight:700; color:#0f172a; margin:0 0 8px;'>MedScan AI</h2>
            <p style='font-size:14px; color:#64748b; margin:0 0 32px;'>AI-Assisted Medical Imaging Analysis System</p>
            <div style='border-top:1px solid #e2e8f0; margin-bottom:24px;'></div>
            <p style='font-size:13px; color:#64748b; margin-bottom:20px;'>Sign in to continue</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("G Sign in with Google", use_container_width=True, type="primary"):
            st.login("google")

    st.stop()
    
# API Key
GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY"  # Replace with your actual API key
client = genai.Client(api_key=GOOGLE_API_KEY)

# Custom CSS
st.markdown("""
<style>
 #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    header button {visibility: visible !important;}
    .stApp {
        background-color: #f0f4ff;
        font-size: 16px !important;
    }

    .block-container {
        max-width: 100% !important;
        padding: 2rem 2rem 2rem 2rem !important;
    }

    [data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid #e2e8f0;
    }

    [data-testid="stSidebar"] .block-container {
        padding: 1.5rem 1rem !important;
    }

    .sidebar-logo {
        background: #1d4ed8;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin-bottom: 20px;
    }

    .sidebar-logo-text {
        color: white;
        font-size: 15px;
        font-weight: 700;
        margin: 8px 0 0;
        letter-spacing: 0.5px;
    }

    .sidebar-logo-sub {
        color: rgba(255,255,255,0.7);
        font-size: 11px;
        margin: 2px 0 0;
    }

    .sidebar-section-title {
        font-size: 11px;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 16px 0 8px;
    }

    .scan-item {
        background: #f8faff;
        border: 1px solid #e0e8ff;
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .scan-name {
        font-size: 12px;
        color: #1e40af;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .scan-time {
        font-size: 10px;
        color: #94a3b8;
        margin: 1px 0 0;
    }

    .main-header {
        background: #1d4ed8;
        padding: 18px 28px;
        border-radius: 14px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .header-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .header-icon {
        background: rgba(255,255,255,0.2);
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }

    .header-title {
        color: white;
        font-size: 20px;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.3px;
    }

    .header-subtitle {
        color: rgba(255,255,255,0.7);
        font-size: 12px;
        margin: 2px 0 0;
    }

    .header-badge {
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 500;
    }

    .section-card-title {
        font-size: 13px;
        font-weight: 700;
        color: #1e40af;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 14px;
    }

    .stButton > button {
        background: #1d4ed8 !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        width: 100% !important;
        letter-spacing: 0.3px !important;
        transition: all 0.2s !important;
    }

    .stButton > button:hover {
        background: #1e40af !important;
        transform: translateY(-1px) !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: #e8f0fe;
        border-radius: 10px;
        padding: 5px;
        gap: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #3b82f6;
        font-size: 13px;
        font-weight: 600;
        padding: 8px 16px;
    }

    .stTabs [aria-selected="true"] {
        background: #1d4ed8 !important;
        color: white !important;
    }

    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 20px;
        min-height: 600px;
    }

    .report-header-box {
        background: #1d4ed8;
        border-radius: 12px;
        padding: 20px 28px;
        text-align: center;
        margin-bottom: 16px;
    }

    .report-hospital {
        color: white;
        font-size: 18px;
        font-weight: 700;
        letter-spacing: 1px;
        margin: 0;
    }

    .report-sub {
        color: rgba(255,255,255,0.75);
        font-size: 11px;
        margin: 4px 0 0;
    }

    .report-disclaimer {
        background: #fefce8;
        border: 1px solid #fde68a;
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 12px;
        color: #92400e;
        text-align: center;
        margin-top: 20px;
    }

    .ref-item {
        background: #f8faff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
        font-size: 13px;
    }

    .empty-state {
        background: white;
        border: 2px dashed #bfdbfe;
        border-radius: 14px;
        padding: 40px 20px;
        text-align: center;
    }

    .empty-state-icon {
        font-size: 40px;
        margin-bottom: 12px;
    }

    .empty-state-text {
        color: #3b82f6;
        font-size: 15px;
        font-weight: 500;
        margin: 0 0 6px;
    }

    .empty-state-sub {
        color: #93c5fd;
        font-size: 13px;
        margin: 0;
    }

    .chat-intro {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 10px;
        padding: 12px 16px;
        font-size: 13px;
        color: #1e40af;
        margin-bottom: 16px;
    }

    hr {
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 20px 0;
    }

    .preview-placeholder {
        background: #f1f5f9;
        border: 2px dashed #bfdbfe;
        border-radius: 10px;
        height: 220px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }

    /* Login page */
    .login-wrapper {
        display: grid;
        grid-template-columns: 1fr 1fr;
        min-height: 100vh;
        margin: -2rem;
    }

    .login-left {
        background: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: flex-start;
        padding: 60px;
    }

    .login-right {
        background: #1d4ed8;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 60px;
        position: relative;
        overflow: hidden;
    }

    .login-logo {
        width: 60px;
        height: 60px;
        background: #1d4ed8;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 24px;
        font-size: 30px;
    }

    .login-title {
        font-size: 28px;
        font-weight: 700;
        color: #0f172a;
        margin: 0 0 8px;
    }

    .login-subtitle {
        font-size: 14px;
        color: #64748b;
        margin: 0 0 36px;
    }

    .login-divider {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 20px 0;
        width: 100%;
    }

    .login-divider hr {
        flex: 1;
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 0;
    }

    .login-divider span {
        color: #94a3b8;
        font-size: 12px;
    }

    .feature-item {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
        color: white;
    }

    .feature-icon {
        width: 40px;
        height: 40px;
        background: rgba(255,255,255,0.15);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        flex-shrink: 0;
    }

    .feature-text h4 {
        margin: 0 0 2px;
        font-size: 14px;
        font-weight: 600;
        color: white;
    }

    .feature-text p {
        margin: 0;
        font-size: 12px;
        color: rgba(255,255,255,0.7);
    }

    .login-badge {
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        margin-bottom: 32px;
        display: inline-block;
    }
        section[data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
    }
</style>
""", unsafe_allow_html=True)

# Prompt
query = """
You are an AI assistant generating a structured medical imaging analysis report for academic evaluation purposes only. This is not a clinical diagnostic tool. Report findings with appropriate uncertainty, avoid definitive diagnoses, and recommend qualified human review for all outputs. Do not claim clinical authority or professional medical expertise. 
Analyse the provided medical image and generate a formal structured radiology report.
You MUST follow this EXACT structure with these EXACT section headings every single time.
Do NOT use asterisks (*) or markdown formatting in your response.
Use plain professional clinical language only.

IMAGE MODALITY:
State the exact imaging modality (X-ray, MRI, CT scan, or Ultrasound) and the anatomical region imaged (e.g. chest, brain, abdomen).

TECHNIQUE:
Describe the imaging technique used, including projection or sequence type, and any relevant technical parameters observed from the image.

FINDINGS:
Provide a detailed and systematic assessment of all visible anatomical structures. Use clear subheadings for each structure examined such as Lungs, Heart, Bones, Brain, etc. State findings clearly and precisely using professional radiological terminology. If a structure appears normal state this explicitly. Do not use bullet points or asterisks.

IMPRESSION:
Provide a numbered list of diagnostic conclusions ranked by clinical significance. State the primary diagnosis first with a confidence level. List any differential diagnoses. Highlight any urgent or critical findings immediately.

PATIENT-FRIENDLY SUMMARY:
Write 3 to 4 sentences in simple plain English that a non-medical person can understand. Explain what was found, whether it is normal or abnormal, and what it generally means. Avoid all medical jargon. Be accurate but reassuring where appropriate.

RECOMMENDATIONS:
Provide specific and actionable clinical recommendations. State exactly what the next steps should be such as follow-up imaging required, specialist referral needed, urgent clinical review required, or routine follow-up. Do not write vague statements like clinical correlation advised only. If the image appears completely normal, state that no follow-up is needed.

IMPORTANT DISCLAIMER:
This report has been generated by an AI-assisted prototype system for academic and educational purposes only. It is not a substitute for interpretation by a qualified radiologist or licensed medical professional. Clinical decisions must not be made based solely on this report.
"""
# PDF Generation
def generate_pdf(report_text, refs):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    elements = []

    # Styles
    institution_style = ParagraphStyle(
        'Institution',
        parent=styles['Normal'],
        fontSize=14,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1e293b'),
        alignment=TA_CENTER,
        spaceAfter=4,
        leading=20
    )

    sub_style = ParagraphStyle(
        'Sub',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica',
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        spaceAfter=2,
        leading=14
    )

    date_style = ParagraphStyle(
        'Date',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica',
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        spaceBefore=6,
        spaceAfter=6,
        leading=14
    )

    report_title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1e293b'),
        alignment=TA_CENTER,
        spaceBefore=8,
        spaceAfter=8,
        leading=18
    )

    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=14,
        spaceAfter=4,
        leading=16
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=4,
        leading=16,
        leftIndent=10
    )

    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=8,
        fontName='Helvetica-Oblique',
        textColor=colors.HexColor('#64748b'),
        alignment=TA_CENTER,
        spaceBefore=10,
        spaceAfter=6,
        leading=13
    )

    # Institution Header
    elements.append(Paragraph("AI MEDICAL IMAGING ANALYSIS SYSTEM", institution_style))
    elements.append(Paragraph("BBIS 7502 Applied Project | ICL Graduate Business School, Auckland, New Zealand", sub_style))
    elements.append(Paragraph("Powered by Google Gemini 2.5 Flash | PubMed Reference Integration", sub_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e293b')))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph("RADIOLOGY REPORT", report_title_style))
    elements.append(Paragraph(f"Date Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}", date_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94a3b8')))
    elements.append(Spacer(1, 0.3*cm))

    # Sections
    section_names = [
        "IMAGE MODALITY",
        "TECHNIQUE",
        "FINDINGS",
        "IMPRESSION",
        "PATIENT-FRIENDLY SUMMARY",
        "RECOMMENDATIONS",
        "IMPORTANT DISCLAIMER"
    ]

    for i, section_name in enumerate(section_names):
        next_sections = section_names[i+1:]
        if next_sections:
            pattern = rf"{section_name}[:\s]+(.*?)(?={'|'.join(next_sections)})"
        else:
            pattern = rf"{section_name}[:\s]+(.*?)$"

        match = re.search(pattern, report_text, re.DOTALL | re.IGNORECASE)

        if match:
            content = match.group(1).strip()
            content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)

            if section_name == "IMPORTANT DISCLAIMER":
                elements.append(Spacer(1, 0.3*cm))
                elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94a3b8')))
                elements.append(Paragraph(f"DISCLAIMER: {content}", disclaimer_style))
            else:
                elements.append(Paragraph(section_name, section_title_style))
                elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94a3b8')))
                elements.append(Spacer(1, 0.2*cm))
                for line in content.split('\n'):
                    line = line.strip()
                    if line:
                        elements.append(Paragraph(line, body_style))

    # References
    elements.append(Spacer(1, 0.5*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94a3b8')))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph("RELATED RESEARCH REFERENCES", section_title_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94a3b8')))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph("Retrieved from PubMed — US National Library of Medicine", body_style))
    elements.append(Spacer(1, 0.2*cm))
    for i, ref in enumerate(refs, 1):
        elements.append(Paragraph(f"[{i}] {ref}", body_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_DB_PASSWORD",  # Replace with your actual database password
        database="YOUR_DB_NAME"  # Replace with your actual database name
    )

def get_or_create_user(google_id, email, name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE google_id = %s", (google_id,))
        user = cursor.fetchone()
        if not user:
            cursor.execute("""
                INSERT INTO users (google_id, email, name)
                VALUES (%s, %s, %s)
            """, (google_id, email, name))
            conn.commit()
            user_id = cursor.lastrowid
        else:
            user_id = user[0]
        cursor.close()
        conn.close()
        return user_id
    except Exception as e:
        st.error(f"User error: {e}")
        return None

def save_analysis(user_id, image_name, image_modality, full_report, is_urgent):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO analysis_history
            (user_id, image_name, image_modality, full_report, is_urgent)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, image_name, image_modality, full_report, is_urgent))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        st.error(f"Database error: {e}")

def get_analysis_history(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, image_name, image_modality, is_urgent, analysed_at
            FROM analysis_history
            WHERE user_id = %s
            ORDER BY analysed_at DESC
            LIMIT 10
        """, (user_id,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        return []

def get_analysis_by_id(analysis_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT full_report, image_name, image_modality, is_urgent, analysed_at
            FROM analysis_history
            WHERE id = %s
        """, (analysis_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        return None
    
# PubMed
def search_pubmed(query_term):
    try:
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {"db": "pubmed", "term": query_term, "retmax": 3, "retmode": "json"}
        response = requests.get(url, params=params)
        data = response.json()
        ids = data["esearchresult"]["idlist"]
        return [f"https://pubmed.ncbi.nlm.nih.gov/{i}/" for i in ids]
    except:
        return ["PubMed search unavailable at this time."]

# Analyze
def analyze_medical_image(image_path):
    try:
        image = PILImage.open(image_path)
        width, height = image.size
        aspect_ratio = width / height
        new_width = 500
        new_height = int(new_width / aspect_ratio)
        resized_image = image.resize((new_width, new_height))
        temp_path = "temp_resized_image.png"
        resized_image.save(temp_path)

        with open(temp_path, "rb") as f:
            image_bytes = f.read()

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                types.Part.from_text(text=query)
            ]
        )
        os.remove(temp_path)
        return response.text
    except Exception as e:
        if os.path.exists("temp_resized_image.png"):
            os.remove("temp_resized_image.png")
        return f"Analysis error: {e}"

# Get or create user in database
user_id = get_or_create_user(
    st.user.sub,
    st.user.email,
    st.user.name
)
# Session state
if "report" not in st.session_state:
    st.session_state.report = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "recent_scans" not in st.session_state:
    st.session_state.recent_scans = []

# Sidebar
with st.sidebar:
    st.write("")  # Force sidebar to render
    st.image("logo.png", width=100)
    st.markdown("""
    <p class='sidebar-logo-text' style='text-align:center; color:white; font-weight:700; margin-top:8px;'>MedScan AI</p>
    <p class='sidebar-logo-sub' style='text-align:center; color:rgba(255,255,255,0.7); font-size:11px;'>Academic Prototype</p>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section-title'>Recent Scans</div>", unsafe_allow_html=True)

    history = get_analysis_history(user_id)
    if history:
        for record in history:
            record_id, img_name, modality, urgent, analysed_at = record
            urgent_icon = "" if urgent else "📄"
            raw_modality = modality if modality and modality != "Unknown" else "Unknown Scan"
            short_modality = raw_modality.split(",")[0].split("(")[0].strip()[:35]
            if st.button(f"{urgent_icon} {short_modality}\n🕐 {analysed_at.strftime('%d %b %Y, %I:%M %p')}", 
                        key=f"load_{record_id}",
                        use_container_width=True):
                result = get_analysis_by_id(record_id)
                if result:
                    full_report, img_name, img_modality, is_urgent, analysed_at = result
                    st.session_state.report = full_report
                    st.session_state.chat_messages = []
                    st.rerun()
    else:
        st.markdown("""
        <div style='background:#f8faff; border:1px dashed #bfdbfe; border-radius:8px;
        padding:16px; text-align:center;'>
            <p style='color:#93c5fd; font-size:12px; margin:0;'>No scans yet</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#fef9c3; border:1px solid #fde68a; border-radius:8px;
    padding:10px 12px; font-size:11px; color:#92400e;'>
        ⚠️ For academic use only. Not intended for clinical diagnosis.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background:#f8faff; border:1px solid #e0e8ff;
    border-radius:8px; padding:10px 12px; font-size:12px; color:#1e40af;'>
        👤 {st.user.name}<br>
        <span style='color:#94a3b8; font-size:10px;'>{st.user.email}</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        st.logout()

# Header
st.markdown("""
<div class='main-header'>
    <div class='header-left'>
        <div class='header-icon'>🩻</div>
        <div>
            <p class='header-title'>AI Medical Imaging Analysis Prototype</p>
            <p class='header-subtitle'>BBIS 7502 Applied Project — ICL Graduate Business School</p>
        </div>
    </div>
    <span class='header-badge'>⚠️ Academic Prototype — Not for Clinical Use</span>
</div>
""", unsafe_allow_html=True)

# Upload and preview
col1, col2 = st.columns([1, 1], gap="small")

with col1:
    st.markdown("<div class='section-card-title'>📤 Upload Medical Image</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drag and drop or browse",
        type=["jpg", "jpeg", "png", "bmp"],
        label_visibility="collapsed"
    )
    st.markdown("<br>", unsafe_allow_html=True)
    analyse_btn = st.button("🔬 Analyse Image")

with col2:
    st.markdown("<div class='section-card-title'>🖼️ Image Preview</div>", unsafe_allow_html=True)
    if uploaded_file:
        st.image(uploaded_file, width=400)
    else:
        st.markdown("""
        <div class='preview-placeholder'>
            <span style='font-size:36px;'>🩻</span>
            <p style='color:#93c5fd; font-size:13px; margin:0;'>Image preview will appear here</p>
            <p style='color:#bfdbfe; font-size:11px; margin:0;'>JPG, JPEG, PNG, BMP supported</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Analyse
if uploaded_file and analyse_btn:
    with st.spinner("🔬 Generating radiology report... Please wait."):
        image_path = f"temp_image.{uploaded_file.type.split('/')[1]}"
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        report = analyze_medical_image(image_path)
        st.session_state.report = report
        st.session_state.chat_messages = []

        scan_entry = {
            "name": uploaded_file.name,
            "time": datetime.now().strftime("%d %b %Y, %I:%M %p")
        }

        if not any(s["name"] == uploaded_file.name for s in st.session_state.recent_scans):
            st.session_state.recent_scans.append(scan_entry)

        if os.path.exists(image_path):
            os.remove(image_path)
            # Extract modality from report
        modality_match = re.search(r'IMAGE MODALITY[:\s]+(.*?)(?=TECHNIQUE)', 
                                    report, re.DOTALL | re.IGNORECASE)
        image_modality = modality_match.group(1).strip()[:100] if modality_match else "Unknown"

        # Save to database
        urgent_keywords = [
            "urgent", "critical", "immediate attention",
            "malignant", "cancer", "hemorrhage", "haemorrhage",
            "stroke", "infarct", "rupture", "emergency",
            "life threatening", "immediately", "urgent referral",
            "urgent review", "urgent clinical"
        ]
        is_urgent = any(word in report.lower() for word in urgent_keywords)
        save_analysis(user_id, uploaded_file.name, image_modality, report, is_urgent)

# Results
if st.session_state.report:
    st.markdown("### 📋 Analysis Report")

    tab1, tab2, tab3 = st.tabs(["📄 Radiology Report", "📚 References", "💬 Chat"])

    with tab1:
        st.markdown("""
        <div class='report-header-box'>
            <p class='report-hospital'>AI MEDICAL IMAGING ANALYSIS SYSTEM</p>
            <p class='report-sub'>BBIS 7502 Applied Project | ICL Graduate Business School, Auckland NZ</p>
            <p class='report-sub'>Powered by Google Gemini 2.5 Flash | PubMed Reference Integration</p>
        </div>
        """, unsafe_allow_html=True)
        # Urgent findings alert
        urgent_keywords = [
            "urgent", "critical", "immediate attention",
            "malignant", "cancer", "hemorrhage", "haemorrhage",
            "stroke", "infarct", "rupture", "emergency",
            "life threatening", "immediately", "urgent referral",
            "urgent review", "urgent clinical"
        ]
        text_lower = st.session_state.report.lower()
        is_urgent = any(word in text_lower for word in urgent_keywords)

        if is_urgent:
            st.markdown("""
            <div style='background:#fef2f2; border:2px solid #ef4444;
            border-radius:12px; padding:16px 20px; margin-bottom:16px;'>
                <p style='color:#b91c1c; font-size:16px; font-weight:700; margin:0 0 6px;'>
                    🚨 URGENT FINDINGS DETECTED
                </p>
                <p style='color:#991b1b; font-size:13px; margin:0;'>
                    This analysis contains findings that may require immediate clinical attention.
                    Please consult a qualified radiologist or medical professional as soon as possible.
                    Do not rely solely on this AI-generated report for clinical decisions.
                </p>
            </div>
            """, unsafe_allow_html=True)
        refs = search_pubmed("medical imaging AI diagnosis radiology deep learning")
        pdf_buffer = generate_pdf(st.session_state.report, refs)
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_buffer,
            file_name=f"radiology_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )
        st.markdown("<br>", unsafe_allow_html=True)
        
        report_text = st.session_state.report
        

        sections = {
           "IMAGE MODALITY": {"icon": "🏥", "color": "#1d4ed8", "bg": "#eff6ff", "border": "#bfdbfe"},
            "TECHNIQUE": {"icon": "⚙️", "color": "#0369a1", "bg": "#f0f9ff", "border": "#bae6fd"},
            "FINDINGS": {"icon": "🔬", "color": "#065f46", "bg": "#f0fdf4", "border": "#bbf7d0"},
            "IMPRESSION": {"icon": "📋", "color": "#7c3aed", "bg": "#f5f3ff", "border": "#ddd6fe"},
            "PATIENT-FRIENDLY SUMMARY": {"icon": "👤", "color": "#b45309", "bg": "#fffbeb", "border": "#fde68a"},
            "RECOMMENDATIONS": {"icon": "💡", "color": "#0f766e", "bg": "#f0fdfa", "border": "#99f6e4"},
            "IMPORTANT DISCLAIMER": {"icon": "⚠️", "color": "#b91c1c", "bg": "#fef2f2", "border": "#fecaca"},
        }

        section_names = list(sections.keys())

        for i, section_name in enumerate(section_names):
            next_sections = section_names[i+1:]
            if next_sections:
                pattern = rf"{section_name}[:\s]+(.*?)(?={'|'.join(next_sections)})"
            else:
                pattern = rf"{section_name}[:\s]+(.*?)$"

            match = re.search(pattern, report_text, re.DOTALL | re.IGNORECASE)

            if match:
                content = match.group(1).strip()
                content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
                content = re.sub(r'\*(.*?)\*', r'<i>\1</i>', content)
                meta = sections[section_name]

                if section_name == "IMPORTANT DISCLAIMER":
                    st.markdown(f"""
                    <div style='background:{meta["bg"]}; border:1px solid {meta["border"]};
                    border-radius:10px; padding:14px 18px; margin-top:8px;
                    text-align:center; font-size:12px; color:{meta["color"]};'>
                        {meta["icon"]} <strong>DISCLAIMER:</strong> {content}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='background:{meta["bg"]}; border:1px solid {meta["border"]};
                    border-radius:12px; padding:18px 22px; margin-bottom:12px;'>
                        <div style='display:flex; align-items:center; gap:8px;
                        margin-bottom:10px; border-bottom:1px solid {meta["border"]};
                        padding-bottom:10px;'>
                            <span style='font-size:20px;'>{meta["icon"]}</span>
                            <span style='font-size:13px; font-weight:700; color:{meta["color"]};
                            text-transform:uppercase; letter-spacing:0.08em; font-size:15px;'>{section_name}</span>
                        </div>
                        <div style='font-size:16px; color:#1e293b; line-height:1.9;'>
                            {content.replace(chr(10), "<br>")}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    with tab2:
        st.markdown("##### 📚 Related Peer-Reviewed Research")
        st.markdown("""
        <p style='font-size:13px; color:#64748b; margin-bottom:16px;'>
        The following references were retrieved from PubMed — US National Library of Medicine.
        These are peer-reviewed academic sources related to AI-assisted medical imaging analysis.
        </p>
        """, unsafe_allow_html=True)

        refs = search_pubmed("medical imaging AI diagnosis radiology deep learning")
        for i, ref in enumerate(refs, 1):
            st.markdown(f"""
            <div class='ref-item'>
                <span style='color:#1d4ed8; font-weight:600;'>[{i}]</span>
                <a href='{ref}' target='_blank' style='color:#2563eb; margin-left:8px;'>{ref}</a>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.markdown("""
        <div class='chat-intro'>
            💬 <strong>Follow-up Chat</strong> — Ask questions about your analysis report.
            The assistant has full context of the analysis and will answer clearly and professionally.
        </div>
        """, unsafe_allow_html=True)

        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if prompt := st.chat_input("Ask a question about the results..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    context = (
                        f"You are a medical imaging assistant helping a user understand their radiology report.\n"
                        f"Here is the full analysis report:\n\n"
                        f"{st.session_state.report}\n\n"
                        f"Answer the following question in simple, clear language that a non-medical person can understand. "
                        f"Be specific and refer directly to the findings in the report above.\n\n"
                        f"Question: {prompt}"
                    )
                    chat_response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[types.Part.from_text(text=context)]
                    )
                    reply = chat_response.text
                    st.write(reply)
                    st.session_state.chat_messages.append({"role": "assistant", "content": reply})

else:
    st.markdown("""
    <div class='empty-state'>
        <div class='empty-state-icon'>🩻</div>
        <p class='empty-state-text'>Ready to analyse your medical image</p>
        <p class='empty-state-sub'>Upload an X-ray, MRI, CT scan, or Ultrasound image and click Analyse Image to begin</p>
    </div>
    """, unsafe_allow_html=True)