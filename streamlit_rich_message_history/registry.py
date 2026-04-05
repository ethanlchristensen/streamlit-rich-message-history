"""
Registry system for the streamlit_rich_message_history package.
"""

from typing import Any, Callable, Dict, Optional

from .enums import ComponentType


class ComponentRegistry:
    """
    Registry to manage custom component types, detectors, and renderers.
    """

    _custom_types: Dict[str, ComponentType] = {}
    _type_detectors: Dict[ComponentType, Callable[[Any, Dict[str, Any]], bool]] = {}
    _renderers: Dict[ComponentType, Callable[[Any, Dict[str, Any]], None]] = {}
    _detector_order: list = []

    @classmethod
    def register_component_type(cls, name: str) -> ComponentType:
        """
        Register a new custom component type.

        Args:
            name (str): The name of the custom component type.

        Returns:
            ComponentType: The newly created or existing ComponentType.
        """
        existing_types = [t.value for t in ComponentType] + list(
            cls._custom_types.keys()
        )
        if name in existing_types:
            import warnings

            warnings.warn(
                f"Component type '{name}' already exists, returning existing type"
            )
            if name in cls._custom_types:
                return cls._custom_types[name]
            else:
                for t in ComponentType:
                    if t.value == name:
                        return t

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

        Args:
            comp_type (ComponentType): The component type to register the detector for.
            detector (Callable): A function that takes (content, kwargs) and returns True if it matches.
        """
        cls._type_detectors[comp_type] = detector
        if comp_type not in cls._detector_order:
            cls._detector_order.insert(
                0, comp_type
            )  # Insert custom detectors at the beginning

    @classmethod
    def register_renderer(
        cls, comp_type: ComponentType, renderer: Callable[[Any, Dict[str, Any]], None]
    ) -> None:
        """
        Register a renderer function for a component type.

        Args:
            comp_type (ComponentType): The component type to register the renderer for.
            renderer (Callable): A function that takes (content, kwargs) and renders using streamlit.
        """
        cls._renderers[comp_type] = renderer

    @classmethod
    def get_custom_type(cls, name: str) -> Optional[ComponentType]:
        """Get a custom component type by name."""
        return cls._custom_types.get(name)

    @classmethod
    def get_all_types(cls) -> list:
        """Get all registered component types (built-in and custom)."""
        return list(ComponentType) + list(cls._custom_types.values())

    @classmethod
    def get_detector(cls, comp_type: ComponentType) -> Optional[Callable]:
        """Get the detector function for a component type."""
        return cls._type_detectors.get(comp_type)

    @classmethod
    def get_renderer(cls, comp_type: ComponentType) -> Optional[Callable]:
        """Get the renderer function for a component type."""
        return cls._renderers.get(comp_type)
