from enum import Enum
from typing import Dict, Any, Callable, Type, Optional


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


# Registry to store custom component renderers
class ComponentRegistry:
    """Registry to manage custom component types and renderers."""
    
    _custom_types: Dict[str, ComponentType] = {}
    _type_detectors: Dict[ComponentType, Callable[[Any, Dict[str, Any]], bool]] = {}
    _renderers: Dict[ComponentType, Callable[[Any, Dict[str, Any]], None]] = {}
    
    @classmethod
    def register_component_type(cls, name: str) -> ComponentType:
        """Register a new component type with the given name."""
        if name in [t.value for t in ComponentType] + list(cls._custom_types.keys()):
            raise ValueError(f"Component type '{name}' already exists")
        
        # Create a new ComponentType dynamically
        custom_type = object.__new__(ComponentType)
        custom_type._name_ = name.upper()
        custom_type._value_ = name
        
        cls._custom_types[name] = custom_type
        return custom_type
    
    @classmethod
    def register_detector(cls, comp_type: ComponentType, 
                         detector: Callable[[Any, Dict[str, Any]], bool]) -> None:
        """Register a detector function for a component type."""
        cls._type_detectors[comp_type] = detector
    
    @classmethod
    def register_renderer(cls, comp_type: ComponentType, 
                         renderer: Callable[[Any, Dict[str, Any]], None]) -> None:
        """Register a renderer function for a component type."""
        cls._renderers[comp_type] = renderer
    
    @classmethod
    def get_custom_type(cls, name: str) -> Optional[ComponentType]:
        """Get a custom component type by name."""
        return cls._custom_types.get(name)
    
    @classmethod
    def get_all_types(cls) -> list:
        """Get all component types (built-in and custom)."""
        return list(ComponentType) + list(cls._custom_types.values())
    
    @classmethod
    def get_detector(cls, comp_type: ComponentType) -> Optional[Callable]:
        """Get the detector function for a component type."""
        return cls._type_detectors.get(comp_type)
    
    @classmethod
    def get_renderer(cls, comp_type: ComponentType) -> Optional[Callable]:
        """Get the renderer function for a component type."""
        return cls._renderers.get(comp_type)