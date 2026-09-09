import streamlit as st
import pandas as pd

from utils.db_connection import get_connection

def show_sql_analytics():
    # =========================================================
    # SQL QUESTIONS
    # =========================================================

    QUERIES = {

        # =====================================================
        # QUESTION 1
        # =====================================================

        "Q1 — Indian Players": """
            SELECT
                player_name AS "Player Name",
                role AS "Role",
                batting_style AS "Batting Style",
                bowling_style AS "Bowling Style"
            FROM players
            WHERE country = 'India'
            ORDER BY player_name;
        """,

        # =====================================================
        # QUESTION 2
        # =====================================================

        "Q2 — Matches in Last 30 Days": """
            SELECT
                m.match_description AS "Match",
                t1.team_name AS "Team 1",
                t2.team_name AS "Team 2",
                v.venue_name AS "Venue",
                v.city AS "City",
                date(m.start_date) AS "Match Date"
            FROM matches m
            LEFT JOIN teams t1
                ON m.team1_id = t1.team_id
            LEFT JOIN teams t2
                ON m.team2_id = t2.team_id
            LEFT JOIN venues v
                ON m.venue_id = v.venue_id
            WHERE date(m.start_date)
                >= date('now', '-30 days')
            ORDER BY date(m.start_date) DESC;
        """,

        # =====================================================
        # QUESTION 3
        # =====================================================

        "Q3 — Top 10 ODI Run Scorers": """
            SELECT
                p.player_name AS "Player",
                SUM(b.runs) AS "Total Runs",
                ROUND(
                    CAST(SUM(b.runs) AS REAL)
                    / NULLIF(
                        COUNT(
                            DISTINCT
                            CASE
                                WHEN b.runs IS NOT NULL
                                THEN b.match_id
                            END
                        ),
                        0
                    ),
                    2
                ) AS "Average Runs per Match",
                SUM(
                    CASE
                        WHEN b.runs >= 100 THEN 1
                        ELSE 0
                    END
                ) AS "Centuries"
            FROM batting_scorecard b
            JOIN players p
                ON b.player_id = p.player_id
            JOIN matches m
                ON b.match_id = m.match_id
            WHERE UPPER(m.match_format) = 'ODI'
            GROUP BY p.player_id, p.player_name
            ORDER BY SUM(b.runs) DESC
            LIMIT 10;
        """,

        # =====================================================
        # QUESTION 4
        # =====================================================

        "Q4 — Large Capacity Venues": """
            SELECT
                venue_name AS "Venue",
                city AS "City",
                country AS "Country",
                capacity AS "Capacity"
            FROM venues
            WHERE capacity > 50000
            ORDER BY capacity DESC;
        """,

        # =====================================================
        # QUESTION 5
        # =====================================================

        "Q5 — Team Wins": """
            SELECT
                t.team_name AS "Team",
                COUNT(mr.match_id) AS "Total Wins"
            FROM teams t
            JOIN match_results mr
                ON t.team_id = mr.winning_team_id
            GROUP BY t.team_id, t.team_name
            ORDER BY COUNT(mr.match_id) DESC;
        """,

        # =====================================================
        # QUESTION 6
        # =====================================================

        "Q6 — Players by Role": """
            SELECT
                COALESCE(role, 'Unknown') AS "Role",
                COUNT(*) AS "Player Count"
            FROM players
            GROUP BY role
            ORDER BY COUNT(*) DESC;
        """,

        # =====================================================
        # QUESTION 7
        # =====================================================

        "Q7 — Highest Individual Score by Format": """
            SELECT
                m.match_format AS "Format",
                MAX(b.runs) AS "Highest Score"
            FROM batting_scorecard b
            JOIN matches m
                ON b.match_id = m.match_id
            WHERE m.match_format IS NOT NULL
            GROUP BY m.match_format
            ORDER BY MAX(b.runs) DESC;
        """,

        # =====================================================
        # QUESTION 8
        # =====================================================

        "Q8 — Series Started in 2024": """
            SELECT
                s.series_name AS "Series",
                s.match_type AS "Match Type",
                s.start_date AS "Start Date",
                s.end_date AS "End Date",
                COUNT(m.match_id) AS "Matches in Database"
            FROM series s
            LEFT JOIN matches m
                ON s.series_id = m.series_id
            WHERE strftime('%Y', s.start_date) = '2024'
            GROUP BY
                s.series_id,
                s.series_name,
                s.match_type,
                s.start_date,
                s.end_date
            ORDER BY s.start_date;
        """,

        # =====================================================
        # QUESTION 9
        # =====================================================

        "Q9 — All-rounders with 1000+ Runs and 50+ Wickets": """
            WITH batting AS (
                SELECT
                    player_id,
                    SUM(runs) AS total_runs
                FROM batting_scorecard
                GROUP BY player_id
            ),
            bowling AS (
                SELECT
                    player_id,
                    SUM(wickets) AS total_wickets
                FROM bowling_scorecard
                GROUP BY player_id
            )
            SELECT
                p.player_name AS "Player",
                b.total_runs AS "Total Runs",
                bw.total_wickets AS "Total Wickets",
                p.role AS "Role"
            FROM players p
            JOIN batting b
                ON p.player_id = b.player_id
            JOIN bowling bw
                ON p.player_id = bw.player_id
            WHERE LOWER(COALESCE(p.role, ''))
                LIKE '%all%'
            AND b.total_runs > 1000
            AND bw.total_wickets > 50
            ORDER BY b.total_runs DESC;
        """,

        # =====================================================
        # QUESTION 10
        # =====================================================

        "Q10 — Last 20 Completed Matches": """
            SELECT
                m.match_description AS "Match",
                t1.team_name AS "Team 1",
                t2.team_name AS "Team 2",
                wt.team_name AS "Winner",
                mr.victory_margin AS "Victory Margin",
                mr.victory_type AS "Victory Type",
                v.venue_name AS "Venue",
                date(m.start_date) AS "Date"
            FROM matches m
            LEFT JOIN teams t1
                ON m.team1_id = t1.team_id
            LEFT JOIN teams t2
                ON m.team2_id = t2.team_id
            LEFT JOIN match_results mr
                ON m.match_id = mr.match_id
            LEFT JOIN teams wt
                ON mr.winning_team_id = wt.team_id
            LEFT JOIN venues v
                ON m.venue_id = v.venue_id
            WHERE LOWER(COALESCE(m.state, ''))
                LIKE '%complete%'
            OR LOWER(COALESCE(m.status, ''))
                LIKE '%won%'
            OR mr.match_id IS NOT NULL
            ORDER BY date(m.start_date) DESC
            LIMIT 20;
        """,

        # =====================================================
        # QUESTION 11
        # =====================================================

        "Q11 — Player Performance Across Formats": """
            WITH format_runs AS (
                SELECT
                    p.player_id,
                    p.player_name,
                    m.match_format,
                    SUM(b.runs) AS total_runs
                FROM players p
                JOIN batting_scorecard b
                    ON p.player_id = b.player_id
                JOIN matches m
                    ON b.match_id = m.match_id
                GROUP BY
                    p.player_id,
                    p.player_name,
                    m.match_format
            ),
            format_count AS (
                SELECT
                    player_id,
                    COUNT(DISTINCT match_format) AS formats_played
                FROM format_runs
                GROUP BY player_id
            )
            SELECT
                fr.player_name AS "Player",
                MAX(
                    CASE
                        WHEN UPPER(fr.match_format) = 'TEST'
                        THEN fr.total_runs
                    END
                ) AS "Test Runs",
                MAX(
                    CASE
                        WHEN UPPER(fr.match_format) = 'ODI'
                        THEN fr.total_runs
                    END
                ) AS "ODI Runs",
                MAX(
                    CASE
                        WHEN UPPER(fr.match_format) IN ('T20', 'T20I')
                        THEN fr.total_runs
                    END
                ) AS "T20 Runs",
                ROUND(
                    SUM(fr.total_runs) * 1.0
                    / NULLIF(fc.formats_played, 0),
                    2
                ) AS "Average Across Formats"
            FROM format_runs fr
            JOIN format_count fc
                ON fr.player_id = fc.player_id
            WHERE fc.formats_played >= 2
            GROUP BY
                fr.player_id,
                fr.player_name,
                fc.formats_played
            ORDER BY fr.player_name;
        """,

        # =====================================================
        # QUESTION 12
        # =====================================================

        "Q12 — Home vs Away Wins": """
            WITH team_matches AS (

                SELECT
                    m.match_id,
                    m.team1_id AS team_id,
                    m.venue_id,
                    mr.winning_team_id
                FROM matches m
                LEFT JOIN match_results mr
                    ON m.match_id = mr.match_id

                UNION ALL

                SELECT
                    m.match_id,
                    m.team2_id AS team_id,
                    m.venue_id,
                    mr.winning_team_id
                FROM matches m
                LEFT JOIN match_results mr
                    ON m.match_id = mr.match_id
            )

            SELECT
                t.team_name AS "Team",
                CASE
                    WHEN LOWER(v.country)
                        = LOWER(t.team_name)
                    THEN 'Home'
                    ELSE 'Away'
                END AS "Condition",
                COUNT(
                    CASE
                        WHEN tm.winning_team_id = tm.team_id
                        THEN 1
                    END
                ) AS "Wins"
            FROM team_matches tm
            JOIN teams t
                ON tm.team_id = t.team_id
            LEFT JOIN venues v
                ON tm.venue_id = v.venue_id
            GROUP BY
                t.team_name,
                CASE
                    WHEN LOWER(v.country)
                        = LOWER(t.team_name)
                    THEN 'Home'
                    ELSE 'Away'
                END
            ORDER BY t.team_name;
        """,

        # =====================================================
        # QUESTION 13
        # =====================================================

        "Q13 — 100+ Run Consecutive Partnerships": """
            WITH batting AS (
                SELECT
                    b.match_id,
                    b.innings_number,
                    b.player_id,
                    b.batting_position,
                    b.runs,
                    p.player_name
                FROM batting_scorecard b
                JOIN players p
                    ON b.player_id = p.player_id
            )
            SELECT
                a.player_name AS "Batsman 1",
                c.player_name AS "Batsman 2",
                a.runs + c.runs AS "Combined Runs",
                a.match_id AS "Match ID",
                a.innings_number AS "Innings"
            FROM batting a
            JOIN batting c
                ON a.match_id = c.match_id
            AND a.innings_number = c.innings_number
            AND c.batting_position = a.batting_position + 1
            WHERE a.runs + c.runs >= 100
            ORDER BY "Combined Runs" DESC;
        """,

        # =====================================================
        # QUESTION 14
        # =====================================================

        "Q14 — Bowling Performance by Venue": """
            WITH bowler_matches AS (
                SELECT
                    bs.player_id,
                    bs.match_id,
                    m.venue_id,
                    bs.overs,
                    bs.wickets,
                    bs.economy_rate
                FROM bowling_scorecard bs
                JOIN matches m
                    ON bs.match_id = m.match_id
                WHERE CAST(bs.overs AS REAL) >= 4
            )
            SELECT
                p.player_name AS "Bowler",
                v.venue_name AS "Venue",
                COUNT(DISTINCT bm.match_id) AS "Matches",
                ROUND(
                    AVG(
                        CAST(bm.economy_rate AS REAL)
                    ),
                    2
                ) AS "Average Economy",
                SUM(bm.wickets) AS "Total Wickets"
            FROM bowler_matches bm
            JOIN players p
                ON bm.player_id = p.player_id
            JOIN venues v
                ON bm.venue_id = v.venue_id
            GROUP BY
                bm.player_id,
                bm.venue_id
            HAVING COUNT(DISTINCT bm.match_id) >= 3
            ORDER BY
                "Average Economy" ASC;
        """,

        # =====================================================
        # QUESTION 15
        # =====================================================

        "Q15 — Players in Close Matches": """
            SELECT
                p.player_name AS "Player",
                ROUND(
                    AVG(b.runs),
                    2
                ) AS "Average Runs",
                COUNT(DISTINCT b.match_id)
                    AS "Close Matches",
                COUNT(
                    DISTINCT CASE
                        WHEN mr.winning_team_id =
                            mp.team_id
                        THEN b.match_id
                    END
                ) AS "Team Wins"
            FROM batting_scorecard b
            JOIN players p
                ON b.player_id = p.player_id
            JOIN match_players mp
                ON b.match_id = mp.match_id
            AND b.player_id = mp.player_id
            JOIN match_results mr
                ON b.match_id = mr.match_id
            WHERE
                (
                    LOWER(COALESCE(mr.victory_type, ''))
                    LIKE '%run%'
                    AND CAST(mr.victory_margin AS REAL) < 50
                )
                OR
                (
                    LOWER(COALESCE(mr.victory_type, ''))
                    LIKE '%wicket%'
                    AND CAST(mr.victory_margin AS REAL) < 5
                )
            GROUP BY
                p.player_id,
                p.player_name
            ORDER BY "Average Runs" DESC;
        """,

        # =====================================================
        # QUESTION 16
        # =====================================================

        "Q16 — Yearly Batting Performance Since 2020": """
            SELECT
                p.player_name AS "Player",
                strftime(
                    '%Y',
                    m.start_date
                ) AS "Year",
                COUNT(DISTINCT b.match_id)
                    AS "Matches",
                ROUND(
                    AVG(b.runs),
                    2
                ) AS "Average Runs",
                ROUND(
                    AVG(
                        CAST(b.strike_rate AS REAL)
                    ),
                    2
                ) AS "Average Strike Rate"
            FROM batting_scorecard b
            JOIN players p
                ON b.player_id = p.player_id
            JOIN matches m
                ON b.match_id = m.match_id
            WHERE CAST(
                strftime('%Y', m.start_date)
                AS INTEGER
            ) >= 2020
            GROUP BY
                p.player_id,
                p.player_name,
                strftime('%Y', m.start_date)
            HAVING COUNT(DISTINCT b.match_id) >= 5
            ORDER BY
                "Year",
                "Average Runs" DESC;
        """,

        # =====================================================
        # QUESTION 17
        # =====================================================

        "Q17 — Toss Advantage": """
            SELECT
                mr.toss_decision AS "Toss Decision",
                COUNT(*) AS "Matches",
                SUM(
                    CASE
                        WHEN mr.toss_winner_id =
                            mr.winning_team_id
                        THEN 1
                        ELSE 0
                    END
                ) AS "Toss Winner Wins",
                ROUND(
                    100.0 *
                    SUM(
                        CASE
                            WHEN mr.toss_winner_id =
                                mr.winning_team_id
                            THEN 1
                            ELSE 0
                        END
                    ) / COUNT(*),
                    2
                ) AS "Win Percentage"
            FROM match_results mr
            WHERE mr.toss_winner_id IS NOT NULL
            AND mr.winning_team_id IS NOT NULL
            GROUP BY mr.toss_decision
            ORDER BY "Win Percentage" DESC;
        """,

        # =====================================================
        # QUESTION 18
        # =====================================================

        "Q18 — Most Economical Bowlers": """
            SELECT
                p.player_name AS "Bowler",
                COUNT(DISTINCT b.match_id)
                    AS "Matches",
                ROUND(
                    SUM(
                        CAST(b.runs_conceded AS REAL)
                    ) * 6.0
                    / NULLIF(
                        SUM(
                            CAST(b.overs AS REAL)
                        ) * 6,
                        0
                    ),
                    2
                ) AS "Overall Economy",
                SUM(b.wickets) AS "Total Wickets",
                ROUND(
                    AVG(
                        CAST(b.overs AS REAL)
                    ),
                    2
                ) AS "Average Overs"
            FROM bowling_scorecard b
            JOIN players p
                ON b.player_id = p.player_id
            JOIN matches m
                ON b.match_id = m.match_id
            WHERE UPPER(m.match_format)
                IN ('ODI', 'T20', 'T20I')
            GROUP BY
                p.player_id,
                p.player_name
            HAVING COUNT(DISTINCT b.match_id) >= 10
            AND AVG(
                CAST(b.overs AS REAL)
            ) >= 2
            ORDER BY "Overall Economy" ASC;
        """,

        # =====================================================
        # QUESTION 19
        # =====================================================

        "Q19 — Most Consistent Batsmen": """
            WITH player_stats AS (
                SELECT
                    b.player_id,
                    p.player_name,
                    AVG(b.runs) AS avg_runs,
                    AVG(
                        b.runs * b.runs
                    ) AS avg_square_runs,
                    COUNT(DISTINCT b.match_id)
                        AS matches_played
                FROM batting_scorecard b
                JOIN players p
                    ON b.player_id = p.player_id
                JOIN matches m
                    ON b.match_id = m.match_id
                WHERE CAST(
                    strftime('%Y', m.start_date)
                    AS INTEGER
                ) >= 2022
                AND CAST(b.balls AS REAL) >= 10
                GROUP BY
                    b.player_id,
                    p.player_name
                HAVING COUNT(DISTINCT b.match_id) >= 1
            )
            SELECT
                player_name AS "Player",
                matches_played AS "Matches",
                ROUND(avg_runs, 2)
                    AS "Average Runs",
                ROUND(
                    sqrt(
                        MAX(
                            avg_square_runs
                            - avg_runs * avg_runs,
                            0
                        )
                    ),
                    2
                ) AS "Standard Deviation"
            FROM player_stats
            ORDER BY "Standard Deviation" ASC;
        """,

        # =====================================================
        # QUESTION 20
        # =====================================================

        "Q20 — Matches and Average by Format": """
            SELECT
                p.player_name AS "Player",

                COUNT(
                    DISTINCT CASE
                        WHEN UPPER(m.match_format) = 'TEST'
                        THEN b.match_id
                    END
                ) AS "Test Matches",

                ROUND(
                    AVG(
                        CASE
                            WHEN UPPER(m.match_format) = 'TEST'
                            THEN b.runs
                        END
                    ),
                    2
                ) AS "Test Batting Average",

                COUNT(
                    DISTINCT CASE
                        WHEN UPPER(m.match_format) = 'ODI'
                        THEN b.match_id
                    END
                ) AS "ODI Matches",

                ROUND(
                    AVG(
                        CASE
                            WHEN UPPER(m.match_format) = 'ODI'
                            THEN b.runs
                        END
                    ),
                    2
                ) AS "ODI Batting Average",

                COUNT(
                    DISTINCT CASE
                        WHEN UPPER(m.match_format)
                            IN ('T20', 'T20I')
                        THEN b.match_id
                    END
                ) AS "T20 Matches",

                ROUND(
                    AVG(
                        CASE
                            WHEN UPPER(m.match_format)
                                IN ('T20', 'T20I')
                            THEN b.runs
                        END
                    ),
                    2
                ) AS "T20 Batting Average",

                COUNT(DISTINCT b.match_id)
                    AS "Total Matches"

            FROM players p
            JOIN batting_scorecard b
                ON p.player_id = b.player_id
            JOIN matches m
                ON b.match_id = m.match_id

            GROUP BY
                p.player_id,
                p.player_name

            HAVING COUNT(DISTINCT b.match_id) >= 20

            ORDER BY "Total Matches" DESC;
        """,

        # =====================================================
        # QUESTION 21
        # =====================================================

        "Q21 — Comprehensive Player Ranking": """
            WITH batting AS (
                SELECT
                    player_id,
                    SUM(runs) AS runs_scored,
                    AVG(runs) AS batting_average,
                    AVG(strike_rate) AS strike_rate
                FROM batting_scorecard
                GROUP BY player_id
            ),
            bowling AS (
                SELECT
                    player_id,
                    SUM(wickets) AS wickets_taken,
                    AVG(
                        CASE
                            WHEN wickets > 0
                            THEN runs_conceded * 1.0
                                / wickets
                            ELSE NULL
                        END
                    ) AS bowling_average,
                    AVG(economy_rate) AS economy_rate
                FROM bowling_scorecard
                GROUP BY player_id
            )
            SELECT
                p.player_name AS "Player",

                ROUND(
                    COALESCE(b.runs_scored, 0) * 0.01
                    +
                    COALESCE(b.batting_average, 0) * 0.5
                    +
                    COALESCE(b.strike_rate, 0) * 0.3,
                    2
                ) AS "Batting Points",

                ROUND(
                    COALESCE(bw.wickets_taken, 0) * 2
                    +
                    (
                        50 -
                        COALESCE(
                            bw.bowling_average,
                            50
                        )
                    ) * 0.5
                    +
                    (
                        6 -
                        COALESCE(
                            bw.economy_rate,
                            6
                        )
                    ) * 2,
                    2
                ) AS "Bowling Points",

                ROUND(
                    (
                        COALESCE(b.runs_scored, 0) * 0.01
                        +
                        COALESCE(b.batting_average, 0)
                        * 0.5
                        +
                        COALESCE(b.strike_rate, 0)
                        * 0.3
                    )
                    +
                    (
                        COALESCE(bw.wickets_taken, 0) * 2
                        +
                        (
                            50 -
                            COALESCE(
                                bw.bowling_average,
                                50
                            )
                        ) * 0.5
                        +
                        (
                            6 -
                            COALESCE(
                                bw.economy_rate,
                                6
                            )
                        ) * 2
                    ),
                    2
                ) AS "Overall Score"

            FROM players p
            LEFT JOIN batting b
                ON p.player_id = b.player_id
            LEFT JOIN bowling bw
                ON p.player_id = bw.player_id

            WHERE b.player_id IS NOT NULL
            OR bw.player_id IS NOT NULL

            ORDER BY "Overall Score" DESC;
        """,

        # =====================================================
        # QUESTION 22
        # =====================================================

        "Q22 — Team Head-to-Head": """
            WITH pair_results AS (
                SELECT
                    CASE
                        WHEN m.team1_id < m.team2_id
                        THEN m.team1_id
                        ELSE m.team2_id
                    END AS team_a_id,

                    CASE
                        WHEN m.team1_id < m.team2_id
                        THEN m.team2_id
                        ELSE m.team1_id
                    END AS team_b_id,

                    m.match_id,
                    m.venue_id,
                    mr.winning_team_id,
                    mr.victory_margin,
                    mr.toss_decision

                FROM matches m
                JOIN match_results mr
                    ON m.match_id = mr.match_id

                WHERE date(m.start_date)
                    >= date('now', '-3 years')
            )

            SELECT
                ta.team_name AS "Team A",
                tb.team_name AS "Team B",
                COUNT(*) AS "Matches",

                SUM(
                    CASE
                        WHEN pr.winning_team_id =
                            pr.team_a_id
                        THEN 1
                        ELSE 0
                    END
                ) AS "Team A Wins",

                SUM(
                    CASE
                        WHEN pr.winning_team_id =
                            pr.team_b_id
                        THEN 1
                        ELSE 0
                    END
                ) AS "Team B Wins",

                ROUND(
                    100.0 *
                    SUM(
                        CASE
                            WHEN pr.winning_team_id =
                                pr.team_a_id
                            THEN 1
                            ELSE 0
                        END
                    ) / COUNT(*),
                    2
                ) AS "Team A Win %",

                ROUND(
                    100.0 *
                    SUM(
                        CASE
                            WHEN pr.winning_team_id =
                                pr.team_b_id
                            THEN 1
                            ELSE 0
                        END
                    ) / COUNT(*),
                    2
                ) AS "Team B Win %"

            FROM pair_results pr
            JOIN teams ta
                ON pr.team_a_id = ta.team_id
            JOIN teams tb
                ON pr.team_b_id = tb.team_id

            GROUP BY
                pr.team_a_id,
                pr.team_b_id

            HAVING COUNT(*) >= 5

            ORDER BY COUNT(*) DESC;
        """,


        # =====================================================
        # QUESTION 23
        # =====================================================

        "Q23 — Recent Player Form": """
            WITH ranked AS (
                SELECT
                    b.player_id,
                    p.player_name,
                    b.match_id,
                    b.runs,
                    b.strike_rate,
                    m.start_date,

                    ROW_NUMBER() OVER (
                        PARTITION BY b.player_id
                        ORDER BY
                            date(m.start_date) DESC,
                            b.match_id DESC
                    ) AS rn

                FROM batting_scorecard b
                JOIN players p
                    ON b.player_id = p.player_id
                JOIN matches m
                    ON b.match_id = m.match_id
            ),

            last10 AS (
                SELECT *
                FROM ranked
                WHERE rn <= 10
            )

            SELECT
                player_name AS "Player",

                COUNT(*) AS "Matches",

                ROUND(
                    AVG(
                        CASE
                            WHEN rn <= 5
                            THEN runs
                        END
                    ),
                    2
                ) AS "Last 5 Avg Runs",

                ROUND(
                    AVG(runs),
                    2
                ) AS "Last 10 Avg Runs",

                ROUND(
                    AVG(
                        CASE
                            WHEN rn <= 5
                            THEN strike_rate
                        END
                    ),
                    2
                ) AS "Recent Strike Rate",

                SUM(
                    CASE
                        WHEN runs >= 50
                        THEN 1
                        ELSE 0
                    END
                ) AS "50+ Scores",

                ROUND(
                    sqrt(
                        MAX(
                            AVG(runs * runs)
                            - AVG(runs)
                            * AVG(runs),
                            0
                        )
                    ),
                    2
                ) AS "Consistency Score"

            FROM last10

            GROUP BY
                player_id,
                player_name

            ORDER BY
                "Last 5 Avg Runs" DESC;
        """,

        # =====================================================
        # QUESTION 24
        # =====================================================

        "Q24 — Best Batting Partnerships": """
            SELECT
                CASE
                    WHEN batsman1_id < batsman2_id
                    THEN batsman1_name
                    ELSE batsman2_name
                END AS "Player 1",

                CASE
                    WHEN batsman1_id < batsman2_id
                    THEN batsman2_name
                    ELSE batsman1_name
                END AS "Player 2",

                COUNT(*) AS "Partnerships",

                ROUND(
                    AVG(partnership_runs),
                    2
                ) AS "Average Partnership Runs",

                SUM(
                    CASE
                        WHEN partnership_runs > 50
                        THEN 1
                        ELSE 0
                    END
                ) AS "50+ Partnerships",

                MAX(partnership_runs)
                    AS "Highest Partnership",

                ROUND(
                    100.0 *
                    SUM(
                        CASE
                            WHEN partnership_runs > 50
                            THEN 1
                            ELSE 0
                        END
                    ) / COUNT(*),
                    2
                ) AS "Success Rate"

            FROM partnerships

            WHERE batsman1_id IS NOT NULL
            AND batsman2_id IS NOT NULL

            GROUP BY
                CASE
                    WHEN batsman1_id < batsman2_id
                    THEN batsman1_id
                    ELSE batsman2_id
                END,

                CASE
                    WHEN batsman1_id < batsman2_id
                    THEN batsman2_id
                    ELSE batsman1_id
                END

            HAVING COUNT(*) >= 5

            ORDER BY
                "Success Rate" DESC,
                "Average Partnership Runs" DESC;
        """,

        # =====================================================
        # QUESTION 25
        # =====================================================

        "Q25 — Player Performance Time Series": """
            WITH quarterly AS (

                SELECT
                    b.player_id,
                    p.player_name,

                    strftime(
                        '%Y',
                        m.start_date
                    ) AS year,

                    (
                        CAST(
                            strftime(
                                '%m',
                                m.start_date
                            ) AS INTEGER
                        ) + 2
                    ) / 3 AS quarter,

                    COUNT(
                        DISTINCT b.match_id
                    ) AS matches,

                    AVG(b.runs) AS avg_runs,

                    AVG(
                        CAST(b.strike_rate AS REAL)
                    ) AS avg_strike_rate

                FROM batting_scorecard b

                JOIN players p
                    ON b.player_id = p.player_id

                JOIN matches m
                    ON b.match_id = m.match_id

                WHERE m.start_date IS NOT NULL

                GROUP BY
                    b.player_id,
                    p.player_name,
                    strftime('%Y', m.start_date),
                    (
                        CAST(
                            strftime(
                                '%m',
                                m.start_date
                            ) AS INTEGER
                        ) + 2
                    ) / 3
            ),

            eligible AS (
                SELECT
                    player_id
                FROM quarterly
                WHERE matches >= 3
                GROUP BY player_id
                HAVING COUNT(*) >= 6
            ),

            trends AS (
                SELECT
                    q.*,

                    LAG(avg_runs) OVER (
                        PARTITION BY player_id
                        ORDER BY year, quarter
                    ) AS previous_avg_runs

                FROM quarterly q

                JOIN eligible e
                    ON q.player_id = e.player_id

                WHERE q.matches >= 3
            )

            SELECT
                player_name AS "Player",

                year || '-Q'
                    || quarter AS "Quarter",

                matches AS "Matches",

                ROUND(
                    avg_runs,
                    2
                ) AS "Average Runs",

                ROUND(
                    avg_strike_rate,
                    2
                ) AS "Average Strike Rate",

                ROUND(
                    avg_runs
                    - COALESCE(
                        previous_avg_runs,
                        avg_runs
                    ),
                    2
                ) AS "Change From Previous Quarter",

                CASE
                    WHEN previous_avg_runs IS NULL
                        THEN 'Stable'

                    WHEN avg_runs >
                        previous_avg_runs * 1.05
                        THEN 'Improving'

                    WHEN avg_runs <
                        previous_avg_runs * 0.95
                        THEN 'Declining'

                    ELSE 'Stable'
                END AS "Trend"

            FROM trends

            ORDER BY
                player_name,
                year,
                quarter;
        """
    }

    # =========================================================
    # DATABASE HELPER
    # =========================================================

    def run_query(sql):
        connection = get_connection()
        try:
            dataframe = pd.read_sql_query(sql,connection)
            return dataframe
        finally:
            connection.close()


    # =========================================================
    # SIDEBAR
    # =========================================================

    # ============================================================
    # SQL ANALYTICS UI
    # ============================================================

    import streamlit as st
    import pandas as pd
    from utils.db_connection import get_connection


    # ------------------------------------------------------------
    # HEADER
    # ------------------------------------------------------------

    st.title("🧮 SQL Query Interface")
    st.caption("Explore Cricbuzz LiveStats data using 25 SQL analytics queries.")

    # ------------------------------------------------------------
    # DATABASE FUNCTION
    # ------------------------------------------------------------

    def run_query(sql):
        connection = get_connection()
        try:
            db_path = connection.execute("PRAGMA database_list").fetchone()[2]
            dataframe = pd.read_sql_query(sql,connection)
            return dataframe, db_path
        finally:
            connection.close()

    # ------------------------------------------------------------
    # QUERY EXECUTION
    # ------------------------------------------------------------

    def execute_sql(sql):
        try:
            result, db_path = run_query(sql)
            return result, db_path, None
        except Exception as error:
            return None, None, str(error)

    # ------------------------------------------------------------
    # QUERY GROUPING
    # ------------------------------------------------------------

    query_items = list(QUERIES.items())
    beginner_queries = query_items[:8]
    intermediate_queries = query_items[8:16]
    advanced_queries = query_items[16:25]

    # ------------------------------------------------------------
    # QUERY SECTION FUNCTION
    # ------------------------------------------------------------

    def render_query_section(title,queries,button_label):
        st.subheader(title)
        if not queries:
            st.warning("No queries available.")
            return

        query_names = [
            name
            for name, sql in queries
        ]

        selected_name = st.selectbox("Pick a Query",query_names,key=f"select_{title}")
        selected_sql = dict(queries)[selected_name]

        if st.button(button_label,key=f"run_{title}",type="primary"):
            result, db_path, error = execute_sql(selected_sql)
            if error:
                st.error("❌ SQL Query Error")
                st.code(error,language="text")
                return

            st.success(
                f"Query executed successfully — "
                f"{len(result)} row(s) returned."
            )

            # ----------------------------------------------------
            # EMPTY RESULT
            # ----------------------------------------------------

            if result.empty:
                st.warning(
                    "⚠️ Query executed successfully, "
                    "but no records were found."
                )
                return

            # ----------------------------------------------------
            # RESULT TABLE
            # ----------------------------------------------------

            st.dataframe(result,use_container_width=True,hide_index=True)

            # ----------------------------------------------------
            # AUTOMATIC CHART
            # ----------------------------------------------------

            numeric_columns = result.select_dtypes(include="number").columns.tolist()
            if (
                len(result.columns) >= 2
                and numeric_columns
            ):
                category_column = result.columns[0]

                if category_column not in numeric_columns:
                    chart_data = result[[category_column] + numeric_columns].copy()
                    chart_data = chart_data.set_index(category_column)
                    st.bar_chart(chart_data,use_container_width=True)

    # ============================================================
    # CATEGORY TABS
    # ============================================================

    beginner_tab, intermediate_tab, advanced_tab = st.tabs(
        [
            "🌱 Beginner (Q1–Q8)",
            "⚡ Intermediate (Q9–Q16)",
            "🚀 Advanced (Q17–Q25)"
        ]
    )

    # ============================================================
    # BEGINNER
    # ============================================================

    with beginner_tab:
        render_query_section("Beginner Queries (Q1–Q8)",beginner_queries,"▶ Run Beginner Query")

    # ============================================================
    # INTERMEDIATE
    # ============================================================

    with intermediate_tab:
        render_query_section("Intermediate Queries (Q9–Q16)",intermediate_queries,"▶ Run Intermediate Query")

    # ============================================================
    # ADVANCED
    # ============================================================

    with advanced_tab:
        render_query_section("Advanced Queries (Q17–Q25)",advanced_queries,"▶ Run Advanced Query")

    # ============================================================
    # CUSTOM SQL
    # ============================================================

    st.divider()
    st.subheader("📝 Or run your own query")
    st.caption("Enter a SELECT SQL query to explore the Cricbuzz database.")
    custom_sql = st.text_area(
        "Enter SQL query",
        value="SELECT * FROM matches;",
        height=130,
        key="custom_sql"
    )
    if st.button("▶ Run Custom Query",key="run_custom_query",type="primary"):
        sql_text = custom_sql.strip()
        if not sql_text:
            st.warning("Please enter a SQL query.")
        else:

            # ----------------------------------------------------
            # BASIC SAFETY CHECK
            # ----------------------------------------------------

            normalized_sql = sql_text.lower().strip()
            allowed_commands = ("select","with","explain")

            if not normalized_sql.startswith(allowed_commands):
                st.error(
                    "❌ Only SELECT, WITH and EXPLAIN "
                    "queries are allowed here."
                )
            else:
                result, db_path, error = execute_sql(sql_text)
                if error:
                    st.error("❌ SQL Query Error")
                    st.code(error,language="text")
                else:
                    st.success(
                        f"Custom query executed successfully — "
                        f"{len(result)} row(s) returned."
                    )
                    if result.empty:
                        st.warning(
                            "⚠️ Query executed successfully, "
                            "but returned no records."
                        )
                    else:
                        st.dataframe(result,use_container_width=True,hide_index=True)

                        numeric_columns = (
                            result.select_dtypes(
                                include="number"
                            ).columns.tolist()
                        )

                        if (
                            len(result.columns) >= 2
                            and numeric_columns
                        ):
                            category_column = (result.columns[0])
                            if category_column not in numeric_columns:
                                chart_data = result[[category_column] + numeric_columns].copy()
                                chart_data = (chart_data.set_index(category_column))
                                st.bar_chart(chart_data,use_container_width=True)