from streamlit_rich_message_history import Message, ComponentType


def test_message_chaining():
    message = Message(user="user", avatar="😈")
    result = message.add_text("Hello").add_metric(42, "Answer")
    assert result is message  # Method chaining returns the message
    assert len(message.components) == 2


def test_message_add_methods():
    message = Message(user="assistant", avatar="☃️")
    message.add_text("Text message")
    message.add_error("Error message")
    message.add_metric(99, "Score")

    assert len(message.components) == 3
    assert message.components[0].component_type == ComponentType.TEXT
    assert message.components[1].component_type == ComponentType.ERROR
    assert message.components[2].component_type == ComponentType.METRIC
