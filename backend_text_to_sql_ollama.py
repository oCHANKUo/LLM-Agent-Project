# backend_text_to_sql_flask.py
import os
import pyodbc
from flask import Flask, request, jsonify
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

app = Flask(__name__)

db = SQLDatabase.from_uri(
    "mssql+pyodbc://admin:admin@localhost\\MSSQLSERVER03/DataWarehouseClassic?driver=ODBC+Driver+17+for+SQL+Server"
)
llm = ChatOllama(model="llama3.1", temperature=0)
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(llm=llm, toolkit=toolkit, verbose=True)

def execute_sql_query(sql: str):
    """Executes SQL safely and returns rows."""
    conn = pyodbc.connect(DB_CONNECTION)
    cursor = conn.cursor()
    cursor.execute(sql)
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]

def format_result_natural(question: str, rows):
    """Turns SQL result into a natural language sentence."""
    if not rows:
        return f"No results found for: {question}"
    
    first_row = rows[0]
    if len(first_row) == 1:
        key, value = list(first_row.items())[0]
        return f"There are {value} {key.replace('_', ' ').lower()} in the database."
    
    return f"Here are the results for '{question}': {rows}"

@app.route("/ask", methods=["POST"])
def ask_question():
    try:
        data = request.get_json()
        question = data.get("question", "")

        if not question:
            return jsonify({"error": "No question provided"}), 400

        # 1. Generate SQL using LLM
        sql_query = agent_executor.run(question)
        if "SELECT" not in sql_query.upper():
            return jsonify({"error": "No valid SQL generated"}), 400

        # 2. Execute SQL
        rows = execute_sql_query(sql_query)

        # 3. Format result
        answer = format_result_natural(question, rows)

        return jsonify({
            "question": question,
            "sql": sql_query,
            "answer": answer,
            "rows": rows
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)