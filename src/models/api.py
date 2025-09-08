#!/usr/bin/env python3

"""
AUTHOR: Dan Njuguna
DATE: 2025-09-07

DESCRIPTION:
This module defines the API inputs and outputs for the
meditreat application.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class UserInput(BaseModel):
    """
    This class defines the structure of user input
    to the API.
    """
    user_id: str
    chat_id: str
    message: str
    username: Optional[str] = "User"
    llm: Optional[str] = "openai"
    temperature: Optional[float] = 0.2

class StreamingChatInput(BaseModel):
    """
    Input model for streaming chat requests.
    """
    user_id: str
    message: str
    llm_provider: Optional[str] = "openai"
    enable_search: Optional[bool] = True
    session_id: Optional[str] = None

class AgentStepResponse(BaseModel):
    """
    Represents a single step in the agent's process.
    """
    step_type: str  # "thinking", "searching", "analyzing", "responding", "error"
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """
    Standard response for non-streaming chat.
    """
    message: str
    user_id: str
    timestamp: datetime
    sources: Optional[List[Dict[str, str]]] = None

