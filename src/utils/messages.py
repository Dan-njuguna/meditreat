#!/usr/bin/env python3

"""
AUTHOR: Dan njuguna
DATE: 07-09-2025

DESCRIPTION:
    This modile defines the tool to use to extract AI Message bodies from langchain response dict.
"""

from langchain_core.messages import AIMessage
from typing import Dict
from utils.config import setup_logger

logger = setup_logger(__name__)

def extract_ai_message(response_json: Dict) -> str:
    """
    Extract the AI's message content from the response JSON.
    """
    messages = response_json.get("messages", [])

    # Normalize messages into a list of dict-like objects
    ai_messages = []
    for msg in messages:
        if isinstance(msg, AIMessage):
            if msg.content and isinstance(msg.content, str):
                ai_messages.append({"content": msg.content})
            else:
                logger.warning(f"AIMessage with invalid content: {msg}")
        elif isinstance(msg, dict):
            ai_messages.append(msg)
        else:
            logger.warning(f"Unexpected message format: {msg}")

            # Handle AIMessage objects with additional_kwargs
            if isinstance(msg, AIMessage):
                additional_kwargs = getattr(msg, "additional_kwargs", {})
                if "tool_calls" in additional_kwargs:
                    logger.debug(f"Tool calls found in AIMessage: {additional_kwargs['tool_calls']}")

    # Step 1: Try last non-empty AI message with valid string content
    for msg in reversed(ai_messages):
        content = msg["content"] if isinstance(msg, dict) and "content" in msg else None
        if content and isinstance(content, str) and content.strip():
            return content.strip()

    # Step 2: Fallback → first AIMessage with valid string content
    for msg in ai_messages:
        content = msg["content"] if isinstance(msg, dict) and "content" in msg else None
        if content and isinstance(content, str):
            return content.strip()

    # Step 3: Log a warning and return a default message
    logger.warning("No valid AI message content found in response.")
    return "I'm sorry, I couldn't generate a response. Please try again."
