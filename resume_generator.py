import streamlit as st
from fpdf import FPDF
import fitz  # PyMuPDF
import tempfile
import base64
import streamlit.components.v1 as components
import language_tool_python

# Constants
THEME_COLORS = {
    "Professional": (0, 0, 0),
    "Creative": (0, 102, 204),
    "Funny": (153, 0, 153)
}
TEMPLATES = ["Classic", "Minimalist", "Modern"]
STANDARD_FONTS = ["Arial", "Courier", "Times"]

# PDF class
class PDF(FPDF):
    def header(self):
        if self.title:
            self.set_font(self.font_choice, 'B', 16)
            self.set_text_color(*self.theme_color)
            self.cell(0, 10, self.title, ln=True, align='C')
            self.ln(5)

# PDF Generator
def make_pdf(data, font_choice, theme_type, template, custom_sections, profile_pic):
    pdf = PDF()
    pdf.font_choice = font_choice if font_choice in STANDARD_FONTS else "Arial"
    pdf.theme_color = THEME_COLORS.get(theme_type, (0, 0, 0))
    pdf.title = data["name"]
    pdf.add_page()

    if profile_pic:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmpfile:
            tmpfile.write(profile_pic.read())
            tmpfile.flush()
            pdf.image(tmpfile.name, x=170, y=8, w=25, h=25)

    pdf.set_font(pdf.font_choice, '', 12)
    pdf.set_text_color(0, 0, 0)

    def section(title, content):
        pdf.set_font(pdf.font_choice, 'B', 13)
        pdf.set_text_color(*pdf.theme_color)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font(pdf.font_choice, '', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 10, content)
        pdf.ln(3)

    pdf.ln(30)
    pdf.set_font(pdf.font_choice, '', 11)
    pdf.cell(0, 10, f"Email: {data['email']} | Phone: {data['phone']}", ln=1)
    if data['linkedin']:
        pdf.cell(0, 10, f"LinkedIn: {data['linkedin']}", ln=1)
    if data['github']:
        pdf.cell(0, 10, f"GitHub: {data['github']}", ln=1)
    if data['address']:
        pdf.multi_cell(0, 10, f"Address: {data['address']}")
        pdf.ln(3)

    for key in ["summary", "education", "experience", "projects", "certifications", "skills", "languages", "hobbies"]:
        if data.get(key):
            section(key.upper().replace("_", " "), data[key])

    for title, content in custom_sections:
        section(title.upper(), content)

    return pdf

# ✅ IMPROVED Resume Rating Function
def rate_resume(text, purpose):
    keyword_db = {
        "internship": {
            "must_have": ["internship", "project", "learning", "teamwork", "academic", "c++", "java", "python"],
            "optional": ["problem-solving", "volunteer", "coursework", "btech", "gpa"]
        },
        "job": {
            "must_have": ["experience", "developed", "achieved", "managed", "python", "sql", "lead", "team"],
            "optional": ["results", "deployed", "impact", "client", "communication", "soft skills"]
        },
        "higher studies": {
            "must_have": ["research", "paper", "cgpa", "publication", "conference", "internship", "academic"],
            "optional": ["abstract", "IEEE", "technical", "scholarship", "GRE", "TOEFL"]
        }
    }

    purpose = purpose.lower()
    selected = "internship" if "intern" in purpose else "job" if "job" in purpose else "higher studies"
    keywords = keyword_db[selected]

    found_must = [kw for kw in keywords["must_have"] if kw.lower() in text.lower()]
    found_opt = [kw for kw in keywords["optional"] if kw.lower() in text.lower()]
    missing = [kw for kw in keywords["must_have"] if kw.lower() not in text.lower()]

    score = round((len(found_must) / len(keywords["must_have"])) * 7 + (len(found_opt) / max(len(keywords["optional"]), 1)) * 3, 2)
    score = min(score, 10.0)

    if score >= 8:
        status = "🟢 Excellent"
    elif score >= 5:
        status = "🟡 Good"
    else:
        status = "🔴 Needs Improvement"

    feedback = f"""
### 🎯 Resume Purpose: `{purpose.title()}`
**📊 Resume Score:** **{score}/10** — {status}

**✅ Must-Have Keywords Found:** {', '.join(found_must) if found_must else 'None'}
**➕ Optional Keywords Found:** {', '.join(found_opt) if found_opt else 'None'}
**❗ Missing Must-Haves:** {', '.join(missing) if missing else 'None'}

---

**💡 Suggestions:**
- Add missing keywords like: `{', '.join(missing[:3]) if missing else 'N/A'}`
- Use strong action verbs: `developed`, `led`, `researched`, `designed`
- Tailor your resume content to reflect your `{purpose.title()}` objective
"""
    return feedback

# Grammar Check
def ai_resume_feedback(text):
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    return f"📝 **Grammar Issues Detected:** {len(matches)}"

# Main UI
st.set_page_config(page_title="Smart Resume", layout="centered")
st.title("📄 Smart Resume Toolkit")

choice = st.radio("Choose an option", ["Resume Generator", "Rate Resume"])

if choice == "Resume Generator":
    with st.form("resume_form"):
        st.subheader("👤 Personal Details")
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        address = st.text_area("Address")
        linkedin = st.text_input("LinkedIn")
        github = st.text_input("GitHub")
        profile_pic = st.file_uploader("Upload Profile Photo", type=["jpg", "png"])

        st.subheader("📚 Resume Content")
        summary = st.text_area("Professional Summary")
        education = st.text_area("Education")
        experience = st.text_area("Experience")
        projects = st.text_area("Projects")
        certifications = st.text_area("Certifications")
        skills = st.text_area("Skills")
        languages = st.text_area("Languages")
        hobbies = st.text_area("Hobbies")

        st.subheader("➕ Custom Sections")
        custom_sections = []
        num_sections = st.number_input("Number of custom sections", 0, 5, 0)
        for i in range(num_sections):
            sec_title = st.text_input(f"Section {i+1} Title", key=f"title{i}")
            sec_content = st.text_area(f"Section {i+1} Content", key=f"content{i}")
            if sec_title and sec_content:
                custom_sections.append((sec_title, sec_content))

        st.subheader("🎨 Customization")
        font_choice = st.selectbox("Font", STANDARD_FONTS)
        theme = st.selectbox("Theme", list(THEME_COLORS.keys()))
        template = st.selectbox("Template", TEMPLATES)

        submitted = st.form_submit_button("📄 Generate Resume")

    if submitted:
        if not name or not email or not phone:
            st.error("❗ Name, Email, and Phone are mandatory.")
        else:
            data = {
                "name": name, "email": email, "phone": phone,
                "address": address, "linkedin": linkedin, "github": github,
                "summary": summary, "education": education, "experience": experience,
                "projects": projects, "certifications": certifications, "skills": skills,
                "languages": languages, "hobbies": hobbies
            }
            pdf = make_pdf(data, font_choice, theme, template, custom_sections, profile_pic)
            pdf_bytes = pdf.output(dest="S").encode("latin1")

            st.success("✅ Resume Generated!")

            st.download_button("⬇ Download PDF", data=pdf_bytes, file_name=f"{name.replace(' ', '_')}_Resume.pdf", mime="application/pdf")

            b64 = base64.b64encode(pdf_bytes).decode()
            preview_html = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="600"></iframe>'
            st.markdown("### 🔍 Resume Preview")
            components.html(preview_html, height=600)

elif choice == "Rate Resume":
    st.subheader("📤 Upload Your Resume PDF")
    uploaded = st.file_uploader("Upload PDF", type="pdf")

    if uploaded:
        st.success("📄 File uploaded.")
        text = ""
        doc = fitz.open(stream=uploaded.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()

        purpose = st.text_input("🎯 Purpose (Internship, Job, Higher Studies)")
        if purpose:
            st.subheader("📊 Resume Feedback")
            st.markdown(rate_resume(text, purpose))
            st.markdown(ai_resume_feedback(text))
