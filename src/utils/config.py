#!/usr/bin/env python3

"""
AUTHOR: Dan njuguna
DATE: 07-09-2025

DESCRIPTION:
    This modile defines the configurations and utilities for the application.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger as loguru_logger
from loguru._logger import Logger
from decouple import config
from typing import cast
import logging
import os, sys

basedir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def setup_logger(
    file_name: str
) -> Logger | logging.Logger:
    """
    This module creates a synchronous logger for the application
    with a fallback for the default logger.
    """
    try:
        logsdir = os.path.join(basedir, "logs")
        if not os.path.exists(logsdir):
            os.makedirs(logsdir)

        if os.path.basename(file_name).endswith(".log"):
            loguru_logger.remove()
            loguru_logger.add(
                f"{logsdir}/{file_name}",
                format="{time} {level} {message}",
                level="DEBUG",
                rotation="10 MB",
                compression="zip",
            )
            loguru_logger.add(
                sys.stdout,
                format="{time} {level} {message}",
                level="INFO",
            )
            return cast(Logger, loguru_logger)
        else:
            file_name += ".log"
            loguru_logger.remove()
            loguru_logger.add(
                f"{logsdir}/{file_name}",
                format="{time} {level} {message}",
                level="DEBUG",
                rotation="10 MB",
                compression="zip",
            )
            loguru_logger.add(
                sys.stdout,
                format="{time} {level} {message}",
                level="INFO",
            )
            return cast(Logger, loguru_logger)

    except Exception as e:
        print(f"Error setting up loguru logger: {e}... \n Falling back to default logger.")
        logger = logging.getLogger(file_name.endswith(".log") and file_name or file_name + ".log")
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(file_name.endswith(".log") and file_name or file_name + ".log")
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger

# TODO: Create global async logger for the application
async def setup_async_logger(
    file_name: str
) -> Logger | logging.Logger:
    """
    This module creates an asyncronous logger for the application
    with a fallback for the default logger.
    """
    try:
        logsdir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        if not os.path.exists(logsdir):
            os.makedirs(logsdir)
        if os.path.basename(file_name).endswith(".log"):
            loguru_logger.remove()
            loguru_logger.add(
                f"{logsdir}/{file_name}",
                format="{time} {level} {message}",
                level="DEBUG",
                rotation="10 MB",
                compression="zip",
            )
            loguru_logger.add(
                sys.stdout,
                format="{time} {level} {message}",
                level="INFO",
            )
            return cast(Logger, loguru_logger)
        else:
            file_name += ".log"
            loguru_logger.remove()
            loguru_logger.add(
                f"{logsdir}/{file_name}",
                format="{time} {level} {message}",
                level="DEBUG",
                rotation="10 MB",
                compression="zip",
            )
            loguru_logger.add(
                sys.stdout,
                format="{time} {level} {message}",
                level="INFO",
            )
            return cast(Logger, loguru_logger)

    except Exception as e:
        print(f"Error setting up loguru logger: {e}... \n Falling back to default logger.")
        logger = logging.getLogger(file_name.endswith(".log") and file_name or file_name + ".log")
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(file_name.endswith(".log") and file_name or file_name + ".log")
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger

def load_system_prompt():
    """Loads the system prompt to the settings for use in LLMs.
    """
    try:
        with open(os.path.join(basedir, "src", "prompts", "base_system_prompt.txt")) as f:
            prompt = f.read()
            return prompt
    except Exception as e:
        loguru_logger.error(f"Error loading system prompt: {e}")
        return "You are a helpful assistant."

class Settings(BaseSettings):
    """
    This class defines the application settings using Pydantic BaseSettings.
    It loads configurations from environment variables and a .env file.
    """
    # API and LLM Configuration
    allowed_origins: str = str(config('ALLOWED_ORIGINS', default="*"))
    openai_api_key: str = str(config('OPENAI_API_KEY', default=""))
    llm_provider: str = str(config('LLM_PROVIDER', default="openai"))
    base_url: str = str(config('BASE_URL', default="https://models.inference.ai.azure.com/"))
    model_name: str = str(config('MODEL_NAME', default="gpt-4o-mini"))
    temperature: float = float(config('TEMPERATURE', default=0.1))
    max_tokens: int = int(config('MAX_TOKENS', default=1024))
    top_p: float = config('TOP_P', default=1.0, cast=float)
    system_prompt: str = load_system_prompt()

    # Database Configuration
    supabase_url: str = str(config('SUPABASE_URL', default="https://your-supabase-url"))
    supabase_key: str = str(config('SUPABASE_KEY', default="your-supabase-key"))

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings().model_dump()
