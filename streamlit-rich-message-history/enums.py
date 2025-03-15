from enum import Enum


class ComponentType(Enum):
    """Enum defining the possible message component types."""

    TEXT = "text"
    DATAFRAME = "dataframe"
    SERIES = "series"
    MATPLOTLIB_FIGURE = "matplotlib_figure"
    PLOTLY_FIGURE = "plotly_figure"
    NUMBER = "number"
    ERROR = "error"
    CODE = "code"
    METRIC = "metric"
    TABLE = "table"
    JSON = "json"
    HTML = "html"
    LIST = "list"
    TUPLE = "tuple"
    DICT = "dict"
