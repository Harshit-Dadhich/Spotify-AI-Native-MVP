# Discovery, Explained — AI-Native MVP

An explainable, comfort-zone-aware music discovery prototype. Users describe their taste
and mood in plain language; the AI interprets both, then generates recommendations with
a plain-English reason and a "distance from your taste" label for each pick.

## Deploy to Streamlit Community Cloud (same process as Part 1)

1. Create a **new** GitHub repo (e.g. `discovery-mvp`) — keep this separate from your
   Part 1 review-engine repo, since these are two different deliverables.
2. Upload `app.py`, `requirements.txt`, and this `README.md`.
3. Go to [share.streamlit.io](https://share.streamlit.io) → New app → select this repo →
   main file path `app.py` → Deploy.
4. You'll get a public link like `https://discovery-mvp-xxxxx.streamlit.app` — this is your
   Part 4 submission link.

## How to use it

1. Open the link.
2. In the sidebar, pick a provider (Gemini is free, no card needed — get a key at
   aistudio.google.com/apikey).
3. Describe your usual taste in a sentence or two.
4. Describe what you're in the mood for right now.
5. Set the comfort-zone slider.
6. Click Discover.

## Why this design

- **Free-text taste input, not dropdowns** — reinforces the "black-box trust" and
  "want to feel understood" findings from the user research; a rigid form would
  contradict the project's own conclusions.
- **Explicit distance-from-taste tagging** — directly targets the comfort-zone-bias
  root cause identified in Part 1/Part 2 research.
- **No live Spotify OAuth** — Spotify tightened third-party developer access in
  Feb 2026 (Premium-only Developer Mode, 5-user cap without a registered business +
  250K MAU for extended quota), making it unusable for a public class-project demo.
  This is a deliberate, documented scope decision, not an oversight.
