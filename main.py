import os
import io
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

# PDF aur DOCX text parsing extraction utilities
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

llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.3  
)

def extract_text_from_file(file: UploadFile) -> str:
    """Helper framework to parse incoming resume documents safely"""
    filename = file.filename.lower()
    file_bytes = file.file.read()
    
    try:
        if filename.endswith('.pdf'):
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            text = "".join([page.extract_text() or "" for page in pdf_reader.pages])
            return text.strip()
        elif filename.endswith('.docx'):
            return docx2txt.process(io.BytesIO(file_bytes)).strip()
        elif filename.endswith('.txt') or filename.endswith('.md'):
            return file_bytes.decode('utf-8').strip()
        return ""
    except Exception as e:
        return ""

@app.post("/analyze")
def analyze_skills_pipeline(
    resume: Optional[UploadFile] = File(None),
    manual_text: Optional[str] = Form(None)
):
    # Base variables initial state setup
    skills_input = []
    role_input = "Corporate Professional"
    resume_extracted_text = ""
    
    # 🌟 Step 1: Secure File Extraction & Input Parsing
    if resume and resume.filename != "":
        resume_extracted_text = extract_text_from_file(resume)

    # 🌟 Step 2: Intelligent Input Decomposition & Structuring
    # Front-end updates structure is sent inside manual_text as Form data
    parsed_manual_skills = ""
    if manual_text:
        # Front-end formats it as: "Skills: XYZ. Target Role: ABC" or "Target Role: ABC"
        if "Skills:" in manual_text and "Target Role:" in manual_text:
            try:
                parts = manual_text.split("Target Role:")
                role_input = parts[1].strip()
                skills_raw = parts[0].replace("Skills:", "").strip()
                skills_input = [s.trim() for s in skills_raw.split(",") if s.strip()]
                parsed_manual_skills = skills_raw
            except Exception:
                pass
        elif "Target Role:" in manual_text:
            role_input = manual_text.replace("Target Role:", "").strip()

    # Fallback to prevent pipeline crash if arrays are empty
    if not skills_input and not resume_extracted_text:
        skills_input = ["General Competencies"]
        
    # 🌟 Step 3: Invoking LangGraph Pipeline
    # If skills list is empty, pass parsed text fragments or placeholders
    graph_result = run_sdr_pipeline(skills_input if skills_input else ["Resume Profiling Active"])
    
    # Universal Corporate Analytics Calculations (Retained Fallback metrics layout)
    total_skills = len(skills_input) if skills_input else 5
    calculated_pecc = min(95, 60 + (total_skills * 5))
    calculated_upe = min(9.8, round(3.5 + (total_skills * 0.6), 1))
    
    legacy_keywords = ["excel basic", "data entry", "jquery", "cold calling", "manual filing"]
    has_legacy = any(any(l in s.lower() for l in legacy_keywords) for s in skills_input)
    calculated_sdr = 90 if has_legacy else 365
    
    # 🌟 Step 4: Strict Priority System Prompting Injection
    prompt = (
        f"You are an Elite Corporate Career Strategy Advisor. Your objective is profile evaluation.\n\n"
        f"INPUT DATA CONTEXT:\n"
        f"1. EXTRACTED RESUME RAW CONTENT: \"\"\"{resume_extracted_text if resume_extracted_text else 'No physical resume uploaded.'}\"\"\"\n"
        f"2. MANUALLY ENTERED COMPETENCIES: \"\"\"{parsed_manual_skills if parsed_manual_skills else 'None provided.'}\"\"\"\n\n"
        f"CRITICAL OPERATIONAL RULES:\n"
        f"- AUTOMATIC ROLE IDENTIFICATION: If the target role value is ambiguous or generic ('Corporate Professional'), look directly inside the EXTRACTED RESUME RAW CONTENT to evaluate what specific tech/management position the user is qualified for, and prioritize analyzing for that role.\n"
        f"- PRIORITY WEIGHT: If both raw resume text and manual competencies are present, give the physical resume 70% priority weight. Treat manual input data merely as short-term user preferences or immediate wishes.\n"
        f"- Target Corporate Assessment Vector: {role_input}.\n\n"
        f"OUTPUT SPECIFICATION:\n"
        f"Provide a razor-sharp, exact 2-line strategic upskilling or transition roadmap focusing on high-impact corporate, tech, or management standards relevant to this specific domain."
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Returning original JSON contract objects to prevent front-end crash mapping
    return {
        "trend_notes": graph_result.get("trend_notes", "Stable pipeline deployment alignment"),
        "results": [
            {
                "tech": ", ".join(skills_input) if skills_input and skills_input != ["General Competencies"] else "Extracted Resume Profile",
                "runway_days": calculated_sdr,
                "status": "watch" if calculated_sdr < 180 else "healthy",
                "replacement_trend": "AI-Driven Automation / Agile Frameworks / Modern Business Analytics",
                "pecc_score": calculated_pecc,
                "upe_score": calculated_upe,
                "note": response.content
            }
        ]
    }
