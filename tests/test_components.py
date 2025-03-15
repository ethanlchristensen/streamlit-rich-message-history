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