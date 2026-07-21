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

# Root Route (Render Health-Check & Handshake Fix)
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
    resume_extracted_text = ""
    if resume and resume.filename != "":
        resume_extracted_text = extract_text_from_file(resume)

    # Intelligent Analysis Instruction Prompt
    prompt = f"""
    You are an expert AI Career Strategy Advisor. Analyze the user profiles based on these inputs:
    
    1. UPLOADED RESUME TEXT: \"\"\"{resume_extracted_text}\"\"\"
    2. MANUAL USER FORM INPUT: \"\"\"{manual_text if manual_text else ''}\"\"\"
    
    STRICT COMPLIANCE DIRECTIONS:
    - If the uploaded resume text contains dense technical details (e.g., Deep Learning, AI/ML, Computer Vision, Software Development) and contradicts the manual text keywords, the UPLOADED RESUME has 90% priority weight.
    - AUTOMATIC POSITION DETECTION: Identify the core professional profile or domain from the resume context (e.g., "AI/ML Engineer", "Technical Program Manager", "Full Stack Developer"). Do not default to manual inputs if the resume explicitly points to a different high-skill career track.
    
    Calculate the following metrics based on the domain match stability:
    - runway_days: Score from 90 to 365 based on skill sustainability.
    - pecc_score: Resilience protection score percentage (value between 50 and 99).
    - upe_score: Capability pivot elasticity score (value between 1.0 and 10.0).
    
    You MUST respond with a VALID JSON object containing exactly these fields. Do not include markdown code blocks or text outside the JSON.
    {{
        "detected_role": "Extracted target profile title here",
        "extracted_skills": "Core technical tools parsed from profile",
        "runway_days": 365,
        "pecc_score": 85,
        "upe_score": 8.5,
        "roadmap_note": "A highly sharp 2-line professional roadmap strategy advice statement."
    }}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    try:
        # Clean response string if LLM appends markdown tags
        clean_content = response.content.strip().replace("```json", "").replace("```", "").strip()
        ai_data = json.loads(clean_content)
    except Exception:
        # Emergency structured fallback framework if JSON structure fails parsing
        ai_data = {
            "detected_role": "AI/ML Engineering Specialist",
            "extracted_skills": "Deep Learning, Computer Vision, AI Models",
            "runway_days": 365,
            "pecc_score": 90,
            "upe_score": 9.2,
            "roadmap_note": "Focus on emerging production architectures like Explainable AI and Edge systems while leveraging your core strengths."
        }
        
    # Trigger LangGraph verification pipeline
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
