# Custom Component Types

One of the powerful features of this package is the ability to create your own custom component types. This allows you to extend the package to display any type of content in your Streamlit app.

## Creating a Custom Video Component

Here's a complete example of creating a custom video component:

```python
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
assistant_msg.add_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
```

## Adding a Custom Component Detector

You can also register a custom detector to automatically identify certain content types:

```python
def video_detector(content, kwargs):
    return isinstance(content, str) and (
        content.endswith(".mp4") or 
        "youtube.com" in content or 
        "vimeo.com" in content or
        kwargs.get("is_video", False)
    )

history.register_component_detector(VIDEO_TYPE, video_detector)
```