# terminal_text_to_sql.py
import re
import pyodbc
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
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(llm=llm, toolkit=toolkit, verbose=False)

def execute_sql_query(sql: str):
    """Executes SQL safely and returns rows as list of dicts."""
    conn = pyodbc.connect(DB_CONNECTION)
    cursor = conn.cursor()
    cursor.execute(sql)
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]

def format_result_natural(rows):
    """Turns SQL result into a natural language sentence."""
    if not rows:
        return "No results found."

    first_row = rows[0]
    if len(first_row) == 1:
        key, value = list(first_row.items())[0]
        return f"There are {value} {key.replace('_', ' ').lower()} in the database."

    return f"Here are the results: {rows}"

# Main loop
def main():
    print("=== Terminal SQL Bot ===\n")
    while True:
        question = input("Enter your question (or 'exit' to quit): ").strip()
        if question.lower() == "exit":
            print("Goodbye!")
            break

        llm_output = agent_executor.run(question)

        match = re.search(r"(SELECT .*?)(?:\n|$)", llm_output, re.IGNORECASE)
        if not match:
            print("Error: No valid SQL generated.\n")
            continue

        sql_query = match.group(1)

        rows = execute_sql_query(sql_query)
        answer = format_result_natural(rows)

        print("\n--- Results ---")
        print(f"Question: {question}")
        print(f"Generated SQL: {sql_query}")
        print(f"Answer: {answer}\n")

if __name__ == "__main__":
    main()