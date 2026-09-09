import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from utils.api_client import (
    get_batting_rankings,
    get_bowling_rankings,
    get_player_profile,
    get_player_batting_stats,
    get_player_bowling_stats
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Top Player Stats",
    page_icon="🏆",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 17px;
        color: #666;
        margin-bottom: 20px;
    }
    .section-title {
        font-size: 25px;
        font-weight: 650;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    .player-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #ddd;
        margin-bottom: 15px;
    }
    .player-name {
        font-size: 25px;
        font-weight: 700;
    }
    .player-info {
        font-size: 16px;
        margin-top: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# HEADER
# =========================================================

st.markdown('<div class="main-title">🏆 Top Player Statistics</div>',unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">'
    'Explore live cricket rankings and detailed player '
    'career statistics using Cricbuzz API.'
    '</div>',
    unsafe_allow_html=True
)

# =========================================================
# REFRESH BUTTON
# =========================================================

refresh_col1, refresh_col2 = st.columns([6, 1])
with refresh_col2:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

st.divider()

# =========================================================
# FORMAT SELECTOR
# =========================================================

format_option = st.selectbox("🏏 Select Format",["ODI", "Test", "T20", "IPL"])
format_map = {
    "ODI": "odi",
    "Test": "test",
    "T20": "t20",
    "IPL": "ipl"
}
format_type = format_map[format_option]

# =========================================================
# FETCH RANKINGS
# =========================================================

try:
    with st.spinner(f"Loading {format_option} rankings..."):
        batting_data = get_batting_rankings(format_type)
        bowling_data = get_bowling_rankings(format_type)
        batting_players = batting_data.get("rank",[])
        bowling_players = bowling_data.get("rank",[])

except Exception:
    st.error("❌ Unable to load player rankings.")
    st.info(
        "Please check your internet connection "
        "and RapidAPI configuration."
    )
    st.stop()

# =========================================================
# TOP PLAYER CARDS
# =========================================================

st.markdown(
    '<div class="section-title">'
    '🌟 Top Ranked Players'
    '</div>',
    unsafe_allow_html=True
)
col1, col2, col3, col4 = st.columns(4)

# ---------------------------------------------------------
# Top Batter
# ---------------------------------------------------------

if batting_players:
    top_batter = batting_players[0]
    with col1:
        st.metric(
            "🥇 Top Batter",
            top_batter.get("name","N/A"),
            f"Rating {top_batter.get('rating', 'N/A')}"
        )

# ---------------------------------------------------------
# Top Bowler
# ---------------------------------------------------------

if bowling_players:
    top_bowler = bowling_players[0]
    with col2:
        st.metric(
            "🎯 Top Bowler",
            top_bowler.get("name","N/A"),
            f"Rating {top_bowler.get('rating', 'N/A')}"
        )

# ---------------------------------------------------------
# Number of Batters
# ---------------------------------------------------------

with col3:
    st.metric("🏏 Batters Listed",len(batting_players))

# ---------------------------------------------------------
# Number of Bowlers
# ---------------------------------------------------------

with col4:
    st.metric("🎯 Bowlers Listed",len(bowling_players))

st.divider()

# =========================================================
# RANKINGS TABS
# =========================================================

bat_tab, bowl_tab = st.tabs(["🏏 Batting Rankings","🎯 Bowling Rankings"])

# =========================================================
# BATTING RANKINGS
# =========================================================

with bat_tab:
    st.subheader(f"Top Batters — {format_option}")
    if batting_players:
        batting_rows = []
        for player in batting_players:
            trend = player.get("trend","N/A")
            if trend.lower() == "up":
                trend_display = "⬆️ Up"
            elif trend.lower() == "down":
                trend_display = "⬇️ Down"
            else:
                trend_display = "➡️ Flat"
            batting_rows.append({
                "Rank":player.get("rank", "N/A"),
                "Player":player.get("name", "N/A"),
                "Country":player.get("country", "N/A"),
                "Rating":player.get("rating", "N/A"),
                "Points":player.get("points", "N/A"),
                "Trend":trend_display,
                "Updated":player.get("lastUpdatedOn","N/A")
            })
        batting_df = pd.DataFrame(batting_rows)
        st.dataframe(batting_df,use_container_width=True,hide_index=True)
    else:
        st.warning("No batting rankings available.")

# =========================================================
# BOWLING RANKINGS
# =========================================================

with bowl_tab:
    st.subheader(f"Top Bowlers — {format_option}")
    if bowling_players:
        bowling_rows = []
        for player in bowling_players:
            trend = player.get("trend","N/A")
            if trend.lower() == "up":
                trend_display = "⬆️ Up"
            elif trend.lower() == "down":
                trend_display = "⬇️ Down"
            else:
                trend_display = "➡️ Flat"
            bowling_rows.append({
                "Rank":player.get("rank", "N/A"),
                "Player":player.get("name", "N/A"),
                "Country":player.get("country", "N/A"),
                "Rating":player.get("rating", "N/A"),
                "Points":player.get("points", "N/A"),
                "Trend":trend_display,
                "Updated":player.get("lastUpdatedOn","N/A")
            })
        bowling_df = pd.DataFrame(bowling_rows)
        st.dataframe(bowling_df,use_container_width=True,hide_index=True)
    else:
        st.warning("No bowling rankings available.")

# =========================================================
# PLAYER DETAILS
# =========================================================

st.divider()
st.markdown(
    '<div class="section-title">'
    '🔎 Player Details'
    '</div>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Combine ranking players
# ---------------------------------------------------------

all_players = {}
for player in batting_players:
    player_id = str(player.get("id"))
    all_players[player_id] = {
        "id": player_id,
        "name": player.get("name","Unknown"),
        "country": player.get("country","Unknown")
    }
for player in bowling_players:
    player_id = str(player.get("id"))
    if player_id not in all_players:
        all_players[player_id] = {
            "id": player_id,
            "name": player.get("name","Unknown"),
            "country": player.get("country","Unknown")
        }

player_list = list(all_players.values())
if not player_list:
    st.warning("No players available.")
    st.stop()

player_options = {
    f"{player['name']} — "
    f"{player['country']}":
        player["id"]
    for player in player_list
}
selected_player_name = st.selectbox("Select Player",list(player_options.keys()))
selected_player_id = player_options[selected_player_name]

# =========================================================
# LOAD PLAYER DETAILS
# =========================================================

try:
    with st.spinner("Loading player profile..."):
        profile = get_player_profile(selected_player_id)
        batting_stats = (get_player_batting_stats(selected_player_id))
        bowling_stats = (get_player_bowling_stats(selected_player_id))

except Exception:
    st.error("❌ Unable to load player details.")
    st.info("Please try selecting another player.")
    st.stop()

# =========================================================
# PLAYER IMAGE LOADER
# =========================================================

def load_player_image(image_url, player_id):

    # -----------------------------------------------------
    # 1. Try Cricbuzz image
    # -----------------------------------------------------

    urls = []
    if image_url:
        urls.append(image_url)
        if image_url.startswith("http://"):
            urls.append(
                image_url.replace("http://","https://",1))
    if player_id:
        urls.append(
            f"https://i.cricketcb.com/"
            f"stats/img/faceImages/{player_id}.jpg"
        )
    for url in urls:
        try:
            response = requests.get(url,headers={"User-Agent": "Mozilla/5.0"},timeout=5)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type","").lower()

            if (
                "image" in content_type
                or response.content.startswith(b"\xff\xd8\xff")
                or response.content.startswith(b"\x89PNG")
            ):
                return BytesIO(response.content)
        except Exception:
            continue
    return None

# =========================================================
# LOCAL PLAYER IMAGE
# =========================================================

def get_local_player_image(player_id):
    from pathlib import Path
    base_dir = Path(__file__).resolve().parent.parent
    image_folder = (
        base_dir
        / "assets"
        / "players"
    )
    extensions = [".jpg",".jpeg",".png",".webp"]
    for extension in extensions:
        image_path = (image_folder / f"{player_id}{extension}")
        if image_path.exists():
            return str(image_path)
    return None

# =========================================================
# DEFAULT PLAYER AVATAR
# =========================================================

def show_default_avatar():
    st.markdown(
        """
        <div style="
            width:180px;
            height:180px;
            border-radius:12px;
            border:1px solid #444;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:80px;
            background:#1f2937;
        ">
            👤
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# PLAYER PROFILE
# =========================================================

profile_col1, profile_col2 = st.columns([1, 3])

# ---------------------------------------------------------
# Player Image
# ---------------------------------------------------------

with profile_col1:
    image_url = profile.get("image")
    player_id = str(
        profile.get("id",selected_player_id))

    # -----------------------------------------------------
    # Try external Cricbuzz image
    # -----------------------------------------------------

    image_data = load_player_image(image_url,player_id)
    if image_data:
        st.image(image_data,width=180)
    else:

        # -------------------------------------------------
        # Try local image
        # -------------------------------------------------

        local_image = get_local_player_image(player_id)
        if local_image:
            st.image(local_image,width=180)
        else:

            # ---------------------------------------------
            # Final fallback
            # ---------------------------------------------

            show_default_avatar()

# ---------------------------------------------------------
# Player Information
# ---------------------------------------------------------

with profile_col2:
    st.markdown(f"### {profile.get('name', 'N/A')}")
    st.write(
        f"**Role:** "
        f"{profile.get('role', 'N/A')}"
    )
    st.write(
        f"**International Team:** "
        f"{profile.get('intlTeam', 'N/A')}"
    )
    st.write(
        f"**Batting Style:** "
        f"{profile.get('bat', 'N/A')}"
    )
    st.write(
        f"**Bowling Style:** "
        f"{profile.get('bowl', 'N/A')}"
    )
    st.write(
        f"**Birth Place:** "
        f"{profile.get('birthPlace', 'N/A')}"
    )

# =========================================================
# STATISTICS CONVERTER
# =========================================================

def stats_to_dataframe(data):
    headers = data.get("headers",[])
    values = data.get("values",[])
    if len(headers) < 2:
        return pd.DataFrame()
    formats = headers[1:]
    rows = []
    for row in values:
        row_values = row.get("values",[])
        if not row_values:
            continue
        statistic = row_values[0]
        row_data = {"Statistic": statistic}
        for index, format_name in enumerate(formats):
            value_index = index + 1
            if value_index < len(row_values):
                row_data[format_name] = row_values[value_index]
            else:
                row_data[format_name] = "-"
        rows.append(row_data)
    return pd.DataFrame(rows)

# =========================================================
# STATISTICS TABS
# =========================================================

st.divider()
bat_stats_tab, bowl_stats_tab = st.tabs(["🏏 Batting Statistics","🎯 Bowling Statistics"])

# =========================================================
# BATTING STATISTICS
# =========================================================

with bat_stats_tab:
    st.subheader("🏏 Career Batting Statistics")
    batting_df = stats_to_dataframe(batting_stats)
    if not batting_df.empty:
        st.dataframe(batting_df,use_container_width=True,hide_index=True)
    else:
        st.info("No batting statistics available.")

# =========================================================
# BOWLING STATISTICS
# =========================================================

with bowl_stats_tab:
    st.subheader("🎯 Career Bowling Statistics")
    bowling_df = stats_to_dataframe(bowling_stats)
    if not bowling_df.empty:
        st.dataframe(bowling_df,use_container_width=True,hide_index=True)
    else:
        st.info("No bowling statistics available.")

# =========================================================
# KEY STATISTICS
# =========================================================

st.divider()
st.markdown(
    '<div class="section-title">'
    f'📊 {format_option} Key Statistics'
    '</div>',
    unsafe_allow_html=True
)

def get_stat_value(data,statistic,format_name):
    headers = data.get("headers",[])
    values = data.get("values",[])
    if format_name not in headers:
        return "N/A"
    format_index = headers.index(format_name)
    for row in values:
        row_values = row.get("values",[])
        if (row_values and row_values[0] == statistic):
            if format_index < len(row_values):
                return row_values[format_index]
    return "N/A"

# ---------------------------------------------------------
# Key batting statistics
# ---------------------------------------------------------

key1, key2, key3, key4 = st.columns(4)

key1.metric("Matches",get_stat_value(batting_stats,"Matches",format_option))
key2.metric("Runs",get_stat_value(batting_stats,"Runs",format_option))
key3.metric("Highest Score",get_stat_value(batting_stats,"Highest",format_option))
key4.metric("Batting Average",get_stat_value(batting_stats,"Average",format_option))

# =========================================================
# EXTRA BATTING STATS
# =========================================================

extra1, extra2, extra3, extra4 = st.columns(4)

extra1.metric("Strike Rate",get_stat_value(batting_stats,"SR",format_option))
extra2.metric("Fours",get_stat_value(batting_stats,"Fours",format_option))
extra3.metric("Sixes",get_stat_value(batting_stats,"Sixes",format_option))
extra4.metric("100s",get_stat_value(batting_stats,"100s",format_option))

# =========================================================
# FOOTER
# =========================================================

st.divider()
st.caption(
    "📡 Data source: Cricbuzz API • "
    f"Format: {format_option}"
)