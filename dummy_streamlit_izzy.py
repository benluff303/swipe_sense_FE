# app_landing_swipe.py
# Landing page + swipe UI (Like/Next/Create Itinerary)

import streamlit as st
import pandas as pd
import base64

try:
    from GPT_itinirary import generate_itinerary, itinerary_to_markdown  # noqa: F401
    HAS_BACKEND = True
except Exception:
    HAS_BACKEND = False

st.set_page_config(page_title="SwipeSense — Travel Picks", page_icon="✈️", layout="wide")

st.markdown(
    """
    <style>
      #MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
      /* Hide Streamlit default header/toolbar bar */
      header, .st-emotion-cache-18ni7ap, .st-emotion-cache-1avcm0n { display: none !important; }

      /* Make Streamlit canvas transparent so the landing bg shows immediately */
      .stApp { background: transparent !important; }
      .block-container { padding-top: 0 !important; }

      .app-container {max-width: 1100px; margin: 0 auto;}
      .hero {background: linear-gradient(135deg, rgba(255,99,132,0.12), rgba(54,162,235,0.12)); border:1px solid rgba(0,0,0,0.05); border-radius:24px; padding:28px 20px; text-align:center; margin:10px 0 22px 0;}
      .hero h1 {margin:0; font-weight:800; letter-spacing:0.3px;}
      .image-card {border-radius:20px; box-shadow:0 10px 30px rgba(0,0,0,0.08); overflow:hidden; background:white; border:1px solid rgba(0,0,0,0.06);}
      .like-badge {position:absolute; top:14px; right:14px; background:rgba(255,255,255,0.9); backdrop-filter:blur(6px); border-radius:999px; padding:8px 12px; font-weight:700; border:1px solid rgba(0,0,0,0.06);}
      .caption { text-align:center; margin-top:10px; opacity:0.85; }

      /* Hero CTA button styling */
            div.stButton > button:first-child {
                background: rgba(255,255,255,0.55); /* semi-transparent white */
                color: #111 !important;
                font-weight: 700;
                border-radius: 999px;
                padding: 0.7rem 1.2rem; /* reduced width */
                min-width: 120px;
                max-width: 180px;
                border: 2px solid #fff; /* white keyline border */
                box-shadow: 0 8px 28px rgba(0,0,0,0.15);
                transition: all 0.3s ease;
            }
            div.stButton > button:first-child:hover {
                background: rgba(255,255,255,0.85);
                color: #000 !important;
                transform: translateY(-2px);
                box-shadow: 0 12px 32px rgba(0,0,0,0.2);
            }
    </style>
    """,
    unsafe_allow_html=True,
)

def show_image(url: str):
    try:
        st.image(url, use_container_width=True)
    except TypeError:
        try:
            st.image(url, use_column_width=True)
        except TypeError:
            st.image(url)

def b64_bg(paths):
    for p in paths:
        try:
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except Exception:
            continue
    return ""

DEFAULT_IMAGES = [
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e",
    "https://images.unsplash.com/photo-1504198266285-165a90eb4317",
    "https://images.unsplash.com/photo-1483683804023-6ccdb62f86ef",
    "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
    "https://images.unsplash.com/photo-1469474968028-56623f02e42e",
]

if "started" not in st.session_state:
    st.session_state.started = False
if "index" not in st.session_state:
    st.session_state.index = 0
if "likes" not in st.session_state:
    st.session_state.likes = set()
if "images" not in st.session_state:
    st.session_state.images = DEFAULT_IMAGES.copy()

BG_B64 = b64_bg(["images/landing_page_BG.png"])  # supplied image
if not BG_B64:
    # graceful fallback: first default image
    import requests
    try:
        BG_B64 = base64.b64encode(requests.get(DEFAULT_IMAGES[0]).content).decode()
    except Exception:
        BG_B64 = ""

LANDING_HTML = f"""
<style>
  .full-bg {{ position: fixed; inset: 0; z-index: -1; background-image: url('data:image/png;base64,{BG_B64}'); background-size: cover; background-position: center; /* reduce darkening for reliability */ filter: brightness(0.9); }}
  .hero-wrap {{ min-height: 100vh; display: flex; align-items: center; justify-content: center; }}
  .hero-content {{ max-width: 1000px; text-align: center; color: #fff; padding: 0 16px; }}
  .hero-title {{ font-size: clamp(36px, 6vw, 72px); font-weight: 800; line-height: 1.05; margin-bottom: 16px; }}
  .hero-sub {{ font-size: clamp(16px, 2vw, 22px); opacity: 0.98; margin-bottom: 28px; }}
</style>
<div class='full-bg'></div>
<div class='hero-wrap'>
  <div class='hero-content'>
    <div style='font-weight:800; letter-spacing:0.5px;'>SwipeSense</div>
    <div class='hero-title'>Weaving Inspiration Into Unforgettable Adventures</div>
    <div class='hero-sub'>We take the effort out of travel planning. Browse our gallery of inspirational destinations and our intelligent system will construct the perfect travel itinerary.</div>
        <div class='landing-btn-row' style='margin-top:38px; display:flex; justify-content:center;'>
            <!-- Streamlit button will be injected here -->
        </div>
  </div>
</div>
"""

if not st.session_state.started:
    st.markdown(LANDING_HTML, unsafe_allow_html=True)
    _, mid, _ = st.columns([3,4,3])
    with mid:
        # Place the button in the landing-btn-row using HTML and Streamlit
        btn_container = st.empty()
        with btn_container:
            # Centered, just below the text
            if st.button("Start your journey", key="start-journey-btn"):
                st.session_state.started = True
                st.rerun()
    st.stop()

with st.container():
    st.markdown('<div class="app-container">', unsafe_allow_html=True)
    st.markdown('<div class="hero"><h1>SwipeSense</h1><p>Discover destinations you\'ll love — tap ❤️ or skip ▶</p></div>', unsafe_allow_html=True)

    left, center, right = st.columns([1,5,1], gap="small")
    with center:
        if not st.session_state.images:
            st.info("No images to show right now. Come back soon!")
        else:
            idx = st.session_state.index % len(st.session_state.images)
            url = st.session_state.images[idx]

            st.markdown('<div class="image-card" style="position:relative;">', unsafe_allow_html=True)
            if idx in st.session_state.likes:
                st.markdown('<div class="like-badge">❤️ Liked</div>', unsafe_allow_html=True)
            show_image(url)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="caption">Photo {idx+1} of {len(st.session_state.images)}</div>', unsafe_allow_html=True)

            c1, c2, c3 = st.columns([1,1,1])
            with c1:
                like_clicked = st.button("❤️ Like", use_container_width=True)
            with c2:
                next_clicked = st.button("▶ Next", use_container_width=True)
            with c3:
                create_clicked = st.button("🗺️ Create Itinerary", type="primary", use_container_width=True)

            if like_clicked:
                if idx in st.session_state.likes:
                    st.session_state.likes.remove(idx)
                else:
                    st.session_state.likes.add(idx)
                st.rerun()

            if next_clicked:
                st.session_state.index = (st.session_state.index + 1) % len(st.session_state.images)
                st.rerun()

            if create_clicked:
                liked_urls = [st.session_state.images[i] for i in sorted(st.session_state.likes)]
                if not liked_urls:
                    st.warning("Like a few destinations first to personalise your itinerary ✨")
                else:
                    if HAS_BACKEND:
                        try:
                            df = pd.DataFrame({"image_url": liked_urls})
                            itinerary = generate_itinerary(df)
                            md = itinerary_to_markdown(itinerary)
                            st.markdown(md)
                        except Exception as e:
                            st.error(f"Backend error while creating itinerary: {e}")
                    else:
                        st.success("Itinerary created (placeholder)")
                        st.markdown("\n".join([f"- Stop {i+1}: {u[:60]}…" for i, u in enumerate(liked_urls)]))

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('---')
col1, col2, col3, col4 = st.columns(4)
col1.metric("Photos", len(st.session_state.images))
col2.metric("Liked", len(st.session_state.likes))
col3.button("⟲ Restart", on_click=lambda: (st.session_state.update({"index":0, "likes":set(), "started":False}),))
col4.write("")
