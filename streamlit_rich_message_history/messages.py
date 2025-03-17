"""
Message classes for the streamlit_rich_message_history package.

This module defines the Message class and its derivatives (UserMessage, AssistantMessage,
ErrorMessage) which represent chat messages with rich content components.
"""

import traceback
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .components import MessageComponent
from .enums import ComponentRegistry, ComponentType


class Message:
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

    def add(self, content: Any, **kwargs):
        """
        Add a component to the message with automatic type detection.

        This is the core method for adding content. All specific add_* methods
        ultimately call this method with appropriate flags.

        Args:
            content: The content to add to the message
            **kwargs: Additional keyword arguments that control rendering behavior
                      Special flags include:
                      - is_error: Treat string content as an error message
                      - is_code: Treat string content as code with syntax highlighting
                      - language: The programming language for code highlighting
                      - is_metric: Treat numeric content as a metric
                      - is_table: Treat content as a static table
                      - is_json: Treat dictionaries or lists as JSON data
                      - is_html: Treat string content as HTML

        Returns:
            Message: Self, for method chaining
        """
        component = MessageComponent(content, **kwargs)
        self.components.append(component)
        return self  # Allow method chaining

    def add_text(self, text: str, **kwargs):
        """
        Add a text component to the message.

        Args:
            text: The text content (supports markdown)
            **kwargs: Additional keyword arguments for the component
                      Common ones include:
                      - title: A title for the text
                      - description: A description

        Returns:
            Message: Self, for method chaining

        Examples:
            >>> message.add_text("Hello, **world**!")
            >>> message.add_text("Expandable content", title="Section Title")
        """
        return self.add(text, **kwargs)

    def add_error(self, error_text: str, **kwargs):
        """
        Add an error component to the message.

        Args:
            error_text: The error message to display
            **kwargs: Additional keyword arguments for the component

        Returns:
            Message: Self, for method chaining

        Examples:
            >>> message.add_error("File not found: example.txt")
        """
        return self.add(error_text, is_error=True, **kwargs)

    def add_code(self, code: str, language: str = "python", **kwargs):
        """
        Add a code component to the message.

        Args:
            code: The code snippet to display
            language: Programming language for syntax highlighting (default: 'python')
            **kwargs: Additional keyword arguments for the component

        Returns:
            Message: Self, for method chaining

        Examples:
            >>> message.add_code("def hello(): print('Hello world')")
            >>> message.add_code("<div>Hello</div>", language="html")
        """
        return self.add(code, is_code=True, language=language, **kwargs)

    def add_dataframe(self, df: pd.DataFrame, **kwargs):
        """
        Add a dataframe component to the message.

        Args:
            df: The pandas DataFrame to display
            **kwargs: Additional keyword arguments for the component
                      Common ones include:
                      - use_container_width: Whether to use the full container width
                      - height: Height of the dataframe in pixels

        Returns:
            Message: Self, for method chaining

        Examples:
            >>> message.add_dataframe(pd.DataFrame({'A': [1, 2], 'B': [3, 4]}))
            >>> message.add_dataframe(df, height=300)
        """
        return self.add(df, **kwargs)

    def add_series(self, series: pd.Series, **kwargs):
        """
        Add a series component to the message.

        Args:
            series: The pandas Series to display
            **kwargs: Additional keyword arguments for the component

        Returns:
            Message: Self, for method chaining

        Examples:
            >>> message.add_series(pd.Series([1, 2, 3, 4]))
        """
        return self.add(series, **kwargs)

    def add_matplotlib_figure(self, fig: plt.Figure, **kwargs):
        """
        Add a matplotlib figure component to the message.

        Args:
            fig: The matplotlib Figure to display
            **kwargs: Additional keyword arguments for the component

        Returns:
            Message: Self, for method chaining

        Examples:
            >>> fig, ax = plt.subplots()
            >>> ax.plot([1, 2, 3, 4])
            >>> message.add_matplotlib_figure(fig)
        """
        return self.add(fig, **kwargs)

    def add_plotly_figure(self, fig: Union[go.Figure, dict], **kwargs):
        """
        Add a plotly figure component to the message.

        Args:
            fig: The plotly Figure to display
            **kwargs: Additional keyword arguments for the component
                      Common ones include:
                      - use_container_width: Whether to use the full container width
                      - height: Height of the chart in pixels

        Returns:
            Message: Self, for method chaining

        Examples:
            >>> fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
            >>> message.add_plotly_figure(fig)
        """
        return self.add(fig, **kwargs)

    def add_number(self, number: Union[int, float], **kwargs):
        """
        Add a number component to the message.

        Args:
            number: The number to display
            **kwargs: Additional keyword arguments for the component
                      Common ones include:
                      - format: Format string (e.g., "{:.2f}%" for percentage)
                      - title: Label for the number

        Returns:
            Message: Self, for method chaining

        Examples:
            >>> message.add_number(42)
            >>> message.add_number(3.14159, format="{:.2f}", title="Pi")
        """
        return self.add(number, **kwargs)

    def add_metric(self, value: Any, label: Optional[str] = None, **kwargs):
        """
        Add a metric component to the message.

        Args:
            value: The value of the metric
            label: Label for the metric
            **kwargs: Additional keyword arguments for the component
                      Common ones include:
                      - delta: Delta value to show
                      - delta_color: Color for delta ('normal', 'inverse', 'off')

        Returns:
            Message: Self, for method chaining

        Examples:
            >>> message.add_metric(42, "Answer")
            >>> message.add_metric(103.5, "Temperature", delta=2.5)
        """
        return self.add(value, is_metric=True, title=label, **kwargs)

    def add_table(self, data: Any, **kwargs):
        """
        Add a static table component to the message.

        Args:
            data: The data to display as a table
            **kwargs: Additional keyword arguments for the component

        Returns:
            Message: Self, for method chaining

        Examples:
            >>> message.add_table(pd.DataFrame({'A': [1, 2], 'B': [3, 4]}))
            >>> message.add_table([[1, 2], [3, 4]])
        """
        return self.add(data, is_table=True, **kwargs)

    def add_json(self, data: Union[Dict, List], **kwargs):
        """
        Add a JSON component to the message.

        Args:
            data: The data to display as JSON
            **kwargs: Additional keyword arguments for the component

        Returns:
            Message: Self, for method chaining

        Examples:
            >>> message.add_json({"name": "John", "age": 30})
            >>> message.add_json([1, 2, 3, {"nested": True}])
        """
        return self.add(data, is_json=True, **kwargs)

    def add_html(self, html_content: str, **kwargs):
        """
        Add an HTML component to the message.

        Args:
            html_content: The HTML content to display
            **kwargs: Additional keyword arguments for the component
                      Common ones include:
                      - height: Height of the HTML content in pixels
                      - scrolling: Whether to enable scrolling

        Returns:
            Message: Self, for method chaining

        Examples:
            >>> message.add_html("<h1>Hello World</h1>")
            >>> message.add_html("<div>Content</div>", height=300, scrolling=True)
        """
        return self.add(html_content, is_html=True, **kwargs)

    def add_list(self, items: List[Any], **kwargs):
        """
        Add a list of items to the message.

        Each item in the list will be rendered as its own component.

        Args:
            items: The list of items to display
            **kwargs: Additional keyword arguments for the component

        Returns:
            Message: Self, for method chaining

        Examples:
            >>> message.add_list(["Text", 42, pd.DataFrame({'A': [1]})])
        """
        return self.add(items, **kwargs)

    def add_tuple(self, items: Tuple[Any, ...], **kwargs):
        """
        Add a tuple of items to the message.

        Each item in the tuple will be rendered as its own component.

        Args:
            items: The tuple of items to display
            **kwargs: Additional keyword arguments for the component

        Returns:
            Message: Self, for method chaining

        Examples:
            >>> message.add_tuple(("Text", 42, pd.DataFrame({'A': [1]})))
        """
        return self.add(items, **kwargs)

    def add_dict(self, items: Dict[str, Any], **kwargs):
        """
        Add a dictionary of items to the message.

        Each value in the dictionary will be rendered as its own component.

        Args:
            items: The dictionary of items to display
            **kwargs: Additional keyword arguments for the component

        Returns:
            Message: Self, for method chaining

        Examples:
            >>> message.add_dict({"text": "Hello", "number": 42})
        """
        return self.add(items, **kwargs)

    def add_custom(self, content: Any, component_type: str, **kwargs):
        """
        Add a custom component type.

        This method is used for components registered through the ComponentRegistry.

        Args:
            content: The content to display
            component_type: The registered component type name
            **kwargs: Additional keyword arguments for the component

        Returns:
            Message: Self, for method chaining

        Raises:
            ValueError: If the component type is not registered

        Examples:
            >>> # After registering an 'image' component type:
            >>> message.add_custom(my_pil_image, "image", width=300)
        """
        # Look up the component type
        custom_type = ComponentRegistry.get_custom_type(component_type)
        if not custom_type:
            raise ValueError(f"Unknown custom component type: {component_type}")

        # Add the component with the specified type
        component = MessageComponent(content, component_type=custom_type, **kwargs)
        self.components.append(component)
        return self

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
