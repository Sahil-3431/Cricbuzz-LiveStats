import streamlit as st
import pandas as pd
from utils.api_client import get_live_matches
from utils.api_client import get_scorecard

st.set_page_config(
    page_title="Live Matches | Cricbuzz",
    page_icon="🏏",
    layout="wide"
)

st.title("🏏 Live Cricket Matches")
st.caption("Real-time cricket matches and detailed scorecards")

def extract_matches(data):
    """Extract matches from Cricbuzz live API response."""
    matches = []
    type_matches = data.get("typeMatches", [])
    for type_match in type_matches:
        series_matches = type_match.get("seriesMatches",[])
        for series_wrapper in series_matches:
            series_ad_wrapper = series_wrapper.get("seriesAdWrapper")
            if not series_ad_wrapper:
                continue
            series_name = series_ad_wrapper.get("seriesName","Unknown Series")
            for match_wrapper in series_ad_wrapper.get("matches",[]):
                match_info = match_wrapper.get("matchInfo",{})
                match_score = match_wrapper.get("matchScore",{})
                if match_info:
                    matches.append({
                        "match_info": match_info,
                        "match_score": match_score,
                        "series_name": series_name
                    })
    return matches

def get_team_name(team):
    """Return team name safely."""
    if not team:
        return "Unknown Team"
    return (
        team.get("teamName")
        or team.get("teamSName")
        or "Unknown Team"
    )

def get_score_value(score):
    """
    Extract runs, wickets and overs from a score object.
    Handles different Cricbuzz response formats.
    """
    if not isinstance(score, dict):
        return None
    runs = score.get("r")
    wickets = score.get("w")
    overs = score.get("o")
    if runs is None:
        runs = score.get("runs")
    if wickets is None:
        wickets = score.get("wickets")
    if overs is None:
        overs = score.get("overs")
    if runs is None:
        return None
    if wickets is None:
        wickets = 0
    if overs is None:
        overs = 0
    return {
        "runs": runs,
        "wickets": wickets,
        "overs": overs
    }

def get_latest_innings(team_score):
    """
    Find the latest innings from team score data.
    """
    if not isinstance(team_score, dict):
        return None

    innings_keys = [
        key
        for key in team_score.keys()
        if key.lower().startswith("inngs")
    ]
    if innings_keys:
        innings_keys.sort(key=lambda x: int(''.join(filter(str.isdigit, x)) or 0),reverse=True)
        for key in innings_keys:
            score = get_score_value(team_score.get(key))
            if score:
                return score
    return get_score_value(team_score)

def extract_team_scores(match_score):
    """
    Extract both team scores from the live response.
    """
    if not isinstance(match_score, dict):
        return None, None
    team1_score = None
    team2_score = None
    possible_team1_keys = ["team1Score","team1score","team1"]
    possible_team2_keys = ["team2Score","team2score","team2"]
    for key in possible_team1_keys:
        if key in match_score:
            team1_score = get_latest_innings(match_score[key])
            if team1_score:
                break
    for key in possible_team2_keys:
        if key in match_score:
            team2_score = get_latest_innings(match_score[key])
            if team2_score:
                break
    return team1_score, team2_score

def format_score(score):
    """Format score for Streamlit."""
    if not score:
        return "Score unavailable"
    return (
        f"{score['runs']}/"
        f"{score['wickets']} "
        f"({score['overs']} overs)"
    )

def display_scorecard(scorecard_data):
    """Display complete match scorecard."""
    scorecard = scorecard_data.get("scorecard",[])
    if not isinstance(scorecard, list):
        st.warning("Scorecard format is unavailable.")
        return
    if not scorecard:
        st.info("No innings data available for this match.")
        return
    for index, innings in enumerate(scorecard,start=1):
        innings_number = innings.get("inningsid",index)
        batting_team = innings.get("batteamname","Unknown Team")
        runs = innings.get("score",0)
        wickets = innings.get("wickets",0)
        overs = innings.get("overs",0)
        run_rate = innings.get("runrate","-")
        st.subheader(
            f"🏏 Innings {innings_number} — "
            f"{batting_team}"
        )
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Score",f"{runs}/{wickets}")
        with col2:
            st.metric("Overs",str(overs))
        with col3:
            st.metric("Run Rate",str(run_rate))
        batsmen = innings.get("batsman",[])
        if batsmen:
            st.markdown("#### 🏏 Batting")
            batting_rows = []
            for batsman in batsmen:
                batting_rows.append({
                    "Batsman": batsman.get("name","-"),
                    "Runs": batsman.get("runs",0),
                    "Balls": batsman.get("balls",0),
                    "4s": batsman.get("fours",0),
                    "6s": batsman.get("sixes",0),
                    "Strike Rate": batsman.get("strkrate",0),
                    "Dismissal": batsman.get("outdec","Not Out")
                })
            st.dataframe(
                pd.DataFrame(batting_rows),
                use_container_width=True,
                hide_index=True
            )
        bowlers = innings.get("bowler",[])
        if bowlers:
            st.markdown("#### 🎯 Bowling")
            bowling_rows = []
            for bowler in bowlers:
                bowling_rows.append({
                    "Bowler": bowler.get("name","-"),
                    "Overs": bowler.get("overs",0),
                    "Maidens": bowler.get("maidens",0),
                    "Runs": bowler.get("runs",0),
                    "Wickets": bowler.get("wickets",0),
                    "Economy": bowler.get("economy",0)
                })
            st.dataframe(
                pd.DataFrame(bowling_rows),
                use_container_width=True,
                hide_index=True
            )
        partnership_object = innings.get("partnership",{})
        partnership_list = partnership_object.get("partnership",[])
        if partnership_list:
            st.markdown("#### 🤝 Partnerships")
            partnership_rows = []
            for partnership in partnership_list:
                partnership_rows.append({
                    "Batsman 1": partnership.get("bat1name","-"),
                    "Batsman 1 Runs": partnership.get("bat1runs",0),
                    "Batsman 2": partnership.get("bat2name","-"),
                    "Batsman 2 Runs": partnership.get("bat2runs",0),
                    "Partnership Runs": partnership.get("totalruns",0),
                    "Partnership Balls": partnership.get("totalballs",0)
                })
            st.dataframe(
                pd.DataFrame(partnership_rows),
                use_container_width=True,
                hide_index=True
            )
        st.divider()

def main():
    """Main Live Matches application."""
    if st.button("🔄 Refresh Live Matches",type="primary"):
        st.rerun()
    try:
        with st.spinner("Fetching live matches..."):
            data = get_live_matches()
    except Exception as error:
        st.error(f"Unable to fetch live matches: {error}")
        return
    matches = extract_matches(data)
    if not matches:
        st.info("No matches are currently available.")
        return
    st.success(f"{len(matches)} match(es) found.")

    # ==========================================
    # MATCH OPTIONS
    # ==========================================

    match_options = {}

    for match in matches:
        match_info = match["match_info"]
        match_id = match_info.get("matchId")
        if not match_id:
            continue
        team1 = get_team_name(match_info.get("team1", {}))
        team2 = get_team_name(match_info.get("team2", {}))
        match_desc = match_info.get("matchDesc","Match")
        status = match_info.get("status",match_info.get("stateTitle","Unknown"))
        match_options[match_id] = (
            f"{team1} vs {team2} "
            f"— {match_desc} "
            f"({status})"
        )
    if not match_options:
        st.warning("No valid matches found.")
        return

    # ==========================================
    # PERSIST SELECTED MATCH
    # ==========================================

    match_ids = list(match_options.keys())

    # First time only:
    # select the first match by default.
    if "selected_match_id" not in st.session_state:
        st.session_state.selected_match_id = match_ids[0]

    # If selected match is no longer available
    # in the latest API response, select first match.
    if (
        st.session_state.selected_match_id
        not in match_ids
    ):
        st.session_state.selected_match_id = (match_ids[0])

    # ==========================================
    # MATCH DROPDOWN
    # ==========================================

    st.subheader("🏏 Select Match")
    selected_match_id = st.selectbox(
        "Choose a match:",
        options=match_ids,
        format_func=lambda match_id:
            match_options[match_id],
        key="selected_match_id"
    )

    # ==========================================
    # GET SELECTED MATCH
    # ==========================================

    selected_match = next(
        (
            match
            for match in matches
            if match["match_info"].get("matchId") == selected_match_id),
        None
    )
    if selected_match is None:
        st.error("Selected match could not be found.")
        return

    match_info = selected_match["match_info"]
    match_score = selected_match["match_score"]
    team1 = match_info.get("team1",{})
    team2 = match_info.get("team2",{})
    team1_name = get_team_name(team1)
    team2_name = get_team_name(team2)
    st.divider()
    st.header(f"{team1_name} vs {team2_name}")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Match",match_info.get("matchDesc","-"))
    with col2:
        st.metric("Format",match_info.get("matchFormat","-"))
    with col3:
        st.metric("Status",match_info.get("status",match_info.get("stateTitle","Unknown")))
    venue = match_info.get("venueInfo",{})
    venue_name = venue.get("ground","Venue unavailable")
    venue_city = venue.get("city","")
    venue_text = venue_name
    if venue_city:
        venue_text += f", {venue_city}"
    st.markdown(f"**📍 Venue:** {venue_text}")
    st.markdown(
        f"**🏆 Series:** "
        f"{selected_match['series_name']}"
    )
    st.divider()
    st.subheader("📊 Live Score")
    team1_live_score, team2_live_score = (extract_team_scores(match_score))
    score_col1, score_col2 = st.columns(2)
    with score_col1:
        st.markdown(f"### {team1_name}")
        st.metric("Current Score",format_score(team1_live_score))
    with score_col2:
        st.markdown(f"### {team2_name}")
        st.metric("Current Score",format_score(team2_live_score))
    st.divider()

    # ==========================================
    # DETAILED SCORECARD
    # ==========================================

    if st.button("📋 Load Detailed Scorecard",type="primary"):
        try:
            with st.spinner(
                f"Loading scorecard for "
                f"{team1_name} vs {team2_name}..."
            ):
                scorecard_data = get_scorecard(selected_match_id)
            st.success(
                f"Scorecard loaded for "
                f"{team1_name} vs {team2_name}"
            )
            display_scorecard(scorecard_data)
        except Exception as error:
            st.error(f"Unable to load scorecard: {error}")

if __name__ == "__main__":
    main()