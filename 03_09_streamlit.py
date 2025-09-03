import streamlit as st
import requests
import time
import pandas as pd
from GPT_itinirary import generate_itinerary, itinerary_to_markdown  # Import GPT functions

# SwipeSense frontend

# Title of page
API = "http://127.0.0.1:8000"

st.set_page_config(page_title="SwipeSense", layout="wide")
st.title("SwipeSense")

MAX_IMAGES = 2

# Initialising session state
if "index" not in st.session_state:
    st.session_state.index = 0
if "responses" not in st.session_state:
    st.session_state.responses = []
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "current" not in st.session_state:
    st.session_state.current = None
if "user_id" not in st.session_state:
    st.session_state.user_id = "default"

user_id = st.text_input("User ID", value="default")

def fetch_next():
    r = requests.post(f"{API}/next", json={"user_id": st.session_state.user_id}).json()
    if r.get("status") == "end":
        st.warning("No more candidates. Restart to try again.")
        st.session_state.current = None
        return None
    st.session_state.current = r
    st.session_state.start_time = time.time()
    return r

# --- Start / Restart Button ---
if st.session_state.index == 0 and not st.session_state.responses:
    if st.button("Start"):
        fetch_next()
        st.rerun()
else:
    if st.button("Restart"):
        st.session_state.index = 0
        st.session_state.responses = []
        st.session_state.num_days = None
        st.session_state.current = None
        st.rerun()

# --- Main Swiping Logic ---
if st.session_state.current:
    # Progress bar
    progress = st.session_state.index / MAX_IMAGES
    st.progress(min(progress, 1.0))
    st.caption(f"{st.session_state.index}/{MAX_IMAGES} images reviewed")

    # Display image
    idx = st.session_state.current["idx"]
    img_resp = requests.get(f"{API}/image/{idx}")
    st.image(
        img_resp.content,
        caption=f"idx={idx} | sim={st.session_state.current.get('sim_score')}",
        use_container_width=True,
        output_format="JPEG"
    )

    def handle_feedback(action: str):
        """Record response locally + send to backend."""
        dwell_time = time.time() - st.session_state.start_time
        st.session_state.responses.append({
            "idx": idx,
            "response": action,
            "dwell_time": dwell_time
        })
        requests.post(f"{API}/feedback", json={
            "user_id": st.session_state.user_id,
            "idx": idx,
            "action": action,
            "dwell": dwell_time
        })
        st.session_state.index += 1
        if st.session_state.index < MAX_IMAGES:
            fetch_next()
        st.rerun()

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Next", use_container_width=True):
            handle_feedback("next")
    with col2:
        if st.button("Like", use_container_width=True):
            handle_feedback("like")

# --- Show itinerary after trip length confirmed ---
elif st.session_state.index >= MAX_IMAGES and st.session_state.responses:
    SwipeSense_url = "https://api.com/endpoint"
    user = {"responses": st.session_state.responses}

    try:
        response = requests.post(SwipeSense_url, json=user)
        response.raise_for_status()
        data = response.json() if response and response.content else {}

        df = pd.DataFrame(data)

        if "location" in df.columns:
            df_top_cities = df[["location", "keywords"]].drop_duplicates().head(5)

            st.header("Top 5 destinations for you:")
            for i, row in df_top_cities.iterrows():
                st.write(f"{i+1}. **{row['location']}**")

            # Generate itinerary
            st.header("Your itinerary:")
            itinerary_result = generate_itinerary(df_top_cities)
            markdown_itinerary = itinerary_to_markdown(itinerary_result)
            st.markdown(markdown_itinerary)

        else:
            st.warning("No destinations returned. Try again later.")

    except Exception as e:
        st.error(f"Something went wrong while fetching predictions: {e}")
