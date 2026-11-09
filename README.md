# 🌈 Rainbow AI Ecosystem

Rainbow AI is a connected set of browser-based tools built around one shared workspace. The project is intentionally built with HTML, CSS, and JavaScript on the frontend, with a separate optional Python/FastAPI adapter for model inference.

## Project pages

| File | Purpose |
|---|---|
| `homepage.html` | Rainbow portal and discovery homepage |
| `index.html` | Main Rainbow AI workspace: chat, projects, agents, knowledge tools, Nova, Prompt Studio, Canvas, and Rainbow Hub |
| `languagebook.html` | Language-learning studio with courses, lessons, practice tests, progress, and vocabulary |
| `calculator.html` | Scientific calculator with keyboard input, expression history, and number-to-words conversion |

The shared `rainbow-ecosystem.css` and `rainbow-ecosystem.js` files provide consistent navigation and contextual handoff between the tools. The **Ask Rainbow** action prepares a prompt containing the current page context in the main workspace; it does not send the prompt automatically.

## Rainbow AI workspace

The main workspace includes:

- Chat interface, conversation history, model/persona controls, and settings.
- Rainbow Agents Studio with configurable agents and sequential prompt workflows.
- Prompt Studio, Projects, Rainbow Canvas, Study Mode, Nova voice companion, and other workspace modules.
- Knowledge Graph and Memory Vault for locally stored notes and relationships.
- Rainbow Hub tools such as File Hub, FlowForge, Code Arena, Rainbow Simulator, StoryWorld, API Playground, Focus Mode, and Personal Dashboard.
- TruthLens and Multi-AI Debate interfaces, which still require their corresponding backend services for full analysis/orchestration.

### Model backend

The frontend talks to a configured gateway. The included `adapter_chat.py` is an optional FastAPI adapter for a llama.cpp server:

- Frontend-compatible route: `POST /call/predict`
- Adapter health route: `GET /`
- Default llama.cpp completion endpoint: `http://127.0.0.1:8081/completion`
- Default llama.cpp health endpoint: `http://127.0.0.1:8081/health`

Install the Python dependencies in your own environment:

```bash
python -m pip install fastapi uvicorn requests pydantic
```

Start the adapter after your llama.cpp server is running:

```bash
python adapter_chat.py
```

The adapter listens on port `8000` by default. Configure the frontend gateway URL to the reachable adapter endpoint. If the model server or tunnel is offline, AI requests cannot complete; the static tools and local page features can still be used.

**Important:** this repository does not include a running hosted model, a live tunnel, or inference credentials. Do not put private API keys or backend secrets in browser JavaScript. Configure allowed browser origins with the `RAINBOW_ALLOWED_ORIGINS` environment variable when hosting the adapter.

## Local data and file handling

- Conversation and tool data may be stored in browser `localStorage`; it is local to that browser profile and is not automatically synced between devices.
- The file intake layer extracts text from supported text, PDF, DOCX, and spreadsheet formats when the optional parsers are available.
- Image, audio, and video attachments are currently metadata-only in the text-only gateway flow; they are not equivalent to image understanding, transcription, or video analysis.
- FlowForge currently saves and hands off workflow plans; it does not execute arbitrary external actions.
- Code Arena runs the local preview in a sandboxed iframe.
- Rainbow Simulator is an educational queue/capacity model, not a production load-testing service.
- TruthLens analysis and Multi-AI Debate orchestration require backend routes that are not included in the current adapter.

## Security notes

- Calculator expressions are evaluated by a restricted arithmetic parser, not JavaScript `eval()` or `Function()`.
- AI-rendered Markdown is sanitized before being inserted into the chat interface.
- User-provided code previews are isolated in a sandboxed iframe.
- Keep backend credentials on the server, validate gateway URLs, and use HTTPS for deployed services.

## Run the frontend

1. Clone or download this repository.
2. Start a local static web server (for example, VS Code Live Server).
3. Open `homepage.html` to explore the portal, or open `index.html` to enter the AI workspace.
4. Open `languagebook.html` or `calculator.html` directly, or navigate to them using the shared Rainbow bar.

A local server is recommended over opening files directly with `file://`, especially for browser storage, module scripts, and speech permissions.

## Branding

The root folder contains the shared Rainbow SVG logo/favicon assets and the workspace icon. Keep these asset paths intact when moving or deploying the pages.

## Rainbow AI assistance across the ecosystem

The shared ecosystem script adds page-aware AI actions:

- **Language Book:** explain the current question, generate a step-by-step tutorial from visible lesson content, create practice questions with an answer key, and explain selected text.
- **Calculator:** request a worked solution for the current expression or generate similar practice problems.
- **Homepage:** ask Rainbow AI to recommend a learning/building path through the available tools.
- **AI handoff:** actions prepare a contextual prompt in the main workspace composer; the user reviews and sends it. A working model backend is still required for generated answers.
- **Workspace navigation:** the Explore button expands the collapsed sidebar and exposes chat search/history and module navigation.

AI-generated tutorials and answers are produced only when the main Rainbow model gateway is online. The existing local lessons and calculator continue to work independently.
