import streamlit as st
import google.generativeai as genai
import json
import re
import html as html_module

st.set_page_config(page_title="Discovery, Explained", page_icon="🎧", layout="wide")

# ---------------------------------------------------------------------------
# Spotify-inspired theme
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: radial-gradient(circle at 50% -10%, #1a2e21 0%, #121212 45%);
    color: #FFFFFF;
}

section[data-testid="stSidebar"] {
    background-color: #000000;
    border-right: 1px solid #282828;
}

/* ---- Hero ---- */
.hero-wrap { text-align: center; padding: 1.2rem 0 0.4rem 0; }
.logo-badge {
    width: 64px; height: 64px; border-radius: 50%;
    background: linear-gradient(145deg, #1ED760, #148A3E);
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 0.9rem auto;
    box-shadow: 0 6px 24px rgba(29,185,84,0.35);
}
.hero-title {
    font-weight: 900; font-size: 2.4rem; letter-spacing: -0.03em;
    margin: 0; color: #FFFFFF;
}
.hero-title .accent { color: #1DB954; }
.hero-subtitle {
    color: #B3B3B3; font-size: 1.05rem; max-width: 640px;
    margin: 0.5rem auto 2rem auto; line-height: 1.5;
}

/* ---- Inputs ---- */
.stTextArea textarea, .stTextInput input {
    background-color: #1E1E1E !important;
    color: #FFFFFF !important;
    border: 1px solid #333333 !important;
    border-radius: 10px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #1DB954 !important;
    box-shadow: 0 0 0 1px #1DB954 !important;
}
label, .stMarkdown p { color: #FFFFFF !important; }

/* ---- Slider ---- */
div[data-testid="stSlider"] div[role="slider"] {
    background-color: #1DB954 !important;
    border: 3px solid #FFFFFF !important;
}
div[data-testid="stSlider"] > div > div > div {
    background: linear-gradient(90deg, #1DB954 0%, #E8A33D 100%) !important;
}

/* ---- Button ---- */
.stButton > button {
    background-color: #1DB954 !important;
    color: #000000 !important;
    border-radius: 500px !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 0.7rem 2.2rem !important;
    font-size: 1rem !important;
    transition: transform 0.15s ease, background-color 0.15s ease;
}
.stButton > button:hover {
    background-color: #1ED760 !important;
    transform: scale(1.03);
}

/* ---- Recommendation cards ---- */
.rec-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.9rem; margin-top: 1.2rem; }
@media (max-width: 900px) { .rec-grid { grid-template-columns: 1fr; } }

.rec-card {
    background-color: #181818;
    border-radius: 12px;
    padding: 1.2rem 1.35rem;
    border: 1px solid #262626;
    border-left: 4px solid #535353;
    transition: all 0.2s ease;
    position: relative;
}
.rec-card:hover {
    background-color: #212121;
    border-left-width: 6px;
    transform: translateY(-2px);
}
.rec-card.close { border-left-color: #6B87B7; }
.rec-card.adjacent { border-left-color: #E8A33D; }
.rec-card.stretch { border-left-color: #1DB954; }

.rec-icon {
    width: 42px; height: 42px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; margin-bottom: 0.7rem;
}
.rec-icon.close { background-color: rgba(107,135,183,0.18); }
.rec-icon.adjacent { background-color: rgba(232,163,61,0.18); }
.rec-icon.stretch { background-color: rgba(29,185,84,0.18); }

.rec-num {
    position: absolute; top: 1.1rem; right: 1.2rem;
    font-size: 1.6rem; font-weight: 800; color: #2A2A2A;
}
.rec-title { font-size: 1.1rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.1rem; padding-right: 2rem; }
.rec-artist { font-size: 0.88rem; color: #B3B3B3; margin-bottom: 0.65rem; }
.rec-reason { font-size: 0.92rem; color: #D9D9D9; line-height: 1.45; margin-bottom: 0.75rem; }

.tag {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    padding: 0.28rem 0.7rem;
    border-radius: 500px;
}
.tag.close { background-color: rgba(107,135,183,0.18); color: #8FA9D6; }
.tag.adjacent { background-color: rgba(232,163,61,0.18); color: #E8A33D; }
.tag.stretch { background-color: rgba(29,185,84,0.18); color: #1DB954; }

.compass-label {
    display: flex; justify-content: space-between;
    color: #B3B3B3; font-size: 0.85rem; margin-top: -0.5rem;
}

.section-divider { border-top: 1px solid #262626; margin: 2rem 0 1.2rem 0; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Hero header with original logo mark (not Spotify's trademarked logo)
# ---------------------------------------------------------------------------
st.markdown("""
<div class="hero-wrap">
    <div class="logo-badge">
        <svg width="30" height="30" viewBox="0 0 24 24" fill="none">
            <path d="M4 14 Q4 8 12 8 Q20 8 20 14" stroke="#0A0A0A" stroke-width="2" stroke-linecap="round" fill="none"/>
            <circle cx="4" cy="16" r="2.3" fill="#0A0A0A"/>
            <circle cx="20" cy="16" r="2.3" fill="#0A0A0A"/>
        </svg>
    </div>
    <p class="hero-title">Discovery, <span class="accent">Explained</span></p>
    <p class="hero-subtitle">Tell it your taste in your own words. Say what you're in the mood for.
    Every suggestion tells you exactly why — and how far it's stretching from what you already know.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar — Gemini key (secrets-first, so testers don't need their own key)
# ---------------------------------------------------------------------------
def get_default_key():
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        return ""

with st.sidebar:
    st.header("⚙️ Settings")

    default_key = get_default_key()

    if default_key:
        api_key = default_key
        st.success("✅ Using built-in API key — no setup needed.")
        with st.expander("Use your own key instead"):
            override = st.text_input("Your Gemini API key", type="password")
            if override:
                api_key = override
    else:
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            help="Get a free key at aistudio.google.com/apikey"
        )

    st.markdown("---")
    st.caption(
        "This prototype simulates taste input via free text rather than live Spotify OAuth, "
        "since Spotify restricted broad third-party developer access in Feb 2026 "
        "(Premium-only Developer Mode, 5-user cap without business-level extended quota)."
    )

# ---------------------------------------------------------------------------
# Main inputs
# ---------------------------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    taste = st.text_area(
        "Describe your usual taste, in your own words",
        placeholder="e.g. Mostly lo-fi and indie, but I get into moody electronic sometimes too",
        height=100,
    )
with col2:
    request = st.text_area(
        "What are you in the mood for right now?",
        placeholder="e.g. something for a late night drive, a bit melancholic",
        height=100,
    )

adventure = st.slider("How far outside your comfort zone do you want to go?", 0, 100, 50)
st.markdown(
    f"<div class='compass-label'><span>Stay safe</span><span>Surprise me completely</span></div>",
    unsafe_allow_html=True
)

go = st.button("🔍 Discover", type="primary")

# ---------------------------------------------------------------------------
# AI call
# ---------------------------------------------------------------------------
def build_prompt(taste, request, adventure):
    return f"""You are a music discovery engine. A listener describes their taste and current mood in plain language.

Listener's usual taste: "{taste}"
What they want right now: "{request}"
Comfort-zone slider (0 = stay very close to usual taste, 100 = surprise them with something genuinely different): {adventure}

FIRST, check whether these inputs make sense as a music taste/mood description. If either input is gibberish,
unrelated to music (e.g. "fix my car", random characters, empty gibberish), or too vague to work with even
with reasonable inference, respond with ONLY this JSON object (no markdown fences, no commentary, no extra text
before or after):
{{"valid": false, "message": "<one short, friendly sentence explaining what's missing or unclear, and what kind of input would work instead>"}}

OTHERWISE — including when the slider is 0 — always return exactly 8 recommendations. At slider 0, all 8 should
simply be tagged "close" and stay very safely within their stated taste; do not skip the list or explain your
reasoning outside the JSON. Interpret their taste (do not ask clarifying questions — infer sensibly), then
recommend 8 real songs/artists that fit their current mood request. Bias your picks toward matching the
comfort-zone slider honestly across its full range.

Respond with ONLY a valid JSON array — no markdown fences, no commentary, no text before or after the array —
where each item has:
- "title": song title
- "artist": artist name
- "reason": one sentence, in plain conversational language, explaining specifically why this fits their mood/taste
- "distance": one of "close", "adjacent", "stretch" — how far this pick is from their stated usual taste

Return exactly 8 items in that case."""


def extract_json(text):
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    # If the model added stray commentary before/after the JSON, isolate the
    # actual JSON array or object by finding the outermost brackets.
    first = min(
        (text.find(c) for c in "[{" if c in text),
        default=-1,
    )
    if first > 0:
        text = text[first:]

    for close_char, open_char in (("]", "["), ("}", "{")):
        last = text.rfind(close_char)
        if last != -1 and text.startswith(open_char):
            text = text[: last + 1]
            break

    return json.loads(text)


DIST_LABEL = {
    "close": "Close to your taste",
    "adjacent": "Adjacent",
    "stretch": "Genuine stretch",
}

@st.dialog("Something went wrong")
def show_error_dialog():
    st.write("We couldn't put together your discovery mix this time. Please try again in a moment.")
    if st.button("OK", type="primary", use_container_width=True):
        st.rerun()

@st.dialog("Missing information")
def show_missing_input_dialog(message):
    st.write(message)
    if st.button("OK", type="primary", use_container_width=True):
        st.rerun()

if go:
    if not api_key:
        show_missing_input_dialog("Please add an API key in the sidebar before discovering music.")
        st.stop()
    if not taste.strip() or not request.strip():
        show_missing_input_dialog("Please fill in both your taste and your current mood/request.")
        st.stop()

    prompt = build_prompt(taste, request, adventure)

    with st.spinner("🎧 Interpreting your taste and finding matches..."):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            raw = response.text

            recs = extract_json(raw)
        except Exception:
            show_error_dialog()
            st.stop()

    # Handle the "input didn't make sense" case
    if isinstance(recs, dict) and recs.get("valid") is False:
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        st.warning(
            f"🔍 **No matches found.** {recs.get('message', 'Try describing your taste and mood a bit differently.')}"
        )
        st.stop()

    if not isinstance(recs, list) or len(recs) == 0:
        st.warning("🔍 **No matches found.** Try describing your taste and mood a bit differently.")
        st.stop()

    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown("### Your discovery mix")

    ICON = {"close": "🎵", "adjacent": "🎶", "stretch": "✨"}

    card_blocks = []
    for i, r in enumerate(recs, 1):
        dist = r.get("distance", "adjacent").lower()
        if dist not in DIST_LABEL:
            dist = "adjacent"
        title = html_module.escape(str(r.get("title", "Untitled")))
        artist = html_module.escape(str(r.get("artist", "Unknown artist")))
        reason = html_module.escape(str(r.get("reason", "")))
        card_blocks.append(
            f'<div class="rec-card {dist}"><div class="rec-num">{i:02d}</div>'
            f'<div class="rec-icon {dist}">{ICON[dist]}</div>'
            f'<div class="rec-title">{title}</div>'
            f'<div class="rec-artist">{artist}</div>'
            f'<div class="rec-reason">{reason}</div>'
            f'<span class="tag {dist}">{DIST_LABEL[dist]}</span></div>'
        )
    cards_html = "<div class='rec-grid'>" + "".join(card_blocks) + "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)

else:
    st.info("👈 Fill in your taste, your current mood, and the comfort-zone slider, then click **Discover**.")
    st.markdown("""
    ### Why this is different from a normal recommendation engine
    - **You describe your taste in your own words** — no rigid genre checkboxes.
    - **Every pick tells you why** — no more wondering if a suggestion is random.
    - **You control how far it stretches** — the comfort-zone slider directly signals how much risk you want the model to take, something traditional collaborative-filtering systems don't expose to the user at all.
    """)

st.markdown("---")
st.caption("AI-native discovery prototype · Spotify Growth PM Graduation Project")
