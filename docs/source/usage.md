# Usage

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