import traceback
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .components import MessageComponent


class Message:
    """Class representing a message with multiple components."""

    def __init__(self, user: str, avatar: str):
        self.user = user
        self.avatar = avatar
        self.components: List[MessageComponent] = []

    def add(self, content: Any, **kwargs):
        """Add a component to the message with automatic type detection."""
        component = MessageComponent(content, **kwargs)
        self.components.append(component)
        return self  # Allow method chaining

    def add_text(self, text: str, **kwargs):
        """Add a text component to the message."""
        return self.add(text, **kwargs)

    def add_error(self, error_text: str, **kwargs):
        """Add an error component to the message."""
        return self.add(error_text, is_error=True, **kwargs)

    def add_code(self, code: str, language: str = "python", **kwargs):
        """Add a code component to the message."""
        return self.add(code, is_code=True, language=language, **kwargs)

    def add_dataframe(self, df: pd.DataFrame, **kwargs):
        """Add a dataframe component to the message."""
        return self.add(df, **kwargs)

    def add_series(self, series: pd.Series, **kwargs):
        """Add a series component to the message."""
        return self.add(series, **kwargs)

    def add_matplotlib_figure(self, fig: plt.Figure, **kwargs):
        """Add a matplotlib figure component to the message."""
        return self.add(fig, **kwargs)

    def add_plotly_figure(self, fig: Union[go.Figure, dict], **kwargs):
        """Add a plotly figure component to the message."""
        return self.add(fig, **kwargs)

    def add_number(self, number: Union[int, float], **kwargs):
        """Add a number component to the message."""
        return self.add(number, **kwargs)

    def add_metric(self, value: Any, label: Optional[str] = None, **kwargs):
        """Add a metric component to the message."""
        return self.add(value, is_metric=True, title=label, **kwargs)

    def add_table(self, data: Any, **kwargs):
        """Add a static table component to the message."""
        return self.add(data, is_table=True, **kwargs)

    def add_json(self, data: Union[Dict, List], **kwargs):
        """Add a JSON component to the message."""
        return self.add(data, is_json=True, **kwargs)

    def add_html(self, html_content: str, **kwargs):
        """Add an HTML component to the message."""
        return self.add(html_content, is_html=True, **kwargs)

    def add_list(self, items: List[Any], **kwargs):
        """Add a list of items to the message."""
        return self.add(items, **kwargs)

    def add_tuple(self, items: Tuple[Any, ...], **kwargs):
        """Add a tuple of items to the message."""
        return self.add(items, **kwargs)

    def add_dict(self, items: Dict[str, Any], **kwargs):
        """Add a dictionary of items to the message."""
        return self.add(items, **kwargs)

    def render(self):
        """Render the message with all its components."""
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


class UserMessage(Message):
    """Convenience class for user messages."""

    def __init__(self, avatar: str, text: Optional[str] = None):
        super().__init__(user="user", avatar=avatar)
        if text:
            self.add_text(text)


class AssistantMessage(Message):
    """Convenience class for assistant messages."""

    def __init__(self, avatar: str):
        super().__init__(user="assistant", avatar=avatar)


class ErrorMessage(Message):
    """Convenience class for error messages."""

    def __init__(self, avatar: str, error_text: str):
        super().__init__(user="error", avatar=avatar)
        self.add_error(error_text)
