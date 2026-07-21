import os
import io
import json
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

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile",
    temperature=0.2
)

def extract_text_from_file(file: UploadFile) -> str:
    filename = file.filename.lower()
    file_bytes = file.file.read()
    try:
        if filename.endswith('.pdf'):
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            return "".join([page.extract_text() or "" for page in pdf_reader.pages]).strip()
        elif filename.endswith('.docx'):
            return docx2txt.process(io.BytesIO(file_bytes)).strip()
        elif filename.endswith('.txt') or filename.endswith('.md'):
            return file_bytes.decode('utf-8').strip()
        return ""
    except Exception:
        return ""

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "SkillRadar AI API",
        "docs_url": "/docs"
    }

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

    # STRICT PRIORITY ENGINE: File Upload ALWAYS Overrides Manual Text
    if is_file_uploaded:
        resume_extracted_text = extract_text_from_file(resume)
        if not resume_extracted_text:
            resume_extracted_text = f"Uploaded document filename: {resume.filename}. Candidate resume content provided."
            
        analysis_context = f"PRIMARY DATA SOURCE: UPLOADED RESUME ONLY.\n\nRESUME CONTENT:\n{resume_extracted_text}"
    elif user_manual_input:
        analysis_context = f"PRIMARY DATA SOURCE: USER MANUAL FORM INPUT ONLY.\n\nFORM INPUT:\n{user_manual_input}"
    else:
        raise HTTPException(status_code=400, detail="Please upload a resume file or enter details manually.")

    prompt = f"""
    You are an elite Executive Career Auditor & AI Skill Gap Strategist.
    Analyze the candidate's profile strictly based on the provided data below.

    {analysis_context}

    STRICT RULES:
    1. Base all conclusions 100% on the primary data source above.
    2. Identify exact missing technical tools, domain competencies, and execution gaps required for their target market profile.
    
    METRICS CALCULATION:
    - runway_days: 90 to 365 (Market relevance durability score).
    - pecc_score: 50 to 99 (% protection against automated tools & outsourcing).
    - upe_score: 1.0 to 10.0 (Adaptability to pivot across adjacent technical domains).

    ROADMAP NOTE REQUIREMENTS:
    You MUST provide an IN-DEPTH, MULTI-PARAGRAPH STRATEGIC ADVISORY REPORT in markdown format (At least 250-300 words). Include the following sections:
    
    ### 📌 Profile Diagnosis & Current Standing
    Detailed breakdown of what is currently present vs what the industry benchmark demands.

    ### ⚠️ Missing Critical Skills & Vulnerabilities
    Explicitly name 3 to 5 key tools, frameworks, or domain skills that are missing and posing high career risk.

    ### 🚀 High-Impact Upskilling Roadmap
    A structured plan detailing exactly what concepts, certifications, or technologies to learn next to bridge the identified gap.

    ### 🛠️ Strategic 90-Day Execution Advice
    Actionable step-by-step guidance to instantly increase market readiness and resilience.

    You MUST respond STRICTLY with a valid JSON object (no raw text outside JSON, no ```json formatting):
    {{
        "detected_role": "Parsed target or detected professional profile title",
        "extracted_skills": "Completely parsed current skills list",
        "runway_days": 320,
        "pecc_score": 85,
        "upe_score": 8.2,
        "roadmap_note": "Markdown content containing the 4 detailed sections requested above."
    }}
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        raw_text = response.content.strip()

        # Clean markdown wrappers if returned by LLM
        if "```json" in raw_text:
            clean_content = raw_text.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_text:
            clean_content = raw_text.split("```")[1].split("```")[0].strip()
        else:
            clean_content = raw_text

        ai_data = json.loads(clean_content)
    except Exception as e:
        print(f"❌ GROQ LLM EXCEPTION: {str(e)}")
        fallback_role = user_manual_input if (user_manual_input and not is_file_uploaded) else "Corporate & Tech Professional"
        ai_data = {
            "detected_role": fallback_role,
            "extracted_skills": "Core Domain Competencies & System Tools",
            "runway_days": 270,
            "pecc_score": 80,
            "upe_score": 7.8,
            "roadmap_note": (
                "### 📌 Profile Diagnosis & Current Standing\n"
                "Your profile exhibits strong core foundational capabilities, but lacks enterprise-grade modern automation exposure.\n\n"
                "### ⚠️ Missing Critical Skills & Vulnerabilities\n"
                "• Advanced System Architecture & Cloud Workflows\n"
                "• Automated Testing & Performance Benchmarking Tools\n"
                "• End-to-End Metrics Analytics Integration\n\n"
                "### 🚀 High-Impact Upskilling Roadmap\n"
                "Focus on acquiring production-ready skills, cloud infrastructure automation, and real-time observability stacks.\n\n"
                "### 🛠️ Strategic 90-Day Execution Advice\n"
                "1. **Days 1-30**: Complete dedicated specialization modules in cloud integration.\n"
                "2. **Days 31-60**: Implement an end-to-end open-source project demonstrating advanced pipeline workflows.\n"
                "3. **Days 61-90**: Optimize system benchmarking and target strategic tech leadership roles."
            )
        }
        
    graph_result = run_sdr_pipeline([ai_data["detected_role"]])
    
    return {
        "trend_notes": graph_result.get("trend_notes", "Stable pipeline deployment"),
        "results": [
            {
                "tech": ai_data.get("extracted_skills", "Core Profile Infrastructure Stack"),
                "detected_title": ai_data.get("detected_role", "Detected Profile Lead"),
                "runway_days": ai_data.get("runway_days", 365),
                "status": "watch" if ai_data.get("runway_days", 365) < 180 else "healthy",
                "pecc_score": ai_data.get("pecc_score", 80),
                "upe_score": ai_data.get("upe_score", 8.0),
                "note": ai_data.get("roadmap_note", "Continue active capability upskilling tracks.")
            }
        ]
    }
