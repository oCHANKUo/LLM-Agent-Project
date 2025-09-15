# backend_text_to_sql_flask.py
import os
import re
import pyodbc
from flask import Flask, request, jsonify
from flask import render_template_string
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

@app.route("/ask", methods=["GET", "POST"])
def ask_question():
    try:
        # Get question from POST JSON or GET query string
        if request.method == "POST":
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 415
            data = request.get_json()
            question = data.get("question", "")
        else:  # GET
            question = request.args.get("question", "")

        if not question:
            return jsonify({"error": "No question provided"}), 400

        # Run agent → returns LLM output (may include SQL + result)
        llm_output = agent_executor.run(question)

        # Extract first SELECT statement to run manually
        match = re.search(r"(SELECT .*?)(?:\n|$)", llm_output, re.IGNORECASE)
        if not match:
            return jsonify({"error": "No valid SQL generated"}), 400

        sql_query = match.group(1)

        # Execute SQL to get structured rows
        rows = execute_sql_query(sql_query)
        answer = format_result_natural(rows)

        # GET → show nicely in browser
        if request.method == "GET":
            return render_template_string(f"""
                <h2>Question:</h2>
                <p>{question}</p>
                <h2>Generated SQL:</h2>
                <pre>{sql_query}</pre>
                <h2>Answer:</h2>
                <p>{answer}</p>
                <br>
                <a href="/">Ask another question</a>
            """)

        # POST → return clean JSON
        return jsonify({
            "question": question,
            "sql": sql_query,
            "rows": rows,
            "answer": answer
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ask SQL Bot</title>
    </head>
    <body style="font-family: Arial; margin: 40px;">
        <h2>Ask a Question</h2>
        <form action="/ask" method="get">
            <input type="text" name="question" placeholder="Type your question here" style="width: 300px; padding: 8px;">
            <button type="submit" style="padding: 8px;">Ask</button>
        </form>
    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run(debug=True)