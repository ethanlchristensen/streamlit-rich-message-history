import pytest
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_rich_message_history import MessageComponent, ComponentType

def test_text_component_detection():
    component = MessageComponent("Hello World")
    assert component.component_type == ComponentType.TEXT

def test_dataframe_component_detection():
    df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    component = MessageComponent(df)
    assert component.component_type == ComponentType.DATAFRAME

def test_error_component_detection():
    component = MessageComponent("Error message", is_error=True)
    assert component.component_type == ComponentType.ERROR

def test_metric_component_detection():
    component = MessageComponent(42, is_metric=True, title="Answer")
    assert component.component_type == ComponentType.METRIC

def test_table_component_detection():
    data = [["Alice", 25], ["Bob", 30]]
    component = MessageComponent(data, is_table=True)
    assert component.component_type == ComponentType.TABLE

def test_series_component_detection():
    series = pd.Series([1, 2, 3, 4])
    component = MessageComponent(series)
    assert component.component_type == ComponentType.SERIES

def test_list_component_detection():
    items = ["item1", "item2", "item3"]
    component = MessageComponent(items)
    assert component.component_type == ComponentType.LIST

def test_tuple_component_detection():
    items = ("item1", "item2", "item3")
    component = MessageComponent(items)
    assert component.component_type == ComponentType.TUPLE

def test_matplotlib_figure_detection():
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    component = MessageComponent(fig)
    assert component.component_type == ComponentType.MATPLOTLIB_FIGURE