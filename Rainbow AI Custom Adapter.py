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
LLAMA_SERVER_URL = "http://127.0.0.1:8081/completion"
LLAMA_HEALTH_URL = "http://127.0.0.1:8081/health"

app = FastAPI(title="Rainbow AI Custom Chat Adapter")

# Allow CORS so your GitHub Pages frontend can communicate without browser blocks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Request Schema matching Rainbow AI Frontend
# -------------------------------------------------------------------
class InferencePayload(BaseModel):
    data: list

# -------------------------------------------------------------------
# Prompt Formatter & Sanitizer
# -------------------------------------------------------------------
def format_prompt_for_model(user_message: str, history: list = None) -> str:
    """
    Constructs the verified prompt structure:
    <|turn>user\n...<|turn>model\n<|channel>final\n
    """
    prompt = ""
    
    # If conversational history is provided, build turns sequentially
    if history:
        for turn in history:
            role = turn.get("role", "user")
            content = turn.get("content", "").strip()
            if role == "user":
                prompt += f"<|turn>user\n{content}\n"
            elif role == "assistant" or role == "model":
                prompt += f"<|turn>model\n<|channel>final\n{content}<|channel|>\n"

    # Append the current active user turn
    prompt += f"<|turn>user\n{user_message.strip()}<|turn>model\n<|channel>final\n"
    return prompt

def sanitize_model_output(raw_text: str) -> str:
    """
    Strips internal model formatting, control tokens, and channel artifacts.
    """
    if not raw_text:
        return ""

    text = raw_text

    # 1. Remove leading channel markers if leaked
    text = re.sub(r"^<\|channel\|>", "", text)
    text = re.sub(r"^final\n*", "", text, flags=re.IGNORECASE)
    
    # 2. Strip any turn markers or trailing channel tags
    control_patterns = [
        r"<\|turn>.*",
        r"<\|channel\|>.*",
        r"<\|turn>",
        r"<\|channel>",
        r"final<\|channel\|>",
    ]
    for pattern in control_patterns:
        text = re.sub(pattern, "", text, flags=re.DOTALL)

    # 3. Clean up leading/trailing whitespace
    return text.strip()

# -------------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------------
@app.get("/")
def health_check():
    """
    Verifies that the adapter is online and checks if llama.cpp is responding.
    """
    llama_status = "offline"
    try:
        r = requests.get(LLAMA_HEALTH_URL, timeout=2)
        if r.status_code == 200:
            llama_status = "connected"
    except Exception:
        llama_status = "unreachable"

    return {
        "adapter_status": "online",
        "llama_cpp_backend": llama_status,
        "target_endpoint": LLAMA_SERVER_URL
    }

@app.post("/call/predict")
def predict(payload: InferencePayload):
    """
    Primary endpoint called by the Rainbow AI website.
    Translates input, queries llama.cpp /completion, cleans output, and returns.
    """
    try:
        # Extract prompt from frontend array: data: [query, model]
        if not payload.data or len(payload.data) == 0:
            raise HTTPException(status_code=400, detail="Empty prompt array received.")

        user_input = str(payload.data[0]).strip()
        selected_model = payload.data[1] if len(payload.data) > 1 else "default"

        if not user_input:
            raise HTTPException(status_code=400, detail="User message cannot be empty.")

        # 1. Format the raw prompt with the model's native turn/channel tags
        formatted_prompt = format_prompt_for_model(user_input)

        # 2. Construct the payload for llama-server's /completion endpoint
        llama_payload = {
            "prompt": formatted_prompt,
            "n_predict": 2048,
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
            # Strict stop tokens to prevent the model from rambling or echoing turns
            "stop": [
                "<|turn>",
                "<|turn>user",
                "<|turn>model",
                "<|channel|>",
                "User:",
                "Assistant:"
            ]
        }

        # 3. Send request to llama-server
        response = requests.post(
            LLAMA_SERVER_URL,
            json=llama_payload,
            timeout=120  # Ample time for 12B token generation on T4
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"llama.cpp error {response.status_code}: {response.text}"
            )

        result_data = response.json()
        raw_completion = result_data.get("content", "")

        # 4. Sanitize control tokens from the response
        clean_text = sanitize_model_output(raw_completion)

        if not clean_text:
            clean_text = "I processed your request, but no text content was returned."

        # 5. Return in the exact shape Rainbow AI expects
        return {"data": [clean_text]}

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Inference timed out on the llama.cpp server.")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Could not connect to llama-server on port 8081.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
