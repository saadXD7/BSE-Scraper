from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os
from dotenv import load_dotenv
from pdf_engine import PDFKnowledgeEngine, LLMFactory

# Load environment variables strictly from .env
load_dotenv(dotenv_path="../.env")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Initialize Engine globally based on .env config
PROVIDER = os.getenv("LLM_PROVIDER", "groq")
API_KEY = os.getenv("API_KEY")

try:
    provider = LLMFactory.get_provider(PROVIDER, api_key=API_KEY)
    engine = PDFKnowledgeEngine("annual_report.pdf", provider)
except Exception as e:
    engine = None
    print(f"Failed to initialize LLM: {e}")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "answer": None})

@app.post("/query", response_class=HTMLResponse)
async def process_query(request: Request, question: str = Form(...)):
    if not engine:
        answer = "System initialization error: Please check your .env API keys."
    else:
        answer = engine.query(question)
    return templates.TemplateResponse("index.html", {"request": request, "question": question, "answer": answer})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)