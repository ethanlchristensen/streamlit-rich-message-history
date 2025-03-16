import streamlit as st
from streamlit_rich_message_history import MessageHistory

# Initialize the message history
history = MessageHistory()

# Step 1: Register the video component type
VIDEO_TYPE = history.register_component_type("video")

# Step 2: Register a renderer for videos
def video_renderer(content, kwargs):
    st.video(content, start_time=kwargs.get("start_time", 0))

history.register_component_renderer(VIDEO_TYPE, video_renderer)

# Step 3: Register the add_video() method
history.register_component_method("add_video", VIDEO_TYPE)

# Now you can use add_video() directly in your application:
assistant_msg = history.add_assistant_message_create("🤖")
assistant_msg.add_text("Here's a sample video:")

# Use the new add_video method directly
assistant_msg.add_video(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ", 
    start_time=0
)

# Render all messages
history.render_all()