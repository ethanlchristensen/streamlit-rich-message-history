"""
Tests for custom component functionality in streamlit_rich_message_history.

This module tests the registration and usage of custom component types,
detectors, renderers, and custom message methods.
"""

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch

from streamlit_rich_message_history.enums import ComponentRegistry, ComponentType
from streamlit_rich_message_history.components import MessageComponent
from streamlit_rich_message_history.messages import Message, UserMessage
from streamlit_rich_message_history.history import MessageHistory


class TestCustomComponents:
    def setup_method(self):
        """Save original registry state before each test."""
        # Save original registries
        self._original_custom_types = ComponentRegistry._custom_types.copy() if hasattr(ComponentRegistry, '_custom_types') else {}
        self._original_type_detectors = ComponentRegistry._type_detectors.copy() if hasattr(ComponentRegistry, '_type_detectors') else {}
        self._original_type_renderers = ComponentRegistry._type_renderers.copy() if hasattr(ComponentRegistry, '_type_renderers') else {}
        self._original_methods = Message._custom_component_methods.copy() if hasattr(Message, '_custom_component_methods') else {}
        
        # Clear registries
        if hasattr(ComponentRegistry, '_custom_types'):
            ComponentRegistry._custom_types = {}
        else:
            ComponentRegistry._custom_types = {}
            
        if hasattr(ComponentRegistry, '_type_detectors'):
            ComponentRegistry._type_detectors = {}
        else:
            ComponentRegistry._type_detectors = {}
            
        if hasattr(ComponentRegistry, '_type_renderers'):
            ComponentRegistry._type_renderers = {}
        else:
            ComponentRegistry._type_renderers = {}
            
        if hasattr(Message, '_custom_component_methods'):
            Message._custom_component_methods = {}
        else:
            Message._custom_component_methods = {}
    
    def teardown_method(self):
        """Restore original registry state after each test."""
        ComponentRegistry._custom_types = self._original_custom_types
        ComponentRegistry._type_detectors = self._original_type_detectors
        ComponentRegistry._type_renderers = self._original_type_renderers
        Message._custom_component_methods = self._original_methods

    def test_register_component_type(self):
        """Test registering a new component type."""
        # Register a new component type
        image_type = MessageHistory.register_component_type("image")
        
        # Verify the type was registered
        assert isinstance(image_type, ComponentType)
        assert image_type.value == "image"
        assert ComponentRegistry.get_custom_type("image") == image_type

    def test_register_component_detector(self):
        """Test registering a detector for a custom component type."""
        # Create a component type
        image_type = MessageHistory.register_component_type("image")
        
        # Create a detector function for PIL images
        def is_pil_image(content, kwargs):
            return hasattr(content, 'mode') and hasattr(content, 'size')
        
        # Register the detector
        MessageHistory.register_component_detector(image_type, is_pil_image)
        
        # Verify the detector was registered
        assert ComponentRegistry.get_detector(image_type) == is_pil_image

    def test_register_component_renderer(self):
        """Test registering a renderer for a custom component type."""
        # Create a component type
        image_type = MessageHistory.register_component_type("image")
        
        # Create a renderer function
        def render_image(content, kwargs):
            # In a real implementation, this would call st.image
            pass
        
        # Register the renderer
        MessageHistory.register_component_renderer(image_type, render_image)
        
        # Verify the renderer was registered
        assert ComponentRegistry.get_renderer(image_type) == render_image

    def test_register_component_method(self):
        """Test registering a custom component method to the Message class."""
        # Create a component type
        image_type = MessageHistory.register_component_type("image")
        
        # Register a method for adding images
        MessageHistory.register_component_method("add_image", image_type)
        
        # Verify the method was registered
        assert hasattr(Message, "add_image")
        assert "add_image" in Message._custom_component_methods
        assert Message._custom_component_methods["add_image"] == image_type

    def test_custom_method_with_custom_function(self):
        """Test registering a component method with a custom function."""
        # Create a component type
        chart_type = MessageHistory.register_component_type("custom_chart")
        
        # Create a custom method function
        def add_custom_chart(self, data, title=None, **kwargs):
            """Add a custom chart component with special processing."""
            # Process the data before adding
            processed_data = {"chart_data": data, "processed": True}
            return self.add_custom(processed_data, component_type=chart_type.value, 
                                   title=title, **kwargs)
        
        # Register the method with the custom function
        MessageHistory.register_component_method(
            "add_custom_chart", chart_type, add_custom_chart)
        
        # Verify the method works as expected
        message = Message("user", "👤")
        with patch.object(message, 'add_custom') as mock_add_custom:
            message.add_custom_chart([1, 2, 3], title="My Chart")
            mock_add_custom.assert_called_once_with(
                {"chart_data": [1, 2, 3], "processed": True}, 
                component_type=chart_type.value, title="My Chart"
            )

    @patch('streamlit.chat_message')
    def test_component_detection_with_custom_detector(self, mock_chat_message):
        """Test that custom component detection works properly."""
        # Create a mock context manager for st.chat_message
        mock_context = MagicMock()
        mock_chat_message.return_value = mock_context
        
        # Create a component type and detector
        special_type = MessageHistory.register_component_type("special")
        
        def is_special(content, kwargs):
            return isinstance(content, dict) and content.get('special') is True
        
        MessageHistory.register_component_detector(special_type, is_special)
        
        # Create a component with content that should be detected as special
        with patch('streamlit_rich_message_history.components.st') as mock_st:
            component = MessageComponent({'special': True})
            
            # Verify the component was detected as the special type
            assert component.component_type == special_type

    @patch('streamlit.chat_message')
    def test_custom_renderer_is_called(self, mock_chat_message):
        """Test that custom renderers are called for custom component types."""
        # Create a mock context manager for st.chat_message
        mock_context = MagicMock()
        mock_chat_message.return_value = mock_context
        
        # Create a component type, detector, and renderer
        special_type = MessageHistory.register_component_type("special")
        
        def is_special(content, kwargs):
            return isinstance(content, dict) and content.get('special') is True
        
        renderer_mock = MagicMock()
        
        MessageHistory.register_component_detector(special_type, is_special)
        MessageHistory.register_component_renderer(special_type, renderer_mock)
        
        # Create and render a component
        component = MessageComponent({'special': True})
        
        with patch('streamlit_rich_message_history.components.st'):
            component._render_content()
            
            # Verify the renderer was called
            renderer_mock.assert_called_once_with({'special': True}, {})

    @patch('streamlit.chat_message')
    def test_custom_method_usage_in_message(self, mock_chat_message):
        """Test using a custom method in a Message."""
        # Create a mock context manager for st.chat_message
        mock_context = MagicMock()
        mock_chat_message.return_value = mock_context
        
        # Register custom component
        badge_type = MessageHistory.register_component_type("badge")
        
        MessageHistory.register_component_method("add_badge", badge_type)
        
        # Create a message and use the custom method
        message = UserMessage("👤", "Hello")
        
        with patch.object(message, 'add_custom') as mock_add_custom:
            message.add_badge({"label": "New", "color": "green"})
            
            # Verify add_custom was called with the right parameters
            mock_add_custom.assert_called_once_with(
                {"label": "New", "color": "green"}, 
                component_type="badge"
            )

    def test_message_history_with_custom_components(self):
        """Test using custom components with MessageHistory."""
        # Register custom component
        alert_type = MessageHistory.register_component_type("alert")
        
        def render_alert(content, kwargs):
            # This would render an alert in a real implementation
            pass
        
        MessageHistory.register_component_renderer(alert_type, render_alert)
        MessageHistory.register_component_method("add_alert", alert_type)
        
        # Create a message history and add messages with custom components
        history = MessageHistory()
        user_msg = history.add_user_message_create("👤", "Check this out:")
        
        with patch.object(user_msg, 'add_custom') as mock_add_custom:
            user_msg.add_alert({"level": "warning", "message": "Low disk space"})
            
            # Verify add_custom was called correctly
            mock_add_custom.assert_called_once_with(
                {"level": "warning", "message": "Low disk space"}, 
                component_type="alert"
            )

    @patch('streamlit.chat_message')
    @patch('streamlit_rich_message_history.components.st')
    def test_error_handling_for_custom_components(self, mock_st, mock_chat_message):
        """Test error handling when rendering custom components."""
        # Create a mock context manager for st.chat_message
        mock_context = MagicMock()
        mock_chat_message.return_value = mock_context
        
        # Create a component type with a renderer that raises an exception
        crash_type = MessageHistory.register_component_type("crash")
        
        def crash_renderer(content, kwargs):
            raise ValueError("Simulated error in custom renderer")
        
        MessageHistory.register_component_renderer(crash_type, crash_renderer)
        
        # Create a component and render it
        component = MessageComponent({'data': 'test'}, component_type=crash_type)
        component._render_content()
        
        # Verify error was displayed
        mock_st.error.assert_called_once()
        assert "error" in mock_st.error.call_args[0][0].lower()
        
        # Verify debug info was shown
        mock_st.expander.assert_called()