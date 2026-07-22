import os
import io
import json
import re
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import pypdf
import docx2txt

from graph import run_sdr_pipeline

app = FastAPI(title="SkillRadar AI - Universal Corporate Analytics API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

groq_key = os.getenv("GROQ_API_KEY")

def get_llm():
    if not groq_key:
        return None
    return ChatGroq(
        groq_api_key=groq_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.2,
        max_tokens=2048
    )

def extract_text_from_file(file: UploadFile) -> str:
    filename = file.filename.lower()
    try:
        file.file.seek(0)
        file_bytes = file.file.read()
        if filename.endswith('.pdf'):
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            return "".join([page.extract_text() or "" for page in pdf_reader.pages]).strip()
        elif filename.endswith('.docx'):
            return docx2txt.process(io.BytesIO(file_bytes)).strip()
        elif filename.endswith('.txt') or filename.endswith('.md'):
            return file_bytes.decode('utf-8').strip()
        return ""
    except Exception as e:
        print(f"File Read Exception: {e}")
        return ""

@app.get("/")
def read_root():
    return {"status": "online", "service": "SkillRadar AI API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/analyze")
def analyze_skills_pipeline(
    resume: Optional[UploadFile] = File(None),
    manual_text: Optional[str] = Form(None)
):
    user_manual_input = manual_text.strip() if manual_text else ""
    is_file_uploaded = resume is not None and resume.filename != ""

    if is_file_uploaded:
        resume_extracted_text = extract_text_from_file(resume)
        if not resume_extracted_text:
            resume_extracted_text = f"Uploaded document: {resume.filename}."
        analysis_context = f"PRIMARY DATA SOURCE: UPLOADED RESUME CONTENT:\n{resume_extracted_text}"
        if user_manual_input:
            analysis_context += f"\n\nADDITIONAL TARGET CONTEXT:\n{user_manual_input}"
    elif user_manual_input:
        analysis_context = f"PRIMARY DATA SOURCE: FORM INPUT ONLY:\n{user_manual_input}"
    else:
        raise HTTPException(status_code=400, detail="Please upload a resume file or enter details manually.")

    prompt = f"""
You are an elite, uncensored Executive Career Auditor & AI Reality-Check Strategist.
Analyze the candidate's provided profile strictly against their target role domain.

{analysis_context}

REALITY-CHECK EVALUATION RULES:
1. Compare current skills vs target role expectations.
2. If there is a severe mismatch (e.g., HR/Talent Acquisition background applied for a UX/UI or Developer role), do NOT force fake validation. Clearly state in the diagnosis that there is 0% domain overlap.
3. Drop scores accordingly (Mismatch = Runway < 120 days, PECC < 40%).
4. Provide an extensive, highly actionable markdown report (minimum 250 words).

REQUIRED MARKDOWN SECTIONS (Inside `roadmap_note`):
### 📌 Profile Reality-Check & Diagnosis
A clear, honest 2-paragraph evaluation comparing candidate tools with modern industry benchmarks for this specific role.

### ⚠️ Critical Missing Skills & Domain Vulnerabilities
List 4 to 6 exact missing tools, libraries, design paradigms, or frameworks necessary for this target role.

### 🚀 High-Impact Technical & Domain Upskilling Roadmap
Specific modern workflows, tools, and practices to master immediately.

### 🛠️ Strategic 90-Day Execution Blueprint
- **Month 1 (Days 1-30)**: Ground-zero foundational mastery.
- **Month 2 (Days 31-60)**: Build 2 production-grade domain projects.
- **Month 3 (Days 61-90)**: Portfolio refactoring, market benchmarking, and mock interviews.

Return STRICTLY a raw valid JSON object (no ```json codeblock formatting):
{{
    "detected_role": "Detected Target Role Title",
    "extracted_skills": "Parsed skills list matching the domain",
    "runway_days": 280,
    "pecc_score": 75,
    "upe_score": 7.0,
    "roadmap_note": "Your full Markdown report matching the 4 sections above."
}}
"""
    
    ai_data = None
    llm = get_llm()

    if llm:
        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            raw_text = response.content.strip()

            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if json_match:
                ai_data = json.loads(json_match.group(0))
        except Exception as e:
            print(f"❌ GROQ LLM EXCEPTION LOG: {str(e)}")

    if not ai_data:
        target_role = user_manual_input if user_manual_input else "Target Role"
        ai_data = {
            "detected_role": target_role,
            "extracted_skills": "Core Industry Tools & Competencies",
            "runway_days": 180,
            "pecc_score": 60,
            "upe_score": 6.5,
            "roadmap_note": (
                f"### 📌 Profile Reality-Check & Diagnosis\n"
                f"⚠️ **Live Groq LLM API Call Failed or Invalid Key.**\n\n"
                f"Evaluation for **{target_role}** requires an active Groq API handshake. Please verify `GROQ_API_KEY` on Render.\n\n"
                f"### ⚠️ Critical Missing Skills & Domain Vulnerabilities\n"
                f"• Missing live API connection to Groq Llama 3.3 pipeline.\n\n"
                f"### 🚀 High-Impact Technical & Domain Upskilling Roadmap\n"
                f"Ensure your Render web service environment variable `GROQ_API_KEY` is configured correctly.\n\n"
                f"### 🛠️ Strategic 90-Day Execution Blueprint\n"
                f"• **Step 1**: Check Render logs for exact exception trace.\n"
                f"• **Step 2**: Re-deploy backend on Render."
            )
        }
        
    graph_result = run_sdr_pipeline([ai_data["detected_role"]])
    
    return {
        "trend_notes": graph_result.get("trend_notes", "Pipeline operational"),
        "results": [
            {
                "tech": ai_data.get("extracted_skills", "Core Skill Stack"),
                "detected_title": ai_data.get("detected_role", "Target Profile Lead"),
                "runway_days": ai_data.get("runway_days", 180),
                "status": "watch" if ai_data.get("runway_days", 180) < 180 else "healthy",
                "pecc_score": ai_data.get("pecc_score", 60),
                "upe_score": ai_data.get("upe_score", 6.5),
                "note": ai_data.get("roadmap_note", "Processing active roadmap track.")
            }
        ]
    }
