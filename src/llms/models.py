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
from utils.messages import stream_extract_message
from utils.config import setup_logger, settings
from langchain_openai import ChatOpenAI
from typing import Any, AsyncGenerator
from core.base import LLMBase

logger = setup_logger("openai_llm.log")

class AIChatCore(LLMBase):
    """
    This implements a general method that interacts with the passed llm models
    flexibly making the application more lightweight.
    """
    def __init__(self, llm):
        super().__init__(llm)

    async def generate(self, prompt: str, context: str, **kwargs: Any) -> AsyncGenerator[str, None]:
        """
        Generate a response from the AI chat model.
        :param prompt: The input prompt for the chat model.
        :param context: The chat context to include in the prompt.
        :param kwargs: Additional parameters for the chat model.

        :return: Stream AI chat model response using AsyncGenerator.
        """
        if not prompt:
            logger.error("Empty prompt provided to AI")
            yield "Invalid prompt."
            return

        user_query = prompt
        system_prompt = settings.get(
            "system_prompt",
            """
            You are MediTreat, a supportive and trustworthy medical assistant chatbot. 

            --- ROLE ---
            - Be friendly, empathetic, and conversational. 
            - Act like a medical assistant, but never claim to be a doctor.

            --- INPUTS ---
            - {context} → summary of the recent conversation and/or retrieved knowledge.
            - {user_query} → the user’s latest question.

            --- INSTRUCTIONS ---
            1. Use {context} only as background — don’t repeat it word-for-word. 
            2. Answer {user_query} naturally in clear, supportive language. 
            3. If the response involves **medical information, advice, symptoms, or treatments**, 
            add the disclaimer at the end:
            I’m not a doctor. This information is for educational purposes only. 
            Please consult a licensed healthcare professional for medical advice.
            4. If the response is just a **greeting, acknowledgement, or small talk**, 
            do **not** include the disclaimer.
            5. If the query might indicate an emergency (chest pain, severe bleeding, 
            difficulty breathing, etc.), explicitly advise seeking urgent medical help. 
            6. If unsure, be honest and recommend consulting a healthcare professional.
            """
        )
        prompt_template = ChatPromptTemplate.from_template(system_prompt)
        chain = prompt_template | self.llm

        async for chunk in chain.astream({"context": context, "user_query": user_query}, **kwargs):
            logger.info(f"Streaming chunk: {chunk}")
            for message in stream_extract_message(chunk):
                yield message

    async def summarize(self, context: str):
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

        result = await chain.ainvoke({"history": context})
        summary = result.content

        logger.info("Context successfully summarized.")
        return summary
