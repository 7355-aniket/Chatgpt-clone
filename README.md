# 🤖 ChatGPT Web Application Clone

A full-featured, lightweight web application clone of OpenAI's **ChatGPT**. Built with a Python FastAPI backend and a responsive, modern HTML5/CSS3/JavaScript frontend with real-time token streaming, Markdown code highlighting, session history, and dual AI provider support.

---

## ✨ Features

- 🎨 **Authentic ChatGPT UI**: Official Dark Mode theme styling, collapsible conversation sidebar, auto-resizing prompt input, and starter prompt cards.
- ⚡ **Real-Time Token Streaming**: Real-time typewriter effect using Server-Sent Events (SSE).
- 🛑 **Stop & Regenerate**: Cancel streaming responses mid-way or regenerate previous responses with a single click.
- 📝 **Markdown & Code Highlighting**: Full Markdown support (tables, lists, blockquotes) and syntax highlighting for code blocks with a 1-click **"Copy code"** button.
- 🤖 **Dual AI Providers**:
  - **Built-in Smart Engine (Default)**: Generates intelligent responses immediately without requiring any API keys.
  - **OpenAI & Gemini API Integration**: Enter your own OpenAI (`gpt-4o`) or Google Gemini (`gemini-1.5-pro`) API key in Settings for live LLM responses.
- 💾 **Local History & Settings**: Saved conversations persist in browser `localStorage` with options to rename, delete, or clear all chats.
- ⚙️ **Custom System Personas**: Choose from preset personas (Default Assistant, Senior Software Engineer, Concise Answerer, Creative Storyteller).

---

## 📁 Repository Structure

```text
chatgpt-clone/
├── server.py             # Python FastAPI server (SSE streaming & API router)
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── LICENSE                # MIT License
├── .gitignore             # Ignored files for git
└── static/
    ├── index.html         # Main HTML layout & modals
    ├── styles.css         # ChatGPT Dark/Light theme CSS
    └── app.js             # ES6 Frontend logic & Marked/Highlight integration
```

---

## 🚀 Quick Start (Local Setup)

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/chatgpt-clone.git
cd chatgpt-clone
```

### 2. Create Virtual Environment & Install Dependencies
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Server
```bash
python server.py
```
Open **`http://localhost:8000`** in your browser!

---

## 🌐 Deploy to Free Cloud Hosting (Render.com)

1. Push this repository to your GitHub account.
2. Sign up for a free account at [Render.com](https://render.com).
3. Click **New +** ➔ **Web Service** ➔ Connect your GitHub repository.
4. Set the runtime environment to **Python 3**.
5. Set the **Start Command**:
   ```bash
   uvicorn server:app --host 0.0.0.0 --port $PORT
   ```
6. Click **Deploy Web Service**. You will get a free live URL (e.g. `https://chatgpt-clone.onrender.com`) accessible from any phone or PC 24/7!

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
