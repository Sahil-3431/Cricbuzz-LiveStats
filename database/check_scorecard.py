from utils.db_connection import get_connection

def main():
    connection = get_connection()
    cursor = connection.cursor()
    print("\n=== PLAYERS ===")
    cursor.execute("""
        SELECT
            player_id,
            player_name,
            role
        FROM players
        ORDER BY player_name
    """)
    for row in cursor.fetchall():
        print(
            row["player_id"],
            row["player_name"],
            row["role"]
        )
    print("\n=== BATTING SCORECARD ===")
    cursor.execute("""
        SELECT
            b.innings_number,
            p.player_name,
            b.runs,
            b.balls,
            b.fours,
            b.sixes,
            b.strike_rate
        FROM batting_scorecard b
        JOIN players p
            ON b.player_id = p.player_id
        ORDER BY
            b.innings_number,
            b.batting_position
    """)
    for row in cursor.fetchall():
        print(
            f"Innings {row['innings_number']} | "
            f"{row['player_name']} | "
            f"{row['runs']} runs | "
            f"{row['balls']} balls | "
            f"{row['fours']} fours | "
            f"{row['sixes']} sixes | "
            f"SR {row['strike_rate']}"
        )
    print("\n=== BOWLING SCORECARD ===")
    cursor.execute("""
        SELECT
            b.innings_number,
            p.player_name,
            b.overs,
            b.maidens,
            b.runs_conceded,
            b.wickets,
            b.economy_rate
        FROM bowling_scorecard b
        JOIN players p
            ON b.player_id = p.player_id
        ORDER BY
            b.innings_number,
            b.bowling_id
    """)
    for row in cursor.fetchall():
        print(
            f"Innings {row['innings_number']} | "
            f"{row['player_name']} | "
            f"{row['overs']} overs | "
            f"{row['maidens']} maidens | "
            f"{row['runs_conceded']} runs | "
            f"{row['wickets']} wickets | "
            f"Econ {row['economy_rate']}"
        )
    connection.close()

if __name__ == "__main__":
    main()