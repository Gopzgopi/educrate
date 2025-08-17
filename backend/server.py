from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import os
from dotenv import load_dotenv
import json
import asyncio
from enum import Enum

load_dotenv()

app = FastAPI(title="EduCrate API", description="Intelligent Educational Platform")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.educrate

# Enums and Models
class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    TEXTUAL = "textual"
    KINESTHETIC = "kinesthetic"

class MoodType(str, Enum):
    FOCUSED = "focused"
    RELAXED = "relaxed"
    ENERGETIC = "energetic"
    STRESSED = "stressed"
    CURIOUS = "curious"

class ContentType(str, Enum):
    SUMMARY = "summary"
    FLASHCARDS = "flashcards"
    AUDIO_LESSON = "audio_lesson"
    VISUAL_DOODLE = "visual_doodle"
    QUIZ = "quiz"

class User(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    learning_styles: List[LearningStyle]
    preferred_language: str = "en"
    timezone: str = "UTC"
    created_at: Optional[datetime] = None

class LearningAssessment(BaseModel):
    user_id: str
    visual_score: int  # 1-10
    auditory_score: int  # 1-10
    textual_score: int  # 1-10
    kinesthetic_score: int  # 1-10
    answers: Dict[str, Any]

class StudySession(BaseModel):
    user_id: str
    mood: MoodType
    available_time: int  # minutes
    energy_level: int  # 1-10
    focus_level: int  # 1-10
    preferred_content_types: List[ContentType]

class LearningKit(BaseModel):
    id: Optional[str] = None
    user_id: str
    topic: str
    source_content: str
    content_items: List[Dict[str, Any]]
    learning_styles: List[LearningStyle]
    difficulty_level: str
    estimated_time: int  # minutes
    created_at: Optional[datetime] = None

class QASession(BaseModel):
    id: Optional[str] = None
    user_id: str
    kit_id: str
    question: str
    answer: str
    context: str
    timestamp: Optional[datetime] = None

# AI Service Interface (Placeholder for local models)
class AIService:
    @staticmethod
    async def generate_summary(content: str, style: LearningStyle, language: str = "en") -> str:
        """Placeholder for local AI summarization"""
        # This will be replaced with your local model calls
        return f"AI-generated summary for {style} learners: {content[:200]}..."
    
    @staticmethod
    async def generate_flashcards(content: str, count: int = 10) -> List[Dict[str, str]]:
        """Placeholder for flashcard generation"""
        # This will be replaced with your local model calls
        return [
            {"question": f"Question {i+1} about the topic", "answer": f"Answer {i+1}"}
            for i in range(count)
        ]
    
    @staticmethod
    async def generate_audio_script(content: str, style: str = "conversational") -> str:
        """Placeholder for audio lesson script generation"""
        return f"Audio script for {style} style: {content}"
    
    @staticmethod
    async def generate_visual_description(concept: str) -> str:
        """Placeholder for visual/doodle description generation"""
        return f"Visual description for concept: {concept}"
    
    @staticmethod
    async def answer_question(question: str, context: str, user_style: LearningStyle) -> str:
        """Placeholder for QA system"""
        return f"Answer tailored for {user_style} learner: Based on the context, {question} can be answered as..."
    
    @staticmethod
    async def suggest_study_approach(mood: MoodType, time_available: int, topic: str) -> Dict[str, Any]:
        """Placeholder for study suggestions based on mood and time"""
        suggestions = {
            "recommended_content_types": ["summary", "flashcards"],
            "study_duration": min(time_available, 30),
            "difficulty_adjustment": "medium",
            "break_intervals": 5,
            "motivation_message": f"Perfect time to explore {topic}!"
        }
        return suggestions

# API Endpoints

@app.get("/")
async def root():
    return {"message": "EduCrate API is running"}

@app.post("/api/users")
async def create_user(user: User):
    user.id = str(uuid.uuid4())
    user.created_at = datetime.utcnow()
    
    result = await db.users.insert_one(user.dict())
    
    if result.inserted_id:
        return {"message": "User created successfully", "user_id": user.id}
    raise HTTPException(status_code=400, detail="User creation failed")

@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/api/users/{user_id}/assessment")
async def save_learning_assessment(user_id: str, assessment: LearningAssessment):
    # Calculate dominant learning styles
    scores = {
        "visual": assessment.visual_score,
        "auditory": assessment.auditory_score,
        "textual": assessment.textual_score,
        "kinesthetic": assessment.kinesthetic_score
    }
    
    # Determine top learning styles (score >= 7)
    dominant_styles = [style for style, score in scores.items() if score >= 7]
    if not dominant_styles:
        dominant_styles = [max(scores, key=scores.get)]
    
    # Update user profile
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"learning_styles": dominant_styles}}
    )
    
    # Save assessment
    assessment_data = assessment.dict()
    assessment_data["id"] = str(uuid.uuid4())
    assessment_data["timestamp"] = datetime.utcnow()
    
    await db.assessments.insert_one(assessment_data)
    
    return {
        "message": "Assessment saved successfully",
        "dominant_styles": dominant_styles,
        "scores": scores
    }

@app.post("/api/users/{user_id}/study-session")
async def start_study_session(user_id: str, session: StudySession):
    # Get AI suggestions based on mood and time
    suggestions = await AIService.suggest_study_approach(
        session.mood, session.available_time, "general"
    )
    
    session_data = session.dict()
    session_data["id"] = str(uuid.uuid4())
    session_data["timestamp"] = datetime.utcnow()
    session_data["ai_suggestions"] = suggestions
    
    await db.study_sessions.insert_one(session_data)
    
    return {
        "session_id": session_data["id"],
        "suggestions": suggestions,
        "message": "Study session started"
    }

@app.post("/api/learning-kits")
async def create_learning_kit(
    user_id: str,
    topic: str,
    source_content: str,
    target_styles: List[LearningStyle] = None
):
    # Get user's learning preferences if not specified
    if not target_styles:
        user = await db.users.find_one({"id": user_id})
        target_styles = user.get("learning_styles", [LearningStyle.TEXTUAL])
    
    # Generate content for each learning style
    content_items = []
    
    for style in target_styles:
        if style == LearningStyle.TEXTUAL:
            summary = await AIService.generate_summary(source_content, style)
            content_items.append({
                "type": ContentType.SUMMARY,
                "learning_style": style,
                "content": summary,
                "metadata": {"word_count": len(summary.split())}
            })
            
            flashcards = await AIService.generate_flashcards(source_content)
            content_items.append({
                "type": ContentType.FLASHCARDS,
                "learning_style": style,
                "content": flashcards,
                "metadata": {"card_count": len(flashcards)}
            })
        
        elif style == LearningStyle.AUDITORY:
            audio_script = await AIService.generate_audio_script(source_content)
            content_items.append({
                "type": ContentType.AUDIO_LESSON,
                "learning_style": style,
                "content": audio_script,
                "metadata": {"duration_estimate": "10-15 minutes"}
            })
        
        elif style == LearningStyle.VISUAL:
            visual_description = await AIService.generate_visual_description(topic)
            content_items.append({
                "type": ContentType.VISUAL_DOODLE,
                "learning_style": style,
                "content": visual_description,
                "metadata": {"complexity": "medium"}
            })
    
    # Create learning kit
    kit = LearningKit(
        id=str(uuid.uuid4()),
        user_id=user_id,
        topic=topic,
        source_content=source_content,
        content_items=content_items,
        learning_styles=target_styles,
        difficulty_level="medium",
        estimated_time=30,
        created_at=datetime.utcnow()
    )
    
    await db.learning_kits.insert_one(kit.dict())
    
    return {
        "message": "Learning kit created successfully",
        "kit": kit.dict(),
        "content_count": len(content_items)
    }

@app.get("/api/users/{user_id}/learning-kits")
async def get_user_learning_kits(user_id: str):
    cursor = db.learning_kits.find({"user_id": user_id}, {"_id": 0}).sort("created_at", -1)
    kits = await cursor.to_list(length=50)
    return {"kits": kits}

@app.get("/api/learning-kits/{kit_id}")
async def get_learning_kit(kit_id: str):
    kit = await db.learning_kits.find_one({"id": kit_id}, {"_id": 0})
    if kit:
        return kit
    raise HTTPException(status_code=404, detail="Learning kit not found")

@app.post("/api/qa-sessions")
async def ask_question(
    user_id: str,
    kit_id: str,
    question: str
):
    # Get kit context
    kit = await db.learning_kits.find_one({"id": kit_id})
    if not kit:
        raise HTTPException(status_code=404, detail="Learning kit not found")
    
    # Get user's learning style for personalized answer
    user = await db.users.find_one({"id": user_id})
    user_style = user.get("learning_styles", [LearningStyle.TEXTUAL])[0]
    
    # Generate AI answer
    context = kit["source_content"]
    answer = await AIService.answer_question(question, context, user_style)
    
    # Save QA session
    qa_session = QASession(
        id=str(uuid.uuid4()),
        user_id=user_id,
        kit_id=kit_id,
        question=question,
        answer=answer,
        context=context,
        timestamp=datetime.utcnow()
    )
    
    await db.qa_sessions.insert_one(qa_session.dict())
    
    return {
        "answer": answer,
        "session_id": qa_session.id,
        "personalized_for": user_style
    }

@app.get("/api/users/{user_id}/analytics")
async def get_user_analytics(user_id: str):
    # Get learning statistics
    total_kits = await db.learning_kits.count_documents({"user_id": user_id})
    total_qa_sessions = await db.qa_sessions.count_documents({"user_id": user_id})
    
    # Learning style distribution
    kits_cursor = db.learning_kits.find({"user_id": user_id})
    kits = await kits_cursor.to_list(length=None)
    
    style_usage = {}
    for kit in kits:
        for style in kit.get("learning_styles", []):
            style_usage[style] = style_usage.get(style, 0) + 1
    
    # Recent activity
    recent_kits_cursor = db.learning_kits.find({"user_id": user_id}).sort("created_at", -1).limit(5)
    recent_kits = await recent_kits_cursor.to_list(length=5)
    
    return {
        "total_kits_created": total_kits,
        "total_questions_asked": total_qa_sessions,
        "learning_style_usage": style_usage,
        "recent_activity": recent_kits,
        "analytics_generated_at": datetime.utcnow()
    }

@app.get("/api/learning-assessment-questions")
async def get_assessment_questions():
    """Return learning style assessment questions"""
    questions = [
        {
            "id": 1,
            "question": "When learning something new, I prefer to:",
            "options": [
                {"value": "visual", "text": "See diagrams, charts, or visual demonstrations"},
                {"value": "auditory", "text": "Listen to explanations or discussions"},
                {"value": "textual", "text": "Read detailed written instructions"},
                {"value": "kinesthetic", "text": "Try it hands-on with practice exercises"}
            ]
        },
        {
            "id": 2,
            "question": "I remember information best when it's:",
            "options": [
                {"value": "visual", "text": "Presented with images, colors, or mind maps"},
                {"value": "auditory", "text": "Explained through verbal discussions"},
                {"value": "textual", "text": "Written in detailed notes or summaries"},
                {"value": "kinesthetic", "text": "Connected to real-world activities"}
            ]
        },
        {
            "id": 3,
            "question": "When solving problems, I tend to:",
            "options": [
                {"value": "visual", "text": "Draw sketches or visualize solutions"},
                {"value": "auditory", "text": "Talk through the problem aloud"},
                {"value": "textual", "text": "Write out step-by-step procedures"},
                {"value": "kinesthetic", "text": "Work through examples physically"}
            ]
        },
        {
            "id": 4,
            "question": "My ideal study environment includes:",
            "options": [
                {"value": "visual", "text": "Good lighting with colorful materials and visual aids"},
                {"value": "auditory", "text": "Background music or the ability to discuss topics"},
                {"value": "textual", "text": "Quiet space with books and written materials"},
                {"value": "kinesthetic", "text": "Space to move around and manipulate objects"}
            ]
        },
        {
            "id": 5,
            "question": "I understand concepts better when:",
            "options": [
                {"value": "visual", "text": "I can see the big picture through diagrams"},
                {"value": "auditory", "text": "I hear multiple perspectives and explanations"},
                {"value": "textual", "text": "I can analyze detailed written information"},
                {"value": "kinesthetic", "text": "I can apply them to real situations"}
            ]
        }
    ]
    return {"questions": questions}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)