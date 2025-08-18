-- =====================================================
-- MLB PITCHING ANALYTICS (Future Enhancement)
-- =====================================================
-- Note: This requires pitching data to be added to the schema
-- Currently showing structure for when pitching data becomes available

-- =====================================================  
-- GAME OUTCOME ANALYSIS
-- =====================================================

-- Game Results and Team Performance
WITH GameResults AS (
    SELECT 
        g.game_id,
        g.game_date,
        g.home_team_id,
        g.away_team_id,
        ht.team_name as home_team,
        at.team_name as away_team,
        
        -- Calculate runs for each team
        COALESCE(home_runs.runs, 0) as home_runs,
        COALESCE(away_runs.runs, 0) as away_runs,
        
        -- Determine winner
        CASE 
            WHEN COALESCE(home_runs.runs, 0) > COALESCE(away_runs.runs, 0) THEN home_team_id
            ELSE away_team_id 
        END as winning_team_id,
        
        CASE 
            WHEN COALESCE(home_runs.runs, 0) > COALESCE(away_runs.runs, 0) THEN ht.team_name
            ELSE at.team_name 
        END as winning_team
        
    FROM games g
    INNER JOIN teams ht ON g.home_team_id = ht.team_id
    INNER JOIN teams at ON g.away_team_id = at.team_id
    LEFT JOIN (
        SELECT b.game_id, b.team_id, SUM(b.runs) as runs
        FROM boxscore b
        INNER JOIN games g2 ON b.game_id = g2.game_id 
        WHERE b.team_id = g2.home_team_id
        GROUP BY b.game_id, b.team_id
    ) home_runs ON g.game_id = home_runs.game_id
    LEFT JOIN (
        SELECT b.game_id, b.team_id, SUM(b.runs) as runs  
        FROM boxscore b
        INNER JOIN games g3 ON b.game_id = g3.game_id
        WHERE b.team_id = g3.away_team_id
        GROUP BY b.game_id, b.team_id
    ) away_runs ON g.game_id = away_runs.game_id
    WHERE g.game_date >= '2025-03-01'
),

-- Team Win-Loss Records
TeamRecords AS (
    SELECT 
        team_id,
        team_name,
        SUM(CASE WHEN winning_team_id = team_id THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN winning_team_id != team_id THEN 1 ELSE 0 END) as losses,
        COUNT(*) as games_played
    FROM (
        SELECT home_team_id as team_id, home_team as team_name, winning_team_id FROM GameResults
        UNION ALL
        SELECT away_team_id as team_id, away_team as team_name, winning_team_id FROM GameResults  
    ) all_games
    GROUP BY team_id, team_name
)

-- Team Standings with Win Percentage
SELECT 
    ROW_NUMBER() OVER (ORDER BY CAST(wins AS DECIMAL(10,3))/games_played DESC) as standing,
    team_name,
    wins,
    losses, 
    games_played,
    FORMAT(CAST(wins AS DECIMAL(10,3))/games_played, 'N3') as win_percentage,
    
    -- Games behind leader (calculated after ordering)
    CAST(
        (SELECT MAX(CAST(wins AS DECIMAL(10,3))/games_played) FROM TeamRecords) - 
        (CAST(wins AS DECIMAL(10,3))/games_played)
    AS DECIMAL(10,1)) * games_played / 2 as games_behind
    
FROM TeamRecords
ORDER BY win_percentage DESC;

-- =====================================================
-- HOME vs AWAY PERFORMANCE
-- =====================================================

-- Home/Away Splits for Teams
WITH HomeAwayStats AS (
    SELECT 
        team_id,
        team_name,
        'Home' as venue,
        SUM(runs) as total_runs,
        SUM(hits) as total_hits,
        SUM(at_bats) as total_at_bats,
        COUNT(DISTINCT game_id) as games
    FROM (
        SELECT 
            g.home_team_id as team_id,
            ht.team_name,
            b.game_id,
            b.runs,
            b.hits, 
            b.at_bats
        FROM games g
        INNER JOIN teams ht ON g.home_team_id = ht.team_id
        INNER JOIN boxscore b ON g.game_id = b.game_id AND b.team_id = g.home_team_id
        WHERE g.game_date >= '2025-03-01'
    ) home_stats
    GROUP BY team_id, team_name
    
    UNION ALL
    
    SELECT 
        team_id,
        team_name,
        'Away' as venue,
        SUM(runs) as total_runs,
        SUM(hits) as total_hits,
        SUM(at_bats) as total_at_bats,
        COUNT(DISTINCT game_id) as games
    FROM (
        SELECT 
            g.away_team_id as team_id,
            at.team_name,
            b.game_id,
            b.runs,
            b.hits,
            b.at_bats
        FROM games g  
        INNER JOIN teams at ON g.away_team_id = at.team_id
        INNER JOIN boxscore b ON g.game_id = b.game_id AND b.team_id = g.away_team_id
        WHERE g.game_date >= '2025-03-01'
    ) away_stats
    GROUP BY team_id, team_name
)

-- Home vs Away Comparison
SELECT 
    team_name,
    venue,
    games,
    total_runs,
    FORMAT(CAST(total_runs AS DECIMAL(10,2)) / games, 'N2') as runs_per_game,
    FORMAT(CAST(total_hits AS DECIMAL(10,3)) / total_at_bats, 'N3') as batting_avg
FROM HomeAwayStats
ORDER BY team_name, venue DESC;

-- =====================================================
-- DAY vs NIGHT GAME ANALYSIS  
-- =====================================================

-- Performance by Game Time (if time data available)
-- Note: This assumes game time can be inferred from game_id or added to schema

SELECT 
    p.player_name,
    t.team_name,
    
    -- Day games (assumed early game_ids or could add time field)
    SUM(CASE WHEN CAST(RIGHT(b.game_id, 1) AS INT) % 2 = 0 THEN b.hits ELSE 0 END) as day_hits,
    SUM(CASE WHEN CAST(RIGHT(b.game_id, 1) AS INT) % 2 = 0 THEN b.at_bats ELSE 0 END) as day_abs,
    
    -- Night games  
    SUM(CASE WHEN CAST(RIGHT(b.game_id, 1) AS INT) % 2 = 1 THEN b.hits ELSE 0 END) as night_hits,
    SUM(CASE WHEN CAST(RIGHT(b.game_id, 1) AS INT) % 2 = 1 THEN b.at_bats ELSE 0 END) as night_abs,
    
    -- Calculate splits
    CASE 
        WHEN SUM(CASE WHEN CAST(RIGHT(b.game_id, 1) AS INT) % 2 = 0 THEN b.at_bats ELSE 0 END) > 0
        THEN FORMAT(
            CAST(SUM(CASE WHEN CAST(RIGHT(b.game_id, 1) AS INT) % 2 = 0 THEN b.hits ELSE 0 END) AS DECIMAL(10,3)) /
            SUM(CASE WHEN CAST(RIGHT(b.game_id, 1) AS INT) % 2 = 0 THEN b.at_bats ELSE 0 END), 'N3'
        )
        ELSE 'N/A'
    END as day_avg,
    
    CASE 
        WHEN SUM(CASE WHEN CAST(RIGHT(b.game_id, 1) AS INT) % 2 = 1 THEN b.at_bats ELSE 0 END) > 0
        THEN FORMAT(
            CAST(SUM(CASE WHEN CAST(RIGHT(b.game_id, 1) AS INT) % 2 = 1 THEN b.hits ELSE 0 END) AS DECIMAL(10,3)) /
            SUM(CASE WHEN CAST(RIGHT(b.game_id, 1) AS INT) % 2 = 1 THEN b.at_bats ELSE 0 END), 'N3'
        )
        ELSE 'N/A'
    END as night_avg
    
FROM boxscore b
INNER JOIN players p ON b.player_id = p.player_id
INNER JOIN teams t ON b.team_id = t.team_id
INNER JOIN games g ON b.game_id = g.game_id
WHERE g.game_date >= '2025-03-01'
GROUP BY p.player_id, p.player_name, t.team_name
HAVING SUM(b.at_bats) >= 50  -- Qualified players
ORDER BY p.player_name;

-- =====================================================
-- WEEKLY PERFORMANCE TRENDS
-- =====================================================

-- Performance by Day of Week
SELECT 
    DATENAME(WEEKDAY, g.game_date) as day_of_week,
    DATEPART(WEEKDAY, g.game_date) as day_number,
    COUNT(DISTINCT g.game_id) as games_played,
    
    -- League totals by day
    SUM(b.runs) as total_runs,
    SUM(b.hits) as total_hits,
    SUM(b.home_runs) as total_hrs,
    SUM(b.at_bats) as total_abs,
    
    -- League averages by day
    FORMAT(CAST(SUM(b.runs) AS DECIMAL(10,2)) / COUNT(DISTINCT g.game_id), 'N2') as runs_per_game,
    FORMAT(CAST(SUM(b.hits) AS DECIMAL(10,3)) / SUM(b.at_bats), 'N3') as league_avg,
    FORMAT(CAST(SUM(b.home_runs) AS DECIMAL(10,2)) / COUNT(DISTINCT g.game_id), 'N2') as hrs_per_game
    
FROM games g
INNER JOIN boxscore b ON g.game_id = b.game_id
WHERE g.game_date >= '2025-03-01'
GROUP BY DATENAME(WEEKDAY, g.game_date), DATEPART(WEEKDAY, g.game_date)
ORDER BY day_number;

-- =====================================================
-- MATCHUP ANALYSIS
-- =====================================================

-- Head-to-Head Team Records
WITH HeadToHead AS (
    SELECT 
        CASE WHEN g.home_team_id < g.away_team_id THEN g.home_team_id ELSE g.away_team_id END as team1_id,
        CASE WHEN g.home_team_id < g.away_team_id THEN g.away_team_id ELSE g.home_team_id END as team2_id,
        CASE WHEN g.home_team_id < g.away_team_id THEN ht.team_name ELSE at.team_name END as team1_name,
        CASE WHEN g.home_team_id < g.away_team_id THEN at.team_name ELSE ht.team_name END as team2_name,
        g.game_id,
        g.game_date,
        
        -- Determine winner for this standardized matchup
        CASE 
            WHEN home_runs.runs > away_runs.runs AND g.home_team_id < g.away_team_id THEN 'team1'
            WHEN home_runs.runs > away_runs.runs AND g.home_team_id > g.away_team_id THEN 'team2'  
            WHEN away_runs.runs > home_runs.runs AND g.away_team_id < g.home_team_id THEN 'team1'
            ELSE 'team2'
        END as winner
        
    FROM games g
    INNER JOIN teams ht ON g.home_team_id = ht.team_id
    INNER JOIN teams at ON g.away_team_id = at.team_id
    LEFT JOIN (
        SELECT b.game_id, SUM(b.runs) as runs
        FROM boxscore b
        INNER JOIN games g2 ON b.game_id = g2.game_id
        WHERE b.team_id = g2.home_team_id  
        GROUP BY b.game_id
    ) home_runs ON g.game_id = home_runs.game_id
    LEFT JOIN (
        SELECT b.game_id, SUM(b.runs) as runs
        FROM boxscore b  
        INNER JOIN games g3 ON b.game_id = g3.game_id
        WHERE b.team_id = g3.away_team_id
        GROUP BY b.game_id
    ) away_runs ON g.game_id = away_runs.game_id
    WHERE g.game_date >= '2025-03-01'
)

-- Head-to-Head Records Summary
SELECT 
    team1_name + ' vs ' + team2_name as matchup,
    COUNT(*) as total_games,
    SUM(CASE WHEN winner = 'team1' THEN 1 ELSE 0 END) as team1_wins,
    SUM(CASE WHEN winner = 'team2' THEN 1 ELSE 0 END) as team2_wins,
    
    -- Most recent game
    MAX(game_date) as last_game_date
    
FROM HeadToHead  
GROUP BY team1_id, team2_id, team1_name, team2_name
HAVING COUNT(*) >= 2  -- Only show matchups with multiple games
ORDER BY total_games DESC, matchup;
