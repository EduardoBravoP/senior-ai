from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph, MessagesState
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from pinecone import Pinecone, ServerlessSpec
import os

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
INDEX_NAME = "notion-docs"  # Nome do índice no Pinecone

pc = Pinecone(api_key=PINECONE_API_KEY)

index = pc.Index(INDEX_NAME, spec=ServerlessSpec(
  cloud="aws",
  region="us-east-1"
))

def query_db(query: str):
    result = pc.inference.embed(
      "multilingual-e5-large",
      inputs=[query],
      parameters={
        "input_type": "query"
      }
    )
    embeddings = result.data[0]['values']

    result = index.query(
      vector=embeddings,
      top_k=3,
      include_metadata=True
    )

    matches = result['matches']
    results = []
    for item in matches:
      value = item['metadata']['text']
      results.append(value)

    return results

@tool
def search_answer(query: str):
  """(MANDATORY) Tool to search for answers in the Pinecone index.
    This tool MUST be used before providing any answer to the user.
    If no relevant data is found, inform the user that you cannot answer.
  """
  print("entrou na ferramenta =====================")

  return query_db(query)

prompt = """
  You are an AI assistant designed to help employees of Edu Code by answering their questions accurately and efficiently. You will search through a vector database containing company documentation to provide precise responses.

  Instructions:
  1. Search the Database: You MUST call the tool search_answer BEFORE responding to any user query. If you do not find relevant information, you MUST explicitly tell the user that you cannot answer.
  2. Format the answer with markdown: Use markdown to format the response for better readability.
  3. Provide Clear Answers: Keep your responses concise, professional, and easy to understand.
  4. Always answer in Portuguese
  5. NEVER answer something that is not in the database: If you don't find the information in the database, let the user know that you can't provide an answer.
"""

tools = [search_answer]
tool_node = ToolNode(tools)

model = ChatGroq(
  temperature = 0,
  groq_api_key=GROQ_API_KEY,
  model_name="deepseek-r1-distill-llama-70b"
).bind_tools(tools)

def call_model(state: MessagesState):
  print(state)
  messages = state["messages"]
  messages = [SystemMessage(content=prompt)] + messages
  response = model.invoke(messages)

  return {"messages": [response]}

def should_continue(state: MessagesState):
  messages = state['messages']
  last_message = messages[-1]

  if last_message.tool_calls:
    return "tools"

  return END

def start_chatbot():
  workflow = StateGraph(MessagesState)

  workflow.add_node('agent', call_model)
  workflow.add_node('tools', tool_node)

  workflow.add_edge(START, 'agent')
  workflow.add_conditional_edges('agent', should_continue)
  workflow.add_edge('tools', 'agent')

  app = workflow.compile()

  return app