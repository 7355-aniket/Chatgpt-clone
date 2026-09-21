import asyncio
import json
import time
import re
import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx

app = FastAPI(title="ChatGPT Web Application")

# Mount static files directory safely (works both with or without static subfolder)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
else:
    app.mount("/static", StaticFiles(directory="."), name="static")

class SettingsModel(BaseModel):
    openai_key: Optional[str] = ""
    gemini_key: Optional[str] = ""
    persona: Optional[str] = "default"
    typing_speed: Optional[int] = 25

class ChatRequest(BaseModel):
    model: str
    messages: List[Dict[str, str]]
    settings: Optional[SettingsModel] = SettingsModel()

@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = "static/index.html" if os.path.exists("static/index.html") else "index.html"
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": time.time()}

@app.post("/api/chat/stream")
async def chat_stream(request_data: ChatRequest):
    messages = request_data.messages
    if not messages:
        raise HTTPException(status_code=400, detail="No messages provided.")

    model = request_data.model
    settings = request_data.settings or SettingsModel()
    last_user_message = messages[-1].get("content", "").strip()

    if model == "gpt-4o" and settings.openai_key:
        return StreamingResponse(
            stream_openai(settings.openai_key, messages),
            media_type="text/event-stream"
        )

    if model == "gemini-pro" and settings.gemini_key:
        return StreamingResponse(
            stream_gemini(settings.gemini_key, messages),
            media_type="text/event-stream"
        )

    return StreamingResponse(
        stream_smart_ai(last_user_message, settings.persona, settings.typing_speed or 25),
        media_type="text/event-stream"
    )

async def stream_smart_ai(prompt: str, persona: str, typing_speed_ms: int):
    response_text = generate_response_for_prompt(prompt, persona)
    tokens = re.findall(r'\S+|\s+', response_text)
    delay_sec = max(0.005, typing_speed_ms / 1000.0)

    for token in tokens:
        data = json.dumps({"content": token})
        yield f"data: {data}\n\n"
        await asyncio.sleep(delay_sec)

    yield "data: [DONE]\n\n"

def generate_response_for_prompt(prompt: str, persona: str) -> str:
    lower_p = prompt.lower()
    prefix = ""
    if persona == "coder":
        prefix = "As a Senior Code Architect, here is the clean, production-ready solution:\n\n"
    elif persona == "concise":
        prefix = "Here is the direct answer:\n\n"
    elif persona == "creative":
        prefix = "Let's bring this idea to life with imagination! ✨\n\n"

    if any(k in lower_p for k in ["python", "script", "code", "scrape", "function", "javascript", "html", "css", "c++", "java", "sql", "api"]):
        if "python" in lower_p or "scrape" in lower_p or "script" in lower_p:
            return prefix + (
                "Here is a complete Python solution designed for clean execution and clarity:\n\n"
                "```python\n"
                "import requests\n"
                "from bs4 import BeautifulSoup\n"
                "import json\n"
                "import sys\n\n"
                "def fetch_news_headlines(url: str):\n"
                "    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}\n"
                "    try:\n"
                "        response = requests.get(url, headers=headers, timeout=10)\n"
                "        response.raise_for_status()\n"
                "        soup = BeautifulSoup(response.text, 'html.parser')\n"
                "        headlines = []\n"
                "        for idx, item in enumerate(soup.find_all(['h1', 'h2', 'h3']), 1):\n"
                "            text = item.get_text(strip=True)\n"
                "            if text and len(text) > 10:\n"
                "                headlines.append({'id': idx, 'headline': text, 'length': len(text)})\n"
                "        return headlines\n"
                "    except Exception as err:\n"
                "        print(f'Error fetching data: {err}', file=sys.stderr)\n"
                "        return []\n\n"
                "if __name__ == '__main__':\n"
                "    target_url = 'https://news.ycombinator.com'\n"
                "    results = fetch_news_headlines(target_url)\n"
                "    print(json.dumps(results[:5], indent=2))\n"
                "```\n\n"
                "### Key Features of this Script:\n"
                "1. **Robust Error Handling**: Handles network timeouts gracefully.\n"
                "2. **Custom User-Agent Header**: Prevents requests from being blocked.\n"
                "3. **Structured JSON Output**: Formats clean data ready for storage.\n"
            )
        else:
            return prefix + (
                "Here is the requested code implementation along with explanations:\n\n"
                "```javascript\n"
                "async function processChatRequest(endpoint, payload) {\n"
                "  try {\n"
                "    const response = await fetch(endpoint, {\n"
                "      method: 'POST',\n"
                "      headers: { 'Content-Type': 'application/json' },\n"
                "      body: JSON.stringify(payload)\n"
                "    });\n"
                "    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);\n"
                "    const data = await response.json();\n"
                "    return { success: true, data };\n"
                "  } catch (error) {\n"
                "    console.error('API Error:', error.message);\n"
                "    return { success: false, error: error.message };\n"
                "  }\n"
                "}\n"
                "```\n"
            )

    if "quantum" in lower_p or "analogy" in lower_p or "explain" in lower_p:
        return prefix + (
            "### 🌌 Quantum Computing Explained\n\n"
            "Imagine a standard classical computer as a **light switch**. It can only ever be in one of two positions:\n"
            "- **OFF (0)** or **ON (1)**\n\n"
            "Now imagine a quantum computer. Instead of a light switch, picture a **spinning coin** on a table:\n\n"
            "1. **Superposition**: While the coin is spinning rapidly, it's a blur of both Heads and Tails at the same time.\n"
            "2. **Entanglement**: Two spinning coins magically linked together.\n"
        )

    return prefix + (
        f"Hello! I am ChatGPT, an AI assistant built to help you with answering questions, writing code, brainstorming creative ideas, and solving complex problems.\n\n"
        f"You asked: **\"{prompt}\"**\n\n"
        "How would you like to explore this topic further?"
    )

async def stream_openai(api_key: str, messages: List[Dict[str, str]]):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": "gpt-4o-mini", "messages": messages, "stream": True}
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    yield f"data: {json.dumps({'content': '⚠️ OpenAI API Error'})}\n\n"
                    yield "data: [DONE]\n\n"
                    return
                async for chunk in response.aiter_lines():
                    if chunk.startswith("data: "):
                        data_str = chunk.replace("data: ", "").strip()
                        if data_str == "[DONE]": break
                        try:
                            parsed = json.loads(data_str)
                            delta = parsed["choices"][0]["delta"].get("content", "")
                            if delta: yield f"data: {json.dumps({'content': delta})}\n\n"
                        except Exception: pass
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'content': f'⚠️ Connection Error: {str(e)}'})}\n\n"
            yield "data: [DONE]\n\n"

async def stream_gemini(api_key: str, messages: List[Dict[str, str]]):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?key={api_key}"
    contents = [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in messages]
    payload = {"contents": contents}
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    yield f"data: {json.dumps({'content': '⚠️ Gemini API Error'})}\n\n"
                    yield "data: [DONE]\n\n"
                    return
                async for chunk in response.aiter_text():
                    try:
                        parsed = json.loads(chunk)
                        if isinstance(parsed, list):
                            for item in parsed:
                                text = item["candidates"][0]["content"]["parts"][0]["text"]
                                yield f"data: {json.dumps({'content': text})}\n\n"
                    except Exception: pass
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'content': f'⚠️ Gemini Connection Error: {str(e)}'})}\n\n"
            yield "data: [DONE]\n\n"

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting ChatGPT Web Server on http://0.0.0.0:{port}")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
