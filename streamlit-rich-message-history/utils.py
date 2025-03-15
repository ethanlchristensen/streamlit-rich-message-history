"""
Streamlit Rich Message History
==============================

A package for creating and managing rich, multi-component chat messages in Streamlit.
"""

__version__ = "0.1.0"

from .enums import ComponentType
from .components import MessageComponent
from .messages import Message, UserMessage, AssistantMessage, ErrorMessage
from .history import MessageHistory

__all__ = [
    "ComponentType",
    "MessageComponent",
    "Message",
    "UserMessage",
    "AssistantMessage",
    "ErrorMessage",
    "MessageHistory",
]
