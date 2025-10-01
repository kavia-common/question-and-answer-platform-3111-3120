from __future__ import annotations

from fastapi import HTTPException
import httpx

from src.api.config import get_settings


# PUBLIC_INTERFACE
async def call_openai_chat(prompt: str) -> str:
    """Call OpenAI Chat Completions API to generate an answer using configured OPENAI_API_KEY."""
    settings = get_settings()
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not set. Please configure it in the environment."
        )

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for a Q&A application."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=f"OpenAI error: {resp.text}")
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
