"""Provider helpers for optional AI copy generation.

Supports common hosted API providers and local model servers such as Ollama or a
custom OpenAI-compatible local endpoint.
"""
from __future__ import annotations

import json
import os
from typing import Any
from urllib import error, request


def get_provider_config() -> dict[str, Any]:
    provider = (os.getenv("AI_PROVIDER") or "offline").strip().lower()
    return {
        "provider": provider,
        "model": os.getenv("AI_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini",
        "api_key": os.getenv("API_KEY") or "",
        "openai_api_key": os.getenv("OPENAI_API_KEY") or "",
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY") or "",
        "gemini_api_key": os.getenv("GEMINI_API_KEY") or "",
        "groq_api_key": os.getenv("GROQ_API_KEY") or "",
        "openrouter_api_key": os.getenv("OPENROUTER_API_KEY") or "",
        "together_api_key": os.getenv("TOGETHER_API_KEY") or "",
        "mistral_api_key": os.getenv("MISTRAL_API_KEY") or "",
        "local_base_url": os.getenv("LOCAL_LLM_BASE_URL") or os.getenv("OLLAMA_BASE_URL") or "http://localhost:11434",
        "local_model": os.getenv("LOCAL_LLM_MODEL") or os.getenv("OLLAMA_MODEL") or "llama3.1",
    }


def _call_json(url: str, payload: dict[str, Any], headers: dict[str, str] | None = None, timeout: int = 45):
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers=headers or {}, method="POST")
    with request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def call_ai_provider(prompt: str, *, provider: str | None = None, model: str | None = None, listing: dict | None = None):
    cfg = get_provider_config()
    provider = (provider or cfg["provider"] or "offline").strip().lower()
    model = (model or cfg["model"] or "gpt-4o-mini").strip()
    listing_text = json.dumps(listing or {}, ensure_ascii=False)[:2000]
    payload_text = f"Rewrite this Etsy title+bullets punchier, keep facts: {listing_text}"

    if provider == "offline" or provider == "none":
        return {"ok": False, "msg": "No AI provider configured — using built-in copy."}

    try:
        if provider in {"openai", "openrouter", "groq", "together", "mistral"}:
            key = (
                cfg["openai_api_key"] if provider == "openai"
                else cfg["openrouter_api_key"] if provider == "openrouter"
                else cfg["groq_api_key"] if provider == "groq"
                else cfg["together_api_key"] if provider == "together"
                else cfg["mistral_api_key"]
            )
            if not key:
                return {"ok": False, "msg": f"{provider.upper()} API key missing."}
            base_url = {
                "openai": "https://api.openai.com/v1/chat/completions",
                "openrouter": "https://openrouter.ai/api/v1/chat/completions",
                "groq": "https://api.groq.com/openai/v1/chat/completions",
                "together": "https://api.together.xyz/v1/chat/completions",
                "mistral": "https://api.mistral.ai/v1/chat/completions",
            }[provider]
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            if provider == "openrouter":
                headers["HTTP-Referer"] = os.getenv("APP_URL", "http://localhost:5000")
                headers["X-Title"] = "Forge3D"
            payload = {"model": model, "messages": [{"role": "user", "content": payload_text}], "max_tokens": 400}
            out = _call_json(base_url, payload, headers=headers)
            content = out["choices"][0]["message"]["content"]
            return {"ok": True, "text": content}

        if provider == "anthropic":
            key = cfg["anthropic_api_key"]
            if not key:
                return {"ok": False, "msg": "ANTHROPIC_API_KEY missing."}
            payload = {
                "model": model,
                "max_tokens": 400,
                "messages": [{"role": "user", "content": payload_text}],
            }
            out = _call_json(
                "https://api.anthropic.com/v1/messages",
                payload,
                headers={
                    "x-api-key": key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                },
            )
            content = out["content"][0]["text"]
            return {"ok": True, "text": content}

        if provider == "gemini":
            key = cfg["gemini_api_key"]
            if not key:
                return {"ok": False, "msg": "GEMINI_API_KEY missing."}
            model_name = model or "gemini-2.0-flash"
            payload = {"contents": [{"parts": [{"text": payload_text}]}], "generationConfig": {"maxOutputTokens": 400}}
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
            out = _call_json(url, payload, headers={"Content-Type": "application/json"})
            content = out["candidates"][0]["content"]["parts"][0]["text"]
            return {"ok": True, "text": content}

        if provider in {"ollama", "local", "local-server", "local_server"}:
            base_url = cfg["local_base_url"].rstrip("/")
            local_model = model or cfg["local_model"]
            url = f"{base_url}/api/chat"
            payload = {"model": local_model, "messages": [{"role": "user", "content": payload_text}], "stream": False}
            out = _call_json(url, payload, headers={"Content-Type": "application/json"}, timeout=90)
            content = out["message"]["content"]
            return {"ok": True, "text": content}

        if provider == "none":
            return {"ok": False, "msg": "No AI provider configured — using built-in copy."}

        return {"ok": False, "msg": f"Unsupported AI provider: {provider}"}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "msg": f"Provider call failed: {exc}"}
