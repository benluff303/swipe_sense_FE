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

MAX_IMAGES = 20

# Initialising session state
if "index" not in st.session_state:
    st.session_state.index = 0
if "responses" not in st.session_state:
    st.session_state.responses = []
if "num_days" not in st.session_state:
    st.session_state.num_days = None
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "current" not in st.session_state:
    st.session_state.current = None

user_id = st.text_input("User ID", value="default")

def fetch_next():
    r = requests.post(f"{API}/next", json={"user_id": user_id}).json()
    if r.get("status") == "end":
        st.warning("No more candidates. You may need to relax filters or restart the backend.")
        st.session_state.current = None
        return None
    st.session_state.current = r
    st.session_state.start_time = time.time()
    return r

if st.button("Start / Next"):
    fetch_next()
    st.rerun()

# Loop that displays images one at a time for next/like being clicked up to 20
if st.session_state.index > 0:
    st.progress(st.session_state.index / MAX_IMAGES)
    st.caption(f"{st.session_state.index}/{MAX_IMAGES} images reviewed")

if st.session_state.current:
    idx = st.session_state.current["idx"]
    img_resp = requests.get(f"{API}/image/{idx}")
    st.image(img_resp.content, caption=f"idx={idx} | sim={st.session_state.current.get('sim_score')}", use_column_width=True)

    # Record the current display start time
    st.session_state.start_time = time.time()

    col1, col2, col3 = st.columns(3)

    def handle_feedback(action: str):
        """Record response locally + send to backend."""
        dwell_time = time.time() - st.session_state.start_time
        st.session_state.responses.append({
            "idx": idx,
            "response": action,
            "dwell_time": dwell_time
        })
        requests.post(f"{API}/feedback", json={
            "user_id": user_id,
            "idx": idx,
            "action": action,
            "dwell": dwell_time
        })
        st.session_state.index += 1
        fetch_next()
        st.rerun()

    with col1:
        if st.button("Next"):
            handle_feedback("next")

    with col2:
        if st.button("Like"):
            handle_feedback("like")

# Once 20 complete use inputs how long their trip will be
elif st.session_state.num_days is None:
    st.write("Before we show your destinations...")
    days = st.slider("How many days will your trip be?", min_value=1, max_value=5, value=1)
    if st.button("Confirm trip length"):
        st.session_state.num_days = days
        st.rerun()

else:
    st.success("✅ Thank you for your input!")
    st.write("Your journey awaits...")

    if st.session_state.responses:
        SwipeSense_url = "https://api.com/endpoint"

        user = {"responses": st.session_state.responses, # This needs to go to file that finds keywords then locations that will go to the GPT itinerary and also be shown on this front end (as in code below)
                "num_days": st.session_state.num_days # This can go straight to GPT itinerary
        }

        try:
            response = requests.post(SwipeSense_url, json=user)
            response.raise_for_status()

            # API call succeeds
            data = response.json() if response and response.content else {}

            # Convert to DataFrame
            df = pd.DataFrame(data)

            # Show top locations
            if "location" in df.columns:
                df_top_cities = df[["location", "keywords"]].drop_duplicates().head(5)

                st.header("Top 5 destinations for you:")
                for i, row in df_top_cities.iterrows():
                    st.write(f"{i+1}. **{row['location']}**")

                # Generate itinerary for these top cities
                st.header("Your 5-day itinerary:")
                itinerary_result = generate_itinerary(df_top_cities)

                # Convert to pretty Markdown
                markdown_itinerary = itinerary_to_markdown(itinerary_result)
                st.markdown(markdown_itinerary)

            else:
                st.warning("No destinations returned. Try again later.")

        except Exception as e:
            st.error(f"Something went wrong while fetching predictions: {e}")

    if st.button("Restart"):
        st.session_state.index = 0
        st.session_state.responses = []
        st.session_state.num_days = None
        st.rerun()
