# Meditreat Chatbot

This repository contains a simple chatbot application consisting of:

- **Python FastAPI Backend** (`src/`): Serves the chat endpoint and interfaces with the Chatbot logic.

---

## Prerequisites
- Python 3.11+  and `uv` for the backend
- Git
- Docker

## Setup

1. Clone the repo and navigate to the folder. `cd meditreat`
2. Configure the env variables as in `.env.example`: `cp .env.example .env`
3. Build docker image. `docker compose up -d --build`

> [!IMPORTANT]
> This responses from the chatbot should not be taken as ground truth and I advice consulting certified medical practitioners for medical attention. Further, the responses from the model may be skewed as the responses are produced through autoregressive predictions and can cause panic, in case of such responses, report the issue and contact a medical practitioner.
> This project is widely still under development.
> Open for collaborations and critism. 