#!/usr/bin/env python3
"""
AUTHOR: Dan Njuguna
DATE: 2025-09-07

DESCRIPTION:
    This module defines the API endpoints for the application.
    It allows retrieval of past user conversations and
    interaction with the selected LLM.
"""

from fastapi import FastAPI, HTTPException, status, WebSocket, WebSocketDisconnect
from utils.config import setup_logger, setup_async_logger
from fastapi.middleware.cors import CORSMiddleware
from memory.supabase import SupabaseMemoryManager
from utils.messages import extract_ai_message
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from models.supabase import MessageRecord
from llms.models import AIChatCore
from utils.config import settings
from llms.factory import get_llm
from utils.types import Sender
from models.api import (
    UserInput
)
import json

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

@app.websocket("/ws/chat")
async def chat(
    websocket: WebSocket
):
    """
    This endpoint handles user chat input and returns
    a response from the selected LLM with persistent memory.
    """
    await websocket.accept()
    try:
        raw = await websocket.receive_json()
        user_input = UserInput.model_validate(raw)
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
        context_summary = await model.summarize(context_str)

        logger.info(f"Context summary generated: {context_summary}")
        ai_tokens = []
        async for token in model.generate(user_input.message, context_str):
            await websocket.send_text(token)
            ai_tokens.append(token)
        ai_message_str = ''.join(ai_tokens)
        await websocket.send_text("[DONE]")
        logger.info(f"Completed response for user {user_input.user_id}")

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
            message=ai_message_str,
            meta={
            "chat_id": user_input.chat_id,
            "llm_provider": user_input.llm,
            "temperature": user_input.temperature
            }
        )

        # Persist to Supabase asynchronously
        try:
            await supabase_manager.add_message_record(user_message)
            await supabase_manager.add_message_record(ai_message)
            logger.info("Messages persisted to Supabase successfully")
        except Exception as e:
            logger.error(f"Failed to persist messages to Supabase: {e}")
    
    except WebSocketDisconnect as we:
        logger.error(f"Error to work with websocket: {we}")

    except Exception as e:
        logger.error(f"Error in /ws/chat endpoint: {e}")
        try:
            await websocket.send_text(f"[ERROR] {e}")
            logger.debug(f"Sent error message to client: {e}")
        except Exception:
            pass

# TODO: Health check endpoint
@app.get("/health")
async def health_check():
    """
    This endpoint checks the health of the API.
    """
    return JSONResponse(content={"status": "ok"}, status_code=status.HTTP_200_OK)
