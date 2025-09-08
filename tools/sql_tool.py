from langchain_community.utilities import SQLDatabase
from langchain.chains import SQLDatabaseChain
from langchain_community.llms import LlamaCpp
import config

llm = LlamaCpp(model_path=config.LLAMA_MODEL_PATH)

db = SQLDatabase.from_uri(config.DB_CONNECTION_STRING)

sql_chain = SQLDatabaseChain(
    llm, db, verbose=True
)

# Tool Function
def text_to_sql(query: str) -> str:
    return sql_chain.run(query)

