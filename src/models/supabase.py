#!/usr/bin/env python3

"""
AUTHOR: Dan Njuguna
DATE: 2025-09-07

DESCRIPTION:
    This module defines the Supabase data models for the application.
    It provides the structure for user messages and conversation history.
"""

from pydantic import BaseModel, Field
from utils.types import Sender
from datetime import datetime
from typing import Optional

class MessageRecord(BaseModel):
    """
    Represents a message in the database (whether from user or system).
    """
    user_id: str = Field(
        description="The ID of the user who sent the message, optional for " \
        "the case of system messages.",
    )
    chat_id: str = Field(
        description="The ID of the chat this message belongs to."
    )
    sender: Sender = Field(
        description="The sender of the message.",
        default=Sender.SYSTEM
    )
    message: str = Field(
        description="The content of the message.",
        default=""
    )
    meta: Optional[dict] = Field(
        description="Additional metadata about the message.",
        default=None
    )
    timestamp: datetime = Field(
        description="The timestamp of when the message was sent.",
        default_factory=datetime.now
    )
