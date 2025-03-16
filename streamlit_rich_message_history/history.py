from typing import Any, Callable, List, Optional

from .enums import ComponentRegistry, ComponentType
from .messages import AssistantMessage, ErrorMessage, Message, UserMessage


class MessageHistory:
    """
    Class to store and manage a history of messages in a Streamlit application.

    The MessageHistory class provides a convenient way to maintain a conversation-like
    interface in Streamlit apps, with support for different types of messages (user,
    assistant, error) and rich content components.

    It manages the addition, storage, and rendering of messages, as well as the
    registration of custom component types, detectors, and renderers.

    Attributes:
        messages: A list of Message objects that comprise the conversation history
    """

    def __init__(self):
        """Initialize an empty message history."""
        self.messages: List[Message] = []

    def add_message(self, message: Message):
        """
        Add a message to the history.

        Args:
            message: The Message object to add to the history

        Returns:
            Message: The added message, allowing for method chaining
        """
        self.messages.append(message)
        return message  # Allow method chaining or further modification

    def add_user_message_create(self, avatar: str, text: str) -> UserMessage:
        """
        Create and add a new user message with text.

        Args:
            avatar: Avatar image URL or emoji for the user
            text: The text content of the user message

        Returns:
            UserMessage: The created user message
        """
        message = UserMessage(avatar, text)
        self.add_message(message)
        return message

    def add_user_message(self, message: UserMessage) -> None:
        """
        Add a pre-created user message to the history.

        Args:
            message: The UserMessage object to add to the history
        """
        self.add_message(message)

    def add_assistant_message_create(self, avatar: str) -> AssistantMessage:
        """
        Create and add a new empty assistant message.

        This creates an assistant message that can be populated with
        components after creation.

        Args:
            avatar: Avatar image URL or emoji for the assistant

        Returns:
            AssistantMessage: The created assistant message
        """
        message = AssistantMessage(avatar)
        self.add_message(message)
        return message

    def add_assistant_message(self, message: AssistantMessage) -> None:
        """
        Add a pre-created assistant message to the history.

        Args:
            message: The AssistantMessage object to add to the history
        """
        self.add_message(message)

    def add_error_message(self, avatar: str, error_text: str) -> ErrorMessage:
        """
        Create and add an error message to the history.

        Args:
            avatar: Avatar image URL or emoji for the error message
            error_text: The error text to display

        Returns:
            ErrorMessage: The created error message
        """
        message = ErrorMessage(avatar, error_text)
        self.add_message(message)
        return message

    def render_all(self):
        """
        Render all messages in the history to the Streamlit UI.

        This renders each message in sequence, from first to last.
        """
        for message in self.messages:
            message.render()

    def render_last(self, n: int = 1):
        """
        Render only the last n messages in the history.

        Args:
            n: Number of most recent messages to render (default: 1)
        """
        for message in self.messages[-n:]:
            message.render()

    def clear(self):
        """Clear all messages from the history, resetting it to empty."""
        self.messages = []

    @staticmethod
    def register_component_type(name: str) -> ComponentType:
        """
        Register a new component type for use in messages.

        This allows extending the library with custom component types
        that can be detected and rendered appropriately.

        Args:
            name: The name of the new component type

        Returns:
            ComponentType: The created component type enum value
        """
        return ComponentRegistry.register_component_type(name)

    @staticmethod
    def register_component_detector(
        component_type: ComponentType, detector: Callable[[Any, dict], bool]
    ) -> None:
        """
        Register a detector function for a component type.

        The detector function determines whether a given content
        should be treated as the specified component type.

        Args:
            component_type: The component type to register a detector for
            detector: A function that takes (content, kwargs) and returns True if
                     the content should be treated as this component type
        """
        ComponentRegistry.register_detector(component_type, detector)

    @staticmethod
    def register_component_renderer(
        component_type: ComponentType, renderer: Callable[[Any, dict], None]
    ) -> None:
        """
        Register a renderer function for a component type.

        The renderer function handles displaying the component in the Streamlit UI.

        Args:
            component_type: The component type to register a renderer for
            renderer: A function that takes (content, kwargs) and renders
                     the component in the Streamlit app
        """
        ComponentRegistry.register_renderer(component_type, renderer)

    @staticmethod
    def register_component_method(
        method_name: str,
        component_type: ComponentType,
        method_func: Optional[Callable] = None,
    ) -> None:
        """
        Register a new component method to the Message class.

        This allows adding custom methods to Message objects for adding
        specific types of components with a convenient API.

        Args:
            method_name: The name of the method to add (e.g., 'add_chart')
            component_type: The component type this method will create
            method_func: Optional custom function to use for the method
                        (if None, a default implementation will be used)
        """
        Message.register_component_method(method_name, component_type, method_func)
