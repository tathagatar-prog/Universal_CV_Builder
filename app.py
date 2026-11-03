
import streamlit as st
import io
import re
from datetime import date
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, Image as PDFImage, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

st.set_page_config(
    page_title="Professional CV Builder",
    page_icon="📄",
    layout="wide"
)

# ---------------- SESSION STATE ----------------

if "step" not in st.session_state:
    st.session_state.step = 0

defaults = {
    "name": "",
    "designation": "",
    "institution": "",
    "email": "",
    "phone": "",
    "address": "",
    "linkedin": "",
    "website": "",
    "summary": "",
    "education": [],
    "experience": [],
    "skills": [],
    "projects": [],
    "publications": [],
    "awards": [],
    "certifications": [],
    "research": "",
    "photo": None,
    "signature": None,
    "place": "",
    "cv_date": str(date.today()),
    "teaching": "",
    "memberships": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------- COMMON FUNCTIONS ----------------

def add_record(section, record):
    st.session_state[section].append(record)


def remove_record(section, index):
    st.session_state[section].pop(index)


def upload_image(uploaded):
    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        img.thumbnail((1200, 1200))

        output = io.BytesIO()
        img.save(output, format="JPEG", quality=85, optimize=True)
        return output.getvalue()

    return None


def declaration_text():
    return (
        "I hereby declare that the information provided in this "
        "Curriculum Vitae is true and correct to the best of my "
        "knowledge and belief. I understand that any discrepancy "
        "or misrepresentation in the information furnished may "
        "affect my candidature or professional consideration."
    )


def safe(text):
    return (
        str(text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )


def make_pdf():
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18*mm,
        leftMargin=18*mm,
        topMargin=17*mm,
        bottomMargin=20*mm
    )

    regular = "Times-Roman"
    bold = "Times-Bold"

    styles = {
        "body": ParagraphStyle(
            "body",
            fontName=regular,
            fontSize=12,
            leading=15,
            textColor=colors.black,
            spaceAfter=4
        ),
        "heading": ParagraphStyle(
            "heading",
            fontName=bold,
            fontSize=14,
            leading=17,
            textColor=colors.black,
            spaceBefore=10,
            spaceAfter=5
        ),
        "name": ParagraphStyle(
            "name",
            fontName=bold,
            fontSize=16,
            leading=19
        ),
        "right": ParagraphStyle(
            "right",
            fontName=bold,
            fontSize=12,
            alignment=TA_RIGHT,
            leading=15
        )
    }

    story = []

    # ---------------- HEADER ----------------

    photo = Spacer(30*mm, 35*mm)

    if st.session_state.photo:
        photo = PDFImage(
            io.BytesIO(st.session_state.photo),
            width=30*mm,
            height=35*mm
        )

    contact = [
        Paragraph(safe(st.session_state.name), styles["name"])
    ]

    for field in [
        st.session_state.designation,
        st.session_state.institution,
        st.session_state.address,
        st.session_state.email,
        st.session_state.phone,
        st.session_state.linkedin,
        st.session_state.website
    ]:
        if field:
            contact.append(Paragraph(safe(field), styles["body"]))

    header = Table(
        [[photo, contact]],
        colWidths=[36*mm, 138*mm]
    )

    header.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("LINEBELOW", (0,0), (-1,-1), 0.8, colors.black)
    ]))

    story += [header, Spacer(1, 8)]

    # ---------------- SECTION FUNCTION ----------------

    def section(title, records):
        if not records:
            return

        story.append(
            Paragraph(title.upper(), styles["heading"])
        )

        story.append(
            HRFlowable(
                width="100%",
                thickness=0.6,
                color=colors.black
            )
        )

        for item in records:

            if isinstance(item, dict):
                heading = " | ".join(
                    str(item.get(k, ""))
                    for k in ["title", "institution", "date"]
                    if item.get(k)
                )

                if heading:
                    story.append(
                        Paragraph(
                            "<b>" + safe(heading) + "</b>",
                            styles["body"]
                        )
                    )

                for key in [
                    "details", "description", "authors",
                    "publisher", "result"
                ]:
                    if item.get(key):
                        story.append(
                            Paragraph(
                                safe(item[key]),
                                styles["body"]
                            )
                        )

            else:
                story.append(
                    Paragraph("• " + safe(item), styles["body"])
                )

            story.append(Spacer(1, 3))

    # ---------------- CV CONTENT ----------------

    if st.session_state.summary:
        section(
            "Professional Profile",
            [st.session_state.summary]
        )

    if st.session_state.research:
        section(
            "Research Interests",
            [st.session_state.research]
        )

    section("Education", st.session_state.education)
    section("Professional Experience", st.session_state.experience)
    section("Technical Skills", st.session_state.skills)
    section("Research Projects", st.session_state.projects)
    section("Publications", st.session_state.publications)
    section("Awards and Achievements", st.session_state.awards)
    section("Certifications", st.session_state.certifications)

    if st.session_state.teaching:
        section("Knowledge Areas", [st.session_state.teaching])

    if st.session_state.memberships:
        section(
            "Professional Memberships",
            [st.session_state.memberships]
        )

    # ---------------- AUTOMATIC DECLARATION ----------------

    story.append(
        Paragraph("DECLARATION", styles["heading"])
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=0.6,
            color=colors.black
        )
    )

    story.append(
        Paragraph(
            safe(declaration_text()),
            styles["body"]
        )
    )

    story.append(Spacer(1, 15))

    left = Paragraph(
        "Place: " + safe(st.session_state.place) +
        "<br/>Date: " + safe(st.session_state.cv_date),
        styles["body"]
    )

    signature_items = []

    if st.session_state.signature:
        signature_items.append(
            PDFImage(
                io.BytesIO(st.session_state.signature),
                width=40*mm,
                height=17*mm
            )
        )

    signature_items.append(
        Paragraph(
            "<b>" + safe(st.session_state.name) + "</b>",
            styles["right"]
        )
    )

    if st.session_state.designation:
        signature_items.append(
            Paragraph(
                safe(st.session_state.designation),
                styles["right"]
            )
        )

    sign_table = Table(
        [[left, signature_items]],
        colWidths=[85*mm, 89*mm]
    )

    sign_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "BOTTOM"),
        ("ALIGN", (1,0), (1,0), "RIGHT"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0)
    ]))

    story.append(sign_table)

    def page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont("Times-Roman", 9)
        canvas.setFillColor(colors.black)
        canvas.drawCentredString(
            A4[0]/2, 9*mm, str(doc.page)
        )
        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=page_number,
        onLaterPages=page_number
    )

    return buffer.getvalue()


# ---------------- APPLICATION HEADER ----------------

st.title("PROFESSIONAL CV BUILDER")

st.write(
    "Create your professional CV step by step, "
    "review it and download the final PDF."
)

steps = [
    "Personal Information",
    "Professional Profile",
    "Education",
    "Experience",
    "Technical Skills",
    "Research and Publications",
    "Additional Information",
    "Final Review"
]

st.progress(
    (st.session_state.step + 1) / len(steps)
)

st.caption(
    f"Step {st.session_state.step + 1} of {len(steps)}: "
    f"{steps[st.session_state.step]}"
)

st.divider()


# ---------------- STEP 1 ----------------

if st.session_state.step == 0:

    st.header("Personal Information")

    st.session_state.name = st.text_input(
        "Full Name *", st.session_state.name
    )

    st.session_state.designation = st.text_input(
        "Designation", st.session_state.designation
    )

    st.session_state.institution = st.text_input(
        "Institution / Company",
        st.session_state.institution
    )

    st.session_state.email = st.text_input(
        "Email", st.session_state.email
    )

    st.session_state.phone = st.text_input(
        "Mobile Number", st.session_state.phone
    )

    st.session_state.address = st.text_area(
        "Address", st.session_state.address
    )

    st.session_state.linkedin = st.text_input(
        "LinkedIn URL", st.session_state.linkedin
    )

    st.session_state.website = st.text_input(
        "Website / Portfolio", st.session_state.website
    )

    st.subheader("Photograph and Signature")

    photo = st.file_uploader(
        "Upload Photograph",
        type=["jpg", "jpeg", "png"],
        key="photo_upload"
    )

    if photo:
        st.session_state.photo = upload_image(photo)
        st.image(st.session_state.photo, width=120)

    signature = st.file_uploader(
        "Upload Signature",
        type=["jpg", "jpeg", "png"],
        key="signature_upload"
    )

    if signature:
        st.session_state.signature = upload_image(signature)
        st.image(st.session_state.signature, width=160)


# ---------------- STEP 2 ----------------

elif st.session_state.step == 1:

    st.header("Professional Profile")

    st.session_state.summary = st.text_area(
        "Professional Summary",
        st.session_state.summary,
        height=180,
        placeholder="Describe your academic and professional background."
    )

    st.session_state.research = st.text_area(
        "Research Interests / Areas of Expertise",
        st.session_state.research,
        height=130
    )


# ---------------- STEP 3 ----------------

elif st.session_state.step == 2:

    st.header("Educational Qualifications")

    with st.form("education_form", clear_on_submit=True):

        title = st.text_input("Degree / Qualification")
        institution = st.text_input("University / Institution")
        year = st.text_input("Year / Duration")
        details = st.text_input("CGPA / Marks / Details")

        submitted = st.form_submit_button("Add Education")

        if submitted and title:
            add_record("education", {
                "title": title,
                "institution": institution,
                "date": year,
                "details": details
            })

    for i, item in enumerate(st.session_state.education):
        st.write(
            f"**{item['title']}** | "
            f"{item['institution']} | {item['date']}"
        )

        if st.button("Delete", key=f"edu{i}"):
            remove_record("education", i)
            st.rerun()


# ---------------- STEP 4 ----------------

elif st.session_state.step == 3:

    st.header("Professional Experience")

    with st.form("experience_form", clear_on_submit=True):

        title = st.text_input("Position / Designation")
        institution = st.text_input("Company / Institution")
        year = st.text_input("Duration")
        details = st.text_area("Roles and Responsibilities")

        submitted = st.form_submit_button("Add Experience")

        if submitted and title:
            add_record("experience", {
                "title": title,
                "institution": institution,
                "date": year,
                "details": details
            })

    for i, item in enumerate(st.session_state.experience):
        st.write(
            f"**{item['title']}** | "
            f"{item['institution']} | {item['date']}"
        )

        if st.button("Delete", key=f"exp{i}"):
            remove_record("experience", i)
            st.rerun()


# ---------------- STEP 5 ----------------

elif st.session_state.step == 4:

    st.header("Technical Skills")

    with st.form("skills_form", clear_on_submit=True):

        title = st.text_input("Skill / Technology")
        details = st.text_input("Proficiency / Details")

        submitted = st.form_submit_button("Add Skill")

        if submitted and title:
            add_record("skills", {
                "title": title,
                "details": details
            })

    for i, item in enumerate(st.session_state.skills):
        st.write(
            f"**{item['title']}** - {item['details']}"
        )

        if st.button("Delete", key=f"skill{i}"):
            remove_record("skills", i)
            st.rerun()

    st.session_state.teaching = st.text_area(
        "Strong Areas / Subjects",
        st.session_state.teaching
    )


# ---------------- STEP 6 ----------------

elif st.session_state.step == 5:

    st.header("Research and Publications")

    st.subheader("Research Projects")

    with st.form("project_form", clear_on_submit=True):

        title = st.text_input("Project Title")
        year = st.text_input("Year / Status")
        details = st.text_area("Description")

        submitted = st.form_submit_button("Add Project")

        if submitted and title:
            add_record("projects", {
                "title": title,
                "date": year,
                "details": details
            })

    for i, item in enumerate(st.session_state.projects):
        st.write(f"**{item['title']}** ({item['date']})")

        if st.button("Delete", key=f"proj{i}"):
            remove_record("projects", i)
            st.rerun()

    st.divider()
    st.subheader("Publications")

    with st.form("publication_form", clear_on_submit=True):

        title = st.text_input("Publication Title")
        institution = st.text_input("Journal / Conference / Publisher")
        year = st.text_input("Year")
        details = st.text_area("Authors / DOI / Volume / Pages")

        submitted = st.form_submit_button("Add Publication")

        if submitted and title:
            add_record("publications", {
                "title": title,
                "institution": institution,
                "date": year,
                "details": details
            })

    for i, item in enumerate(st.session_state.publications):
        st.write(f"**{item['title']}** ({item['date']})")

        if st.button("Delete", key=f"pub{i}"):
            remove_record("publications", i)
            st.rerun()


# ---------------- STEP 7 ----------------

elif st.session_state.step == 6:

    st.header("Additional Information")

    st.subheader("Awards and Achievements")

    with st.form("award_form", clear_on_submit=True):

        title = st.text_input("Award / Achievement")
        institution = st.text_input("Organization")
        year = st.text_input("Year")
        details = st.text_area("Details")

        submitted = st.form_submit_button("Add Award")

        if submitted and title:
            add_record("awards", {
                "title": title,
                "institution": institution,
                "date": year,
                "details": details
            })

    for i, item in enumerate(st.session_state.awards):
        st.write(f"**{item['title']}** ({item['date']})")

        if st.button("Delete", key=f"award{i}"):
            remove_record("awards", i)
            st.rerun()

    st.divider()

    st.subheader("Certifications")

    with st.form("cert_form", clear_on_submit=True):

        title = st.text_input("Certification Name")
        institution = st.text_input("Issuing Organization")
        year = st.text_input("Year")

        submitted = st.form_submit_button("Add Certification")

        if submitted and title:
            add_record("certifications", {
                "title": title,
                "institution": institution,
                "date": year
            })

    for i, item in enumerate(st.session_state.certifications):
        st.write(f"**{item['title']}** - {item['institution']}")

        if st.button("Delete", key=f"cert{i}"):
            remove_record("certifications", i)
            st.rerun()

    st.divider()

    st.session_state.memberships = st.text_area(
        "Professional Memberships",
        st.session_state.memberships
    )

    st.session_state.place = st.text_input(
        "Place", st.session_state.place
    )

    st.session_state.cv_date = st.text_input(
        "Date", st.session_state.cv_date
    )


# ---------------- STEP 8: REVIEW ----------------

elif st.session_state.step == 7:

    st.header("Final CV Review")

    if not st.session_state.name.strip():
        st.error("Please enter your name in Personal Information.")
    else:

        st.subheader(st.session_state.name)

        st.write(
            " | ".join(x for x in [
                st.session_state.designation,
                st.session_state.institution,
                st.session_state.email,
                st.session_state.phone
            ] if x)
        )

        if st.session_state.photo:
            st.image(st.session_state.photo, width=120)

        review_sections = [
            ("Professional Profile", "summary"),
            ("Research Interests", "research"),
            ("Education", "education"),
            ("Professional Experience", "experience"),
            ("Technical Skills", "skills"),
            ("Research Projects", "projects"),
            ("Publications", "publications"),
            ("Awards", "awards"),
            ("Certifications", "certifications"),
            ("Areas of Strength", "teaching"),
            ("Professional Memberships", "memberships")
        ]

        for heading, key in review_sections:

            value = st.session_state[key]

            if value:
                st.markdown(f"**{heading}**")

                if isinstance(value, list):
                    for item in value:
                        st.write(
                            "• " + " | ".join(
                                str(v) for v in item.values() if v
                            )
                        )
                else:
                    st.write(value)

        st.divider()

        st.subheader("Declaration")

        # Automatically generated. Student cannot edit this.
        st.write(declaration_text())

        if st.session_state.signature:
            st.image(
                st.session_state.signature,
                width=160,
                caption="Signature"
            )

        st.write("Place:", st.session_state.place)
        st.write("Date:", st.session_state.cv_date)

        if st.button("Generate Final PDF", type="primary"):
            if not st.session_state.name.strip():
                st.error("Name is required.")
            else:
                try:
                    pdf = make_pdf()

                    st.download_button(
                        "Download CV PDF",
                        data=pdf,
                        file_name=re.sub(
                            r"[^A-Za-z0-9_-]",
                            "_",
                            st.session_state.name
                        ) + "_CV.pdf",
                        mime="application/pdf"
                    )

                    st.success(
                        "CV generated successfully. "
                        "Open the PDF and press Ctrl + P to print."
                    )

                except Exception as e:
                    st.error(f"PDF generation failed: {e}")


# ---------------- NAVIGATION ----------------

st.divider()

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.session_state.step > 0:
        if st.button("← Previous", use_container_width=True):
            st.session_state.step -= 1
            st.rerun()

with col2:
    st.caption(
        f"Current section: {steps[st.session_state.step]}"
    )

with col3:
    if st.session_state.step < len(steps) - 1:
        if st.button("Next →", type="primary", use_container_width=True):
            if (
                st.session_state.step == 0
                and not st.session_state.name.strip()
            ):
                st.error("Please enter your full name.")
            else:
                st.session_state.step += 1
                st.rerun()

st.markdown("---")
st.caption(
    "Professional CV Builder | Black & White | A4 | "
    "Tutoring Comp Science & Applications | ALL RIGHTS RESERVED | 2026"
)
