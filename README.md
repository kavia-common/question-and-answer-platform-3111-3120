# question-and-answer-platform-3111-3120

This repository contains a full stack Question and Answer application.

Backend (qna_backend):
- FastAPI service providing:
  - Auth: signup, login (JWT), current user
  - Questions: create, list, get by id
  - Answers: list all, create (manual or AI via OpenAI), list by question
- Ocean Professional themed API docs available at /docs
- OpenAPI spec generated to qna_backend/interfaces/openapi.json

How to run backend locally:
1. cd question-and-answer-platform-3111-3120/qna_backend
2. Create .env from .env.example and set values (OPENAI_API_KEY required for AI generation)
3. pip install -r requirements.txt
4. uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload

Environment variables (see .env.example):
- JWT_SECRET_KEY, JWT_EXPIRE_MINUTES
- OPENAI_API_KEY

Notes:
- Current implementation uses in-memory storage for users, questions, and answers (for demo). Replace with a database in production.