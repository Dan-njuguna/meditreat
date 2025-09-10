#!/usr/bin/env python3

"""
AUTHOR: Dan Njuguna
DATE: 2025-09-07

DESCRIPTION: Base class for all LLMs in the application.
"""

from utils.config import setup_logger
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator

logger = setup_logger("llm_base.log")

class LLMBase(ABC):
    """Base wrapper for any LangChain LLM."""

    def __init__(
        self,
        llm,
    ):
        self.llm = llm
        logger.info(f"{self.__class__.__name__} initialized with {llm.__class__.__name__}")

    @abstractmethod
    async def generate(self, prompt: str, context: str, **kwargs: Any) -> AsyncGenerator[str, None]:
        """Generate a response from the LLM."""
        if False:
            yield ""
        raise NotImplementedError("Subclasses must implement generate method.")
