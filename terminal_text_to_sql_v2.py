# terminal_text_to_sql.py
import pyodbc
from db_schema import TABLE_SCHEMAS
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent
from langchain_community.chat_models import ChatOllama

DB_CONNECTION = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\MSSQLSERVER03;"
    "DATABASE=DataWarehouseClassic;"
    "UID=admin;"
    "PWD=admin;"
)

db = SQLDatabase.from_uri(
    "mssql+pyodbc://admin:admin@localhost\\MSSQLSERVER03/DataWarehouseClassic?driver=ODBC+Driver+17+for+SQL+Server"
)
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
            raw_answer = agent_executor.run(question)
            human_answer = llm.invoke(f"""
            You are a helpful assistant. 
            The user asked: "{question}"
            The database returned: "{raw_answer}"

            Write a short, natural language answer for the user.
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