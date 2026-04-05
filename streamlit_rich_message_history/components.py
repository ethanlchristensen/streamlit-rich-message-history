"""
Component handling for the streamlit_rich_message_history package.

This module defines the core MessageComponent class that detects, processes, and
renders different types of content in a Streamlit application.
"""

import traceback
from typing import Any, Optional, Union

import streamlit as st

from .builtin_components import initialize_builtins
from .enums import ComponentType
from .registry import ComponentRegistry

# Initialize built-in components
initialize_builtins()


class MessageComponent:
    """
    Base class for all message components with automatic type detection.

    This class handles the automatic detection, proper rendering, and error handling
    for different types of content within a message in a Streamlit application.

    Attributes:
        content: The actual content to be displayed
        component_type: The type of component (automatically detected if not specified)
        title: Optional title for the component
        description: Optional description text for the component
        expanded: Whether expandable sections should be expanded by default
        kwargs: Additional keyword arguments for rendering
    """

    def __init__(
        self,
        content: Any,
        component_type: Optional[ComponentType] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        expanded: bool = False,
        **kwargs,
    ):
        """
        Initialize a new message component.

        Args:
            content: The content to be displayed
            component_type: Manually specify the component type (auto-detected if None)
            title: Optional title for the component (creates an expander if provided)
            description: Optional description text for the component
            expanded: Whether expandable sections should be expanded by default
            **kwargs: Additional keyword arguments that control rendering behavior
                      Special flags include:
                      - is_error: Treat string content as an error message
                      - is_code: Treat string content as code with syntax highlighting
                      - language: The programming language for code highlighting
                      - is_metric: Treat numeric content as a metric
                      - is_table: Treat content as a static table
                      - is_json: Treat dictionaries or lists as JSON data
                      - is_html: Treat string content as HTML
        """
        self.content = content
        self.kwargs = kwargs

        if component_type is None:
            component_type = self._detect_component_type(content)

        self.component_type = component_type
        self.title = title
        self.description = description
        self.expanded = expanded

    def _detect_component_type(self, content: Any) -> ComponentType:
        """
        Detect the appropriate component type based on content.
        """
        # Try custom and builtin detectors in order
        for comp_type in ComponentRegistry._detector_order:
            detector = ComponentRegistry.get_detector(comp_type)
            if detector and detector(content, self.kwargs):
                return comp_type

        # Default fallback
        return ComponentType.TEXT

    def render(self):
        """
        Render the component with appropriate context.

        If a title is provided, the component is wrapped in an expander.
        If a description is provided, it's shown before the content.
        """
        if self.title:
            with st.expander(self.title, expanded=self.expanded):
                if self.description:
                    st.markdown(self.description)
                self._render_content()
        else:
            if self.description:
                st.markdown(self.description)
            self._render_content()

    def _render_content(self):
        """
        Render the component based on its detected type.

        This method handles the rendering of all built-in component types
        and delegates to custom renderers for custom component types.
        It also includes error handling to prevent component rendering errors
        from breaking the entire application.
        """
        try:
            # First check if there's a custom renderer
            custom_renderer = ComponentRegistry.get_renderer(self.component_type)
            if custom_renderer:
                custom_renderer(self.content, self.kwargs)
                return

            # Special handling for collections which recurse
            if (
                self.component_type == ComponentType.LIST
                or self.component_type == ComponentType.TUPLE
            ):
                for idx, item in enumerate(self.content):
                    self._render_collection_item(item, idx)
            elif self.component_type == ComponentType.DICT:
                for key, value in self.content.items():
                    self._render_collection_item(value, key)
            else:
                st.write(str(self.content))
        except Exception as e:
            error_message = f"Error rendering component of type {self.component_type.value}: {str(e)}"
            stack_trace = traceback.format_exc()
            st.error(error_message)
            with st.expander("Stack Trace", expanded=False):
                st.code(stack_trace, language="python")

            # Try to show the original content as simple text if possible
            with st.expander("Component Content (Debug View)", expanded=False):
                try:
                    if hasattr(self.content, "__repr__"):
                        st.code(repr(self.content), language="python")
                    else:
                        st.code(str(self.content), language="python")
                except Exception as e:
                    st.error(f"Unable to display component content: {e}")

    def _render_collection_item(
        self, item: Any, index: Optional[Union[int, str]] = None
    ):
        """
        Render a single item from a collection.

        Args:
            item: The item to render
            index: Optional index or key for error reporting
        """
        try:
            # Create a new MessageComponent for the item
            item_component = MessageComponent(item)
            # Render the item
            item_component._render_content()
        except Exception as e:
            if isinstance(index, (int, str)):
                index_str = f" at index/key '{index}'"
            else:
                index_str = ""

            error_message = f"Error rendering collection item{index_str}: {str(e)}"
            st.error(error_message)
            with st.expander("Item Debug View", expanded=False):
                try:
                    st.code(repr(item), language="python")
                except Exception as e:
                    st.error(f"Unable to display item content: {e}")
