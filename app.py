"""entry point — launches the Streamlit UI"""

from dotenv import load_dotenv

import streamlit as st
from ui.streamlit_ui import main

# Load GOOGLE_API_KEY (and any other secrets) from .env into the environment
# before the evaluator instantiates the Gemini client.
load_dotenv()

if __name__ == "__main__":
    main()
