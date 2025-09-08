#!/usr/bin/env python3
"""
AUTHOR: Dan Njuguna
DATE: 2025-09-07

DESCRIPTION:
    This module defines the API endpoints for the application.
    It allows retrieval of past user conversations and
    interaction with the selected LLM.
"""

from models.api import (
    UserInput,
    ChatResponse
)
from fastapi.responses import JSONResponse
from utils.config import setup_logger, setup_async_logger
from utils.serialization import to_dict
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from memory.supabase import SupabaseMemoryManager
from models.supabase import MessageRecord
from utils.types import Sender
from llms.factory import get_llm
from llms.models import AIChatCore
from datetime import datetime
from utils.config import settings
from utils.messages import extract_ai_message

logger = setup_logger("main.log")

allowed_origins = settings.get("allowed_origins", "*").split(",")

@asynccontextmanager
async def lifespan(
    app: FastAPI
):
    """
    Setting up lifespan events for the application.
    """
    try:
        app.state.logger = await setup_async_logger("main.log")
        app.state.logger.info("Application startup: Logger initialized")

        yield
    except Exception as e:
        if hasattr(app.state, 'logger'):
            app.state.logger.error(f"Error during application lifespan: {e}")
        else:
            print(f"Error during application lifespan: {e}")

app = FastAPI(
    title="Meditreat",
    description="API for interacting with LLMs to acquire business insights and" \
                " generate business workplans.",
    version="0.1.0",
    lifespan=lifespan
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(
    user_input: UserInput
):
    """
    This endpoint handles user chat input and returns
    a response from the selected LLM with persistent memory.
    """
    try:
        # Validate user input
        if not user_input.user_id or not user_input.message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id and message are required fields."
            )
        logger.info(f"Received message from user {user_input.user_id}")

        if user_input.llm is None:
            user_input.llm = "openai"

        # Get the LLM based on user preference
        llm = get_llm(user_input.llm)

        # model
        model = AIChatCore(llm=llm)

        # Save messages to Supabase
        supabase_manager = SupabaseMemoryManager(logger)

        context = await supabase_manager.get_conversation_history(
            user_id=user_input.user_id,
            chat_id=user_input.chat_id
        )

        logger.debug(f"Retrieved context: {context}")

        context_str = "\n".join([f"{record.sender}: {record.message}" for record in context])
        context_summary = model.summarize(context_str)

        logger.info(f"Context summary generated: {context_summary}")

        response = model.generate(user_input.message, context_str)

        logger.info(f"Response generated: {response}")

        # Validate response structure
        if not isinstance(response, dict) or "messages" not in response or not response["messages"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid response structure from LLM."
            )

        message = extract_ai_message(response)
        usage = getattr(response["messages"][0], "response_metadata", {})

        # Save user message
        user_message = MessageRecord(
            user_id=user_input.user_id,
            chat_id=user_input.chat_id,
            sender=Sender.USER,
            message=user_input.message,
            meta={
                "chat_id": user_input.chat_id,
                "llm_provider": user_input.llm,
                "temperature": user_input.temperature,
                "username": user_input.username
            }
        )
        
        # Save AI response
        ai_message = MessageRecord(
            user_id=user_input.user_id,
            chat_id=user_input.chat_id,
            sender=Sender.SYSTEM,
            message=message,
            meta={
                "chat_id": user_input.chat_id,
                "llm_provider": user_input.llm,
                "temperature": user_input.temperature,
                "usage": usage
            }
        )
        
        # Persist to Supabase asynchronously
        try:
            await supabase_manager.add_message_record(user_message)
            await supabase_manager.add_message_record(ai_message)
            logger.info("Messages persisted to Supabase successfully")
        except Exception as e:
            logger.error(f"Failed to persist messages to Supabase: {e}")
        
        # Create response object
        model_response = ChatResponse(
            message=message,
            user_id=user_input.user_id,
            timestamp=datetime.now(),
            sources=None
        )

        # Use model_dump with mode='json' to ensure proper serialization
        response_dict = model_response.model_dump(mode='json')

        response = to_dict(response_dict)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response
        )

    except Exception as e:
        logger.error(f"Error in /chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request."
        )

# TODO: Health check endpoint
@app.get("/health")
async def health_check():
    """
    This endpoint checks the health of the API.
    """
    return JSONResponse(content={"status": "ok"}, status_code=status.HTTP_200_OK)
