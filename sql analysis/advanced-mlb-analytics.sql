-- =====================================================
-- ADVANCED MLB ANALYTICS - SQL VERSION
-- =====================================================
-- Comprehensive SQL-based analytics for MLB data
-- Designed for SQL Server with mlb_data database

-- =====================================================
-- BASIC PERFORMANCE METRICS
-- =====================================================

-- Player Season Statistics with Advanced Metrics
WITH PlayerSeasonStats AS (
    SELECT 
        p.player_id,
        p.player_name,
        t.team_name,
        COUNT(DISTINCT b.game_id) as games_played,
        SUM(b.at_bats) as total_at_bats,
        SUM(b.hits) as total_hits,
        SUM(b.runs) as total_runs,
        SUM(b.rbi) as total_rbi,
        SUM(b.home_runs) as total_home_runs,
        SUM(b.doubles) as total_doubles,
        SUM(b.triples) as total_triples,
        SUM(b.walks) as total_walks,
        SUM(b.strikeouts) as total_strikeouts,
        
        -- Calculated Advanced Metrics
        CASE 
            WHEN SUM(b.at_bats) > 0 
            THEN CAST(SUM(b.hits) AS DECIMAL(10,3)) / SUM(b.at_bats)
            ELSE 0 
        END as batting_average,
        
        CASE 
            WHEN SUM(b.at_bats + b.walks) > 0 
            THEN CAST(SUM(b.hits + b.walks) AS DECIMAL(10,3)) / SUM(b.at_bats + b.walks)
            ELSE 0 
        END as on_base_percentage,
        
        CASE 
            WHEN SUM(b.at_bats) > 0 
            THEN CAST(SUM(b.hits + b.doubles + 2*b.triples + 3*b.home_runs) AS DECIMAL(10,3)) / SUM(b.at_bats)
            ELSE 0 
        END as slugging_percentage
        
    FROM boxscore b
    INNER JOIN players p ON b.player_id = p.player_id
    INNER JOIN teams t ON b.team_id = t.team_id
    INNER JOIN games g ON b.game_id = g.game_id
    WHERE g.game_date >= '2025-03-01'  -- Current season
    GROUP BY p.player_id, p.player_name, t.team_name
    HAVING SUM(b.at_bats) >= 50  -- Minimum plate appearances
),

-- =====================================================
-- ADVANCED SABERMETRICS
-- =====================================================

-- OPS and Advanced Metrics
PlayerAdvancedStats AS (
    SELECT *,
        (on_base_percentage + slugging_percentage) as OPS,
        
        -- Runs Created (simplified Bill James formula)
        CASE 
            WHEN total_at_bats > 0
            THEN ((total_hits + total_walks) * (total_hits + total_doubles + 2*total_triples + 3*total_home_runs)) / (total_at_bats + total_walks)
            ELSE 0
        END as runs_created,
        
        -- Power Factor (ISO - Isolated Power)
        (slugging_percentage - batting_average) as isolated_power,
        
        -- Plate Discipline
        CASE 
            WHEN (total_at_bats + total_walks + total_strikeouts) > 0
            THEN CAST(total_walks AS DECIMAL(10,3)) / (total_at_bats + total_walks + total_strikeouts)
            ELSE 0
        END as walk_rate,
        
        CASE 
            WHEN (total_at_bats + total_walks + total_strikeouts) > 0
            THEN CAST(total_strikeouts AS DECIMAL(10,3)) / (total_at_bats + total_walks + total_strikeouts)
            ELSE 0
        END as strikeout_rate
        
    FROM PlayerSeasonStats
)

-- Final Player Rankings with Performance Categories
SELECT 
    ROW_NUMBER() OVER (ORDER BY OPS DESC) as ranking,
    player_name,
    team_name,
    games_played,
    
    -- Core Stats
    FORMAT(batting_average, 'N3') as BA,
    FORMAT(on_base_percentage, 'N3') as OBP,
    FORMAT(slugging_percentage, 'N3') as SLG,
    FORMAT(OPS, 'N3') as OPS,
    
    -- Power Stats
    total_home_runs as HR,
    total_doubles as [2B],
    total_triples as [3B],
    FORMAT(isolated_power, 'N3') as ISO,
    
    -- Discipline Stats  
    FORMAT(walk_rate, 'N3') as BB_Rate,
    FORMAT(strikeout_rate, 'N3') as K_Rate,
    
    -- Production Stats
    total_runs as R,
    total_rbi as RBI,
    CAST(runs_created as INT) as RC,
    
    -- Performance Category
    CASE 
        WHEN OPS >= 0.900 THEN '⭐ Elite'
        WHEN OPS >= 0.800 THEN '🌟 Above Average' 
        WHEN OPS >= 0.700 THEN '📊 Average'
        WHEN OPS >= 0.600 THEN '📉 Below Average'
        ELSE '🚨 Poor'
    END as performance_category
    
FROM PlayerAdvancedStats
WHERE total_at_bats >= 100  -- Qualified players only
ORDER BY OPS DESC;

-- =====================================================
-- TEAM OFFENSIVE ANALYSIS
-- =====================================================

-- Team Offensive Rankings
WITH TeamOffense AS (
    SELECT 
        t.team_name,
        COUNT(DISTINCT g.game_id) as games_played,
        SUM(b.runs) as total_runs,
        SUM(b.hits) as total_hits,
        SUM(b.home_runs) as total_home_runs,
        SUM(b.rbi) as total_rbi,
        SUM(b.at_bats) as total_at_bats,
        SUM(b.walks) as total_walks,
        SUM(b.strikeouts) as total_strikeouts,
        
        -- Team Averages
        CAST(SUM(b.runs) AS DECIMAL(10,2)) / COUNT(DISTINCT g.game_id) as runs_per_game,
        CAST(SUM(b.hits) AS DECIMAL(10,3)) / SUM(b.at_bats) as team_batting_avg,
        CAST(SUM(b.home_runs) AS DECIMAL(10,2)) / COUNT(DISTINCT g.game_id) as hr_per_game
        
    FROM teams t
    INNER JOIN boxscore b ON t.team_id = b.team_id  
    INNER JOIN games g ON b.game_id = g.game_id
    WHERE g.game_date >= '2025-03-01'
    GROUP BY t.team_id, t.team_name
)

SELECT 
    ROW_NUMBER() OVER (ORDER BY runs_per_game DESC) as offense_rank,
    team_name,
    games_played,
    total_runs,
    FORMAT(runs_per_game, 'N2') as RPG,
    FORMAT(team_batting_avg, 'N3') as Team_BA,
    total_home_runs as HR,
    FORMAT(hr_per_game, 'N2') as HR_per_game,
    
    -- Team Strength Classification
    CASE 
        WHEN runs_per_game >= 5.5 THEN '🏆 Elite Offense'
        WHEN runs_per_game >= 4.8 THEN '💪 Strong Offense'
        WHEN runs_per_game >= 4.2 THEN '⚖️ Average Offense' 
        WHEN runs_per_game >= 3.5 THEN '📉 Weak Offense'
        ELSE '🆘 Poor Offense'
    END as offensive_rating
    
FROM TeamOffense
ORDER BY runs_per_game DESC;

-- =====================================================
-- SITUATIONAL PERFORMANCE ANALYSIS  
-- =====================================================

-- Clutch Performance Analysis (Players with high RBI per Hit ratio)
SELECT 
    TOP 20
    p.player_name,
    t.team_name,
    SUM(b.hits) as total_hits,
    SUM(b.rbi) as total_rbi,
    CASE 
        WHEN SUM(b.hits) > 0 
        THEN CAST(SUM(b.rbi) AS DECIMAL(10,2)) / SUM(b.hits)
        ELSE 0 
    END as rbi_per_hit,
    
    -- Context
    COUNT(DISTINCT b.game_id) as games_played,
    FORMAT(CAST(SUM(b.hits) AS DECIMAL(10,3)) / SUM(b.at_bats), 'N3') as batting_avg
    
FROM boxscore b
INNER JOIN players p ON b.player_id = p.player_id
INNER JOIN teams t ON b.team_id = t.team_id
INNER JOIN games g ON b.game_id = g.game_id
WHERE g.game_date >= '2025-03-01'
GROUP BY p.player_id, p.player_name, t.team_name
HAVING SUM(b.hits) >= 30  -- Minimum hits for meaningful sample
ORDER BY rbi_per_hit DESC;

-- =====================================================
-- TREND ANALYSIS - MONTHLY PERFORMANCE
-- =====================================================

-- Monthly Batting Performance Trends
SELECT 
    YEAR(g.game_date) as season_year,
    MONTH(g.game_date) as month,
    DATENAME(MONTH, g.game_date) as month_name,
    
    -- Aggregate Stats
    COUNT(DISTINCT b.game_id) as games_played,
    SUM(b.hits) as total_hits,
    SUM(b.at_bats) as total_at_bats,
    SUM(b.home_runs) as total_home_runs,
    SUM(b.runs) as total_runs,
    
    -- League Averages by Month
    FORMAT(CAST(SUM(b.hits) AS DECIMAL(10,3)) / SUM(b.at_bats), 'N3') as league_batting_avg,
    CAST(SUM(b.runs) AS DECIMAL(10,2)) / COUNT(DISTINCT b.game_id) as runs_per_game,
    CAST(SUM(b.home_runs) AS DECIMAL(10,2)) / COUNT(DISTINCT b.game_id) as hr_per_game
    
FROM boxscore b
INNER JOIN games g ON b.game_id = g.game_id
WHERE g.game_date >= '2025-03-01'
GROUP BY YEAR(g.game_date), MONTH(g.game_date), DATENAME(MONTH, g.game_date)
ORDER BY season_year, month;

-- =====================================================
-- HOT/COLD STREAK ANALYSIS
-- =====================================================

-- Recent Performance (Last 10 Games per Player)
WITH RecentGames AS (
    SELECT 
        b.player_id,
        p.player_name,
        t.team_name,
        g.game_date,
        b.hits,
        b.at_bats,
        ROW_NUMBER() OVER (PARTITION BY b.player_id ORDER BY g.game_date DESC) as game_recency
    FROM boxscore b
    INNER JOIN players p ON b.player_id = p.player_id
    INNER JOIN teams t ON b.team_id = t.team_id
    INNER JOIN games g ON b.game_id = g.game_id
    WHERE g.game_date >= '2025-03-01'
    AND b.at_bats > 0
),

Last10Games AS (
    SELECT 
        player_id,
        player_name,
        team_name,
        SUM(hits) as recent_hits,
        SUM(at_bats) as recent_at_bats,
        CAST(SUM(hits) AS DECIMAL(10,3)) / SUM(at_bats) as recent_avg
    FROM RecentGames 
    WHERE game_recency <= 10
    GROUP BY player_id, player_name, team_name
    HAVING SUM(at_bats) >= 20  -- Minimum recent at-bats
),

SeasonStats AS (
    SELECT 
        b.player_id,
        CAST(SUM(b.hits) AS DECIMAL(10,3)) / SUM(b.at_bats) as season_avg
    FROM boxscore b
    INNER JOIN games g ON b.game_id = g.game_id
    WHERE g.game_date >= '2025-03-01'
    GROUP BY b.player_id
    HAVING SUM(b.at_bats) >= 50
)

-- Hot/Cold Streak Classification
SELECT 
    l.player_name,
    l.team_name,
    FORMAT(l.recent_avg, 'N3') as last_10_avg,
    FORMAT(s.season_avg, 'N3') as season_avg,
    FORMAT(l.recent_avg - s.season_avg, 'N3') as avg_difference,
    
    -- Streak Classification
    CASE 
        WHEN l.recent_avg > s.season_avg * 1.2 THEN '🔥 Red Hot'
        WHEN l.recent_avg > s.season_avg * 1.1 THEN '🌡️ Hot'
        WHEN l.recent_avg < s.season_avg * 0.8 THEN '🧊 Cold'
        WHEN l.recent_avg < s.season_avg * 0.7 THEN '❄️ Ice Cold'
        ELSE '📊 Normal'
    END as current_streak
    
FROM Last10Games l
INNER JOIN SeasonStats s ON l.player_id = s.player_id
ORDER BY (l.recent_avg - s.season_avg) DESC;

-- =====================================================
-- MILESTONE TRACKING
-- =====================================================

-- Players Approaching Milestones
WITH PlayerProgress AS (
    SELECT 
        p.player_id,
        p.player_name,
        t.team_name,
        SUM(b.hits) as current_hits,
        SUM(b.home_runs) as current_hrs,
        SUM(b.rbi) as current_rbi,
        COUNT(DISTINCT b.game_id) as games_played,
        
        -- Pace calculations (games remaining estimated as 162 - games_played)
        CASE 
            WHEN COUNT(DISTINCT b.game_id) > 0 
            THEN (162 - COUNT(DISTINCT b.game_id)) * (CAST(SUM(b.hits) AS DECIMAL(10,2)) / COUNT(DISTINCT b.game_id))
            ELSE 0 
        END as projected_hits
        
    FROM boxscore b
    INNER JOIN players p ON b.player_id = p.player_id  
    INNER JOIN teams t ON b.team_id = t.team_id
    INNER JOIN games g ON b.game_id = g.game_id
    WHERE g.game_date >= '2025-03-01'
    GROUP BY p.player_id, p.player_name, t.team_name
)

SELECT 
    player_name,
    team_name,
    current_hits,
    CAST(projected_hits as INT) as projected_season_hits,
    
    -- Milestone Tracking
    CASE 
        WHEN projected_hits >= 200 THEN '🎯 200 Hit Pace'
        WHEN projected_hits >= 180 THEN '📈 180+ Hit Pace'
        WHEN projected_hits >= 160 THEN '📊 160+ Hit Pace'
        ELSE '📉 Below 160 Pace'
    END as hit_milestone_status,
    
    -- Games to milestone (if on pace)
    CASE 
        WHEN current_hits < 100 AND projected_hits >= 100 
        THEN CEILING((100 - current_hits) / (CAST(current_hits AS DECIMAL(10,2)) / games_played))
        ELSE NULL
    END as games_to_100_hits
    
FROM PlayerProgress
WHERE games_played >= 20  -- Meaningful sample size
ORDER BY projected_hits DESC;

-- =====================================================
-- LEAGUE LEADERS DASHBOARD
-- =====================================================

-- Top 10 in Major Categories
SELECT 'Batting Average' as category, player_name, team_name, FORMAT(stat_value, 'N3') as value, stat_value as sort_value
FROM (
    SELECT TOP 10 
        p.player_name, t.team_name,
        CAST(SUM(b.hits) AS DECIMAL(10,3)) / SUM(b.at_bats) as stat_value
    FROM boxscore b
    INNER JOIN players p ON b.player_id = p.player_id
    INNER JOIN teams t ON b.team_id = t.team_id  
    INNER JOIN games g ON b.game_id = g.game_id
    WHERE g.game_date >= '2025-03-01'
    GROUP BY p.player_id, p.player_name, t.team_name
    HAVING SUM(b.at_bats) >= 100
) leaders

UNION ALL

SELECT 'Home Runs' as category, player_name, team_name, CAST(stat_value as VARCHAR) as value, CAST(stat_value AS DECIMAL(10,3)) as sort_value  
FROM (
    SELECT TOP 10
        p.player_name, t.team_name,
        SUM(b.home_runs) as stat_value
    FROM boxscore b
    INNER JOIN players p ON b.player_id = p.player_id
    INNER JOIN teams t ON b.team_id = t.team_id
    INNER JOIN games g ON b.game_id = g.game_id  
    WHERE g.game_date >= '2025-03-01'
    GROUP BY p.player_id, p.player_name, t.team_name
) hr_leaders

UNION ALL

SELECT 'RBI' as category, player_name, team_name, CAST(stat_value as VARCHAR) as value, CAST(stat_value AS DECIMAL(10,3)) as sort_value
FROM (
    SELECT TOP 10
        p.player_name, t.team_name, 
        SUM(b.rbi) as stat_value
    FROM boxscore b
    INNER JOIN players p ON b.player_id = p.player_id
    INNER JOIN teams t ON b.team_id = t.team_id
    INNER JOIN games g ON b.game_id = g.game_id
    WHERE g.game_date >= '2025-03-01'
    GROUP BY p.player_id, p.player_name, t.team_name
) rbi_leaders

ORDER BY category, sort_value DESC;
