"""
Built-in component registration for the streamlit_rich_message_history package.
"""

import streamlit as st

from .enums import ComponentType
from .registry import ComponentRegistry


# Add an initial initialization function that can be called when components.py is loaded.
def register_builtin_components():
    """Register all built-in component detectors and renderers."""

    # Text
    def detect_text(content, kwargs):
        if not isinstance(content, str):
            return False
        return not any(kwargs.get(k) for k in ["is_error", "is_code", "is_html"])

    ComponentRegistry.register_detector(ComponentType.TEXT, detect_text)
    ComponentRegistry.register_renderer(ComponentType.TEXT, lambda c, k: st.markdown(c))

    # Error
    ComponentRegistry.register_detector(
        ComponentType.ERROR,
        lambda c, k: isinstance(c, str) and k.get("is_error", False),
    )
    ComponentRegistry.register_renderer(ComponentType.ERROR, lambda c, k: st.error(c))

    # Code
    ComponentRegistry.register_detector(
        ComponentType.CODE, lambda c, k: isinstance(c, str) and k.get("is_code", False)
    )
    ComponentRegistry.register_renderer(
        ComponentType.CODE,
        lambda c, k: st.code(c, language=k.get("language", "python")),
    )

    # HTML
    ComponentRegistry.register_detector(
        ComponentType.HTML, lambda c, k: isinstance(c, str) and k.get("is_html", False)
    )
    ComponentRegistry.register_renderer(
        ComponentType.HTML,
        lambda c, k: st.html(
            c, height=k.get("height"), scrolling=k.get("scrolling", False)
        ),
    )

    # Number
    def detect_number(content, kwargs):
        return isinstance(content, (int, float)) and not kwargs.get("is_metric", False)

    ComponentRegistry.register_detector(ComponentType.NUMBER, detect_number)

    def render_number(content, kwargs):
        format_str = kwargs.get("format", None)
        title = kwargs.get("title", "Result")
        if format_str:
            st.write(f"{title}: {format_str.format(content)}")
        else:
            st.write(f"{title}: {content}")

    ComponentRegistry.register_renderer(ComponentType.NUMBER, render_number)

    # Metric
    ComponentRegistry.register_detector(
        ComponentType.METRIC, lambda c, k: k.get("is_metric", False)
    )

    def render_metric(content, kwargs):
        st.metric(
            label=kwargs.get("title", "Metric"),
            value=content,
            delta=kwargs.get("delta"),
            delta_color=kwargs.get("delta_color", "normal"),
        )

    ComponentRegistry.register_renderer(ComponentType.METRIC, render_metric)

    # Table
    ComponentRegistry.register_detector(
        ComponentType.TABLE, lambda c, k: k.get("is_table", False)
    )
    ComponentRegistry.register_renderer(ComponentType.TABLE, lambda c, k: st.table(c))

    # JSON
    ComponentRegistry.register_detector(
        ComponentType.JSON,
        lambda c, k: isinstance(c, (dict, list)) and k.get("is_json", False),
    )
    ComponentRegistry.register_renderer(ComponentType.JSON, lambda c, k: st.json(c))

    # Collections
    ComponentRegistry.register_detector(
        ComponentType.LIST,
        lambda c, k: isinstance(c, list)
        and not k.get("is_table")
        and not k.get("is_json"),
    )
    ComponentRegistry.register_detector(
        ComponentType.TUPLE, lambda c, k: isinstance(c, tuple) and not k.get("is_table")
    )
    ComponentRegistry.register_detector(
        ComponentType.DICT, lambda c, k: isinstance(c, dict) and not k.get("is_json")
    )

    # The rendering of collections relies on the MessageComponent class internal loop.
    # To keep dependencies light, we will let pandas, matplotlib, and plotly be registered
    # lazily or through safe imports.


def register_pandas_components():
    """Register Pandas related components."""
    try:
        import pandas as pd

        ComponentRegistry.register_detector(
            ComponentType.DATAFRAME, lambda c, k: isinstance(c, pd.DataFrame)
        )
        ComponentRegistry.register_renderer(
            ComponentType.DATAFRAME,
            lambda c, k: st.dataframe(
                c,
                use_container_width=k.get("use_container_width", True),
                height=k.get("height"),
            ),
        )
        ComponentRegistry.register_detector(
            ComponentType.SERIES, lambda c, k: isinstance(c, pd.Series)
        )
        ComponentRegistry.register_renderer(
            ComponentType.SERIES, lambda c, k: st.dataframe(c.to_frame())
        )
    except ImportError:
        pass


def register_matplotlib_components():
    """Register Matplotlib related components."""
    try:
        import matplotlib.pyplot as plt

        ComponentRegistry.register_detector(
            ComponentType.MATPLOTLIB_FIGURE, lambda c, k: isinstance(c, plt.Figure)
        )
        ComponentRegistry.register_renderer(
            ComponentType.MATPLOTLIB_FIGURE, lambda c, k: st.pyplot(c)
        )
    except ImportError:
        pass


def register_plotly_components():
    """Register Plotly related components."""
    try:
        import plotly.graph_objects as go

        def detect_plotly(c, k):
            if isinstance(c, go.Figure):
                return True
            if isinstance(c, dict) and isinstance(
                getattr(c, "data", None), (list, tuple)
            ):
                return True
            return False

        ComponentRegistry.register_detector(ComponentType.PLOTLY_FIGURE, detect_plotly)
        ComponentRegistry.register_renderer(
            ComponentType.PLOTLY_FIGURE,
            lambda c, k: st.plotly_chart(
                c,
                use_container_width=k.get("use_container_width", True),
                height=k.get("height"),
            ),
        )
    except ImportError:
        pass


def initialize_builtins():
    register_builtin_components()
    register_pandas_components()
    register_matplotlib_components()
    register_plotly_components()
