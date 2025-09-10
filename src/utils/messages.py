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

def stream_extract_message(chunk) -> list[str]:
    """
    Extract message strings from a streaming chunk (dict, object, or JSON string).
    Returns a list of message strings.
    """
    import json
    messages = []
    # If chunk is an object with .content
    if hasattr(chunk, "content") and isinstance(chunk.content, str):
        messages.append(chunk.content)
    # If chunk is a dict
    elif isinstance(chunk, dict):
        # Try to extract 'content' directly
        if "content" in chunk and isinstance(chunk["content"], str):
            messages.append(chunk["content"])
        # Or look for messages in nested dicts
        elif "agent" in chunk and "messages" in chunk["agent"]:
            for msg in chunk["agent"]["messages"]:
                if hasattr(msg, "content") and isinstance(msg.content, str):
                    messages.append(msg.content)
                elif isinstance(msg, dict) and "content" in msg and isinstance(msg["content"], str):
                    messages.append(msg["content"])
    # If chunk is a JSON string
    elif isinstance(chunk, str) and chunk.startswith("{"):
        try:
            data = json.loads(chunk)
            if "content" in data and isinstance(data["content"], str):
                messages.append(data["content"])
            elif "agent" in data and "messages" in data["agent"]:
                for msg in data["agent"]["messages"]:
                    if isinstance(msg, dict) and "content" in msg and isinstance(msg["content"], str):
                        messages.append(msg["content"])
        except Exception:
            messages.append(str(chunk))
    else:
        messages.append(str(chunk))
    return messages
