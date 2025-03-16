"""
Component handling for the streamlit_rich_message_history package.

This module defines the core MessageComponent class that detects, processes, and
renders different types of content in a Streamlit application.
"""

import traceback
from typing import Any, Optional, Union

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .enums import ComponentRegistry, ComponentType


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

        This method uses a combination of registered custom detectors and built-in
        type detection logic to determine the most appropriate component type
        for the given content.

        Args:
            content: The content to detect the type for

        Returns:
            ComponentType: The detected component type
        """
        # First try custom detectors
        for comp_type in ComponentRegistry._type_detectors:
            detector = ComponentRegistry.get_detector(comp_type)
            if detector and detector(content, self.kwargs):
                return comp_type

        # Then do built-in detection logic
        if isinstance(content, (list, tuple)) and not self.kwargs.get(
            "is_table", False
        ):
            return (
                ComponentType.LIST if isinstance(content, list) else ComponentType.TUPLE
            )
        elif isinstance(content, dict) and not self.kwargs.get("is_json", False):
            return ComponentType.DICT

        if isinstance(content, str):
            if self.kwargs.get("is_error", False):
                return ComponentType.ERROR
            elif self.kwargs.get("is_code", False):
                return ComponentType.CODE
            elif self.kwargs.get("is_html", False):
                return ComponentType.HTML
            else:
                return ComponentType.TEXT
        elif isinstance(content, pd.DataFrame):
            return ComponentType.DATAFRAME
        elif isinstance(content, pd.Series):
            return ComponentType.SERIES
        elif isinstance(content, plt.Figure):
            return ComponentType.MATPLOTLIB_FIGURE
        elif isinstance(content, go.Figure) or (
            isinstance(content, dict)
            and isinstance(getattr(content, "data", None), (list, tuple))
        ):
            return ComponentType.PLOTLY_FIGURE
        elif isinstance(content, (int, float)) and not self.kwargs.get(
            "is_metric", False
        ):
            return ComponentType.NUMBER
        elif self.kwargs.get("is_metric", False):
            return ComponentType.METRIC
        elif self.kwargs.get("is_table", False):
            return ComponentType.TABLE
        elif isinstance(content, (dict, list)) and self.kwargs.get("is_json", False):
            return ComponentType.JSON
        else:
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

            # Standard component rendering
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
                if self.component_type == ComponentType.TEXT:
                    st.markdown(self.content)
                elif self.component_type == ComponentType.ERROR:
                    st.error(self.content)
                elif self.component_type == ComponentType.CODE:
                    language = self.kwargs.get("language", "python")
                    st.code(self.content, language=language)
                elif self.component_type == ComponentType.DATAFRAME:
                    use_container_width = self.kwargs.get("use_container_width", True)
                    height = self.kwargs.get("height", None)
                    st.dataframe(
                        self.content,
                        use_container_width=use_container_width,
                        height=height,
                    )
                elif self.component_type == ComponentType.SERIES:
                    st.dataframe(self.content.to_frame())
                elif self.component_type == ComponentType.MATPLOTLIB_FIGURE:
                    st.pyplot(self.content)
                elif self.component_type == ComponentType.PLOTLY_FIGURE:
                    use_container_width = self.kwargs.get("use_container_width", True)
                    height = self.kwargs.get("height", None)
                    st.plotly_chart(
                        self.content,
                        use_container_width=use_container_width,
                        height=height,
                    )
                elif self.component_type == ComponentType.NUMBER:
                    format_str = self.kwargs.get("format", None)
                    if format_str:
                        st.write(
                            f"{self.title or 'Result'}: {format_str.format(self.content)}"
                        )
                    else:
                        st.write(f"{self.title or 'Result'}: {self.content}")
                elif self.component_type == ComponentType.METRIC:
                    delta = self.kwargs.get("delta", None)
                    delta_color = self.kwargs.get("delta_color", "normal")
                    st.metric(
                        label=self.title or "Metric",
                        value=self.content,
                        delta=delta,
                        delta_color=delta_color,
                    )
                elif self.component_type == ComponentType.TABLE:
                    st.table(self.content)
                elif self.component_type == ComponentType.JSON:
                    st.json(self.content)
                elif self.component_type == ComponentType.HTML:
                    height = self.kwargs.get("height", None)
                    scrolling = self.kwargs.get("scrolling", False)
                    st.html(self.content, height=height, scrolling=scrolling)
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
