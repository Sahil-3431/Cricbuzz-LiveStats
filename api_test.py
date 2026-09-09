import requests
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏"
)

st.title("🏏 Cricbuzz LiveStats - Match Data")

# -----------------------------
# API CONFIGURATION
# -----------------------------

API_KEY = st.secrets["RAPIDAPI_KEY"]
API_HOST = st.secrets["RAPIDAPI_HOST"]

url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}


# -----------------------------
# API REQUEST
# -----------------------------

try:

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    st.write("Status Code:", response.status_code)

    if response.status_code == 200:

        data = response.json()

        st.success("API Connected Successfully!")

        # -----------------------------
        # EXTRACT MATCHES
        # -----------------------------

        matches = []

        for type_match in data.get("typeMatches", []):

            for series_match in type_match.get("seriesMatches", []):

                series_wrapper = series_match.get(
                    "seriesAdWrapper"
                )

                if not series_wrapper:
                    continue

                series_matches = series_wrapper.get(
                    "matches", []
                )

                for match in series_matches:

                    match_info = match.get(
                        "matchInfo", {}
                    )

                    team1 = match_info.get(
                        "team1", {}
                    )

                    team2 = match_info.get(
                        "team2", {}
                    )

                    match_record = {

                        "match_id":
                            match_info.get("matchId"),

                        "series_id":
                            match_info.get("seriesId"),

                        "series_name":
                            match_info.get("seriesName"),

                        "match_description":
                            match_info.get("matchDesc"),

                        "match_format":
                            match_info.get("matchFormat"),

                        "start_date":
                            match_info.get("startDate"),

                        "end_date":
                            match_info.get("endDate"),

                        "state":
                            match_info.get("state"),

                        "status":
                            match_info.get("status"),

                        "team1_id":
                            team1.get("teamId"),

                        "team1_name":
                            team1.get("teamName"),

                        "team1_short_name":
                            team1.get("teamSName"),

                        "team2_id":
                            team2.get("teamId"),

                        "team2_name":
                            team2.get("teamName"),

                        "team2_short_name":
                            team2.get("teamSName")
                    }

                    matches.append(match_record)


        # -----------------------------
        # CREATE DATAFRAME
        # -----------------------------

        df = pd.DataFrame(matches)

        st.subheader("📊 Match Data")

        st.write(
            "Number of matches:",
            len(df)
        )

        if not df.empty:

            st.dataframe(
                df,
                use_container_width=True
            )

            # -----------------------------
            # SHOW COLUMNS
            # -----------------------------

            st.subheader("📋 DataFrame Columns")

            st.write(
                list(df.columns)
            )

        else:

            st.warning(
                "No live matches found."
            )

    else:

        st.error(
            "API request failed."
        )

        st.write(
            "Status Code:",
            response.status_code
        )

        st.code(response.text)

except requests.exceptions.RequestException as e:

    st.error("Request Error")

    st.exception(e)