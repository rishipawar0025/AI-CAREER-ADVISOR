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

# Model change kar rahe hain DeepSeek-R1 distil model par (High Reasoning & Long Output)
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="deepseek-r1-distill-llama-70b", # Deep Intelligence & Long Reasoning
    temperature=0.3
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
    Perform an IN-DEPTH, COMPREHENSIVE, AND DETAILED skill audit for the profile provided below.

    {analysis_context}

    STRICT OUTPUT GUIDELINES:
    1. Base all conclusions 100% on the primary data source above.
    2. Provide an EXTENSIVE, RICH, AND HIGHLY DETAILED roadmap note. Do NOT summarize or shorten sections. 
    3. Include complete technical frameworks, specific tools, architectures, and deep execution strategies.

    ROADMAP NOTE FORMATTING (Must be thorough and multi-paragraph):
    
    ### 📌 Profile Diagnosis & Industry Benchmark
    Write a detailed 2-paragraph analysis comparing current candidate experience with modern enterprise standards.

    ### ⚠️ Missing Critical Skills & Architecture Vulnerabilities
    Provide an extensive list (5 to 7 specific tools/frameworks) with explicit reasoning on why missing each tool poses a career risk.

    ### 🚀 High-Impact Technical Upskilling Roadmap
    Provide an in-depth breakdown of concepts, cloud engineering, pipeline design, and system optimizations needed.

    ### 🛠️ Strategic 90-Day Execution Blueprint
    - **Month 1 (Days 1-30)**: Detailed learning tasks & hands-on modules.
    - **Month 2 (Days 31-60)**: End-to-end production architecture project execution.
    - **Month 3 (Days 61-90)**: Benchmarking, portfolio optimization, and interview readiness.

    Respond STRICTLY with a valid raw JSON object (no ```json codeblock wrappers):
    {{
        "detected_role": "Parsed target or detected professional profile title",
        "extracted_skills": "Completely parsed current skills list",
        "runway_days": 320,
        "pecc_score": 85,
        "upe_score": 8.2,
        "roadmap_note": "Extensive Markdown Content matching the 4 sections above"
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
                "### 📌 Profile Diagnosis\n"
                "Strong foundational profile, needs modernization.\n\n"
                "### ⚠️ Missing Critical Skills\n"
                "• Cloud Architecture & Microservices\n"
                "• CI/CD & Automated Pipelines\n\n"
                "### 🚀 High-Impact Upskilling\n"
                "Focus on Cloud Native Tools and Production AI Systems.\n\n"
                "### 🛠️ 90-Day Execution Plan\n"
                "• **Month 1**: Learn Cloud Architecture.\n"
                "• **Month 2**: Build end-to-end production pipeline project.\n"
                "• **Month 3**: Benchmark skills and apply for target roles."
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
