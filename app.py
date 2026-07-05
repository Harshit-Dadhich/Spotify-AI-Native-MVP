import streamlit as st
import google.generativeai as genai
import anthropic
import json
import re

st.set_page_config(page_title="Discovery, Explained", page_icon="🎧", layout="wide")

# ---------------------------------------------------------------------------
# Spotify-inspired theme
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background-color: #121212;
    color: #FFFFFF;
}

section[data-testid="stSidebar"] {
    background-color: #000000;
    border-right: 1px solid #282828;
}

h1 {
    font-weight: 800 !important;
    letter-spacing: -0.02em;
}

h1 .accent { color: #1DB954; }

.subtitle {
    color: #B3B3B3;
    font-size: 1.05rem;
    margin-top: -0.6rem;
    margin-bottom: 1.8rem;
}

.stTextArea textarea, .stTextInput input {
    background-color: #242424 !important;
    color: #FFFFFF !important;
    border: 1px solid #3E3E3E !important;
    border-radius: 8px !important;
}

.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #1DB954 !important;
    box-shadow: 0 0 0 1px #1DB954 !important;
}

label, .stMarkdown p { color: #FFFFFF !important; }

.stButton > button {
    background-color: #1DB954 !important;
    color: #000000 !important;
    border-radius: 500px !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 0.6rem 1.6rem !important;
    transition: transform 0.15s ease, background-color 0.15s ease;
}
.stButton > button:hover {
    background-color: #1ED760 !important;
    transform: scale(1.02);
}

.rec-card {
    background-color: #181818;
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.9rem;
    border-left: 4px solid #535353;
    transition: background-color 0.2s ease;
}
.rec-card:hover { background-color: #202020; }

.rec-card.close { border-left-color: #6B87B7; }
.rec-card.adjacent { border-left-color: #E8A33D; }
.rec-card.stretch { border-left-color: #1DB954; }

.rec-title { font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.15rem; }
.rec-artist { font-size: 0.9rem; color: #B3B3B3; margin-bottom: 0.5rem; }
.rec-reason { font-size: 0.92rem; color: #D9D9D9; line-height: 1.4; margin-bottom: 0.6rem; }

.tag {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    padding: 0.22rem 0.65rem;
    border-radius: 500px;
}
.tag.close { background-color: rgba(107,135,183,0.18); color: #8FA9D6; }
.tag.adjacent { background-color: rgba(232,163,61,0.18); color: #E8A33D; }
.tag.stretch { background-color: rgba(29,185,84,0.18); color: #1DB954; }

.compass-label {
    display: flex;
    justify-content: space-between;
    color: #B3B3B3;
    font-size: 0.85rem;
    margin-top: -0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("<h1>🎧 Discovery, <span class='accent'>Explained</span></h1>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Tell it your taste in your own words. Say what you're in the mood for. "
    "Every suggestion tells you exactly why — and how far it's stretching from what you already know.</div>",
    unsafe_allow_html=True
)

# ---------------------------------------------------------------------------
# Sidebar — provider/key
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    provider = st.radio(
        "AI Provider",
        ["Gemini (free)", "Claude"],
        help="Gemini's API has a free tier with no credit card needed. Claude requires paid credits."
    )
    if provider == "Gemini (free)":
        api_key = st.text_input("Gemini API Key", type="password",
                                 help="Free key, no card required: aistudio.google.com/apikey")
    else:
        api_key = st.text_input("Claude API Key", type="password")

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
Your job: interpret their taste (do not ask clarifying questions — infer sensibly), then recommend 8 real songs/artists
that fit their current mood request.

Listener's usual taste: "{taste}"
What they want right now: "{request}"
Comfort-zone slider (0 = stay very close to usual taste, 100 = surprise them with something genuinely different): {adventure}

Bias your picks toward matching this slider value honestly — a high number should include genuinely less-obvious,
farther-from-taste picks, not just more of the same with a different label.

Respond with ONLY a valid JSON array (no markdown fences, no commentary), where each item has:
- "title": song title
- "artist": artist name
- "reason": one sentence, in plain conversational language, explaining specifically why this fits their mood/taste
- "distance": one of "close", "adjacent", "stretch" — how far this pick is from their stated usual taste

Return exactly 8 items."""


def extract_json(text):
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return json.loads(text)


DIST_LABEL = {
    "close": "Close to your taste",
    "adjacent": "Adjacent",
    "stretch": "Genuine stretch",
}

if go:
    if not api_key:
        st.error("⚠️ Please enter your API key in the sidebar.")
        st.stop()
    if not taste.strip() or not request.strip():
        st.error("⚠️ Please fill in both your taste and your current mood/request.")
        st.stop()

    prompt = build_prompt(taste, request, adventure)

    with st.spinner("🎧 Interpreting your taste and finding matches..."):
        try:
            if provider == "Gemini (free)":
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(prompt)
                raw = response.text
            else:
                client = anthropic.Anthropic(api_key=api_key)
                msg = client.messages.create(
                    model="claude-sonnet-4-5",
                    max_tokens=1500,
                    messages=[{"role": "user", "content": prompt}],
                )
                raw = msg.content[0].text

            recs = extract_json(raw)
        except json.JSONDecodeError:
            st.error("The AI response wasn't valid JSON. Try clicking Discover again.")
            st.stop()
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.stop()

    st.markdown("### Your discovery mix")
    for r in recs:
        dist = r.get("distance", "adjacent").lower()
        if dist not in DIST_LABEL:
            dist = "adjacent"
        st.markdown(f"""
        <div class="rec-card {dist}">
            <div class="rec-title">{r.get('title', 'Untitled')}</div>
            <div class="rec-artist">{r.get('artist', 'Unknown artist')}</div>
            <div class="rec-reason">{r.get('reason', '')}</div>
            <span class="tag {dist}">{DIST_LABEL[dist]}</span>
        </div>
        """, unsafe_allow_html=True)

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
