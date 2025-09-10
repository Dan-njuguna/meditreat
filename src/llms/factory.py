#!/usr/bin/env python3

"""
AUTHOR: Dan Njuguna
DATE: 2025-09-07

DESCRIPTION:
    This module describes the default factory for selecting llms
    to work with when running requests in the application.
"""

from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent
from utils.config import setup_logger, settings
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

logger = setup_logger("llm_factory.log")

def get_llm(llm_name: str = "openai"):
    """
    This function returns the default llm to work with,
    as selected by the user in the dropdown for models.
    Defaults to OpenAI model
    Returns an LLM client instance.
    Priority:
      1. Explicit llm_name argument
      2. LLM_PROVIDER env variable
      3. Default = OpenAI GPT-4o-mini
    """
    model_name = settings.get("model_name", "gpt-4o-mini")
    if llm_name == "openai":
        llm = ChatOpenAI(
            model=model_name,
            temperature=settings.get("temperature", 0),
            api_key=settings.get("openai_api_key"),
            base_url=settings.get("base_url"),
            streaming=True
        )
        search_tool = DuckDuckGoSearchRun()
        agent = create_react_agent(
            tools=[search_tool],
            model=llm
        )
        return agent
    elif llm_name == "anthropic":
        logger.info("Using Anthropic as the LLM provider")
        model = ChatAnthropic(
            model_name="claude-3",
            temperature=0,
            api_key=settings.get("ANTROPIC_API_KEY", ""),
            timeout=60,
            stop=None
        )
        return model
    else:
        logger.debug(f"LLM provider {llm_name} not supported, defaulting to OpenAI")
        llm = ChatOpenAI(
            model=model_name,
            temperature=settings.get("temperature", 0),
            api_key=settings.get("openai_api_key"),
            base_url=settings.get("base_url"),
            streaming=True
        )
        search_tool = DuckDuckGoSearchRun()
        agent = create_react_agent(
            tools=[search_tool],
            model=llm
        )
        return agent
