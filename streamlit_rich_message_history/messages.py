"""
Message classes for the streamlit_rich_message_history package.

This module defines the Message class and its derivatives (UserMessage, AssistantMessage,
ErrorMessage) which represent chat messages with rich content components.
"""

import traceback
from typing import Callable, Dict, List, Optional

import streamlit as st

from .components import MessageComponent
from .enums import ComponentType
from .mixins import MessageBuilderMixin


class Message(MessageBuilderMixin):
    """
    Class representing a message with multiple components.

    This is the core class for creating rich messages with various content types.
    A message represents a single chat bubble/entry that can contain multiple
    components (text, code, charts, tables, etc.).

    Attributes:
        user: The sender of the message ('user', 'assistant', etc.)
        avatar: Avatar image for the message sender
        components: List of MessageComponent objects in this message
    """

    def __init__(self, user: str, avatar: str):
        """
        Initialize a new message.

        Args:
            user: The sender of the message ('user', 'assistant', etc.)
            avatar: Avatar image for the message sender (URL or emoji)
        """
        self.user = user
        self.avatar = avatar
        self.components: List[MessageComponent] = []

    _custom_component_methods: Dict[str, ComponentType] = {}

    def render(self):
        """
        Render the message with all its components.

        This method displays the message in a Streamlit app using st.chat_message
        and renders all components within it.

        Raises:
            Displays an error message in the UI if rendering fails
        """
        try:
            with st.chat_message(name=self.user, avatar=self.avatar):
                for component in self.components:
                    component.render()
        except Exception as e:
            error_message = f"Error rendering message from {self.user}: {str(e)}"
            stack_trace = traceback.format_exc()

            with st.chat_message(name="error", avatar="🚫"):
                st.error(error_message)
                with st.expander("Stack Trace", expanded=False):
                    st.code(stack_trace, language="python")

    @classmethod
    def register_component_method(
        cls,
        method_name: str,
        component_type: ComponentType,
        method_func: Optional[Callable] = None,
    ):
        """
        Register a new component method for the Message class.
        This method dynamically adds a new add_* method to the Message class
        for a custom component type. If a method with this name already exists,
        returns the existing method with a warning instead of raising an exception.

        Args:
            method_name: Name of the method to add (typically 'add_xyz')
            component_type: The component type to associate with this method
            method_func: Optional custom function for the method
                        If None, a default implementation is created

        Returns:
            Callable: The created or existing method function

        Examples:
            >>> IMAGE_TYPE = ComponentRegistry.register_component_type("image")
            >>> Message.register_component_method("add_image", IMAGE_TYPE)
            >>> # Now message.add_image() is available
            >>> # Registering the same method again will return the existing method
            >>> Message.register_component_method("add_image", IMAGE_TYPE)
            >>> # A warning will be printed and the existing method will be returned
        """
        if hasattr(cls, method_name) and method_name != "add_custom":
            import warnings

            warnings.warn(
                f"Method '{method_name}' already exists in Message class, returning existing method"
            )
            return getattr(cls, method_name)

        # Create a method function if not provided
        if method_func is None:

            def default_method(self, content, **kwargs):
                return self.add_custom(
                    content, component_type=component_type.value, **kwargs
                )

            method_func = default_method

        # Add the method to the class
        setattr(cls, method_name, method_func)
        cls._custom_component_methods[method_name] = component_type
        return method_func


class UserMessage(Message):
    """
    Convenience class for user messages.

    This class creates a Message with the 'user' role pre-configured,
    making it easier to create user messages in a chat interface.

    Attributes:
        user: Always set to 'user'
        avatar: Avatar image for the user
        components: List of MessageComponent objects in this message
    """

    def __init__(self, avatar: str, text: Optional[str] = None):
        """
        Initialize a new user message.

        Args:
            avatar: Avatar image for the user (URL or emoji)
            text: Optional initial text for the message. If provided,
                  adds a text component automatically.
        """
        super().__init__(user="user", avatar=avatar)
        if text:
            self.add_text(text)


class AssistantMessage(Message):
    """
    Convenience class for assistant messages.

    This class creates a Message with the 'assistant' role pre-configured,
    making it easier to create assistant/AI responses in a chat interface.

    Attributes:
        user: Always set to 'assistant'
        avatar: Avatar image for the assistant
        components: List of MessageComponent objects in this message
    """

    def __init__(self, avatar: str):
        """
        Initialize a new assistant message.

        Args:
            avatar: Avatar image for the assistant (URL or emoji)
        """
        super().__init__(user="assistant", avatar=avatar)


class ErrorMessage(Message):
    """
    Convenience class for error messages.

    This class creates a Message with the 'error' role pre-configured
    and automatically adds an error component, making it easier to
    display errors in a chat interface.

    Attributes:
        user: Always set to 'error'
        avatar: Avatar image for error messages
        components: List of MessageComponent objects in this message
    """

    def __init__(self, avatar: str, error_text: str):
        """
        Initialize a new error message.

        Args:
            avatar: Avatar image for the error message (URL or emoji)
            error_text: The error message to display
        """
        super().__init__(user="error", avatar=avatar)
        self.add_error(error_text)
