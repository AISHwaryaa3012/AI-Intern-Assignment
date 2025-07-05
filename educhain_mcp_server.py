"""
EduChain MCP Server - Corrected Version
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
from dotenv import load_dotenv
from educhain import Educhain

# Load environment variables
load_dotenv()

# Verify API key is set
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY not found in environment variables")

app = FastAPI(
    title="EduChain MCP Server",
    version="1.0.0",
    description="Educational content generation server"
)

# Initialize Educhain
edu_chain = Educhain()

class MCQRequest(BaseModel):
    topic: str
    num_questions: int = 5
    difficulty: Optional[str] = "medium"

class LessonPlanRequest(BaseModel):
    subject: str
    grade_level: Optional[str] = "middle school"
    duration: Optional[str] = "1 hour"

@app.post("/tools/generate_mcqs")
async def generate_mcqs(request: MCQRequest):
    try:
        questions = edu_chain.generate_questions(
            topic=request.topic,
            num_questions=request.num_questions,
            difficulty=request.difficulty,
            question_type="mcq"
        )
        return {"status": "success", "questions": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/resources/get_lesson_plan")
async def get_lesson_plan(request: LessonPlanRequest):
    try:
        plan = edu_chain.generate_lesson_plan(
            subject=request.subject,
            grade_level=request.grade_level,
            duration=request.duration
        )
        return {"status": "success", "lesson_plan": plan}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def run_server():
    uvicorn.run(
        "educhain_mcp_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    run_server()