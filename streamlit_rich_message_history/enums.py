"""
Component type definitions and registry for the streamlit_rich_message_history package.

This module defines the core component types and provides a registry system
for extending the package with custom component types, detectors, and renderers.
"""

from enum import Enum
from typing import Any, Callable, Dict, Optional


class ComponentType(Enum):
    """
    Enum defining the possible message component types.

    These types correspond to different ways content can be displayed in messages,
    such as text, dataframes, charts, etc.

    Attributes:
        TEXT: Plain text content
        DATAFRAME: Pandas DataFrame display
        SERIES: Pandas Series display
        MATPLOTLIB_FIGURE: Matplotlib plot
        PLOTLY_FIGURE: Plotly chart
        NUMBER: Numeric value
        ERROR: Error message
        CODE: Code snippet with syntax highlighting
        METRIC: Metric with optional delta
        TABLE: Static table display
        JSON: JSON data viewer
        HTML: HTML content
        LIST: List of items
        TUPLE: Tuple of items
        DICT: Dictionary of items
    """

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


class ComponentRegistry:
    """
    Registry to manage custom component types, detectors, and renderers.

    This class provides static methods for registering and retrieving:
    - Custom component types (extending ComponentType)
    - Type detection functions that identify content types
    - Rendering functions that display specific content types

    The registry is a central point for extending the package with custom components.
    """

    _custom_types: Dict[str, ComponentType] = {}
    _type_detectors: Dict[ComponentType, Callable[[Any, Dict[str, Any]], bool]] = {}
    _renderers: Dict[ComponentType, Callable[[Any, Dict[str, Any]], None]] = {}

    @classmethod
    def register_component_type(cls, name: str) -> ComponentType:
        """
        Register a new component type with the given name.
        If a component type with this name already exists, returns the existing type
        with a warning instead of raising an exception.

        Args:
            name: String identifier for the new component type

        Returns:
            ComponentType: The newly created component type or existing component type

        Examples:
            >>> IMAGE_TYPE = ComponentRegistry.register_component_type("image")
            >>> # IMAGE_TYPE can now be used like a standard ComponentType
            >>> # Registering the same type again will return the existing type
            >>> SAME_IMAGE_TYPE = ComponentRegistry.register_component_type("image")
            >>> # A warning will be printed and SAME_IMAGE_TYPE == IMAGE_TYPE
        """
        # Check if the type already exists
        existing_types = [t.value for t in ComponentType] + list(
            cls._custom_types.keys()
        )
        if name in existing_types:
            import warnings

            warnings.warn(
                f"Component type '{name}' already exists, returning existing type"
            )

            # Return the existing type
            if name in cls._custom_types:
                return cls._custom_types[name]
            else:
                # Find and return the enum value from ComponentType
                for t in ComponentType:
                    if t.value == name:
                        return t

        # Create a new ComponentType dynamically
        custom_type = object.__new__(ComponentType)
        custom_type._name_ = name.upper()
        custom_type._value_ = name
        cls._custom_types[name] = custom_type
        return custom_type

    @classmethod
    def register_detector(
        cls, comp_type: ComponentType, detector: Callable[[Any, Dict[str, Any]], bool]
    ) -> None:
        """
        Register a detector function for a component type.

        The detector function determines if content should be treated as this component type.

        Args:
            comp_type: The component type to register a detector for
            detector: Function that takes content and kwargs and returns True if the
                    content should be handled as this component type

        Examples:
            >>> def image_detector(content, kwargs):
                    return isinstance(content, PIL.Image.Image)
            >>> ComponentRegistry.register_detector(IMAGE_TYPE, image_detector)
        """
        cls._type_detectors[comp_type] = detector

    @classmethod
    def register_renderer(
        cls, comp_type: ComponentType, renderer: Callable[[Any, Dict[str, Any]], None]
    ) -> None:
        """
        Register a renderer function for a component type.

        The renderer function handles displaying the content in a Streamlit app.

        Args:
            comp_type: The component type to register a renderer for
            renderer: Function that takes content and kwargs and renders it in Streamlit

        Examples:
            >>> def image_renderer(content, kwargs):
                    st.image(content, **{k: v for k, v in kwargs.items()
                                     if k in ['caption', 'width', 'use_column_width']})
            >>> ComponentRegistry.register_renderer(IMAGE_TYPE, image_renderer)
        """
        cls._renderers[comp_type] = renderer

    @classmethod
    def get_custom_type(cls, name: str) -> Optional[ComponentType]:
        """
        Get a custom component type by name.

        Args:
            name: String identifier of the component type

        Returns:
            ComponentType: The component type if found, None otherwise
        """
        return cls._custom_types.get(name)

    @classmethod
    def get_all_types(cls) -> list:
        """
        Get all component types (built-in and custom).

        Returns:
            list: List containing all ComponentType values
        """
        return list(ComponentType) + list(cls._custom_types.values())

    @classmethod
    def get_detector(cls, comp_type: ComponentType) -> Optional[Callable]:
        """
        Get the detector function for a component type.

        Args:
            comp_type: The component type to get the detector for

        Returns:
            Callable: The detector function if registered, None otherwise
        """
        return cls._type_detectors.get(comp_type)

    @classmethod
    def get_renderer(cls, comp_type: ComponentType) -> Optional[Callable]:
        """
        Get the renderer function for a component type.

        Args:
            comp_type: The component type to get the renderer for

        Returns:
            Callable: The renderer function if registered, None otherwise
        """
        return cls._renderers.get(comp_type)
