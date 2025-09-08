#!/usr/bin/env python3

"""
AUTHOR: Dan Njuguna
DATE: 2025-09-01

DESCRIPTION:
    This module provides utility functions for serializing
    Python objects to JSON and vice versa.
"""

from dataclasses import is_dataclass, asdict
from datetime import datetime, date
from pydantic import BaseModel
from typing import Any, Dict
from decimal import Decimal
import numpy as np
import json

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any):  # type: ignore[index]
        # Pydantic models - use model_dump() method
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        # Dataclasses
        if is_dataclass(obj):
            return asdict(obj)  # type: ignore
        # Datetime and date
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        # Set and frozenset
        if isinstance(obj, (set, frozenset)):
            return list(obj)
        # Decimal numbers
        try:
            if isinstance(obj, Decimal):
                return float(obj)
        except ImportError:
            pass
        # Complex numbers: represent as [real, imag]
        if isinstance(obj, complex):
            return [obj.real, obj.imag]
        # Bytes: attempt to decode via utf-8, else use list representation
        if isinstance(obj, bytes):
            try:
                return obj.decode('utf-8')
            except UnicodeDecodeError:
                return list(obj)
        # Numpy arrays and scalar types
        try:
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, (np.integer, np.floating)):
                return obj.item()
        except ImportError:
            pass
        # Iterables (except strings and bytes)
        if hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            return list(obj)  # type: ignore
        # Handle objects with __dict__
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        # Fallback: use superclass default, or convert to string if TypeError is raised
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

def to_json(obj: Any) -> str:
    """
    Serialize any object to a JSON string, handling Pydantic models, dataclasses, datetime, etc.
    """
    return json.dumps(obj, cls=EnhancedJSONEncoder)

def to_dict(obj: Any) -> Dict:
    """
    Convert any object to a dictionary that can be safely JSON serialized.
    """
    return json.loads(to_json(obj))
