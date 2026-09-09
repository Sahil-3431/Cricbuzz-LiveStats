import streamlit as st
from utils.api_client import get_live_matches
from utils.db_connection import get_connection

@st.cache_data(ttl=300)
def check_api_status():
    try:
        get_live_matches()
        return True
    except Exception:
        return False

def load_sidebar_css():
    st.markdown(
        """
        <style>

        /* ================================
           SIDEBAR
        ================================= */

        [data-testid="stSidebar"] {
            background: linear-gradient(
                180deg,
                #0f172a 0%,
                #111827 100%
            );
        }
        [data-testid="stSidebar"] * {
            color: #f8fafc;
        }

        /* ================================
           BRAND
        ================================= */

        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 4px 12px 4px;
        }
        .sidebar-logo {
            font-size: 38px;
        }
        .sidebar-title {
            font-size: 24px;
            font-weight: 800;
        }
        .sidebar-subtitle {
            font-size: 14px;
            opacity: 0.75;
        }

        /* ================================
           DIVIDER
        ================================= */

        [data-testid="stSidebar"] hr {
            margin: 10px 0;
            border-color: rgba(255,255,255,0.15);
        }

        /* ================================
           BUTTONS
        ================================= */

        [data-testid="stSidebar"] .stButton > button {
            width: 100%;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.12);
            background: rgba(255,255,255,0.05);
            transition: all 0.2s ease;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255,255,255,0.12);
            border-color: rgba(255,255,255,0.25);
        }

        /* ================================
           LINKS
        ================================= */

        [data-testid="stSidebar"] a {
            text-decoration: none !important;
        }

        /* ================================
           CAPTION
        ================================= */

        [data-testid="stSidebar"] .stCaption {
            opacity: 0.65;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_sidebar():
    load_sidebar_css()
    with st.sidebar:
        # =========================================
        # BRAND
        # =========================================
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-logo">🏏</div>
                <div>
                    <div class="sidebar-title">
                        Cricbuzz
                    </div>
                    <div class="sidebar-subtitle">
                        LiveStats
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.divider()
        st.markdown("### 🧭 Navigation")
        if st.button("🏠 Home", use_container_width=True):
            st.session_state["current_page"] = "home"
        if st.button("🔴 Live Matches", use_container_width=True):
            st.session_state["current_page"] = "live_matches"
        if st.button("🏆 Player Statistics", use_container_width=True):
            st.session_state["current_page"] = "player_stats"
        if st.button("📊 SQL Analytics", use_container_width=True):
            st.session_state["current_page"] = "sql_analytics"
        if st.button("✏️ CRUD Operations", use_container_width=True):
            st.session_state["current_page"] = "crud"

        st.divider()
        st.markdown("### 🎯 Global Filters")
        st.selectbox(
            "🏏 Format",
            ["ODI", "Test", "T20", "IPL"],
            key="global_format"
        )
        st.selectbox(
            "📅 Season",
            ["2026", "2025", "2024", "2023"],
            key="global_season"
        )
        st.selectbox(
            "🇮🇳 Team",
            [
                "All Teams",
                "India",
                "Australia",
                "England",
                "South Africa",
                "New Zealand"
            ],
            key="global_team"
        )
        st.divider()
        st.markdown("### ⚙️ Settings")
        st.slider(
            "📊 Rows per Table",
            5,
            50,
            10,
            5,
            key="global_rows_per_page"
        )
        st.toggle("🔄 Auto Refresh",key="global_auto_refresh")
        if st.button("🔄 Refresh Application",use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        # =========================================
        # STATUS
        # =========================================

        st.markdown("### 📡 System Status")

        if check_api_status():
            st.success("🟢 API Online")
        else:
            st.error("🔴 API Offline")

        try:
            conn = get_connection()
            conn.close()
            st.success("🟢 Database Online")
        except Exception:
            st.error("🔴 Database Error")

        # =========================================
        # ABOUT
        # =========================================

        with st.expander("ℹ️ About Project"):
            st.markdown(
                """
                **Cricbuzz LiveStats**

                Cricket analytics dashboard built with:

                🐍 Python  
                🎈 Streamlit  
                🗄️ SQLite  
                📊 Pandas  
                🌐 Cricbuzz API

                **Modules**

                🏏 Live Matches  
                🏆 Player Statistics  
                📊 SQL Analytics  
                ✏️ CRUD Operations
                """
            )
        st.divider()
        github_url = "https://github.com/Sahil-3431/Cricbuzz-LiveStats"
        st.link_button(
            "⭐ View Project on GitHub",
            github_url,
            use_container_width=True
        )
        st.divider()
        st.markdown(
            """
            <div style="text-align:center;">
                <div style="font-size:22px;">
                    👨‍💻
                </div>
                <div style="font-weight:700;">
                    SAHIL KHAN
                </div>
                <div style="font-size:12px; opacity:0.7;">
                    Cricbuzz LiveStats
                </div>
                <div style="font-size:11px; opacity:0.6;">
                    Built with ❤️ using Streamlit
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )