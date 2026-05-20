"""
Air Quality Platform - AI Chatbot Routes
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    current_aqi: Optional[float] = None
    location: Optional[str] = None
    temperature: Optional[float] = None


@router.post("/chat")
async def chat(msg: ChatMessage):
    """Chat with the AI Health Assistant."""
    from backend.ml_models.model_manager import model_manager
    context = {}
    if msg.current_aqi:
        context["current_aqi"] = msg.current_aqi
    if msg.location:
        context["location"] = msg.location
    if msg.temperature:
        context["temperature"] = msg.temperature
    return model_manager.chat(msg.message, context)


@router.get("/chat/history")
async def chat_history():
    """Get chat conversation history."""
    from backend.ml_models.nlp_assistant import nlp_assistant
    return {"history": nlp_assistant.get_history()}
