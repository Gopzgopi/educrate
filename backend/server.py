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
import logging
import time

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class ProcessingStatus(BaseModel):
    step: str
    status: str
    message: str
    timestamp: datetime

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

class KitCreateRequest(BaseModel):
    user_id: str
    topic: str
    source_content: str
    target_styles: Optional[List[LearningStyle]] = None

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
    processing_logs: List[ProcessingStatus] = []

class QASession(BaseModel):
    id: Optional[str] = None
    user_id: str
    kit_id: str
    question: str
    answer: str
    context: str
    timestamp: Optional[datetime] = None

# Local AI Service Implementation (No External APIs)
class LocalAIService:
    @staticmethod
    async def generate_summary(content: str, style: LearningStyle, language: str = "en") -> str:
        """Local AI summarization - simulated intelligent processing"""
        logger.info(f"🧠 Generating summary for {style} learners...")
        
        # Simulate processing time
        await asyncio.sleep(1.5)
        
        # Extract key points from content
        sentences = content.replace('\n', ' ').split('. ')
        key_sentences = [s.strip() + '.' for s in sentences[:3] if len(s.strip()) > 20]
        
        # Style-specific formatting
        if style == LearningStyle.VISUAL:
            summary = "📊 Visual Summary:\n\n"
            summary += "\n".join([f"• {sentence}" for sentence in key_sentences])
            summary += f"\n\n🎯 Key Concept: {content.split('.')[0]}."
            
        elif style == LearningStyle.AUDITORY:
            summary = "🎵 Audio-Friendly Summary:\n\n"
            summary += "Listen carefully to these main points:\n"
            summary += "\n".join([f"{i+1}. {sentence}" for i, sentence in enumerate(key_sentences)])
            summary += "\n\nRemember to repeat these concepts aloud for better retention."
            
        elif style == LearningStyle.TEXTUAL:
            summary = "📖 Detailed Text Summary:\n\n"
            summary += content[:300] + "...\n\n"
            summary += "Key Takeaways:\n"
            summary += "\n".join([f"- {sentence}" for sentence in key_sentences])
            
        else:  # KINESTHETIC
            summary = "🏃‍♂️ Hands-On Summary:\n\n"
            summary += "Practice these concepts through:\n"
            summary += "\n".join([f"✋ Activity: Apply '{sentence.split(' ')[0]}' in a real scenario" for sentence in key_sentences])
            
        logger.info(f"✅ Summary generated successfully for {style}")
        return summary
    
    @staticmethod
    async def generate_flashcards(content: str, count: int = 10) -> List[Dict[str, str]]:
        """Local flashcard generation"""
        logger.info(f"🎴 Generating {count} flashcards...")
        
        await asyncio.sleep(2.0)
        
        # Extract sentences and create Q&A pairs
        sentences = [s.strip() for s in content.replace('\n', ' ').split('.') if len(s.strip()) > 10]
        
        flashcards = []
        for i, sentence in enumerate(sentences[:count]):
            words = sentence.split()
            if len(words) > 5:
                # Create question by removing key word
                key_word = words[len(words)//2] if len(words) > 5 else words[-1]
                question = sentence.replace(key_word, "____")
                answer = key_word
                
                flashcards.append({
                    "question": f"Fill in the blank: {question}",
                    "answer": answer,
                    "hint": f"Think about: {sentence[:50]}..."
                })
        
        # Add some concept questions
        if len(flashcards) < count:
            topic_words = content.split()[:20]
            for word in topic_words:
                if len(word) > 5 and len(flashcards) < count:
                    flashcards.append({
                        "question": f"What is {word}?",
                        "answer": f"A key concept related to the main topic",
                        "hint": f"Context: ...{word}..."
                    })
        
        logger.info(f"✅ Generated {len(flashcards)} flashcards")
        return flashcards[:count]
    
    @staticmethod
    async def generate_audio_script(content: str, style: str = "conversational") -> str:
        """Local audio script generation"""
        logger.info(f"🎤 Generating audio script in {style} style...")
        
        await asyncio.sleep(1.8)
        
        # Create conversational audio script
        script = f"""
🎧 Audio Lesson Script - {style.title()} Style

[INTRO - Upbeat tone]
Welcome to your personalized audio lesson! Today we're exploring an exciting topic that will expand your knowledge.

[MAIN CONTENT - Clear and engaging]
Let me walk you through the key concepts:

{content[:200]}...

[INTERACTIVE ELEMENTS]
Now, let's pause here. Can you think of how this applies to your daily life?

[SUMMARY - Reinforcing tone]
To recap what we've learned:
- The main concept focuses on practical applications
- Key insights that you can implement immediately
- Connections to broader learning objectives

[OUTRO - Encouraging tone]
Great job completing this audio lesson! Remember to review these concepts and practice applying them.

[TOTAL ESTIMATED DURATION: 8-12 minutes]
"""
        
        logger.info("✅ Audio script generated successfully")
        return script
    
    @staticmethod
    async def generate_visual_description(concept: str) -> str:
        """Local visual/doodle description generation"""
        logger.info(f"🎨 Generating visual doodle description for: {concept}")
        
        await asyncio.sleep(1.2)
        
        # Create detailed visual description
        description = f"""
🎨 Doodle-Style Visual Description

MAIN CONCEPT: {concept}

Visual Elements to Draw:
━━━━━━━━━━━━━━━━━━━━

🔵 CENTRAL IMAGE:
Draw a large circle in the center representing the core concept of "{concept}". 
Use bold, simple lines - think stick figures and basic shapes.

🔗 CONNECTING BRANCHES:
From the central circle, draw 3-4 wavy lines extending outward like tree branches. 
Each branch represents a key aspect of the concept.

📝 TEXT BUBBLES:
Add small speech bubbles along each branch with 1-2 key words.
Use fun, rounded bubble shapes - no perfect circles needed!

🎯 HIGHLIGHT BOXES:
Draw rectangular boxes around the most important terms.
Make them look hand-drawn with slightly wobbly lines.

🌟 DECORATIVE ELEMENTS:
Add small stars, arrows, and simple icons around the drawing.
Use dashed lines to show connections between related ideas.

COLOR SUGGESTIONS:
- Blue for main concepts
- Orange for examples  
- Green for benefits/positives
- Purple for advanced topics

DRAWING STYLE:
Keep it simple and fun! This should look like creative notes, not perfect art.
Use thick markers or bold pencils for visibility.

ESTIMATED DRAWING TIME: 5-7 minutes
"""
        
        logger.info("✅ Visual description generated successfully")
        return description
    
    @staticmethod
    async def answer_question(question: str, context: str, user_style: LearningStyle) -> str:
        """Local QA system"""
        logger.info(f"❓ Answering question for {user_style} learner: {question[:50]}...")
        
        await asyncio.sleep(1.0)
        
        # Extract relevant context
        context_sentences = [s.strip() for s in context.split('.') if question.lower().split()[0] in s.lower()]
        relevant_context = '. '.join(context_sentences[:2]) if context_sentences else context[:100]
        
        # Style-specific answer formatting
        if user_style == LearningStyle.VISUAL:
            answer = f"""
📊 Visual Answer for: "{question}"

🎯 Direct Answer:
Based on the context, {relevant_context}.

📈 Visual Breakdown:
• Main Point → {question.split()[-1]}
• Supporting Evidence → {relevant_context.split('.')[0]}
• Application → Think of this as a flowchart where each step builds on the previous

🔍 Visual Memory Tip:
Imagine this concept as a diagram with interconnected parts!
"""
            
        elif user_style == LearningStyle.AUDITORY:
            answer = f"""
🎵 Audio Answer for: "{question}"

🗣️ Listen to this explanation:
{relevant_context}. 

🎧 Key Points to Remember:
1. The main idea is...
2. This connects to...
3. You can apply this by...

💭 Think-Aloud Strategy:
Try explaining this answer out loud to reinforce your understanding!
"""
            
        elif user_style == LearningStyle.TEXTUAL:
            answer = f"""
📖 Detailed Written Answer:

Question: {question}

Comprehensive Response:
{relevant_context}

Analysis:
The key components of this answer include multiple layers of understanding. First, we must consider the foundational concepts, then build upon them with specific examples and applications.

References:
Based on the provided context and educational principles.
"""
            
        else:  # KINESTHETIC
            answer = f"""
🏃‍♂️ Hands-On Answer for: "{question}"

✋ Interactive Response:
{relevant_context}

🔧 Try This Activity:
1. Write down the question on paper
2. Create a physical model or gesture representing the answer
3. Explain it to someone else using hand motions

🎯 Practice Application:
Find a real-world scenario where you can apply this knowledge immediately!
"""
        
        logger.info("✅ Question answered successfully")
        return answer
    
    @staticmethod
    async def suggest_study_approach(mood: MoodType, time_available: int, topic: str) -> Dict[str, Any]:
        """Local study suggestion system"""
        logger.info(f"🎯 Generating study suggestions for {mood} mood, {time_available} minutes")
        
        await asyncio.sleep(0.8)
        
        # Mood-based recommendations
        mood_strategies = {
            MoodType.FOCUSED: {
                "content_types": ["summary", "flashcards", "quiz"],
                "difficulty": "high",
                "break_frequency": 25,
                "motivation": "Perfect! Your focused state is ideal for deep learning."
            },
            MoodType.RELAXED: {
                "content_types": ["audio_lesson", "visual_doodle"],
                "difficulty": "medium",
                "break_frequency": 15,
                "motivation": "Great time to absorb information naturally and calmly."
            },
            MoodType.ENERGETIC: {
                "content_types": ["flashcards", "quiz", "visual_doodle"],
                "difficulty": "medium-high",
                "break_frequency": 20,
                "motivation": "Channel that energy into active learning!"
            },
            MoodType.STRESSED: {
                "content_types": ["audio_lesson", "summary"],
                "difficulty": "low",
                "break_frequency": 10,
                "motivation": "Take it easy. Learning should be enjoyable, not stressful."
            },
            MoodType.CURIOUS: {
                "content_types": ["summary", "visual_doodle", "audio_lesson"],
                "difficulty": "medium",
                "break_frequency": 30,
                "motivation": "Your curiosity is a superpower! Explore and discover."
            }
        }
        
        strategy = mood_strategies.get(mood, mood_strategies[MoodType.FOCUSED])
        
        suggestions = {
            "recommended_content_types": strategy["content_types"],
            "study_duration": min(time_available, 45),
            "difficulty_adjustment": strategy["difficulty"],
            "break_intervals": strategy["break_frequency"],
            "motivation_message": strategy["motivation"],
            "specific_tips": [
                f"Start with {strategy['content_types'][0]} content",
                f"Take breaks every {strategy['break_frequency']} minutes",
                f"Focus on {strategy['difficulty']} difficulty level"
            ],
            "estimated_completion": f"{min(time_available, 45)} minutes for {topic}"
        }
        
        logger.info("✅ Study suggestions generated")
        return suggestions
    
    @staticmethod
    async def create_qa_index(content: str, topic: str) -> Dict[str, Any]:
        """Local QA indexing system"""
        logger.info(f"🔍 Creating QA index for topic: {topic}")
        
        await asyncio.sleep(1.5)
        
        # Extract key terms and concepts for indexing
        sentences = content.replace('\n', ' ').split('.')
        key_terms = []
        concepts = []
        
        for sentence in sentences:
            words = sentence.strip().split()
            # Extract potential key terms (longer words)
            potential_terms = [word.strip('.,!?()[]') for word in words if len(word) > 5]
            key_terms.extend(potential_terms[:2])
            
            # Extract potential concepts (sentences with specific patterns)
            if any(indicator in sentence.lower() for indicator in ['is', 'are', 'means', 'refers to']):
                concepts.append(sentence.strip())
        
        qa_index = {
            "topic": topic,
            "key_terms": list(set(key_terms))[:10],
            "concepts": concepts[:5],
            "content_length": len(content),
            "indexed_sections": len(sentences),
            "searchable_elements": len(set(key_terms)),
            "index_created_at": datetime.utcnow(),
            "status": "ready_for_queries"
        }
        
        logger.info(f"✅ QA index created with {len(qa_index['key_terms'])} key terms")
        return qa_index

# API Endpoints

@app.get("/")
async def root():
    return {"message": "EduCrate API is running", "status": "healthy"}

@app.post("/api/users")
async def create_user(user: User):
    user.id = str(uuid.uuid4())
    user.created_at = datetime.utcnow()
    
    result = await db.users.insert_one(user.dict())
    
    if result.inserted_id:
        logger.info(f"✅ User created: {user.name} ({user.id})")
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
    
    logger.info(f"✅ Assessment saved for user {user_id}, dominant styles: {dominant_styles}")
    
    return {
        "message": "Assessment saved successfully",
        "dominant_styles": dominant_styles,
        "scores": scores
    }

@app.post("/api/users/{user_id}/study-session")
async def start_study_session(user_id: str, session: StudySession):
    # Get AI suggestions based on mood and time
    suggestions = await LocalAIService.suggest_study_approach(
        session.mood, session.available_time, "general"
    )
    
    session_data = session.dict()
    session_data["id"] = str(uuid.uuid4())
    session_data["timestamp"] = datetime.utcnow()
    session_data["ai_suggestions"] = suggestions
    
    await db.study_sessions.insert_one(session_data)
    
    logger.info(f"✅ Study session started for user {user_id}")
    
    return {
        "session_id": session_data["id"],
        "suggestions": suggestions,
        "message": "Study session started"
    }

@app.post("/api/kit/create")
async def create_learning_kit(request: KitCreateRequest):
    """NEW ENDPOINT: Create learning kit with detailed logging"""
    
    logger.info(f"🚀 Starting kit creation for user {request.user_id}")
    logger.info(f"📚 Topic: {request.topic}")
    
    # Get user's learning preferences if not specified
    if not request.target_styles:
        user = await db.users.find_one({"id": request.user_id}, {"_id": 0})
        if user:
            request.target_styles = user.get("learning_styles", [LearningStyle.TEXTUAL])
        else:
            request.target_styles = [LearningStyle.TEXTUAL]
    
    # Initialize kit
    kit_id = str(uuid.uuid4())
    processing_logs = []
    
    def add_log(step: str, status: str, message: str):
        log = ProcessingStatus(
            step=step,
            status=status,
            message=message,
            timestamp=datetime.utcnow()
        )
        processing_logs.append(log.dict())
        logger.info(f"📝 {step}: {message}")
    
    try:
        add_log("initialization", "started", f"Initializing kit creation for topic: {request.topic}")
        
        # Generate content for each learning style
        content_items = []
        
        for style in request.target_styles:
            add_log(f"{style}_processing", "started", f"Processing content for {style} learners...")
            
            if style == LearningStyle.TEXTUAL:
                # Generate summary
                add_log("summarizing", "in_progress", "📖 Analyzing content and generating summary...")
                summary = await LocalAIService.generate_summary(request.source_content, style)
                content_items.append({
                    "type": ContentType.SUMMARY,
                    "learning_style": style,
                    "content": summary,
                    "metadata": {"word_count": len(summary.split()), "generated_at": datetime.utcnow()}
                })
                add_log("summarizing", "completed", "✅ Summary generated successfully")
                
                # Generate flashcards
                add_log("flashcards", "in_progress", "🎴 Creating interactive flashcards...")
                flashcards = await LocalAIService.generate_flashcards(request.source_content)
                content_items.append({
                    "type": ContentType.FLASHCARDS,
                    "learning_style": style,
                    "content": flashcards,
                    "metadata": {"card_count": len(flashcards), "generated_at": datetime.utcnow()}
                })
                add_log("flashcards", "completed", f"✅ Generated {len(flashcards)} flashcards")
            
            elif style == LearningStyle.AUDITORY:
                add_log("audio", "in_progress", "🎤 Generating audio lesson script...")
                audio_script = await LocalAIService.generate_audio_script(request.source_content)
                content_items.append({
                    "type": ContentType.AUDIO_LESSON,
                    "learning_style": style,
                    "content": audio_script,
                    "metadata": {"duration_estimate": "10-15 minutes", "generated_at": datetime.utcnow()}
                })
                add_log("audio", "completed", "✅ Audio lesson script generated")
            
            elif style == LearningStyle.VISUAL:
                add_log("doodle", "in_progress", "🎨 Creating visual doodle descriptions...")
                visual_description = await LocalAIService.generate_visual_description(request.topic)
                content_items.append({
                    "type": ContentType.VISUAL_DOODLE,
                    "learning_style": style,
                    "content": visual_description,
                    "metadata": {"complexity": "medium", "generated_at": datetime.utcnow()}
                })
                add_log("doodle", "completed", "✅ Visual doodle description created")
        
        # Create QA index
        add_log("qa_index", "in_progress", "🔍 Building QA search index...")
        qa_index = await LocalAIService.create_qa_index(request.source_content, request.topic)
        add_log("qa_index", "completed", "✅ QA index created and ready for queries")
        
        # Create final learning kit
        kit = LearningKit(
            id=kit_id,
            user_id=request.user_id,
            topic=request.topic,
            source_content=request.source_content,
            content_items=content_items,
            learning_styles=request.target_styles,
            difficulty_level="medium",
            estimated_time=len(content_items) * 10,  # 10 minutes per content item
            created_at=datetime.utcnow(),
            processing_logs=processing_logs
        )
        
        # Save to database
        await db.learning_kits.insert_one(kit.dict())
        
        add_log("completion", "success", f"🎉 Learning kit '{request.topic}' created successfully!")
        
        logger.info(f"✅ Kit creation completed: {kit_id}")
        
        return {
            "success": True,
            "message": "Learning kit created successfully",
            "kit": kit.dict(),
            "content_count": len(content_items),
            "processing_logs": processing_logs,
            "qa_index": qa_index
        }
    
    except Exception as e:
        add_log("error", "failed", f"❌ Error during kit creation: {str(e)}")
        logger.error(f"❌ Kit creation failed: {str(e)}")
        
        # Save partial kit with error info
        error_kit = {
            "id": kit_id,
            "user_id": request.user_id,
            "topic": request.topic,
            "status": "failed",
            "error": str(e),
            "processing_logs": processing_logs,
            "created_at": datetime.utcnow()
        }
        
        await db.learning_kits.insert_one(error_kit)
        
        raise HTTPException(status_code=500, detail=f"Kit creation failed: {str(e)}")

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
    kit = await db.learning_kits.find_one({"id": kit_id}, {"_id": 0})
    if not kit:
        raise HTTPException(status_code=404, detail="Learning kit not found")
    
    # Get user's learning style for personalized answer
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    user_style = user.get("learning_styles", [LearningStyle.TEXTUAL])[0]
    
    # Generate AI answer
    context = kit["source_content"]
    answer = await LocalAIService.answer_question(question, context, user_style)
    
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
    
    logger.info(f"✅ Question answered for user {user_id}")
    
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
    kits_cursor = db.learning_kits.find({"user_id": user_id}, {"_id": 0})
    kits = await kits_cursor.to_list(length=None)
    
    style_usage = {}
    for kit in kits:
        for style in kit.get("learning_styles", []):
            style_usage[style] = style_usage.get(style, 0) + 1
    
    # Recent activity
    recent_kits_cursor = db.learning_kits.find({"user_id": user_id}, {"_id": 0}).sort("created_at", -1).limit(5)
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