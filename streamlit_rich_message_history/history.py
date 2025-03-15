from typing import List

from .messages import AssistantMessage, ErrorMessage, Message, UserMessage


class MessageHistory:
    """Class to store and manage a history of messages."""

    def __init__(self):
        self.messages: List[Message] = []

    def add_message(self, message: Message):
        """Add a message to the history."""
        self.messages.append(message)
        return message  # Allow method chaining or further modification

    def add_user_message_create(self, avatar: str, text: str) -> UserMessage:
        """Add a user message with text."""
        message = UserMessage(avatar, text)
        self.add_message(message)
        return message

    def add_user_message(self, message: UserMessage) -> None:
        """Add a user message with text."""
        self.add_message(message)

    def add_assistant_message_create(self, avatar: str) -> AssistantMessage:
        """Add an empty assistant message (components to be added later)."""
        message = AssistantMessage(avatar)
        self.add_message(message)
        return message

    def add_assistant_message(self, message: AssistantMessage) -> None:
        """Add an already created assistant message to the history."""
        self.add_message(message)

    def add_error_message(self, avatar: str, error_text: str) -> ErrorMessage:
        """Add an error message."""
        message = ErrorMessage(avatar, error_text)
        self.add_message(message)
        return message

    def render_all(self):
        """Render all messages in the history."""
        for message in self.messages:
            message.render()

    def render_last(self, n: int = 1):
        """Render the last n messages."""
        for message in self.messages[-n:]:
            message.render()

    def clear(self):
        """Clear all messages from history."""
        self.messages = []
