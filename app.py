# File: app.py

import streamlit as st
import os
import tempfile
from db_schema_logic import extract_schema, setup_llm_chain, generate_sql_query

# Set the page title
st.set_page_config(page_title="SQL Query Generator", page_icon=":mag:")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');
    
    body {
        font-family: 'Roboto', sans-serif;
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .stApp {
        background-color: #1E1E1E;
    }
    .app-title {
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        color: #FFFFFF;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .app-description {
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 3rem;
        color: #B0B0B0;
    }
    .custom-button {
        display: inline-block;
        width: 100%;
        padding: 1.5rem;
        background: linear-gradient(145deg, #2E2E2E, #1A1A1A);
        border: none;
        border-radius: 15px;
        box-shadow: 5px 5px 15px #0D0D0D, -5px -5px 15px #2D2D2D;
        text-align: center;
        text-decoration: none;
        color: #FFFFFF;
        font-size: 1.2rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .custom-button:hover {
        background: linear-gradient(145deg, #1A1A1A, #2E2E2E);
        transform: translateY(-5px);
        box-shadow: 8px 8px 20px #0D0D0D, -8px -8px 20px #2D2D2D;
    }
    .icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .icon-websites { color: #FF6B6B; }
    .icon-database { color: #4ECDC4; }
    .icon-pdf { color: #45B7D1; }
    .footer {
        text-align: center;
        color: #B0B0B0;
        margin-top: 3rem;
        padding: 1rem;
        font-size: 0.9rem;
    }
    .social-links a {
        color: #808080;  /* Greyish color for the icons */
        font-size: 2rem;
        margin: 0 10px;
    }
</style>
""", unsafe_allow_html=True)

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

st.markdown("""
<div class="footer">
    <div class="social-links">
        <a href="https://www.instagram.com/parasmadan.in/" target="_blank"><i class="fab fa-instagram"></i></a>
        <a href="https://www.linkedin.com/in/paras-madan-a9863716b/" target="_blank"><i class="fab fa-linkedin"></i></a>
        <a href="https://twitter.com/ParasMadan9" target="_blank"><i class="fab fa-twitter"></i></a>
        <a href="https://parasmadan.in/" target="_blank"><i class="fas fa-globe"></i></a>
    </div>
</div>
""", unsafe_allow_html=True)
