# streamlit_app.py
# Minimal Streamlit client that talks to the FastAPI backend.

import requests
import streamlit as st
import time
# import numpy as np
import pandas as pd
from GPT_itinirary import generate_itinerary, itinerary_to_markdown

# API = st.secrets.get("API_URL", "http://localhost:8000")  # set in .streamlit/secrets.toml optionally

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="SwipeSense", layout="wide")
st.title("SwipeSense — Streamlit UI")

# User id
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
        st.image(img_resp.content, caption=f"idx={idx} | sim={st.session_state.current.get('sim_score')}", use_column_width=True)
    else:
        st.info("Press **Start / Next** to begin.")

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
    # api_response = {
    #     "locations": [
    #         {"rank": 1, "name": "Québec City"},
    #         {"rank": 2, "name": "Seoul"},
    #         {"rank": 3, "name": "London"},
    #         {"rank": 4, "name": "Toronto"},
    #         {"rank": 5, "name": "Clacton"}
    #     ],
    #     "phrases": [
    #         "beach holiday",
    #         "mountain escape"
    #         "beach holiday",
    #         "mountain escape",
    #         "mountain escape"
    #     ]
    # }

    # locations = api_response['locations']
    # phrases = api_response['phrases']

    # Generate itinerary
    api_response = requests.get(f"{API}/user_profile/{user_id}").json()
    st.header("Your itinerary:")
    itinerary_result = generate_itinerary(api_response)
    markdown_itinerary = itinerary_to_markdown(itinerary_result)
    st.markdown(markdown_itinerary)
