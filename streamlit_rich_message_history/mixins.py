"""
Mixins for Message classes.
"""

from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go

from .components import MessageComponent
from .registry import ComponentRegistry


class MessageBuilderMixin:
    """
    Mixin containing convenience methods for adding specific types of components to a message.
    """

    components: List[MessageComponent]

    def add(self, content: Any, **kwargs):
        """Add a component to the message with automatic type detection."""
        component = MessageComponent(content, **kwargs)
        self.components.append(component)
        return self

    def add_text(self, text: str, **kwargs):
        return self.add(text, **kwargs)

    def add_error(self, error_text: str, **kwargs):
        return self.add(error_text, is_error=True, **kwargs)

    def add_code(self, code: str, language: str = "python", **kwargs):
        return self.add(code, is_code=True, language=language, **kwargs)

    def add_dataframe(self, df: pd.DataFrame, **kwargs):
        return self.add(df, **kwargs)

    def add_series(self, series: pd.Series, **kwargs):
        return self.add(series, **kwargs)

    def add_matplotlib_figure(self, fig: plt.Figure, **kwargs):
        return self.add(fig, **kwargs)

    def add_plotly_figure(self, fig: Union[go.Figure, dict], **kwargs):
        return self.add(fig, **kwargs)

    def add_number(self, number: Union[int, float], **kwargs):
        return self.add(number, **kwargs)

    def add_metric(self, value: Any, label: Optional[str] = None, **kwargs):
        return self.add(value, is_metric=True, title=label, **kwargs)

    def add_table(self, data: Any, **kwargs):
        return self.add(data, is_table=True, **kwargs)

    def add_json(self, data: Union[Dict, List], **kwargs):
        return self.add(data, is_json=True, **kwargs)

    def add_html(self, html_content: str, **kwargs):
        return self.add(html_content, is_html=True, **kwargs)

    def add_list(self, items: List[Any], **kwargs):
        return self.add(items, **kwargs)

    def add_tuple(self, items: Tuple[Any, ...], **kwargs):
        return self.add(items, **kwargs)

    def add_dict(self, items: Dict[str, Any], **kwargs):
        return self.add(items, **kwargs)

    def add_custom(self, content: Any, component_type: str, **kwargs):
        custom_type = ComponentRegistry.get_custom_type(component_type)
        if not custom_type:
            raise ValueError(f"Unknown custom component type: {component_type}")

        component = MessageComponent(content, component_type=custom_type, **kwargs)
        self.components.append(component)
        return self
