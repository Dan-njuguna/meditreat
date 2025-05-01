#!/usr/bin/env python3

"""
AUTHOR: Dan Njuguna
DATE: 2025-05-01

DESCRIPTION:
    - `Meditreat`, a medical chatbot that provides information about
        various medical conditions and treatments as well as recommends better
        dietary improvements to accelerate healing.
"""

import os
import sys
sys.dont_write_bytecode = True
from openai import OpenAI

from openai import RateLimitError, OpenAIError
import logging
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
os.makedirs("../logs", exist_ok=True)
file_handler = logging.FileHandler("../logs/chatbot.log")
stream_handler = logging.StreamHandler()
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Constants
with open(os.path.join(os.path.dirname(__file__), "prompts/agent.txt"), "r") as f:
    SYSTEM_PROMPT = f.read()
MODEL_ID = os.getenv("MODEL_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY is None:
    logger.error("OPENAI_API_KEY environment variable not set.")

client = OpenAI(api_key=OPENAI_API_KEY)


class Chatbot:
    def __init__(self):
        self.model_id = MODEL_ID
        self.instruction = SYSTEM_PROMPT

    def chat(self, query: str) -> str:
        logger.info(f"User query was sampled to be: {query[:10]} ...")
        try:
            response = client.chat.completions.create(model=self.model_id,
            messages=[
                {"role": "system", "content": self.instruction},
                {"role": "user", "content": query}
            ])
            message = response.choices[0].message.content
            logger.info(f"Meditreat response to user query: {message[:10]} ...")

        except RateLimitError:
            logger.error("Insufficient quota: please check your plan and billing details. RATELIMITERROR")
            message = "Experiencing errors processing your request, please try again later!"
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            message = "Experiencing errors processing your request, please try again later!"

        return message