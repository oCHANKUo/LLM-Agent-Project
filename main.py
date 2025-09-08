from langchain_community.llms import LlamaCpp
from langchain.agents import initialize_agent, AgentType, Tool
from tools import sql_tool
from tools import predictive_tools
import config

llm = LlamaCpp(model_path=config.LLAMA_MODEL_PATH)

sql_query_tool = Tool(
    name="SQLQuery",
    func=sql_tool.text_to_sql_tool,
    description="Query the MSSQL data warehouse."
)

all_tools = [sql_query_tool] + predictive_tools.tools

agent = initialize_agent(
    tools=all_tools,
    llm=llm,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

if __name__ == "__main__":
    print(agent.run("What are sales for January of 2014?"))