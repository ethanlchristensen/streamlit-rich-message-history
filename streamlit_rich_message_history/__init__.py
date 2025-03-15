"""
Streamlit Rich Message History
==============================

A package for creating and managing rich, multi-component chat messages in Streamlit.
"""

__version__ = "0.1.0"

from .components import MessageComponent
from .enums import ComponentType
from .history import MessageHistory
from .messages import AssistantMessage, ErrorMessage, Message, UserMessage

__all__ = [
    "ComponentType",
    "MessageComponent",
    "Message",
    "UserMessage",
    "AssistantMessage",
    "ErrorMessage",
    "MessageHistory",
]
