# File: app.py

import streamlit as st
import os
import tempfile
from db_schema_logic import extract_schema, setup_llm_chain, generate_sql_query

# Set the page title
st.set_page_config(page_title="SQL Query Generator", page_icon=":mag:")

def main():
    st.title("Advanced Text to SQL")
    st.write("Generate SQL queries from natural language")

    # Sidebar for configuration
    st.sidebar.header("Configuration")
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    
    # Default database URL
    default_db_url = "sqlite:///new.db"
    
    # File uploader for database
    uploaded_file = st.sidebar.file_uploader("Upload a SQLite database", type=["db", "sqlite"])
    
    # Button to process the uploaded database
    process_db = st.sidebar.button("Process Uploaded Database")
    
    # Initialize session state
    if 'db_processed' not in st.session_state:
        st.session_state.db_processed = False
    if 'db_url' not in st.session_state:
        st.session_state.db_url = default_db_url
    if 'schema' not in st.session_state:
        st.session_state.schema = None
    if 'temp_db_file' not in st.session_state:
        st.session_state.temp_db_file = None
    
    if uploaded_file is not None and process_db:
        # Create a temporary file to store the uploaded database
        if st.session_state.temp_db_file:
            st.session_state.temp_db_file.close()
        
        st.session_state.temp_db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        st.session_state.temp_db_file.write(uploaded_file.getvalue())
        st.session_state.temp_db_file.flush()
        
        st.session_state.db_url = f"sqlite:///{st.session_state.temp_db_file.name}"
        st.session_state.db_processed = True
        with st.spinner("Extracting database schema..."):
            st.session_state.schema = extract_schema(st.session_state.db_url)
        st.sidebar.success("Database processed successfully!")
    elif process_db and uploaded_file is None:
        st.sidebar.warning("Please upload a database file first.")
    
    st.sidebar.markdown("[Download sample database](https://example.com/sample.db)")  # Replace with actual download link
    
    if not openai_api_key:
        st.warning("Please enter your OpenAI API key in the sidebar.")
        return

    if st.session_state.schema:
        st.subheader("Database Schema")
        st.code(st.session_state.schema)

        # Set up LLM chain
        try:
            chain = setup_llm_chain(openai_api_key)
        except ValueError as e:
            st.error(f"Error setting up the language model: {str(e)}")
            return

        # User input
        user_question = st.text_input("Enter your question:")

        if user_question:
            with st.spinner("Generating SQL query..."):
                sql_query = generate_sql_query(chain, st.session_state.schema, user_question)
            
            st.subheader("Generated SQL Query")
            st.code(sql_query, language="sql")

            # Option to copy the query
            if st.button("Copy Query"):
                st.write("Query copied to clipboard!", icon="✅")
                st.balloons()
                st.experimental_set_query_params(clipboard=sql_query)

    else:
        st.info("Please upload a database and click 'Process Uploaded Database' to start.")

    st.sidebar.markdown("---")
    st.sidebar.write("Note: This app generates SQL queries based on the schema but does not execute them.")

if __name__ == "__main__":
    main()

# Cleanup function to be called when the Streamlit app is closed or rerun
def cleanup():
    if st.session_state.temp_db_file:
        st.session_state.temp_db_file.close()
        os.unlink(st.session_state.temp_db_file.name)
        st.session_state.temp_db_file = None

# Register the cleanup function
import atexit
atexit.register(cleanup)