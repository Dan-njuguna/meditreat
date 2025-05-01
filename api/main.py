#!/usr/bin/env python3
import os
import sys
sys.dont_write_bytecode = True

import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from api.chatbot import Chatbot
from api.models import UserRequest, BotResponse
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

os.makedirs("../logs", exist_ok=True)
file_handler = logging.FileHandler("../logs/api.log")
stream_handler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

app = FastAPI(title="Meditreat")

# Configure CORS to handle preflight and allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend origin
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat", response_model=BotResponse)
async def chat(request: UserRequest):
    if not request.query:
        logger.error("Empty query provided.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty."
        )
    
    bot = Chatbot()
    try:
        logger.info("Querying response from Meditreat. Passing user query ...")
        result = bot.chat(request.query)
        if result:
            return BotResponse(
                response=result,
                status="success",
                status_code=status.HTTP_200_OK
            )
        else:
            logger.warning("No response received from Chatbot.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No response from chatbot."
            )
    
    except Exception as e:
        logger.exception("Unexpected error occurred.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred."
        )