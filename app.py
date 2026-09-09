import streamlit as st

st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide"
)

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