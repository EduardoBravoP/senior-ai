from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage
from fastapi.middleware.cors import CORSMiddleware

from chatbot import start_chatbot

load_dotenv()

app = FastAPI()

chatbot = start_chatbot()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens (para produção, use um domínio específico)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os headers
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/")
def google_chat_webhook(request: ChatRequest):
    user_message = HumanMessage(content=request.message)
    response = chatbot.invoke({"messages": [user_message]})
    return ChatResponse(response=response["messages"][-1].content)