# File: db_schema_logic.py

from langchain import OpenAI, LLMChain
from langchain.prompts import PromptTemplate
from sqlalchemy import create_engine, inspect

def extract_schema(db_url):
    """Extract schema from the database without accessing data."""
    engine = create_engine(db_url)
    inspector = inspect(engine)
    
    schema_info = []
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        schema_info.append(f"Table: {table_name}")
        for column in columns:
            schema_info.append(f"  - {column['name']} ({column['type']})")
    
    return "\n".join(schema_info)

def setup_llm_chain(openai_api_key):
    """Set up the LangChain components."""
    llm = OpenAI(temperature=0, openai_api_key=openai_api_key)

    prompt_template = """
    You are an AI assistant that generates SQL queries based on user requests.
    You have access to the following database schema:

    {schema}

    Based ONLY on this schema, generate a SQL query to answer the following question:

    {question}

    If the question cannot be answered using ONLY the provided schema, respond with "I cannot answer this question based on the given schema."

    SQL Query:
    """

    prompt = PromptTemplate(
        input_variables=["schema", "question"],
        template=prompt_template,
    )

    return LLMChain(llm=llm, prompt=prompt)

def generate_sql_query(chain, schema, question):
    """Generate SQL query based on the schema and question."""
    return chain.run(schema=schema, question=question)