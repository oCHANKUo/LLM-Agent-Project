from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.llms import LlamaCpp
import config

llm = LlamaCpp(
    model_path=config.LLAMA_MODEL_PATH,
    model_kwargs={"temperature": 0.7, "max_tokens": 512}
)


db = SQLDatabase.from_uri(config.DB_CONNECTION_STRING)

sql_chain = create_sql_query_chain(
    llm, db, verbose=True
)

# Tool Function
def text_to_sql(query: str) -> str:
    return sql_chain.run(query)

