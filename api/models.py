#!/usr/bin/env python3

"""
AUTHOR: Dan Njuguna
DATE: 2025-05-01

DESCRIPTION: This module only handles the pydantic basemodels to be used by the API
"""

import sys
sys.dont_write_bytecode = True
from pydantic import Field, BaseModel

class UserRequest(BaseModel):
    query: str = Field(description="The user message/request to the chatbot")

class BotResponse(BaseModel):
    assistant: str = Field(description="The chatbot name", default="Meditreat")
    response: str = Field(description="This is the response from the model", example="Tibu iyo kitu banaa")
    status: str = Field(description="The status message for the response")
    status_code: int = Field(description="The status code for the response")
