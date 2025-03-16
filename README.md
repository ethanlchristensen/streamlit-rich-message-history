# Streamlit Rich Message History

A Python package for creating rich, multi-component chat messages in Streamlit.

## Installation

### pip
```bash
pip install streamlit-rich-message-history
```

### poetry
```bash
poetry add streamlit-rich-message-history
```

## Basic Usage

```python
import streamlit as st
from streamlit_rich_message_history import MessageHistory, UserMessage, AssistantMessage

# Initialize message history
history = MessageHistory()

# Add a simple user message
history.add_user_message_create("👤", "Hello, I need data analysis help")

# Create a rich assistant response
assistant_msg = AssistantMessage("🤖")
assistant_msg.add_text("I'd be happy to help! Here's a sample dataframe:")

import pandas as pd
import numpy as np

# Create a sample dataframe
df = pd.DataFrame({
    'A': np.random.randn(5),
    'B': np.random.randn(5),
    'C': np.random.randn(5)
})

# Add components to the message
assistant_msg.add_dataframe(df, title="Sample Data")
assistant_msg.add_code("import pandas as pd\ndf = pd.read_csv('data.csv')", 
                      language="python", 
                      title="Loading Data Code")

# Add the message to history
history.add_assistant_message(assistant_msg)

# Render all messages
history.render_all()
```

## Features

- Multi-component chat messages
- Automatic type detection
- Support for various content types:
  - Text and Markdown
  - DataFrames and Series
  - Matplotlib and Plotly figures
  - Code blocks with syntax highlighting
  - Error messages
  - Metrics
  - And more!
- Custom component types

## Custom Component Types

One of the powerful features of this package is the ability to create your own custom component types. This allows you to extend the package to display any type of content in your Streamlit app.

### Creating a Custom Video Component

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

# Use the new add_video method directly
assistant_msg.add_video(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ", 
    start_time=0
)

# Render all messages
history.render_all()
```

### Custom Component with Type Detection

You can also register a detector function that will automatically detect your custom content type:

```python
# Register a detector for video content
def video_detector(content, kwargs):
    return isinstance(content, str) and (
        content.endswith(".mp4") or 
        "youtube.com" in content or 
        "vimeo.com" in content or
        kwargs.get("is_video", False)
    )

history.register_component_detector(VIDEO_TYPE, video_detector)

# Now you can add videos without explicitly using add_video
assistant_msg = history.add_assistant_message_create("🤖")
assistant_msg.add("https://www.youtube.com/watch?v=dQw4w9WgXcQ")  # Will be detected as video
```

### Custom Method Implementation

You can provide your own implementation for the custom component method:

```python
# Create a custom implementation with validation and preprocessing
def custom_video_method(self, url, start_time=0, **kwargs):
    """Add a video to the message with custom validation."""
    if not isinstance(url, str):
        raise TypeError("URL must be a string")
    
    # Normalize YouTube URLs
    if "youtube.com/watch?v=" in url:
        # Extract video ID and format URL
        video_id = url.split("watch?v=")[1].split("&")[0]
        url = f"https://youtube.com/watch?v={video_id}"
    
    return self.add_custom(url, component_type="video", start_time=start_time, **kwargs)

# Register with custom implementation
history.register_component_method("add_video", VIDEO_TYPE, custom_video_method)
```

## Documentation

For more examples and detailed documentation, visit [our documentation site](https://your-docs-site.com).

## License

MIT