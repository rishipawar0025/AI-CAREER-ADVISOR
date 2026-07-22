import os
import io
import re
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
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

class AuditResultSchema(BaseModel):
    detected_role: str = Field(description="Detected target role title")
    extracted_skills: str = Field(description="Parsed skill summary or main gaps")
    runway_days: int = Field(description="Days of sustainability (e.g. 90-360)")
    pecc_score: int = Field(description="Automation protection score (0-100)")
    upe_score: float = Field(description="Adaptability score (0.0-10.0)")
    roadmap_note: str = Field(description="Full markdown audit report")

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

    parser = JsonOutputParser(pydantic_object=AuditResultSchema)

    prompt_text = (
        "You are an elite, uncensored Executive Career Auditor & AI Reality-Check Strategist.\n"
        "Analyze the candidate's provided profile strictly against their target role domain.\n\n"
        f"{analysis_context}\n\n"
        "REALITY-CHECK EVALUATION RULES:\n"
        "1. Compare current skills vs target role expectations.\n"
        "2. If there is a severe mismatch (e.g., HR/Talent Acquisition background applied for a UX/UI or Developer role), "
        "do NOT force fake validation. Clearly state in the diagnosis that there is 0% domain overlap.\n"
        "3. Drop scores accordingly (Mismatch = Runway < 120 days, PECC < 40%).\n"
        "4. Provide an extensive, highly actionable markdown report (minimum 250 words).\n\n"
        "REQUIRED MARKDOWN SECTIONS (Inside `roadmap_note`):\n"
        "### 📌 Profile Reality-Check & Diagnosis\n"
        "A clear, honest 2-paragraph evaluation comparing candidate tools with modern industry benchmarks for this specific role.\n\n"
        "### ⚠️ Critical Missing Skills & Domain Vulnerabilities\n"
        "List 4 to 6 exact missing tools, libraries, design paradigms, or frameworks necessary for this target role.\n\n"
        "### 🚀 High-Impact Technical & Domain Upskilling Roadmap\n"
        "Specific modern workflows, tools, and practices to master immediately.\n\n"
        "### 🛠️ Strategic 90-Day Execution Blueprint\n"
        "- Month 1 (Days 1-30): Ground-zero foundational mastery.\n"
        "- Month 2 (Days 31-60): Build 2 production-grade domain projects.\n"
        "- Month 3 (Days 61-90): Portfolio refactoring, market benchmarking, and mock interviews.\n\n"
        f"{parser.get_format_instructions()}"
    )

    ai_data = None
    llm = get_llm()

    if llm:
        try:
            response = llm.invoke([HumanMessage(content=prompt_text)])
            ai_data = parser.parse(response.content)
        except Exception as e:
            print(f"❌ GROQ LLM EXCEPTION LOG: {str(e)}")

    if not ai_data:
        target_role = user_manual_input if user_manual_input else "Target Role"
        ai_data = {
            "detected_role": target_role,
            "extracted_skills": "Core Industry Tools & Competencies",
            "runway_days": 110,
            "pecc_score": 35,
            "upe_score": 4.5,
            "roadmap_note": (
                f"### 📌 Profile Reality-Check & Diagnosis\n"
                f"⚠️ **Live Groq LLM Handshake Issue.**\n\n"
                f"Evaluation for **{target_role}** requires an active Groq API connection. Please check Render Environment Variables.\n\n"
                f"### ⚠️ Critical Missing Skills & Domain Vulnerabilities\n"
                f"• Missing live API connection to Groq Llama 3.3 pipeline.\n\n"
                f"### 🚀 High-Impact Technical & Domain Upskilling Roadmap\n"
                f"Ensure `GROQ_API_KEY` is configured correctly on Render.\n\n"
                f"### 🛠️ Strategic 90-Day Execution Blueprint\n"
                f"• **Step 1**: Verify API key.\n"
                f"• **Step 2**: Clear build cache & redeploy."
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
