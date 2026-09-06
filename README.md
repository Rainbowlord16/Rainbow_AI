# 🌈 Rainbow AI Ecosystem

Rainbow AI Ecosystem is a cutting-edge, privacy-first personal AI assistant built for local browser execution via WebGPU and the MLC WebLLM engine. It features a sleek dark/light minimalist interface, custom AI personas, voice-to-text integration, an integrated Spectra image generation pipeline, and the Nova learning assistant.

## 🚀 Key Features

* **Local WebGPU Execution:** Run powerful AI models directly in your browser without sending your private data to external cloud servers.
* **Custom Personas:** Switch seamlessly between **Rainbow Coder**, **Rainbow Poet**, and **Rainbow Balanced** personas to match your workflow.
* **Spectra Image Generator:** Built-in Stable Diffusion pipeline support for generating creative artwork directly within the dashboard.
* **Nova Learning Companion:** A safe, encouraging assistant mode optimized for educational exploration.
* **Interactive Code Sandboxes:** Run JavaScript code snippets directly inside AI chat responses with an integrated execution terminal.
* **Voice-to-Text Support:** Talk directly to your AI using the browser's native Web Speech API.
* **Chat Management & Export:** Save conversations locally to browser memory, search history instantly, or export transcripts to `.txt` files.

## 🛠️ Tech Stack

* **Engine:** [@mlc-ai/web-llm](https://github.com/mlc-ai/web-llm)
* **Markdown & Syntax Highlighting:** Marked.js & Highlight.js
* **Styling & Icons:** Pure CSS3, Glassmorphic UI design, Inter font family
* **Branding:** Custom inline SVG neon-glow vector logo (`RAINBOW_favicon.svg`)

## 🚀 Getting Started

1. Clone or download this repository to your local machine.
2. Ensure your custom SVG logo is saved in the root folder as **`RAINBOW_favicon.svg`**.
3. Open `index.html` using a local development server (such as Live Server in VS Code) to allow WebGPU model loading and voice permissions to function correctly.
