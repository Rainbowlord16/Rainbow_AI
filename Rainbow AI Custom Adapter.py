import logging
import os
import re

import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
LLAMA_SERVER_URL = os.getenv("LLAMA_SERVER_URL", "http://127.0.0.1:8081/completion").strip()
LLAMA_HEALTH_URL = os.getenv("LLAMA_HEALTH_URL", "http://127.0.0.1:8081/health").strip()
LLAMA_REQUEST_TIMEOUT = max(10.0, float(os.getenv("LLAMA_REQUEST_TIMEOUT", "120")))

DEFAULT_ALLOWED_ORIGINS = (
    "https://rainbowlord16.github.io,"
    "http://localhost:5500,"
    "http://127.0.0.1:5500"
)
ALLOWED_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.getenv("RAINBOW_ALLOWED_ORIGINS", DEFAULT_ALLOWED_ORIGINS).split(",")
    if origin.strip()
]

app = FastAPI(title="Rainbow AI Custom Chat Adapter")

# CORS applies to browser origins, not the gateway host. Override the
# allow-list with RAINBOW_ALLOWED_ORIGINS if the frontend domain changes.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)


class InferencePayload(BaseModel):
    data: list


def format_prompt_for_model(user_message: str, history: list = None) -> str:
    """Build the model's expected turn/channel prompt format."""
    prompt = ""
    if history:
        for turn in history:
            if not isinstance(turn, dict):
                continue
            role = turn.get("role", "user")
            content = str(turn.get("content", "")).strip()
            if role == "user":
                prompt += f"<|turn>user\n{content}\n"
            elif role in ("assistant", "model"):
                prompt += f"<|turn>model\n<|channel>final\n{content}<|channel|>\n"
    prompt += f"<|turn>user\n{user_message.strip()}<|turn>model\n<|channel>final\n"
    return prompt


def sanitize_model_output(raw_text: str) -> str:
    """Remove leaked model control markers from the visible answer."""
    if not raw_text:
        return ""
    text = str(raw_text).strip()
    text = re.split(r"<\|turn>(?:user|model)?", text, maxsplit=1)[0]
    text = re.sub(r"<\|channel\|>", "", text)
    text = re.sub(r"<\|channel>", "", text)
    text = re.sub(r"^final\s*", "", text, flags=re.IGNORECASE)
    return text.strip()


@app.get("/")
def health_check():
    """Report adapter health separately from llama.cpp health."""
    llama_status = "unreachable"
    try:
        response = requests.get(LLAMA_HEALTH_URL, timeout=3)
        llama_status = "connected" if response.ok else "offline"
    except requests.exceptions.Timeout:
        llama_status = "timeout"
    except requests.exceptions.RequestException:
        llama_status = "unreachable"

    return {
        "adapter_status": "online",
        "llama_cpp_backend": llama_status,
        "target_endpoint": LLAMA_SERVER_URL,
    }


@app.post("/call/predict")
def predict(payload: InferencePayload):
    """
    FastAPI contract used by Rainbow AI:
      request:  {"data": ["prompt", "model/persona"]}
      response: {"data": ["assistant response"]}
    """
    try:
        if not isinstance(payload.data, list) or not payload.data:
            raise HTTPException(status_code=400, detail="A non-empty data array is required.")
        if not isinstance(payload.data[0], str):
            raise HTTPException(status_code=400, detail="The prompt must be a string.")

        user_input = payload.data[0].strip()
        if not user_input:
            raise HTTPException(status_code=400, detail="The prompt cannot be empty.")
        if len(user_input) > 30000:
            raise HTTPException(status_code=413, detail="The prompt is too long (maximum 30000 characters).")

        # Keep the second array value accepted for frontend compatibility.
        # This adapter currently uses the one model loaded by llama.cpp.
        if len(payload.data) > 1 and not isinstance(payload.data[1], (str, int, float)):
            raise HTTPException(status_code=400, detail="The model/persona value must be a string or number.")

        llama_payload = {
            "prompt": format_prompt_for_model(user_input),
            "n_predict": 2048,
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
            "stop": ["<|turn>", "<|turn>user", "<|turn>model", "User:", "Assistant:"],
        }

        try:
            response = requests.post(
                LLAMA_SERVER_URL,
                json=llama_payload,
                timeout=LLAMA_REQUEST_TIMEOUT,
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise HTTPException(status_code=504, detail="Inference timed out on the llama.cpp server.")
        except requests.exceptions.ConnectionError:
            raise HTTPException(status_code=503, detail="The inference backend is unavailable.")
        except requests.exceptions.RequestException:
            logging.exception("llama.cpp request failed")
            raise HTTPException(status_code=502, detail="The inference backend returned an unsuccessful response.")

        try:
            result_data = response.json()
        except ValueError:
            raise HTTPException(status_code=502, detail="The inference backend returned invalid JSON.")

        if not isinstance(result_data, dict):
            raise HTTPException(status_code=502, detail="The inference backend returned an unexpected response.")

        raw_completion = result_data.get("content")
        if not isinstance(raw_completion, str):
            raise HTTPException(status_code=502, detail="The inference backend response did not contain text.")

        clean_text = sanitize_model_output(raw_completion)
        if not clean_text:
            clean_text = "I processed your request, but no text content was returned."

        return {"data": [clean_text]}

    except HTTPException:
        # Preserve intentional 4xx/5xx responses instead of turning them into 500s.
        raise
    except Exception:
        logging.exception("Unexpected Rainbow AI adapter error")
        raise HTTPException(status_code=500, detail="An unexpected inference adapter error occurred.")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
