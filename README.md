# Meditreat Chatbot

- This solution is meant to help medical practitioners, casual users and curious minds.
- It is plug and play all round llm solution with realtime response streaming from the model.
- Further, the architecture is extensible and easily allows extension of the Chatmodel to a wide array of use cases
and multiple chatbot assistants.
- Uses Websocket connection to expose the chat endpoint for realtime responses/streamed responses. Be careful when plugin it to the UI.
- Additionally extending to a simple authentication system to protect the endpoints using a middleware and social auth.

## Design Choice

- Langchain to handle `llm`s responses, easy to use and extensible for large LLM applications, has extra packages not natively available in base SDKs for different LLM providers.
- FastAPI for the API - easy to use, fast to build and deploy with, natively supports asyncronous serger gateway interface.
- React Frontend(In Development) - good choice for responsive UIs.
- Keycloak Auth(in dev) - free and opensource, secure and trusted by many.
- Docker containerization and orchestration - Multi-environment support and easier deployment process due to selmanaged environments in containers.
- Heroku Deployment - self-provisioning resources and reliable cloud deployment platform for ML/AI solutions.
- Supabase Database - Easy plug and play SQL based db, secure fast, scalable and reliable.


## Setup

1. Clone the repo and navigate to the folder. `cd meditreat`
2. Configure the env variables as in `.env.example`: `cp .env.example .env`
3. Build docker image. `docker compose up -d --build`

> [!IMPORTANT]
>
> This responses from the chatbot should not be taken as ground truth and I advice consulting certified medical practitioners for medical attention. Further, the responses from the model may be skewed as the responses are produced through autoregressive predictions and can cause panic, in case of such responses, report the issue and contact a medical practitioner.
> This project is widely still under development.
> Open for collaborations and critism. 