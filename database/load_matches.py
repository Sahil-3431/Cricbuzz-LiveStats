from utils.api_client import get_live_matches
from utils.db_connection import get_connection


def load_live_matches():
    data = get_live_matches()
    connection = get_connection()
    cursor = connection.cursor()
    match_count = 0
    for type_match in data.get("typeMatches", []):
        for series_match in type_match.get("seriesMatches", []):
            series_wrapper = series_match.get("seriesAdWrapper")
            if not series_wrapper:
                continue
            series_matches = series_wrapper.get("matches", [])
            for match in series_matches:
                match_info = match.get("matchInfo", {})

                # -------------------------
                # SERIES
                # -------------------------

                series_id = match_info.get("seriesId")
                series_name = match_info.get("seriesName")
                if series_id:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO series (
                            series_id,
                            series_name,
                            match_type,
                            start_date,
                            end_date
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            series_id,
                            series_name,
                            match_info.get("matchFormat"),
                            match_info.get("startDate"),
                            match_info.get("endDate")
                        )
                    )

                # -------------------------
                # TEAMS
                # -------------------------

                team1 = match_info.get("team1", {})
                team2 = match_info.get("team2", {})
                for team in [team1, team2]:
                    team_id = team.get("teamId")
                    if team_id:
                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO teams (
                                team_id,
                                team_name,
                                short_name
                            )
                            VALUES (?, ?, ?)
                            """,
                            (
                                team_id,
                                team.get("teamName"),
                                team.get("teamSName")
                            )
                        )

                # -------------------------
                # MATCH
                # -------------------------

                match_id = match_info.get("matchId")
                if match_id:
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO matches (
                            match_id,
                            series_id,
                            match_description,
                            match_format,
                            start_date,
                            end_date,
                            state,
                            status,
                            team1_id,
                            team2_id
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            match_id,
                            series_id,
                            match_info.get("matchDesc"),
                            match_info.get("matchFormat"),
                            match_info.get("startDate"),
                            match_info.get("endDate"),
                            match_info.get("state"),
                            match_info.get("status"),
                            team1.get("teamId"),
                            team2.get("teamId")
                        )
                    )
                    match_count += 1
    connection.commit()
    connection.close()
    return match_count

if __name__ == "__main__":
    count = load_live_matches()
    print(f"Successfully loaded {count} live matches.")