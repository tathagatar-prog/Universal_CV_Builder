# Universal CV Builder

A Streamlit application for entering CV information, reviewing it, generating a black-and-white A4 PDF, and printing it.

## Features

- Personal information and contact details
- Optional photograph at the top-left of the PDF
- Optional signature at the bottom-right of the declaration area
- Education, experience, skills, research projects, publications, awards, certifications, memberships, workshops and teaching areas
- Add and delete multiple records in repeatable sections
- Preview entered information before generating the PDF
- PDF download and JSON data backup
- Black-and-white PDF with 14 pt bold section headings and 12 pt body text
- Times-style PDF font; upload a Times New Roman `.ttf` file in the preview tab for exact Times New Roman output

## Image size note

Uploaded images are converted to JPEG and compressed toward 50–100 KB where feasible. The app does not add meaningless padding to force a very simple image above 50 KB. It displays the resulting size so the user can check it.

## Run locally

1. Install Python 3.10 or later.
2. Open a terminal in this folder.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run:

   ```bash
   streamlit run app.py
   ```

5. Open the local URL shown by Streamlit, usually `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload `app.py`, `requirements.txt`, and `README.md`.
3. Open https://share.streamlit.io/
4. Sign in with GitHub and choose the repository, branch, and `app.py`.
5. Deploy. Share the generated public app URL.

## Important deployment notes

- The app does not currently save CVs to a central database. Each visitor builds and downloads their own CV during their session.
- Users should download their PDF and JSON backup before closing or refreshing the app.
- Do not upload a font file unless you have the right to use and distribute it. Users can upload a Times New Roman TTF file for their own PDF generation.
- For a public production service, consider adding privacy notice, rate limits, file-size limits, and server-side session cleanup.
