import streamlit as st
from utils.sidebar import render_sidebar

st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
render_sidebar()

# Default page
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "home"

current_page = st.session_state["current_page"]

# =========================================================
# HOME
# =========================================================

if current_page == "home":
    st.title("🏏 Cricbuzz LiveStats")
    st.subheader("Real-Time Cricket Insights & SQL-Based Analytics")
    st.markdown("""
    Welcome to **Cricbuzz LiveStats**.

    This application combines live cricket data from the Cricbuzz API
    with SQL-based analytics and a structured SQLite database.
    """)

    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Live Cricket","Real-Time")
    with col2:
        st.metric("Database","SQLite")
    with col3:
        st.metric("Analytics","25+ SQL Queries")

    st.divider()
    st.subheader("📌 Project Features")
    st.markdown("""
    ### 🏏 Live Matches
    View currently available live matches with:
    - Match status
    - Teams
    - Venue
    - Scorecard
    - Batting statistics
    - Bowling statistics
    - Partnerships

    ### 📊 Top Player Statistics
    Analyze player performance using batting and bowling data.

    ### 🗄️ SQL Analytics
    Run analytical SQL queries against the cricket database.

    ### ✏️ CRUD Operations
    Create, read, update, and delete selected database records.

    ---

    ### 👈 Use the sidebar

    Select **Live Matches** from the sidebar to view the current
    cricket matches.
    """)

    st.info("Start with the Live Matches page from the sidebar.")

# =========================================================
# LIVE MATCHES
# =========================================================

elif current_page == "live_matches":
    from views.live_matches import show_live_matches
    show_live_matches()

# =========================================================
# PLAYER STATISTICS
# =========================================================

elif current_page == "player_stats":
    from views.top_player_stats import show_player_stats
    show_player_stats()

# =========================================================
# SQL ANALYTICS
# =========================================================

elif current_page == "sql_analytics":
    from views.sql_analytics import show_sql_analytics
    show_sql_analytics()

# =========================================================
# CRUD
# =========================================================

elif current_page == "crud":
    from views.crud import show_crud
    show_crud()
