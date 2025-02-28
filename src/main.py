from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import BaseModel
from chatbot import start_chatbot
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

app = FastAPI()

chatbot = start_chatbot()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/")
def google_chat_webhook(request: ChatRequest):
    user_message = HumanMessage(content=request.message)
    response = chatbot.invoke({"messages": [user_message]})
    return ChatResponse(response=response["messages"][-1].content)