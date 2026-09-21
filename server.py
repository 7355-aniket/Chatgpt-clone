import asyncio
import json
import time
import re
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx

app = FastAPI(title="ChatGPT Web Application")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

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
    with open("static/index.html", "r", encoding="utf-8") as f:
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

    # Check if user requested live OpenAI API with custom key
    if model == "gpt-4o" and settings.openai_key:
        return StreamingResponse(
            stream_openai(settings.openai_key, messages),
            media_type="text/event-stream"
        )

    # Check if user requested live Gemini API with custom key
    if model == "gemini-pro" and settings.gemini_key:
        return StreamingResponse(
            stream_gemini(settings.gemini_key, messages),
            media_type="text/event-stream"
        )

    # Default: Built-in Smart AI Response Generator
    return StreamingResponse(
        stream_smart_ai(last_user_message, settings.persona, settings.typing_speed or 25),
        media_type="text/event-stream"
    )

async def stream_smart_ai(prompt: str, persona: str, typing_speed_ms: int):
    """Generates intelligent, structured markdown responses with token-by-token streaming."""
    response_text = generate_response_for_prompt(prompt, persona)
    
    # Tokenize text into words/chunks
    tokens = re.findall(r'\S+|\s+', response_text)
    
    delay_sec = max(0.005, typing_speed_ms / 1000.0)

    for token in tokens:
        data = json.dumps({"content": token})
        yield f"data: {data}\n\n"
        await asyncio.sleep(delay_sec)

    yield "data: [DONE]\n\n"

def generate_response_for_prompt(prompt: str, persona: str) -> str:
    """Intelligent prompt analyzer and template generator."""
    lower_p = prompt.lower()

    prefix = ""
    if persona == "coder":
        prefix = "As a Senior Code Architect, here is the clean, production-ready solution:\n\n"
    elif persona == "concise":
        prefix = "Here is the direct answer:\n\n"
    elif persona == "creative":
        prefix = "Let's bring this idea to life with imagination! ✨\n\n"

    # Code / Programming Query
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
                "    headers = {\n"
                "        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'\n"
                "    }\n"
                "    try:\n"
                "        response = requests.get(url, headers=headers, timeout=10)\n"
                "        response.raise_for_status()\n"
                "        soup = BeautifulSoup(response.text, 'html.parser')\n"
                "        \n"
                "        headlines = []\n"
                "        for idx, item in enumerate(soup.find_all(['h1', 'h2', 'h3']), 1):\n"
                "            text = item.get_text(strip=True)\n"
                "            if text and len(text) > 10:\n"
                "                headlines.append({\n"
                "                    'id': idx,\n"
                "                    'headline': text,\n"
                "                    'length': len(text)\n"
                "                })\n"
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
                "1. **Robust Error Handling**: Handles network timeouts and HTTP error codes gracefully.\n"
                "2. **Custom User-Agent Header**: Prevents requests from being blocked by standard anti-bot filters.\n"
                "3. **Structured JSON Output**: Extracts clean text data and formats it ready for API or database storage.\n\n"
                "Feel free to customize `target_url` or add pagination support!"
            )
        else:
            return prefix + (
                "Here is the requested code implementation along with explanations:\n\n"
                "```javascript\n"
                "// Modern Async Handler Pattern\n"
                "async function processChatRequest(endpoint, payload) {\n"
                "  try {\n"
                "    const response = await fetch(endpoint, {\n"
                "      method: 'POST',\n"
                "      headers: {\n"
                "        'Content-Type': 'application/json'\n"
                "      },\n"
                "      body: JSON.stringify(payload)\n"
                "    });\n\n"
                "    if (!response.ok) {\n"
                "      throw new Error(`HTTP error! status: ${response.status}`);\n"
                "    }\n\n"
                "    const data = await response.json();\n"
                "    return { success: true, data };\n"
                "  } catch (error) {\n"
                "    console.error('API Error:', error.message);\n"
                "    return { success: false, error: error.message };\n"
                "  }\n"
                "}\n"
                "```\n\n"
                "### How It Works:\n"
                "- **Async/Await**: Maintains clean readable code without nested callback hell.\n"
                "- **Error Boundary**: Wraps network transactions in try/catch for zero-crash UI operations."
            )

    # Quantum Computing / Scientific Query
    if "quantum" in lower_p or "analogy" in lower_p or "explain" in lower_p:
        return prefix + (
            "### 🌌 Quantum Computing Explained\n\n"
            "Imagine a standard classical computer as a **light switch**. It can only ever be in one of two positions:\n"
            "- **OFF (0)** or **ON (1)**\n\n"
            "Every program, photo, video, and web page on your device right now is made of billions of these microscopic switches called **bits**.\n\n"
            "---\n\n"
            "### 🪙 The Coin Analogy: Quantum Bits (Qubits)\n\n"
            "Now imagine a quantum computer. Instead of a light switch, picture a **spinning coin** on a table:\n\n"
            "1. **Superposition**: While the coin is spinning rapidly through the air, is it Heads or Tails? *It's a blur of both at the same time!* Only when you stop the coin (measure it) does it land on Heads (1) or Tails (0).\n"
            "2. **Entanglement**: Imagine two spinning coins that are magically linked. If you stop one coin and it lands on Heads, the second coin *instantly* stops on Tails, even if it's light-years away.\n\n"
            "### Why Does This Matter?\n"
            "Because quantum computers can evaluate millions of potential solutions **all at once** (while coins are spinning), making them exponentially faster at:\n"
            "- 💊 **Drug Discovery**: Simulating molecular structures in seconds.\n"
            "- 🔐 **Cryptography**: Breaking and creating next-generation encryption algorithms.\n"
            "- 📊 **Optimization**: Solving massive logistics and traffic patterns worldwide."
        )

    # Startup / Brainstorming Query
    if "startup" in lower_p or "idea" in lower_p or "healthcare" in lower_p or "brainstorm" in lower_p:
        return prefix + (
            "Here are **5 unique AI-driven startup concepts** in the healthcare sector:\n\n"
            "1. 🩺 **MedPulse AI — Predictive ICU Monitoring**\n"
            "   - *Concept*: Real-time stream processing of patient vitals in ICUs to predict sepsis and cardiac arrest 4 hours before onset.\n"
            "   - *Target Market*: Hospitals and critical care centers.\n\n"
            "2. 🔬 **OncoVision — Instant Biopsy Scan Analysis**\n"
            "   - *Concept*: Handheld imaging device powered by computer vision that assists dermatologists in detecting skin cancers instantly during routine physicals.\n\n"
            "3. 💊 **PharmaGenie — Personalized Dosage Intelligence**\n"
            "   - *Concept*: AI algorithm analyzing patient DNA profiles and metabolic rates to optimize prescription dosages and minimize adverse drug reactions.\n\n"
            "4. 🧠 **ClarityMind — Voice Biomarker Mental Health Companion**\n"
            "   - *Concept*: Mobile SDK that analyzes acoustic voice tone and speech cadence during daily phone calls to detect early signs of depression and anxiety.\n\n"
            "5. 📑 **ChartDoc AI — Automated Clinical Documentation**\n"
            "   - *Concept*: Ambient microphone software that listens to doctor-patient consultations and automatically generates accurate EHR (Electronic Health Record) notes in real time."
        )

    # Professional Email Query
    if "email" in lower_p or "meeting" in lower_p or "stakeholder" in lower_p:
        return prefix + (
            "Subject: Discussion: Project Roadmap & Next Steps Alignment\n\n"
            "Dear [Stakeholder Name],\n\n"
            "I hope this message finds you well.\n\n"
            "As we progress with the [Project Name] initiative, I would like to schedule a brief 20-30 minute meeting with you next week to review key milestones, share initial progress, and gather your guidance on upcoming decisions.\n\n"
            "Would any of the following times work for your schedule?\n"
            "- **Tuesday, Oct 3** at 10:00 AM EST\n"
            "- **Wednesday, Oct 4** at 2:00 PM EST\n"
            "- **Thursday, Oct 5** at 11:30 AM EST\n\n"
            "If another time suits you better, please let me know and I will gladly adjust.\n\n"
            "Thank you for your time and continued support.\n\n"
            "Best regards,\n\n"
            "**[Your Name]**  \n"
            "[Your Title / Department]"
        )

    # General / Greeting Query
    return prefix + (
        f"Hello! I am ChatGPT, an AI assistant built to help you with answering questions, writing code, brainstorming creative ideas, and solving complex problems.\n\n"
        f"You asked: **\"{prompt}\"**\n\n"
        "How would you like to explore this topic further? I can:\n"
        "- Provide step-by-step technical guides or code snippets\n"
        "- Summarize key points into bullet lists\n"
        "- Draft content or documentation for your project"
    )

async def stream_openai(api_key: str, messages: List[Dict[str, str]]):
    """Proxies streaming requests directly to OpenAI API."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "stream": True
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    err_body = await response.aread()
                    err_json = json.loads(err_body.decode('utf-8', errors='ignore'))
                    err_msg = err_json.get("error", {}).get("message", "OpenAI API request failed.")
                    yield f"data: {json.dumps({'content': f'⚠️ OpenAI API Error: {err_msg}'})}\n\n"
                    yield "data: [DONE]\n\n"
                    return

                async for chunk in response.aiter_lines():
                    if chunk.startswith("data: "):
                        data_str = chunk.replace("data: ", "").trim()
                        if data_str == "[DONE]":
                            break
                        try:
                            parsed = json.loads(data_str)
                            delta = parsed["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield f"data: {json.dumps({'content': delta})}\n\n"
                        except Exception:
                            pass
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'content': f'⚠️ Connection Error: {str(e)}'})}\n\n"
            yield "data: [DONE]\n\n"

async def stream_gemini(api_key: str, messages: List[Dict[str, str]]):
    """Proxies streaming requests directly to Google Gemini API."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?key={api_key}"
    
    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    payload = {"contents": contents}

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    yield f"data: {json.dumps({'content': '⚠️ Gemini API Error. Check your API key in Settings.'})}\n\n"
                    yield "data: [DONE]\n\n"
                    return

                async for chunk in response.aiter_text():
                    # Parse Gemini stream chunks
                    try:
                        parsed = json.loads(chunk)
                        if isinstance(parsed, list):
                            for item in parsed:
                                text = item["candidates"][0]["content"]["parts"][0]["text"]
                                yield f"data: {json.dumps({'content': text})}\n\n"
                    except Exception:
                        pass
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'content': f'⚠️ Gemini Connection Error: {str(e)}'})}\n\n"
            yield "data: [DONE]\n\n"

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting ChatGPT Web Server on http://0.0.0.0:{port}")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
