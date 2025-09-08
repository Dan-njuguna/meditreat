#!/usr/bin/env python3

"""
AUTHOR: Dan Njuguna
DATE: 2025-09-07

DESCRIPTION:
    This module defines the LLM client to work with
    when running requests in the application for different
    AI interfaces.
"""

from langchain_core.prompts import ChatPromptTemplate
from utils.config import setup_logger, settings
from langchain_openai import ChatOpenAI
from core.base import LLMBase
from typing import Any

logger = setup_logger("openai_llm.log")

class AIChatCore(LLMBase):
    """
    This implements a general method that interacts with the passed llm models
    flexibly making the application more lightweight.
    """
    def __init__(self, llm):
        super().__init__(llm)

    def generate(self, prompt: str, context: str, **kwargs: Any):
        """
        Generate a response from the AI chat model.
        :param prompt: The input prompt for the chat model.
        :param context: The chat context to include in the prompt.
        :param kwargs: Additional parameters for the chat model.

        :return: The generated response from the chat model.
        """
        if not prompt:
            logger.error("Empty prompt provided to AI")
            return "Invalid prompt."
        
        user_query = prompt
        system_prompt = settings.get(
            "system_prompt", 
            "You are a helpful assistant. Always use web search to provide up-to-date and location-specific insights. Context for past chats is: {context}. Search and respond to: {user_query}"
        )

        prompt_template = ChatPromptTemplate.from_template(system_prompt)

        chain = prompt_template | self.llm

        if kwargs:
            response = chain.invoke({"context": context, "user_query": user_query}, **kwargs)
            logger.info(f"Response from llm: {response}")
        else:
            response = chain.invoke({"context": context, "user_query": user_query})
        
        logger.info("Successfully received response from AI")
        return response

    def summarize(self, context: str):
        """Summarize the given context using the loaded prompt."""
        prompt = ChatPromptTemplate.from_template(
            "Summarize the chat history in reported speech in less than 100 words: {history}"
        )
        llm = ChatOpenAI(
            model=settings.get("model_name", "gpt-4o-mini"),
            temperature=settings.get("temperature", 0),
            api_key=settings.get("openai_api_key"),
            base_url=settings.get("base_url")
        )
        if not context.strip():
            logger.warning("Empty context provided for summarization.")
            return "No context available."
        
        chain = prompt | llm

        result = chain.invoke({"history": context})
        summary = result.content

        logger.info("Context successfully summarized.")
        return summary
