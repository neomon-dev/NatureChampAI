"""NatureChamp AI Streamlit application."""

from datetime import date
import csv
from io import BytesIO, StringIO
import json
from pathlib import Path

import streamlit as st

from config import settings
from database.db import Database
from database.journal_repository import JournalRepository
from database.progress_repository import ProgressRepository
from services.llm_service import LLMService, OllamaError
from services.mission_service import (
    VALID_DIFFICULTIES,
    VALID_ENVIRONMENTS,
    VALID_INTERESTS,
    VALID_TIMES,
    MissionService,
)
from services.nature_facts import load_facts
from services.vision_service import validate_image, VisionService


st.set_page_config(page_title="NatureChamp AI", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")
ASSET_DIR = Path(__file__).parent / "assets"
st.markdown(
    """
    <style>
    :root { --forest:#173d2d; --body:#20352b; --sage:#dce9d7; --cream:#faf9f3; --sidebar:#eaf1e5; --earth:#8c512f; --border:#d4e1d1; }
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background:var(--cream); color:var(--body); }
    [data-testid="stSidebar"] { background:var(--sidebar); border-right:1px solid var(--border); }
    [data-testid="stSidebar"] * { color:var(--body); }
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stCaption, label, [data-testid="stWidgetLabel"] p,
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stFileUploaderDropzone"] { color:var(--body); }
    h1, h2, h3, h4, h5, h6 { color:var(--forest); letter-spacing:-.02em; }
    .hero { background:var(--forest); color:#fff; padding:2.6rem; min-height:270px; display:flex; flex-direction:column; justify-content:center; border-radius:22px; margin-bottom:1.25rem; }
    .hero h1, .hero p { color:#fff; margin:0; text-shadow:0 1px 2px rgba(0,0,0,.25); }
    .hero h1 { font-size:clamp(2.1rem,5vw,3.4rem); margin-bottom:.35rem; }
    .hero p { max-width:630px; font-size:1.05rem; }
    .card { background:#fff; color:var(--body); border:1px solid var(--border); border-radius:16px; padding:1.1rem; margin:.5rem 0; box-shadow:0 4px 18px rgba(23,73,54,.06); }
    .card h2, .card h3, .card p, .card small { color:var(--body); }
    .card h2, .card h3 { color:var(--forest); }
    .muted, .stCaption, small { color:#4a6155 !important; }
    .badge { display:inline-block; background:var(--sage); color:var(--forest); padding:.25rem .6rem; border-radius:999px; font-size:.8rem; margin-right:.25rem; }
    .screen-reminder { border-left:4px solid var(--earth); background:#fff3e9; padding:.75rem 1rem; border-radius:8px; color:#633d28; }
    .feature-card { overflow:hidden; padding:0 0 1rem; }
    .feature-card img { width:100%; height:150px; object-fit:cover; display:block; }
    .feature-card h3, .feature-card p { margin: .8rem 1rem 0; }
    .feature-card p { color:var(--body); }
    .stButton > button { color:var(--forest); border-color:#9db9a0; background:#fff; font-weight:600; }
    .stButton > button[kind="primary"] { color:#fff; background:var(--forest); border-color:var(--forest); }
    .stButton > button:hover { color:#fff; background:#2b624b; border-color:#2b624b; }
    [data-baseweb="select"] > div, [data-baseweb="input"] > div, textarea { background:#fff; color:var(--body); border-color:#9db9a0; }
    [data-baseweb="select"] *, [data-baseweb="input"] *, textarea { color:var(--body) !important; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label { color:var(--body) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_db() -> Database:
    return Database(settings.database_path)


def repositories() -> tuple[JournalRepository, ProgressRepository]:
    connection = get_db().connection()
    return JournalRepository(connection), ProgressRepository(connection)


def render_header(title: str, subtitle: str = "") -> None:
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def local_image(name: str, caption: str) -> Path | None:
    path = ASSET_DIR / name
    if path.exists():
        return path
    st.warning(f"Image asset unavailable: {name}")
    return None


def home_page() -> None:
    journal, progress = repositories()
    summary = progress.summary()
    hero_image = local_image("forest-trail.jpg", "Forest trail")
    hero_col, text_col = st.columns([1.15, 1], gap="large")
    with hero_col:
        if hero_image:
            st.image(str(hero_image), caption="A trail is waiting", use_container_width=True)
    with text_col:
        st.markdown('<div class="hero"><h1>NatureChamp AI</h1><p>Your local, open-weight AI companion for learning outside.</p><p>Read a mission, put the phone away, and let curiosity lead.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="screen-reminder">🌱 <strong>Touch grass reminder:</strong> this app is a launchpad for outdoor time, not a destination. Prepare here, then explore away from the screen.</div>', unsafe_allow_html=True)
    st.subheader("Your local footprint")
    cols = st.columns(4)
    for col, label, value in zip(cols, ("Missions", "Outdoor minutes", "Journal entries", "Categories"), (summary["missions"], summary["minutes"], summary["entries"], summary["categories"])):
        col.metric(label, value)
    st.subheader("Start with a small adventure")
    if st.button("Start an Outdoor Mission", type="primary", use_container_width=True):
        st.session_state["page"] = "Outdoor Missions"
        st.rerun()
    st.subheader("Explore your surroundings")
    features = [
        ("bird-habitat.jpg", "AI Nature Companion", "Ask thoughtful questions and get local, safety-first guidance."),
        ("forest-trail.jpg", "Outdoor Missions", "Turn five, fifteen, or thirty minutes into a purposeful adventure."),
        ("wildflower.jpg", "Discover Nature", "Explore plants, birds, insects, and trees with cautious photo analysis."),
    ]
    feature_cols = st.columns(3)
    for col, (image_name, title, description) in zip(feature_cols, features):
        with col:
            image = local_image(image_name, title)
            if image:
                st.image(str(image), caption=title, use_container_width=True)
            st.markdown(f'<div class="card feature-card"><h3>{title}</h3><p>{description}</p></div>', unsafe_allow_html=True)
    garden_image = local_image("garden-trees.jpg", "Garden and trees")
    if garden_image:
        st.image(str(garden_image), caption="Gardens and trees are full of small stories", use_container_width=True)
    st.subheader("A fact for the trail")
    fact = load_facts()[summary["missions"] % len(load_facts())]
    st.markdown(f'<div class="card"><span class="badge">{fact["subject"]}</span><p>{fact["fact"]}</p><small>Source: {fact["source"]}</small></div>', unsafe_allow_html=True)


def companion_page() -> None:
    render_header("AI Nature Companion", "Ask the local open-weight model for concise, safety-first guidance.")
    st.info(f"Configured local model: `{settings.ollama_model}`. Conversations stay on this machine when Ollama is used.")
    prompts = ["What birds might I see in a city park?", "Why do leaves change color?", "What should I look for during a 20-minute walk?"]
    cols = st.columns(3)
    for col, prompt in zip(cols, prompts):
        if col.button(prompt, key=f"prompt-{prompt}"):
            st.session_state["chat_input"] = prompt
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Hi! Ask me something about the living world. I will help you observe safely and suggest an offline activity."}]
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if st.button("Reset conversation"):
        st.session_state["messages"] = st.session_state["messages"][:1]
        st.rerun()
    prompt = st.chat_input("Ask a nature question...")
    prompt = prompt or st.session_state.pop("chat_input", None)
    if prompt:
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        system = (
            "You are NatureChamp AI. Be concise, warm, educational, and suggest a real-world activity. "
            "Never advise eating unknown plants, handling wildlife, approaching nests, or disturbing habitats. "
            "Mention uncertainty and local expert guidance when identification or safety is unclear."
        )
        try:
            answer = LLMService().chat([{"role": "system", "content": system}] + st.session_state["messages"])
        except OllamaError as exc:
            answer = f"**Local AI unavailable.** {exc}\n\nNo fabricated answer was generated. You can still use the offline missions and facts while Ollama is offline."
        st.session_state["messages"].append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)


def missions_page() -> None:
    render_header("Outdoor Missions", "Choose your constraints, read the plan, then leave your phone behind.")
    cols = st.columns(4)
    minutes = cols[0].selectbox("Time", VALID_TIMES, format_func=lambda n: f"{n} minutes")
    environment = cols[1].selectbox("Environment", VALID_ENVIRONMENTS)
    difficulty = cols[2].selectbox("Difficulty", VALID_DIFFICULTIES)
    interest = cols[3].selectbox("Interest", VALID_INTERESTS)
    if st.button("Generate mission", type="primary"):
        with st.spinner("Checking the local model, then preparing your mission..."):
            mission, ai_generated = MissionService(LLMService()).generate(minutes, environment, difficulty, interest)
        st.session_state["mission"] = mission
        st.session_state["mission_ai"] = ai_generated
    mission = st.session_state.get("mission")
    if not mission:
        st.markdown('<div class="card"><h3>Your next small adventure</h3><p>Start with five minutes. Notice more than you photograph.</p></div>', unsafe_allow_html=True)
        return
    label = "Generated by local open-weight AI" if st.session_state.get("mission_ai") else "Offline deterministic mission (not AI-generated)"
    st.success(label)
    st.markdown(f'<div class="card"><h2>{mission["title"]}</h2><p>{mission["description"]}</p><span class="badge">{mission["duration_minutes"]} min</span><span class="badge">{mission["difficulty"]}</span></div>', unsafe_allow_html=True)
    st.subheader("Tasks")
    for task in mission["tasks"]:
        st.checkbox(task, key=f"task-{hash(task)}")
    st.subheader("Observation tips")
    for tip in mission["observation_tips"]:
        st.markdown(f"- {tip}")
    st.info(f"Reflection: {mission['reflection_question']}")
    st.caption("Complete the mission in the real world, then confirm honestly.")
    if st.button("✅ I completed this mission"):
        repositories()[1].record_mission(mission["title"], mission["duration_minutes"], interest)
        st.success("Nice work. Your confirmed outdoor time was recorded.")


def discover_page() -> None:
    render_header("Discover from Photo", "Local-only image handling with honest uncertainty.")
    uploaded = st.file_uploader("Upload a nature photo", type=["jpg", "jpeg", "png", "webp"], help=f"Maximum {settings.max_image_size_mb} MB. The photo is processed in memory and not saved.")
    if not uploaded:
        st.markdown('<div class="card"><p>For the most useful result, include the whole subject and its surroundings. AI identification is never definitive.</p></div>', unsafe_allow_html=True)
        return
    image_bytes = uploaded.getvalue()
    valid, error = validate_image(image_bytes, uploaded.type, settings.max_image_size_mb)
    if not valid:
        st.error(error)
        return
    st.image(image_bytes, caption="Your photo (not saved permanently)", use_container_width=True)
    if st.button("Describe with configured local vision model", type="primary"):
        with st.spinner("Analyzing locally..."):
            result, ai = VisionService(LLMService()).describe(image_bytes)
        st.success("Local vision response" if ai else "Vision model unavailable")
        st.markdown(result)
        st.warning("AI image analysis is not definitive. Do not eat, touch, or handle unknown plants or wildlife.")


def journal_page() -> None:
    render_header("Nature Journal", "Keep observations local. Precise GPS is never collected.")
    journal, _ = repositories()
    with st.expander("＋ New journal entry", expanded=not journal.list()):
        with st.form("journal-form"):
            entry_date = st.date_input("Date", date.today())
            location = st.text_input("Location label (optional)", max_chars=100)
            title = st.text_input("Observation title", max_chars=120)
            notes = st.text_area("Notes", max_chars=5000)
            mission_done = st.checkbox("This entry records a completed mission")
            photo = st.file_uploader("Optional photo", type=["jpg", "jpeg", "png", "webp"])
            if st.form_submit_button("Save entry", type="primary"):
                if not title.strip() or not notes.strip():
                    st.error("Add a title and some notes before saving.")
                else:
                    journal.create({"entry_date": entry_date.isoformat(), "location_label": location.strip(), "title": title.strip(), "notes": notes.strip(), "photo": photo.getvalue() if photo else None, "mission_completed": mission_done})
                    st.success("Journal entry saved locally.")
                    st.rerun()
    search = st.text_input("Search your entries")
    entries = journal.list(search)
    if not entries:
        st.info("No entries yet. A five-minute sit spot is a great first page.")
    for entry in entries:
        with st.container(border=True):
            st.subheader(entry["title"])
            st.caption(f"{entry['entry_date']} · {entry['location_label'] or 'Location not specified'}")
            st.write(entry["notes"])
            if entry["photo"]:
                st.image(BytesIO(entry["photo"]), width=240)
            col1, col2 = st.columns(2)
            if col1.button("Delete", key=f"delete-{entry['id']}"):
                journal.delete(entry["id"])
                st.rerun()
            if col2.button("Edit", key=f"edit-{entry['id']}"):
                st.session_state["editing_entry"] = entry["id"]
                st.rerun()
            if entry["mission_completed"]:
                st.success("Mission noted")
        if st.session_state.get("editing_entry") == entry["id"]:
            with st.form(f"edit-form-{entry['id']}"):
                edited_title = st.text_input("Title", value=entry["title"])
                edited_location = st.text_input("Location", value=entry["location_label"])
                edited_notes = st.text_area("Notes", value=entry["notes"])
                if st.form_submit_button("Save changes"):
                    if edited_title.strip() and edited_notes.strip():
                        journal.update(entry["id"], {"entry_date": entry["entry_date"], "location_label": edited_location.strip(), "title": edited_title.strip(), "notes": edited_notes.strip(), "photo": entry["photo"], "mission_completed": entry["mission_completed"]})
                        st.session_state.pop("editing_entry", None)
                        st.rerun()
                    st.error("Title and notes are required.")
    if entries:
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(["date", "location", "title", "notes", "mission_completed"])
        writer.writerows((e["entry_date"], e["location_label"], e["title"], e["notes"], e["mission_completed"]) for e in entries)
        st.download_button("Download journal CSV", csv_buffer.getvalue(), "naturechamp-journal.csv", "text/csv")
        st.download_button("Download journal JSON", json.dumps([dict(e) for e in entries], indent=2, default=str), "naturechamp-journal.json", "application/json")


def progress_page() -> None:
    render_header("Progress & Achievements", "Only confirmed completions count.")
    _, progress = repositories()
    summary = progress.summary()
    cols = st.columns(4)
    for col, label, key in zip(cols, ("Missions completed", "Outdoor minutes", "Journal entries", "Categories explored"), ("missions", "minutes", "entries", "categories")):
        col.metric(label, summary[key])
    badges = [("First step", summary["missions"] >= 1), ("Hour outside", summary["minutes"] >= 60), ("Field noter", summary["entries"] >= 3), ("Curious generalist", summary["categories"] >= 4)]
    st.subheader("Badges")
    for name, earned in badges:
        st.markdown(f'<div class="card">{"🏅" if earned else "🔒"} <strong>{name}</strong> {"Earned" if earned else "Keep exploring"}</div>', unsafe_allow_html=True)
    st.subheader("Weekly activity")
    weekly = progress.weekly_minutes()
    st.bar_chart({week: minutes for week, minutes in weekly} if weekly else {"No activity yet": 0})


def settings_page() -> None:
    render_header("Settings", "Local-first configuration and privacy boundaries.")
    st.markdown(f"- Ollama URL: `{settings.ollama_base_url}`\n- Chat model: `{settings.ollama_model}`\n- Vision model: `{settings.ollama_vision_model or 'not configured'}`\n- Database: `{settings.database_path}`")
    st.info("Set values in a `.env` file based on `.env.example`, then restart Streamlit. NatureBuddy does not require a paid API key.")
    st.subheader("Model guidance")
    st.write("The default `qwen2.5:3b` is a configurable open-weight model tag commonly supported by Ollama. Verify the model card and license for the exact tag you install. Qwen model licenses may include additional conditions; review the upstream license before redistribution.")
    st.subheader("Privacy")
    st.write("Chat, journal data, and uploaded photos stay local by default. Photos are analyzed in memory and are not written to the database. Do not enter sensitive personal information in journal notes.")


def main() -> None:
    if "page" not in st.session_state:
        st.session_state["page"] = "Home Dashboard"
    with st.sidebar:
        st.markdown("## 🌿 NatureBuddy")
        page = st.radio("Explore", ["Home Dashboard", "AI Nature Companion", "Outdoor Missions", "Discover from Photo", "Nature Journal", "Progress & Achievements", "Settings"], index=["Home Dashboard", "AI Nature Companion", "Outdoor Missions", "Discover from Photo", "Nature Journal", "Progress & Achievements", "Settings"].index(st.session_state["page"]))
        st.session_state["page"] = page
        st.divider()
        st.caption("Open-weight AI. Local data. More time outside.")
    {"Home Dashboard": home_page, "AI Nature Companion": companion_page, "Outdoor Missions": missions_page, "Discover from Photo": discover_page, "Nature Journal": journal_page, "Progress & Achievements": progress_page, "Settings": settings_page}[page]()


if __name__ == "__main__":
    main()
