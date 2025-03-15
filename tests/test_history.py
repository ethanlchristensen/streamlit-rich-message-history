import pytest
from streamlit_rich_message_history import MessageHistory, Message

def test_history_add_message():
    history = MessageHistory()
    message = Message(user="user", avatar="😈")
    history.add_message(message)
    
    assert len(history.messages) == 1
    assert history.messages[0] is message

def test_history_render_last():
    history = MessageHistory()
    message1 = Message(user="user", avatar="😈")
    message2 = Message(user="assistant", avatar="☃️")
    
    history.add_message(message1)
    history.add_message(message2)
    
    # This test would need mocking as render will interact with Streamlit
    # Just testing the basic functionality without rendering
    assert len(history.messages) == 2
    assert history.messages[-1] is message2