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
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASH_DIR = os.path.join(BASE_DIR, '..', 'dashboard')
LAND_DIR = os.path.join(BASE_DIR, '..', 'landing')
if os.path.exists(DASH_DIR):
      app.mount('/dashboard', StaticFiles(directory=DASH_DIR, html=True), name='dashboard')
  if os.path.exists(LAND_DIR):
        app.mount('/landing', StaticFiles(directory=LAND_DIR, html=True), name='landing')
    WIDG_DIR = os.path.join(BASE_DIR, '..', 'widget')
if os.path.exists(WIDG_DIR):
      app.mount('/widget', StaticFiles(directory=WIDG_DIR, html=True), name='widget')

CLIENT_CONFIG = {
      "business_name": "Zara Beauty Salon",
      "agent_name": "Zara",
      "description": "Premium beauty salon offering haircuts, coloring, facials, bridal packages.",
      "services": ["Haircut", "Hair Coloring", "Facial", "Bridal Package", "Nail Art"],
      "hours": "Monday to Saturday, 9 AM to 8 PM",
      "location": "DHA Phase 2, Lahore, Pakistan",
      "phone": "+92-300-1234567",
      "pricing": {
                "Haircut": "Rs. 800 to 2000",
                "Hair Coloring": "Rs. 3000 to 8000",
                "Facial": "Rs. 1500 to 4000",
                "Bridal Package": "Rs. 25,000 to 60,000",
                "Nail Art": "Rs. 600 to 1500",
      }
}

SYSTEM_PROMPT = f"""You are {CLIENT_CONFIG['agent_name']}, a friendly AI support agent for {CLIENT_CONFIG['business_name']}.
About: {CLIENT_CONFIG['description']}
Services: {', '.join(CLIENT_CONFIG['services'])}
Hours: {CLIENT_CONFIG['hours']}
Location: {CLIENT_CONFIG['location']}
Phone: {CLIENT_CONFIG['phone']}
Pricing: {str(CLIENT_CONFIG['pricing'])}
Instructions: Answer customer queries helpfully. Help book appointments. Capture leads. Be warm and concise. Respond in same language as customer. Keep replies under 100 words."""

class Message(BaseModel):
      role: str
      content: str

class ChatRequest(BaseModel):
      messages: List[Message]
      client_id: Optional[str] = "default"

class ChatResponse(BaseModel):
      reply: str
      model: str

@app.get("/")
def root():
      return {"status": "ReplyAgent running", "business": CLIENT_CONFIG["business_name"]}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
      api_key = os.getenv("GROQ_API_KEY")
      if not api_key:
                raise HTTPException(status_code=500, detail="GROQ_API_KEY not set.")
            client = Groq(api_key=api_key)
    history = [{"role": m.role, "content": m.content} for m in req.messages]
    response = client.chat.completions.create(
              model="llama-3.3-70b-versatile",
              messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
              max_tokens=512,
              temperature=0.7,
    )
    return ChatResponse(reply=response.choices[0].message.content, model=response.model)

@app.get("/status")
def status():

  
      key = os.getenv("GROQ_API_KEY", "")
    return {"agent": CLIENT_CONFIG["agent_name"], "business": CLIENT_CONFIG["business_name"], "api_key_set": bool(key)}

if __name__ == "__main__":
      import uvicorn
    uvicorn.run("agent:app", host="0.0.0.0", port=8000, reload=True)
