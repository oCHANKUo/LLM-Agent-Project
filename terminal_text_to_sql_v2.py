# terminal_text_to_sql.py
import pyodbc
from db_schema import TABLE_SCHEMAS
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
# from langchain.agents import create_sql_agent
from langchain_community.agent_toolkits.sql.base import create_sql_agent
# from langchain_community.chat_models import ChatOllama
from langchain_ollama import ChatOllama
import warnings
from sqlalchemy.exc import SAWarning

warnings.filterwarnings("ignore", category=SAWarning)
# Suppress specific SQLAlchemy warnings for cleaner output

db = SQLDatabase.from_uri(
    "mssql+pyodbc://admin:admin@localhost\\MSSQLSERVER03/DataWarehouseClassic?driver=ODBC+Driver+17+for+SQL+Server"
)

system_prompt = """
You are a SQL assistant for a business database.
- Always return human-readable names for products, territories, customers, etc. (e.g., ProductName instead of ProductKey) unless the user explicitly asks for keys.
- Use SQL Server syntax (TOP, OFFSET/FETCH) instead of LIMIT.
- Format numeric totals appropriately.
- Generate queries that return clear, human-readable output.
"""
llm = ChatOllama(model="llama3.1", temperature=0)
toolkit = SQLDatabaseToolkit(db=db, llm=llm, table_info=TABLE_SCHEMAS)
agent_executor = create_sql_agent(llm=llm, toolkit=toolkit, verbose=True)  # verbose=True to see steps

def main():
    print("=== Terminal SQL Bot ===\n")
    while True:
        question = input("Enter your question (or 'exit' to quit): ").strip()
        if question.lower() == "exit":
            print("Goodbye!")
            break

        try:
            # raw_answer = agent_executor.run(question)
            raw_answer = agent_executor.invoke(question)
            human_answer = llm.invoke(f"""
            You are a helpful assistant. 
            The user asked: "{question}"
            The database returned: "{raw_answer}"

            Write the answer using the following format:

            1. Short summary sentence (1-2 lines)
            2. If tabular data, include a neat ASCII table
            3. Highlight key numbers or totals clearly

            Always follow this structure. Do not deviate.

            """) 

            # If the result is a ChatResult object, get the text:
            if hasattr(human_answer, "content"):
                human_answer = human_answer.content

            print("\n--- Results ---")
            print(f"Question: {question}")
            print(f"Answer: {human_answer}\n")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()