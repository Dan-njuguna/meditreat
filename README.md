# Meditreat Chatbot

This repository contains a simple chatbot application consisting of:

- **Python FastAPI Backend** (`api/`): Serves the chat endpoint and interfaces with the Chatbot logic.
- **Next.js Frontend** (`matibabu/`): A React UI styled with Tailwind CSS for users to chat with the bot.

---

## Prerequisites

- Node.js (v16+) and [pnpm](https://pnpm.io/) for the frontend
- Python 3.9+ (recommend 3.11) and `pip` for the backend
- Git

## Environment Variables

Create a `.env` file in the project root (alongside `requirements.txt`) to define any secrets used by the `api/chatbot.py` logic. Example:

```env
# .env
OPENAI_API_KEY=your_openai_api_key_here
OTHER_API_TOKEN=...
```

## Backend (FastAPI)

1. Navigate to the project root:
   ```bash
   cd /home/dan/haki
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Review or update CORS settings in `api/main.py` if your frontend runs on a different origin.
4. Start the API server with Uvicorn:
   ```bash
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```
5. The chat endpoint will be available at `http://localhost:8000/chat`.

## Frontend (Next.js)

1. Change into the `matibabu` directory:
   ```bash
   cd matibabu
   ```
2. Install Node dependencies:
   ```bash
   pnpm install
   ```
3. Run the development server:
   ```bash
   pnpm dev
   ```
4. Open `http://localhost:3000` in your browser to use the chatbot UI.

## Project Structure

```
/ meditreat
├─ api/                 # Python FastAPI backend
│  ├─ main.py           # Server entrypoint
│  ├─ chatbot.py        # Chatbot logic
│  └─ models.py         # Pydantic request/response models
├─ matibabu/            # Next.js frontend
│  ├─ app/              # Route definitions and global styles
│  ├─ components/       # React components (ChatWindow, Sidebar)
│  ├─ services/         # API client for chat endpoint
│  └─ tailwind.config.js
├─ requirements.txt     # Python dependencies
└─ README.md            # This file
```

## Usage

- Type your message in the input box and press Enter (or click Send) to talk to *Meditreat*.
- Use **Shift+Enter** to insert a newline.
- Click **Clear Chat** to reset conversation history.

## Troubleshooting

- **Module not found** errors in the frontend? Make sure you ran `pnpm install` in `matibabu/` and restarted the dev server.
- **CORS errors** or preflight failures? Verify the `allow_origins` setting in `api/main.py` matches your frontend URL.
- **422 validation errors**? Ensure the frontend is posting `{ "query": "your message" }` to `/api/chat`.

---

Happy chatting! 🚀