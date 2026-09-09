import streamlit as st
import pandas as pd

from utils.db_connection import get_connection

def show_crud():
    # ============================================================
    # DATABASE HELPERS
    # ============================================================

    def execute_query(query, params=(), fetch=False):
        connection = get_connection()

        try:
            cursor = connection.cursor()
            cursor.execute(query, params)

            if fetch:
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            connection.commit()
            return True
        except Exception as error:
            connection.rollback()
            raise error
        finally:
            connection.close()

    def get_players():
        return execute_query(
            """
            SELECT
                player_id,
                player_name,
                role,
                batting_style,
                bowling_style,
                country
            FROM players
            ORDER BY player_name
            """,
            fetch=True
        )

    def get_teams():
        return execute_query(
            """
            SELECT
                team_id,
                team_name,
                short_name
            FROM teams
            ORDER BY team_name
            """,
            fetch=True
        )

    def get_matches():
        return execute_query(
            """
            SELECT
                m.match_id,
                m.match_description,
                m.match_format,
                m.start_date,
                m.end_date,
                m.state,
                m.status,
                t1.team_name AS team1,
                t2.team_name AS team2
            FROM matches m
            LEFT JOIN teams t1
                ON m.team1_id = t1.team_id
            LEFT JOIN teams t2
                ON m.team2_id = t2.team_id
            ORDER BY m.start_date DESC
            """,
            fetch=True
        )

    # ============================================================
    # HEADER
    # ============================================================

    st.title("🛠️ CRUD Operations")
    st.markdown("Create, Read, Update and Delete records from the Cricbuzz database.")
    st.divider()

    # ============================================================
    # CRUD TABS
    # ============================================================

    tab_create, tab_read, tab_update, tab_delete = st.tabs(
        [
            "🟢 Create",
            "🔵 Read",
            "🟡 Update",
            "🔴 Delete"
        ]
    )

    # ============================================================
    # CREATE
    # ============================================================

    with tab_create:
        st.subheader("➕ Create New Record")
        create_type = st.selectbox("Select record type",["Player","Team"],key="create_type")

        # --------------------------------------------------------
        # CREATE PLAYER
        # --------------------------------------------------------

        if create_type == "Player":
            st.markdown("### 👤 Add Player")
            col1, col2 = st.columns(2)
            with col1:
                player_id = st.number_input(
                    "Player ID",
                    min_value=1,
                    step=1,
                    key="create_player_id"
                )
                player_name = st.text_input("Player Name",key="create_player_name")
                role = st.selectbox(
                    "Role",
                    ["Batsman","Bowler","All-rounder","Wicket-keeper"],
                    key="create_player_role"
                )
            with col2:
                batting_style = st.text_input("Batting Style",key="create_batting_style")
                bowling_style = st.text_input("Bowling Style",key="create_bowling_style")
                country = st.text_input("Country",key="create_country")
            if st.button("➕ Add Player",type="primary",use_container_width=True):
                if not player_name.strip():
                    st.error("Player name is required.")
                else:
                    try:
                        execute_query(
                            """
                            INSERT INTO players (
                                player_id,
                                player_name,
                                role,
                                batting_style,
                                bowling_style,
                                country
                            )
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (
                                player_id,
                                player_name.strip(),
                                role,
                                batting_style.strip() or None,
                                bowling_style.strip() or None,
                                country.strip() or None
                            )
                        )
                        st.success(f"Player '{player_name}' added successfully.")
                    except Exception as error:
                        st.error(f"Could not add player: {error}")

        # --------------------------------------------------------
        # CREATE TEAM
        # --------------------------------------------------------

        elif create_type == "Team":
            st.markdown("### 🏏 Add Team")
            col1, col2 = st.columns(2)
            with col1:
                team_id = st.number_input(
                    "Team ID",
                    min_value=1,
                    step=1,
                    key="create_team_id"
                )
            with col2:
                team_name = st.text_input("Team Name",key="create_team_name")
            short_name = st.text_input(
                "Short Name",
                max_chars=10,
                key="create_team_short_name"
            )
            if st.button("➕ Add Team",type="primary",use_container_width=True):
                if not team_name.strip():
                    st.error("Team name is required.")
                else:
                    try:
                        execute_query(
                            """
                            INSERT INTO teams (
                                team_id,
                                team_name,
                                short_name
                            )
                            VALUES (?, ?, ?)
                            """,
                            (
                                team_id,
                                team_name.strip(),
                                short_name.strip() or None
                            )
                        )
                        st.success(f"Team '{team_name}' added successfully.")
                    except Exception as error:
                        st.error(f"Could not add team: {error}")

    # ============================================================
    # READ
    # ============================================================

    with tab_read:
        st.subheader("📋 View Database Records")
        read_type = st.selectbox(
            "Select table",
            [
                "Players",
                "Teams",
                "Matches",
                "Batting Scorecard",
                "Bowling Scorecard",
                "Partnerships"
            ],
            key="read_type"
        )
        if read_type == "Players":
            rows = get_players()
            if rows:
                st.dataframe(
                    pd.DataFrame(rows),
                    use_container_width=True,
                    hide_index=True
                )
                st.caption(f"Total players: {len(rows)}")
            else:
                st.info("No players found.")

        elif read_type == "Teams":
            rows = get_teams()
            if rows:
                st.dataframe(
                    pd.DataFrame(rows),
                    use_container_width=True,
                    hide_index=True
                )
                st.caption(f"Total teams: {len(rows)}")
            else:
                st.info("No teams found.")

        elif read_type == "Matches":
            rows = get_matches()

            if rows:
                st.dataframe(
                    pd.DataFrame(rows),
                    use_container_width=True,
                    hide_index=True
                )
                st.caption(f"Total matches: {len(rows)}")
            else:
                st.info("No matches found.")

        elif read_type == "Batting Scorecard":
            rows = execute_query(
                """
                SELECT
                    b.batting_id,
                    b.match_id,
                    p.player_name,
                    b.innings_number,
                    b.batting_position,
                    b.runs,
                    b.balls,
                    b.fours,
                    b.sixes,
                    b.strike_rate
                FROM batting_scorecard b
                JOIN players p
                    ON b.player_id = p.player_id
                ORDER BY b.match_id, b.innings_number, b.batting_position
                """,
                fetch=True
            )
            if rows:
                st.dataframe(
                    pd.DataFrame(rows),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No batting records found.")

        elif read_type == "Bowling Scorecard":
            rows = execute_query(
                """
                SELECT
                    b.bowling_id,
                    b.match_id,
                    p.player_name,
                    b.innings_number,
                    b.overs,
                    b.maidens,
                    b.runs_conceded,
                    b.wickets,
                    b.economy_rate
                FROM bowling_scorecard b
                JOIN players p
                    ON b.player_id = p.player_id
                ORDER BY b.match_id, b.innings_number
                """,
                fetch=True
            )
            if rows:
                st.dataframe(
                    pd.DataFrame(rows),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No bowling records found.")
        elif read_type == "Partnerships":
            rows = execute_query(
                """
                SELECT
                    partnership_id,
                    match_id,
                    innings_number,
                    batsman1_name,
                    batsman2_name,
                    batsman1_runs,
                    batsman2_runs,
                    partnership_runs,
                    partnership_balls
                FROM partnerships
                ORDER BY match_id, innings_number, partnership_id
                """,
                fetch=True
            )
            if rows:
                st.dataframe(
                    pd.DataFrame(rows),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No partnership records found.")

    # ============================================================
    # UPDATE
    # ============================================================

    with tab_update:
        st.subheader("✏️ Update Existing Record")
        update_type = st.selectbox("Select record type",["Player","Team"],key="update_type")

        # --------------------------------------------------------
        # UPDATE PLAYER
        # --------------------------------------------------------

        if update_type == "Player":
            players = get_players()

            if not players:
                st.info("No players available.")
            else:
                player_options = {
                    f"{p['player_name']} ({p['player_id']})":
                        p["player_id"]
                    for p in players
                }

                selected_player = st.selectbox(
                    "Select Player",
                    list(player_options.keys()),
                    key="update_player_select"
                )
                selected_player_id = player_options[selected_player]

                current_player = next(
                    p for p in players
                    if p["player_id"] == selected_player_id
                )
                st.markdown("### Current Details")
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input(
                        "Player Name",
                        value=current_player["player_name"] or "",
                        key="update_player_name"
                    )
                    role_options = ["Batsman","Bowler","All-rounder","Wicket-keeper"]
                    current_role = current_player["role"]
                    if current_role not in role_options:
                        current_role = "Batsman"

                    new_role = st.selectbox(
                        "Role",
                        role_options,
                        index=role_options.index(current_role),
                        key="update_player_role"
                    )
                with col2:
                    new_batting_style = st.text_input(
                        "Batting Style",
                        value=current_player["batting_style"] or "",
                        key="update_player_batting"
                    )
                    new_bowling_style = st.text_input(
                        "Bowling Style",
                        value=current_player["bowling_style"] or "",
                        key="update_player_bowling"
                    )
                    new_country = st.text_input(
                        "Country",
                        value=current_player["country"] or "",
                        key="update_player_country"
                    )
                if st.button("💾 Update Player",type="primary",use_container_width=True):
                    if not new_name.strip():
                        st.error("Player name cannot be empty.")
                    else:
                        try:
                            execute_query(
                                """
                                UPDATE players
                                SET
                                    player_name = ?,
                                    role = ?,
                                    batting_style = ?,
                                    bowling_style = ?,
                                    country = ?
                                WHERE player_id = ?
                                """,
                                (
                                    new_name.strip(),
                                    new_role,
                                    new_batting_style.strip() or None,
                                    new_bowling_style.strip() or None,
                                    new_country.strip() or None,
                                    selected_player_id
                                )
                            )
                            st.success(f"Player '{new_name}' updated successfully.")
                        except Exception as error:
                            st.error(f"Could not update player: {error}")

        # --------------------------------------------------------
        # UPDATE TEAM
        # --------------------------------------------------------

        elif update_type == "Team":
            teams = get_teams()

            if not teams:
                st.info("No teams available.")
            else:
                team_options = {
                    f"{t['team_name']} ({t['team_id']})":
                        t["team_id"]
                    for t in teams
                }

                selected_team = st.selectbox(
                    "Select Team",
                    list(team_options.keys()),
                    key="update_team_select"
                )
                selected_team_id = team_options[selected_team]

                current_team = next(
                    t for t in teams
                    if t["team_id"] == selected_team_id
                )
                new_team_name = st.text_input(
                    "Team Name",
                    value=current_team["team_name"] or "",
                    key="update_team_name"
                )
                new_short_name = st.text_input(
                    "Short Name",
                    value=current_team["short_name"] or "",
                    max_chars=10,
                    key="update_team_short_name"
                )
                if st.button("💾 Update Team",type="primary",use_container_width=True):
                    if not new_team_name.strip():
                        st.error("Team name cannot be empty.")
                    else:
                        try:
                            execute_query(
                                """
                                UPDATE teams
                                SET
                                    team_name = ?,
                                    short_name = ?
                                WHERE team_id = ?
                                """,
                                (
                                    new_team_name.strip(),
                                    new_short_name.strip() or None,
                                    selected_team_id
                                )
                            )
                            st.success(f"Team '{new_team_name}' updated successfully.")
                        except Exception as error:
                            st.error(f"Could not update team: {error}")

    # ============================================================
    # DELETE
    # ============================================================

    with tab_delete:
        st.subheader("🗑️ Delete Record")
        st.warning(
            "⚠️ Delete operations can fail when the record is referenced "
            "by other tables because foreign-key protection is enabled."
        )
        delete_type = st.selectbox("Select record type",["Player","Team"],key="delete_type")

        # --------------------------------------------------------
        # DELETE PLAYER
        # --------------------------------------------------------

        if delete_type == "Player":
            players = get_players()

            if not players:
                st.info("No players available.")

            else:
                player_options = {
                    f"{p['player_name']} ({p['player_id']})":
                        p["player_id"]
                    for p in players
                }
                selected_player = st.selectbox(
                    "Select Player to Delete",
                    list(player_options.keys()),
                    key="delete_player_select"
                )
                selected_player_id = player_options[selected_player]

                confirm = st.checkbox(
                    "I understand that this may affect related records.",
                    key="delete_player_confirm"
                )
                if st.button(
                    "🗑️ Delete Player",
                    type="secondary",
                    disabled=not confirm,
                    use_container_width=True
                ):
                    try:
                        execute_query(
                            """
                            DELETE FROM players
                            WHERE player_id = ?
                            """,
                            (selected_player_id,)
                        )
                        st.success(f"Player '{selected_player}' deleted successfully.")
                    except Exception as error:
                        st.error(
                            "Player could not be deleted. "
                            "The player may be referenced by scorecards "
                            f"or other tables.\n\nDetails: {error}"
                        )

        # --------------------------------------------------------
        # DELETE TEAM
        # --------------------------------------------------------

        elif delete_type == "Team":
            teams = get_teams()

            if not teams:
                st.info("No teams available.")

            else:
                team_options = {
                    f"{t['team_name']} ({t['team_id']})":
                        t["team_id"]
                    for t in teams
                }

                selected_team = st.selectbox(
                    "Select Team to Delete",
                    list(team_options.keys()),
                    key="delete_team_select"
                )

                selected_team_id = team_options[selected_team]

                confirm = st.checkbox(
                    "I understand that this may affect matches and related records.",
                    key="delete_team_confirm"
                )

                if st.button(
                    "🗑️ Delete Team",
                    type="secondary",
                    disabled=not confirm,
                    use_container_width=True
                ):
                    try:
                        execute_query(
                            """
                            DELETE FROM teams
                            WHERE team_id = ?
                            """,
                            (selected_team_id,)
                        )
                        st.success(f"Team '{selected_team}' deleted successfully.")

                    except Exception as error:
                        st.error(
                            "Team could not be deleted because it may be "
                            f"referenced by matches or other tables.\n\nDetails: {error}"
                        )


    # ============================================================
    # FOOTER
    # ============================================================

    st.divider()
    st.caption("Cricbuzz LiveStats • SQLite CRUD Interface")