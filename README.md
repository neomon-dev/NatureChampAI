# NatureChamp AI 🌿

NatureChamp AI is a local-first Streamlit companion that turns curiosity into real outdoor observation. It combines a configurable open-weight Ollama model with deterministic offline missions, a local SQLite journal, progress tracking, curated nature facts, and cautious local photo analysis.

## Features

- **AI Nature Companion:** conversational, safety-first answers from a local Ollama model.
- **Outdoor Mission Generator:** time, environment, difficulty, and interest controls; AI missions fall back to clearly labeled offline content.
- **Discover from Photo:** validates images locally and optionally sends them only to a configured local Ollama vision model.
- **Nature Journal:** create, view, edit, delete, search, and export entries. Location is voluntary and no GPS is collected.
- **Progress:** confirmed mission completions, minutes, categories, badges, and weekly activity.
- **Offline facts:** curated facts remain available without internet access.
- **Bundled imagery:** forest, bird, flower, and garden photographs are stored in `assets/` for offline dashboard rendering. Sources and license notes are in [`assets/SOURCES.md`](assets/SOURCES.md).
## Deployment
https://naturebuddyai.streamlit.app/
## Screenshots
<img width="1906" height="1147" alt="image" src="https://github.com/user-attachments/assets/fbe8d5b8-202b-4599-8e4d-e67cfb381ad1" />

<img width="1912" height="1142" alt="image" src="https://github.com/user-attachments/assets/4db466ba-eb7b-40a9-8796-426c50859c61" />

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the component map, AI flow, storage schema, fallback behavior, and privacy boundaries.

## Windows PowerShell setup

Prerequisites: Python 3.11 or 3.12. Ollama is optional for offline missions/facts, but required for local AI chat and AI mission generation.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

Install Ollama from [ollama.com](https://ollama.com), start it, and download a compatible model:

```powershell
ollama pull qwen2.5:3b
```

Set `OLLAMA_MODEL` in `.env` if you use another installed model. For image analysis, install a compatible vision model and set `OLLAMA_VISION_MODEL` (for example, a vision-capable Ollama tag). Do not assume a model is installed: the app checks `/api/tags` and gives an actionable message.

## Offline and privacy behavior

After dependencies and any desired models are downloaded, the facts, journal, progress, image validation, and deterministic mission library work without internet. AI features require a running local Ollama server and installed model. A failed AI request is never replaced with fake AI output. Journal data is stored in `naturechamp.db`; uploaded photos are processed in memory and are not persisted. No paid API key is used and no third-party service receives user photos or conversations.

The default `qwen2.5:3b` is an open-weight Ollama model tag. Verify the exact upstream model card and license before redistribution; Qwen releases can have license-specific conditions. The application itself can be distributed under the repository's chosen open-source license.

## Troubleshooting

- **Ollama not reachable:** start Ollama and confirm `http://localhost:11434/api/tags` responds.
- **Model unavailable:** run `ollama list`, then `ollama pull <model>` or update `OLLAMA_MODEL`.
- **PowerShell activation blocked:** use `Set-ExecutionPolicy -Scope Process Bypass`.
- **Database issue:** stop Streamlit and check that the configured `NATURECHAMP_DB_PATH` directory is writable.

## Testing

```powershell
python -m pytest -q
```

Tests mock Ollama and use temporary SQLite databases; they do not require internet or a downloaded model.

## License

Add the project's preferred open-source license before publishing. Third-party model licenses are separate; consult each model's upstream license and attribution requirements.
