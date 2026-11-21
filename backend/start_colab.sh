#!/usr/bin/env bash
set -Eeuo pipefail

# Rainbow AI Colab reboot launcher. Override paths with environment variables if needed.
ROOT="${RAINBOW_ROOT:-/content}"
MODEL="${RAINBOW_MODEL_PATH:-$ROOT/models/Rainbow-AI-12B-Unified.Q4_K_M.gguf}"
LLAMA_BIN="${LLAMA_SERVER_BIN:-$ROOT/llama-prebuilt/cuda-12.8/llama-server}"
LLAMA_LIB="${LLAMA_LIB_DIR:-$ROOT/llama-prebuilt/cuda-12.8}"
API_FILE="${RAINBOW_API_FILE:-$ROOT/Rainbow_AI/backend/rainbow_fastapi.py}"
API_LOG="$ROOT/rainbow_fastapi.log"
LLAMA_LOG="$ROOT/llama_server.log"
TUNNEL_LOG="$ROOT/cloudflared.log"

if [[ ! -f "$MODEL" ]]; then echo "ERROR: GGUF model not found: $MODEL"; exit 2; fi
if [[ ! -x "$LLAMA_BIN" ]]; then echo "ERROR: llama-server not executable: $LLAMA_BIN"; exit 2; fi
if [[ ! -f "$API_FILE" ]]; then echo "ERROR: FastAPI file not found: $API_FILE"; exit 2; fi

export LD_LIBRARY_PATH="$LLAMA_LIB:/usr/local/cuda/lib64:/usr/local/cuda/compat:${LD_LIBRARY_PATH:-}"
export LLAMA_COMPLETION_URL="http://127.0.0.1:8081/completion"
export RAINBOW_ALLOWED_ORIGINS="${RAINBOW_ALLOWED_ORIGINS:-https://rainbowlord16.github.io,http://localhost:5500,http://127.0.0.1:5500}"

if ! curl -fsS http://127.0.0.1:8081/health >/dev/null 2>&1; then
  pkill -f "$LLAMA_BIN" 2>/dev/null || true
  nohup "$LLAMA_BIN" -m "$MODEL" -ngl "${RAINBOW_GPU_LAYERS:-99}" --host 127.0.0.1 --port 8081 -c "${RAINBOW_CONTEXT_SIZE:-4096}" >"$LLAMA_LOG" 2>&1 &
  echo $! > "$ROOT/llama_server.pid"
  echo "Waiting for llama.cpp..."
  for i in $(seq 1 180); do
    if curl -fsS http://127.0.0.1:8081/health >/dev/null 2>&1; then break; fi
    sleep 2
  done
  curl -fsS http://127.0.0.1:8081/health >/dev/null || { echo "ERROR: llama-server did not become healthy. See $LLAMA_LOG"; exit 3; }
fi

pkill -f "uvicorn rainbow_fastapi:app" 2>/dev/null || true
cd "$(dirname "$API_FILE")"
nohup python -m uvicorn rainbow_fastapi:app --host 0.0.0.0 --port 8000 >"$API_LOG" 2>&1 &
echo $! > "$ROOT/rainbow_fastapi.pid"
for i in $(seq 1 40); do
  if curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then break; fi
  sleep 1
done
curl -fsS http://127.0.0.1:8000/health >/dev/null || { echo "ERROR: FastAPI did not become healthy. See $API_LOG"; exit 4; }

if ! command -v cloudflared >/dev/null 2>&1; then
  curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o "$ROOT/cloudflared"
  chmod +x "$ROOT/cloudflared"
  export PATH="$ROOT:$PATH"
fi
pkill -f "cloudflared tunnel --url http://127.0.0.1:8000" 2>/dev/null || true
nohup cloudflared tunnel --url http://127.0.0.1:8000 --no-autoupdate >"$TUNNEL_LOG" 2>&1 &
echo $! > "$ROOT/cloudflared.pid"

echo "Waiting for Cloudflare quick tunnel URL..."
URL=""
for i in $(seq 1 60); do
  URL="$(grep -Eo 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' "$TUNNEL_LOG" | head -n1 || true)"
  [[ -n "$URL" ]] && break
  sleep 1
done
if [[ -z "$URL" ]]; then echo "ERROR: Tunnel URL not detected. See $TUNNEL_LOG"; exit 5; fi
echo "$URL" > "$ROOT/rainbow_gateway_url.txt"
echo
echo "RAINBOW_GATEWAY_URL=$URL"
echo "HEALTH_URL=$URL/health"
echo "FASTAPI_URL=$URL/call/predict"
echo "Gateway URL is written to $ROOT/rainbow_gateway_url.txt"
