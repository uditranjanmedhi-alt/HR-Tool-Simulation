# hr_simulate/data/data_loader.py
"""Utility to load CSV or Excel files into a Pandas DataFrame.
Used by the upload component across modules.
"""
import pandas as pd
import io

def load_file(uploaded_file) -> pd.DataFrame | None:
    """Load a Streamlit uploaded file into a DataFrame.

    Parameters
    ----------
    uploaded_file : UploadedFile
        The file object returned by st.file_uploader.

    Returns
    -------
    pd.DataFrame or None
        Returns a DataFrame if successful, otherwise None.
    """
    try:
        filename = uploaded_file.name
        if filename.lower().endswith('.csv'):
            # read directly from bytes
            return pd.read_csv(io.BytesIO(uploaded_file.getvalue()))
        elif filename.lower().endswith(('.xlsx', '.xls')):
            return pd.read_excel(io.BytesIO(uploaded_file.getvalue()))
        else:
            return None
    except Exception as e:
        print(f"Error loading file {uploaded_file.name}: {e}")
        return None
