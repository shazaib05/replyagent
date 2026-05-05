import os, json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="ReplyAgent API", version="1.0.0")

app.add_middleware(
          CORSMiddleware,
          allow_origins=["*"],
          allow_credentials=True,
          allow_methods=["*"],
          allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASH_DIR = os.path.join(BASE_DIR, '..', 'dashboard')
LAND_DIR = os.path.join(BASE_DIR, '..', 'landing')

if os.path.exists(DASH_DIR):
          app.mount('/dashboard', StaticFiles(directory=DASH_DIR, html=True), name='dashboard')

if os.path.exists(LAND_DIR):
          app.mount('/', StaticFiles(directory=LAND_DIR, html=True), name='landing')

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class ChatMessage(BaseModel):
          role: str
          content: str

class ChatRequest(BaseModel):
          messages: List[ChatMessage]
          model: Optional[str] = "llama3-70b-8192"

@app.post("/api/chat")
async def chat(request: ChatRequest):
          try:
                        response = client.chat.completions.create(
                                          model=request.model,
                                          messages=[{"role": m.role, "content": m.content} for m in request.messages],
                        )
                        return {"response": response.choices[0].message.content}
except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
          import uvicorn
          uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
      
