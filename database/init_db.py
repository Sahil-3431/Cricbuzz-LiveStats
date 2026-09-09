from utils.db_connection import get_connection

def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    # ---------------------------------
    # SERIES TABLE
    # ---------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS series (
            series_id INTEGER PRIMARY KEY,
            series_name TEXT NOT NULL,
            match_type TEXT,
            start_date TEXT,
            end_date TEXT
        )
    """)

    # ---------------------------------
    # TEAMS TABLE
    # ---------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            team_id INTEGER PRIMARY KEY,
            team_name TEXT NOT NULL,
            short_name TEXT
        )
    """)

    # ---------------------------------
    # VENUES TABLE
    # ---------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS venues (
            venue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            venue_name TEXT,
            city TEXT,
            country TEXT,
            capacity INTEGER
        )
    """)

    # ---------------------------------
    # MATCHES TABLE
    # ---------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            match_id INTEGER PRIMARY KEY,
            series_id INTEGER,
            match_description TEXT,
            match_format TEXT,
            start_date TEXT,
            end_date TEXT,
            state TEXT,
            status TEXT,
            team1_id INTEGER,
            team2_id INTEGER,
            venue_id INTEGER,

            FOREIGN KEY (series_id)
                REFERENCES series(series_id),

            FOREIGN KEY (team1_id)
                REFERENCES teams(team_id),

            FOREIGN KEY (team2_id)
                REFERENCES teams(team_id),

            FOREIGN KEY (venue_id)
                REFERENCES venues(venue_id)
        )
    """)

    # ---------------------------------
    # PLAYERS TABLE
    # ---------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY,
            player_name TEXT NOT NULL,
            role TEXT,
            batting_style TEXT,
            bowling_style TEXT,
            country TEXT
        )
    """)

    # ---------------------------------
    # MATCH PLAYERS TABLE
    # ---------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS match_players (
            match_id INTEGER,
            player_id INTEGER,
            team_id INTEGER,

            PRIMARY KEY (
                match_id,
                player_id
            ),

            FOREIGN KEY (match_id)
                REFERENCES matches(match_id),

            FOREIGN KEY (player_id)
                REFERENCES players(player_id),

            FOREIGN KEY (team_id)
                REFERENCES teams(team_id)
        )
    """)

    # ---------------------------------
    # BATTING SCORECARD TABLE
    # ---------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS batting_scorecard (
            batting_id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            player_id INTEGER,
            innings_number INTEGER,
            batting_position INTEGER,
            runs INTEGER DEFAULT 0,
            balls INTEGER DEFAULT 0,
            fours INTEGER DEFAULT 0,
            sixes INTEGER DEFAULT 0,
            strike_rate REAL,

            FOREIGN KEY (match_id)
                REFERENCES matches(match_id),

            FOREIGN KEY (player_id)
                REFERENCES players(player_id)
        )
    """)

    # ---------------------------------
    # BOWLING SCORECARD TABLE
    # ---------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bowling_scorecard (
            bowling_id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            player_id INTEGER,
            innings_number INTEGER,
            overs REAL DEFAULT 0,
            maidens INTEGER DEFAULT 0,
            runs_conceded INTEGER DEFAULT 0,
            wickets INTEGER DEFAULT 0,
            economy_rate REAL,

            FOREIGN KEY (match_id)
                REFERENCES matches(match_id),

            FOREIGN KEY (player_id)
                REFERENCES players(player_id)
        )
    """)

    # ---------------------------------
    # PARTNERSHIPS TABLE
    # ---------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS partnerships (
            partnership_id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            innings_number INTEGER NOT NULL,
            batsman1_id INTEGER,
            batsman1_name TEXT,
            batsman2_id INTEGER,
            batsman2_name TEXT,
            batsman1_runs INTEGER,
            batsman1_balls INTEGER,
            batsman2_runs INTEGER,
            batsman2_balls INTEGER,
            partnership_runs INTEGER,
            partnership_balls INTEGER,
            FOREIGN KEY (match_id) REFERENCES matches(match_id),
            FOREIGN KEY (batsman1_id) REFERENCES players(player_id),
            FOREIGN KEY (batsman2_id) REFERENCES players(player_id)
        )
    """)

    # ---------------------------------
    # MATCH RESULT TABLE
    # ---------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS match_results (
            match_id INTEGER PRIMARY KEY,
            winning_team_id INTEGER,
            victory_margin INTEGER,
            victory_type TEXT,
            toss_winner_id INTEGER,
            toss_decision TEXT,

            FOREIGN KEY (match_id)
                REFERENCES matches(match_id),

            FOREIGN KEY (winning_team_id)
                REFERENCES teams(team_id),

            FOREIGN KEY (toss_winner_id)
                REFERENCES teams(team_id)
        )
    """)
    connection.commit()
    connection.close()
    print("Database and tables created successfully!")

if __name__ == "__main__":
    create_tables()