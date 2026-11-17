"""Session management utilities.
Provides a function to initialise required keys in Streamlit's session_state.
"""
import streamlit as st

def init_session():
    """Initialise default session_state values.
    Called once at app start.
    """
    defaults = {
        "random_seed": 42,
        "synthetic_data": {},  # module -> DataFrame
        "uploaded_data": {},   # module -> DataFrame
        "scenarios": [],       # saved scenarios list
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
