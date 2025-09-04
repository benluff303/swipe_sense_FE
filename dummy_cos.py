# streamlit_app.py
# Minimal Streamlit client that talks to the FastAPI backend.

import requests
import streamlit as st
import time
# import numpy as np
import pandas as pd
from GPT_itinirary import generate_itinerary, itinerary_to_markdown
import os

# API = st.secrets.get("API_URL", "http://localhost:8000")  # set in .streamlit/secrets.toml optionally

API = "https://swipesense-51860419257.europe-west2.run.app/"

st.set_page_config(page_title="SwipeSense", layout="wide")

# ===== Landing page (inserted) =====
# Global CSS and CTA styling
st.markdown(
    """
    <style>
      #MainMenu {visibility: hidden;} footer {visibility: hidden;}
      header, .st-emotion-cache-18ni7ap, .st-emotion-cache-1avcm0n { display: none !important; }
      .stApp { background: transparent !important; }
      .block-container { padding-top: 0 !important; }
      div.stButton > button:first-child {
        background: rgba(255,255,255,0.9); color:#111 !important; font-weight:700;
        border-radius:999px; padding:0.9rem 2rem; border:1px solid rgba(255,255,255,0.7);
        box-shadow:0 8px 28px rgba(0,0,0,0.15); transition: all 0.3s ease;
      }
      div.stButton > button:first-child:hover {
        background:#fff; color:#000 !important; transform: translateY(-2px);
        box-shadow:0 12px 32px rgba(0,0,0,0.2);
      }

  /* Make all Streamlit images consistently sized without cropping */
  .stImage img {
    width: 100% !important;
    height: auto !important;
    max-height: 75vh;           /* keep large but inside viewport */
    object-fit: contain !important;  /* avoid cropping */
    display: block;
  }
</style>
    """, unsafe_allow_html=True
)
st.markdown("""
<style>
  /* Hide sidebar completely */
  section[data-testid="stSidebar"] { display:none !important; }
  div[data-testid="stSidebarNav"] { display:none !important; }
  /* Expand main area if sidebar was taking space */
  .main { width: 100% !important; }

  /* Fixed reset button (top-right) */
  .reset-wrap { position: fixed; top: 16px; right: 16px; z-index: 9999; }
  .reset-wrap button {
    background: rgba(255,255,255,0.9);
    color: #111 !important;
    font-weight: 700;
    border-radius: 999px;
    padding: 0.5rem 1rem;
    border: 1px solid rgba(255,255,255,0.7);
    box-shadow: 0 8px 28px rgba(0,0,0,0.15);
    transition: all 0.2s ease;
  }
  .reset-wrap button:hover {
    background:#fff; color:#000 !important; transform: translateY(-1px);
    box-shadow: 0 12px 32px rgba(0,0,0,0.2);
  }
</style>
""", unsafe_allow_html=True)

def _do_reset(): # reset backend state too
    st.session_state.started = False
    st.session_state.idx = 0
    st.session_state.likes = []
    st.session_state.image_ids = []
    res = requests.get(f"{API}/reset_user_prefs")
    st.write(res.json())
    st.rerun()

# Show only when started
if st.session_state.get("started"):
    st.markdown('<div class="reset-wrap">', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# Helper: base64-encode hero image
import base64 as _b64mod
def _b64(data: bytes) -> str:
    try:
        return _b64mod.b64encode(data).decode()
    except Exception:
        return ""

def _hero_b64():
    # Try local ./images folder first
    for p in ("./images/landing_page_BG.png", "landing_page_BG.png"):
        if os.path.exists(p):
            with open(p, "rb") as f:
                return _b64(f.read())
    return ""
# Replace your existing helper with this
def show_image_bytes(img_bytes: bytes):
    try:
        st.image(img_bytes, use_container_width=True)
    except TypeError:
        # Old Streamlit fallback (no deprecation warning)
        st.image(img_bytes)


if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    _BG = _hero_b64()
    _LANDING_HTML = f"""
    <style>
      .full-bg {{ position: fixed; inset: 0; z-index: -1;
        background-image: url('data:image/png;base64,{_BG}');
        background-size: cover; background-position: center;
        filter: brightness(0.9); }}
      .brand {{ position: absolute; top: 20px; left: 30px;
        font-weight: 800; font-size: 16px; letter-spacing: 0.5px;
        color: #fff; z-index: 2; }}
      .hero-wrap {{ min-height: 100vh; display: flex; align-items: center; justify-content: center; }}
      .hero-content {{ max-width: 1000px; text-align: center; color: #fff; padding: 0 16px; }}
      .hero-title {{ font-size: clamp(28px, 6vw, 72px); font-weight: 800;
        line-height: 1.05; margin-bottom: 16px; }}
      .hero-sub {{ font-size: clamp(16px, 2vw, 22px); opacity: 0.98; margin-bottom: 28px; }}

      /* Make all Streamlit images consistently sized without cropping */
      .stImage img {{
        width: 100% !important;
        height: auto !important;
        max-height: 75vh;
        object-fit: contain !important;
        display: block;
      }}
    </style>
    <div class='full-bg'></div>
    <div class='brand'>SwipeSense</div>
    <div class='hero-wrap'>
      <div class='hero-content'>
        <div class='hero-title'>Weaving Inspiration Into Unforgettable Adventures</div>
        <div class='hero-sub'>We take the effort out of travel planning. Browse our gallery of inspirational destinations and our intelligent system will construct the perfect travel itinerary.</div>
      </div>
    </div>
    """

    st.markdown(_LANDING_HTML, unsafe_allow_html=True)
    _, _mid, _ = st.columns([3,4,3])
    with _mid:
        if st.button("Start your journey", use_container_width=True):
            st.session_state.started = True
            st.rerun()
    st.stop()

# ===== End landing page =====

# ===== Global reset controls =====

# Put page title on the left, user_id on the right
col_left, col_right = st.columns([3, 1])

with col_left:
    st.markdown(
        "<h2 style='margin-top:0; font-size:2rem; font-weight:700;'>"
        "SwipeSense ✈️ Your Travel Itinerary Generator"
        "</h2>",
        unsafe_allow_html=True,
    )

with col_right:
    # smaller text input
    st.markdown(
        """
        <style>
        div[data-testid="stTextInput"] label {font-size: 0.8rem !important; color: #666;}
        div[data-testid="stTextInput"] input {font-size: 0.8rem !important; padding: 0.25rem 0.5rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    user_id = st.text_input("User ID", value="default")



# State
if "current" not in st.session_state:
    st.session_state.current = None
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()


def fetch_next():
    r = requests.post(f"{API}/next", json={"user_id": user_id}).json()
    if r.get("status") == "end":
        st.warning("No more candidates. You may need to relax filters or restart the backend.")
        st.session_state.current = None
        return None
    st.session_state.current = r
    return r

col1, col2 = st.columns([3, 1])

with col1:
    if st.session_state.current:
        idx = st.session_state.current["idx"]
        img_resp = requests.get(f"{API}/image/{idx}")
        st.image(img_resp.content, caption=f"idx={idx} | sim={st.session_state.current.get('sim_score')}", use_container_width=True)
    else:
        fetch_next()

with col2:
    st.subheader("Controls")
    if st.button("Start / Next ▶"):
        fetch_next()

    if st.session_state.current:
        idx = st.session_state.current["idx"]
        if st.button("🔥 Like"):
            requests.post(f"{API}/feedback", json={"user_id": user_id, "idx": idx, "action": "like", "dwell": None})
            fetch_next()
        if st.button("➡️ Skip"):
            dwell_time = time.time() - st.session_state.start_time
            requests.post(f"{API}/feedback", json={"user_id": user_id, "idx": idx, "action": "swipe", "dwell": dwell_time})
            fetch_next()
        # if st.button("Get user profile"):
        #     r = requests.get(f"{API}/user_profile/{user_id}").json()
        #     st.write(r)

            # api call to get df locations + keywords, from user vector (vector already sitting backend)
            # SwipeSense_url = "https://api.com/endpoint"
            # user = {"responses": st.session_state.responses}



            # try:
            #     response = requests.post(SwipeSense_url, json=user)
            #     response.raise_for_status()
            #     data = response.json() if response and response.content else {}

            #     df = pd.DataFrame(data)

            #     if "location" in df.columns:
            #         df_top_cities = df[["location", "keywords"]].drop_duplicates().head(5)

            #         st.header("Top 5 destinations for you:")
            #         for i, row in df_top_cities.iterrows():
            #             st.write(f"{i+1}. **{row['location']}**")

            #         # Generate itinerary
            #         st.header("Your itinerary:")
            #         itinerary_result = generate_itinerary(df_top_cities)
            #         markdown_itinerary = itinerary_to_markdown(itinerary_result)
            #         st.markdown(markdown_itinerary)

            #     else:
            #         st.warning("No destinations returned. Try again later.")

            # except Exception as e:
            #     st.error(f"Something went wrong while fetching predictions: {e}")


st.divider()
st.caption("Backend API must be running. Start with:  `uvicorn app:app --reload`  and run this with:  `streamlit run streamlit_app.py`")
st.divider()

if st.button("Get itinerary"):
    #hardcode for now but this will be an api request of a dict containing locations and phrases, e.g.:
    #unused
    # api_response = {
    #       "locations": [
    #         "Québec City",
    #         "Seoul"
    #         "London",
    #         "Toronto",
    #         "Clacton"
    #     ],
    #     "phrases": [
    #         "beach holiday",
    #         "mountain escape"
    #         "beach holiday",
    #         "mountain escape",
    #         "mountain escape"
    #     ]
    # }

    # api_response = {
    #     "locations":
    #     [{"location": "Bariloche", "combined_score":0.8447093820002858},
    #      {"location":"Hong Kong","combined_score":0.7035136820583936},
    #      {"location":"Interlaken","combined_score":0.6597705607685682},
    #      {"location":"Lofoten Islands","combined_score":0.6403650713268992},
    #      {"location":"Lake Titicaca","combined_score":0.6309902693763838}
    #     ],
    #     "phrases":
    #         ["a scene of a mountain",
    #          "a travel scene that feels contemplative",
    #          "a rocky or mountainous place where someone could do rock climbing",
    #          "a travel scene that feels rugged",
    #          "a travel scene that feels sombre"
    #          ]
    # }

    # Generate itinerary
    api_response = requests.get(f"{API}/user_to_keywords/").json()
    
    locations = api_response['locations']
    phrases = api_response['phrases']
    #for testing, showing scores
    st.header("Your Top 5 locations:")
    st.dataframe(pd.DataFrame(data=locations))
    city_names = [loc["location"] for loc in locations]


    # st.markdown(locations)
    st.header("Your itinerary:")
    itinerary_result = generate_itinerary(city_names, phrases)
    markdown_itinerary = itinerary_to_markdown(itinerary_result)
    st.markdown(markdown_itinerary)



# ===== Footer reset (optional) =====
if st.session_state.get("started"):
    st.markdown('---')
    col_a, col_b, col_c = st.columns([1,2,1])
    with col_b:
        if st.button("⟲ Reset and start over", use_container_width=True):
            _do_reset()
