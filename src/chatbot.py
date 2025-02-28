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
  """Tool to search for answers in the Pinecone index"""
  print("entrou na ferramenta =====================")

  return query_db(query)

prompt = """
  You are an AI assistant designed to help employees of Edu Code by answering their questions accurately and efficiently. You will search through a vector database containing company documentation, policies, guidelines, and relevant information to provide precise responses.

  Instructions:
  1. Search the Database: Retrieve the most relevant information from the vector database before responding.
  2. Provide Clear Answers: Keep your responses concise, professional, and easy to understand.
  3. Always answer in Portuguese: Edu Code is a Brazilian company, and all communication should be in Portuguese.
  4. NEVER answer something that is not in the database: If you don't find the information in the database, let the user know that you can't provide an answer.
"""

tools = [search_answer]
tool_node = ToolNode(tools)

model = ChatGroq(
  temperature = 0,
  groq_api_key=GROQ_API_KEY,
  model_name="llama-3.1-8b-instant"
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