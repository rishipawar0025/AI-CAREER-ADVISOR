import os
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

app = FastAPI(title="SkillRadar AI - Universal Corporate Analytics API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    tech_stack: List[str]
    target_role: str  # Added target_role to payload for multi-domain analysis

# Initialize universal token engine execution
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.3  # Slightly increased for more creative corporate roadmaps
)

@app.post("/analyze")
def analyze_skills_pipeline(payload: AnalyzeRequest):
    skills_input = payload.tech_stack
    role_input = payload.target_role
    
    # Universal Corporate Analytics Calculations
    total_skills = len(skills_input)
    
    # 1. PECC calculation core logic parameters (Dynamic Scaling)
    # More diverse corporate skills mean higher enterprise readiness coverage
    calculated_pecc = min(95, 60 + (total_skills * 5))
    
    # 2. Dynamic SDR values calculation (Universal Shelf-Life calculation)
    # Legacy tools or repetitive admin tasks score lower, modern strategies score higher
    legacy_keywords = ["excel basic", "data entry", "jquery", "cold calling", "manual filing"]
    has_legacy = any(any(l in s.lower() for l in legacy_keywords) for s in skills_input)
    calculated_sdr = 90 if has_legacy else 365
    
    # 3. UPE evaluation calculations (Adaptability Index)
    calculated_upe = min(9.8, round(3.5 + (total_skills * 0.6), 1))
    
    # Domain-Agnostic Corporate Prompting Template
    prompt = (
        f"You are an Elite Corporate Career Strategy Advisor. Analyze the user's skill set: {skills_input} "
        f"against the target corporate role: '{role_input}'. "
        f"Provide a razor-sharp, exact 2-line strategic upskilling or transition roadmap "
        f"focusing on high-impact corporate, tech, or management standards relevant to this specific domain."
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        "trend_notes": [f"Processed {total_skills} domain parameters securely."],
        "results": [
            {
                "tech": ", ".join(skills_input),
                "runway_days": calculated_sdr,
                "status": "watch" if calculated_sdr < 180 else "healthy",
                "replacement_trend": "AI-Driven Automation / Agile Frameworks / Modern Business Analytics",
                "pecc_score": calculated_pecc,
                "upe_score": calculated_upe,
                "note": response.content
            }
        ]
    }