# NatureBuddy AI architecture

## Boundaries

`app.py` is the Streamlit composition layer. `services/` contains model adapters, mission policy, image validation, and facts. `database/` contains parameterized SQLite repositories. `data/` contains deterministic content that ships with the app. `assets/` contains locally bundled dashboard photographs and their source/license notes.

## AI flow

The companion and mission generator call `LLMService`, which checks Ollama's local `/api/tags` endpoint before using `/api/chat`. The model and base URL are environment-configurable. Mission output is parsed as JSON and normalized; malformed or unavailable responses select a deterministic library mission and label it **not AI-generated**. Companion failures show the actual category of failure rather than inventing an answer.

Photo uploads are checked for content type, size, and image integrity with Pillow. `VisionService` uses a configured local vision model only when one is explicitly configured. Without it, the app explains that vision analysis is unavailable; it never pretends to identify a species.

## Data model

SQLite initializes two tables:

- `journal_entries`: date, voluntary location label, title, notes, optional photo blob, and mission flag.
- `mission_completions`: mission title, minutes, category, and completion timestamp.

Repositories use parameterized SQL. Mission completion is idempotent for the same mission title on the same day. Progress is computed from these confirmed records; there is no seeded history.

## Privacy

The default database is local. Exact GPS coordinates are not collected. Uploaded photos are held in memory for validation/analysis and are not inserted into SQLite. Ollama runs on the local machine; the app has no paid API integration.

## UX principle

The product is deliberately screen-light: users select and read a mission, then are encouraged to put the device away. AI is a material helper, but core missions and facts remain usable without a model.
