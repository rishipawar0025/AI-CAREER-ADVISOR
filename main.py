import os
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from graph import run_sdr_pipeline  

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
    target_role: str  

llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.3  
)

@app.post("/analyze")
def analyze_skills_pipeline(payload: AnalyzeRequest):
    skills_input = payload.tech_stack
    role_input = payload.target_role
    
    # 🚀 Step 1: Invoking LangGraph State Pipeline for Academic Validation
    graph_result = run_sdr_pipeline(skills_input)
    
    # Universal Corporate Analytics Calculations (Fallback metrics layer)
    total_skills = len(skills_input)
    calculated_pecc = min(95, 60 + (total_skills * 5))
    calculated_upe = min(9.8, round(3.5 + (total_skills * 0.6), 1))
    
    legacy_keywords = ["excel basic", "data entry", "jquery", "cold calling", "manual filing"]
    has_legacy = any(any(l in s.lower() for l in legacy_keywords) for s in skills_input)
    calculated_sdr = 90 if has_legacy else 365
    
    # Domain-Agnostic Corporate Prompting Template
    prompt = (
        f"You are an Elite Corporate Career Strategy Advisor. Analyze the user's skill set: {skills_input} "
        f"against the target corporate role: '{role_input}'. "
        f"Provide a razor-sharp, exact 2-line strategic upskilling or transition roadmap "
        f"focusing on high-impact corporate, tech, or management standards relevant to this specific domain."
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Returning LangGraph trend logs alongside calculations
    return {
        "trend_notes": graph_result["trend_notes"],  # Extracted from LangGraph State mapping
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