#!/usr/bin/env python3

"""
AUTHOR: Dan Njuguna
DATE: 2025-08-30

DESCRIPTION:
    This module defines the types used throughout the application.
    It provides type aliases and shared data structures.
"""

from enum import Enum

class Sender(Enum):
    USER = "user"
    SYSTEM = "assistant"
