from openai import OpenAI
import pandas as pd
import json
import re

client = OpenAI(api_key="APIKEY")

def generate_itinerary(locations, keywords):
    """
    Generates a 5-day itinerary for the top city from a DataFrame in one GPT call.
    Returns a dict {city_name: {"df": DataFrame}}.
    """

    # Select first city from list of cities
    top_city = locations[0]["name"]

    # GPT prompt for ALL cities at once
    prompt = f"""
    Create a separate 5-day itinerary for the following city: {top_city}.
    Use these holiday preferences: {', '.join(keywords)}.

    Requirements:
    - Each day should have 3-4 activities with times (e.g., "09:00", "12:30").
    - Include the location for each activity.
    - Output MUST be structured JSON like this:

    {{
        "Day 1": [
            {{"time": "09:00", "activity": "...", "location": "{top_city}"}},
            {{"time": "12:30", "activity": "...", "location": "{top_city}"}},
            {{"time": "15:30", "activity": "...", "location": "{top_city}"}}
        ],
        "Day 2": [ ... ],
        "Day 3": [ ... ],
        "Day 4": [ ... ],
        "Day 5": [ ... ]
    }}
    """

    # One GPT call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a helpful travel planner."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract GPT content
    gpt_output = response.choices[0].message.content

    # Clean any markdown/code fences
    gpt_output_clean = re.sub(r"^```json\s*|\s*```$", "", gpt_output.strip(), flags=re.MULTILINE)

    try:
        itinerary_dict = json.loads(gpt_output_clean)
    except json.JSONDecodeError:
        return {"error": "Could not parse JSON", "raw_output": gpt_output_clean}

    # Convert JSON to DataFrame
    rows = []
    if isinstance(itinerary_dict, dict) and "error" not in itinerary_dict:
        for day, activities in itinerary_dict.items():
            for act in activities:
                rows.append({
                    "Day": day,
                    "Time": act.get("time", "??:??"),
                    "Activity": act.get("activity", ""),
                    "Location": act.get("location", top_city)
                })
    df_itinerary = pd.DataFrame(rows)

    return {top_city: {"df": df_itinerary}}

def itinerary_to_markdown(itinerary_dict: dict) -> str:
    """
    Convert the parsed itinerary dict (city -> df) into pretty Markdown.
    Each city gets its own section, each day its own sub-section.
    """
    lines = []

    for city, content in itinerary_dict.items():
        lines.append(f"### {city} ###\n")  # City title

        df = content.get("df")
        if df is None or df.empty:
            lines.append("_No itinerary available_\n")
            continue

        # Group by Day
        for day, day_df in df.groupby("Day"):
            lines.append(f"## {day}")
            # Iterate over rows
            for _, row in day_df.iterrows():
                time = row.get("Time", "??:??")
                activity = row.get("Activity", "")
                loc = row.get("Location", city)
                lines.append(f"- **{time}** — {activity} (_{loc}_)")
            lines.append("")  # blank line after each day

    return "\n".join(lines)
