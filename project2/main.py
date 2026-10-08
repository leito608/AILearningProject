import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Resume Critiquer", page_icon="📃", layout="centered")
st.title("AI Resume Critiquer")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

upload_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
job_role = st.text_input("Enter the job role you're targeting (optional)")

analyze = st.button("Analyze Resume")


def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += (page.extract_text() or "") + "\n"
    return text


def extract_text_from_file(upload_file):
    if upload_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(upload_file.read()))
    return upload_file.read().decode("utf-8")


if analyze and upload_file:
    try:
        with st.spinner("Analyzing..."):
            file_content = extract_text_from_file(upload_file)

            if not file_content.strip():
                st.error("File does not have any content...")
                st.stop()

            target = job_role.strip() if job_role and job_role.strip() else None
            target_line = (
                f"Target role: {target}. Prioritize what this role's hiring managers and ATS typically scan for."
                if target
                else "No target role was given. Judge fitness for strong general applications, then note how feedback would change for 1–2 likely roles."
            )

            prompt = f"""Critique this resume as a hiring manager + ATS reviewer. Be specific, evidence-based, and actionable.

{target_line}

Rules:
- Use only facts in the resume. Do not invent jobs, metrics, tools, or credentials.
- Quote short phrases from the resume when you criticize or rewrite them.
- Prefer concrete rewrites over vague advice ("be more impactful").
- Rank issues by hiring impact. Skip filler praise.

Evaluate:
1. First impression (summary/headline, positioning vs the target)
2. Impact of bullets (action verbs, quantified results, ownership vs duties)
3. Skills & keywords (relevance, evidence in experience, ATS gaps)
4. Experience & education (clarity, recency, missing context)
5. Structure, length, and scannability (sections, dates, formatting artifacts from PDF extraction)

Output in this exact structure:

## Overall verdict
2–4 sentences: hireability for the target, biggest strength, biggest risk.

## Score (1–10)
- Positioning
- Impact / metrics
- Skills match
- Clarity / structure
Briefly justify each score.

## What to change first
Top 5 fixes, ordered by impact. Each item: problem → why it hurts → exact fix.

## Bullet rewrites
Pick 3–6 of the weakest bullets. For each:
- Original: "..."
- Why it fails
- Stronger: "..." (keep truthful; use [X] only if a number is missing)

## Keyword / ATS gaps
List missing or underused terms for the target. Note which ones the candidate likely already has evidence for vs. should not claim.

## Keep doing
2–4 things that already work — cite them.

Resume:
\"\"\"
{file_content}
\"\"\""""

            client = OpenAI(
                api_key=GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
            )
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior recruiter and resume editor. "
                            "You give blunt, structured critiques grounded in the resume text. "
                            "You never invent experience. You always include rewritten bullets the candidate can paste."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_completion_tokens=4000,
            )
            st.markdown("### Analysis Results")
            st.markdown(response.choices[0].message.content)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")