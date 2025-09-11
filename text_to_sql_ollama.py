# text_to_sql_ollama.py
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent
from langchain_community.chat_models import ChatOllama


db = SQLDatabase.from_uri(
    "mssql+pyodbc://admin:admin@localhost\\MSSQLSERVER03/DataWarehouseClassic?driver=ODBC+Driver+17+for+SQL+Server"
)

llm = ChatOllama(model="llama3.1", temperature=0)

# Create toolkit & agent
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,  # Show reasoning + SQL queries in terminal
)

print("Llama 3.1 SQL Agent connected. Type 'exit' to quit.\n")

while True:
    user_input = input("Ask a question about your data: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    try:
        response = agent_executor.run(user_input)
        print(f"Answer:\n{response}\n")
    except Exception as e:
        print(f"Error: {e}\n")
