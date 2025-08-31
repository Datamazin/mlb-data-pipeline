-- =====================================================
-- BOXSCORE COUNTS & DATA VALIDATION
-- =====================================================
-- Daily counts, data quality checks, and summary statistics
-- for MLB boxscore data

-- =====================================================
-- OVERALL SUMMARY
-- =====================================================

-- Database Overview
SELECT 
    'Database Overview' as section,
    DB_NAME() as database_name,
    @@SERVERNAME as server_name,
    GETDATE() as query_timestamp;

-- Table Counts Summary
SELECT 
    'games' as table_name,
    COUNT(*) as record_count,
    MIN(game_date) as earliest_date,
    MAX(game_date) as latest_date
FROM games

UNION ALL

SELECT 
    'boxscore' as table_name,
    COUNT(*) as record_count,
    MIN(g.game_date) as earliest_date,
    MAX(g.game_date) as latest_date
FROM boxscore b
INNER JOIN games g ON b.game_id = g.game_id

UNION ALL

SELECT 
    'players' as table_name,
    COUNT(*) as record_count,
    NULL as earliest_date,
    NULL as latest_date
FROM players

UNION ALL

SELECT 
    'teams' as table_name,
    COUNT(*) as record_count,
    NULL as earliest_date,
    NULL as latest_date
FROM teams;

-- =====================================================
-- DAILY BOXSCORE COUNTS
-- =====================================================

-- Boxscore counts by date (last 30 days)
SELECT 
    g.game_date,
    COUNT(*) as boxscore_records,
    COUNT(DISTINCT g.game_id) as unique_games,
    COUNT(DISTINCT b.player_id) as unique_players,
    COUNT(DISTINCT b.team_id) as unique_teams,
    
    -- Average records per game
    CAST(COUNT(*) AS DECIMAL(10,1)) / COUNT(DISTINCT g.game_id) as avg_records_per_game,
    
    -- Data completeness indicators
    SUM(CASE WHEN b.at_bats > 0 THEN 1 ELSE 0 END) as records_with_at_bats,
    SUM(CASE WHEN b.hits > 0 THEN 1 ELSE 0 END) as records_with_hits,
    SUM(CASE WHEN b.home_runs > 0 THEN 1 ELSE 0 END) as records_with_home_runs
    
FROM boxscore b
INNER JOIN games g ON b.game_id = g.game_id
WHERE g.game_date >= DATEADD(DAY, -30, GETDATE())
GROUP BY g.game_date
ORDER BY g.game_date DESC;

-- =====================================================
-- BOXSCORE COUNTS AFTER 8/15/2025
-- =====================================================

USE mlb_data;

-- Overall count after 8/15/2025
SELECT 
    'Boxscores after 8/15/2025' as metric,
    COUNT(*) as count
FROM boxscore b
INNER JOIN games g ON b.game_id = g.game_id
WHERE g.game_date > '2025-08-15';

-- Daily breakdown after 8/15/2025
SELECT 
    g.game_date,
    COUNT(*) as boxscore_records,
    COUNT(DISTINCT g.game_id) as unique_games,
    COUNT(DISTINCT b.player_id) as unique_players
FROM boxscore b
INNER JOIN games g ON b.game_id = g.game_id
WHERE g.game_date > '2025-08-15'
GROUP BY g.game_date
ORDER BY g.game_date;

-- Summary by team after 8/15/2025
SELECT 
    t.team_name,
    COUNT(*) as boxscore_records,
    COUNT(DISTINCT g.game_id) as games_played,
    COUNT(DISTINCT b.player_id) as unique_players
FROM boxscore b
INNER JOIN games g ON b.game_id = g.game_id
INNER JOIN teams t ON b.team_id = t.team_id
WHERE g.game_date > '2025-08-15'
GROUP BY t.team_id, t.team_name
ORDER BY boxscore_records DESC;

-- Daily breakdown after 8/15/2025
SELECT 
    g.game_date,
    COUNT(*) as boxscore_records,
    COUNT(DISTINCT g.game_id) as games,
    COUNT(DISTINCT b.player_id) as players,
    
    -- Team breakdown for the day
    COUNT(DISTINCT CASE WHEN b.team_id = g.home_team_id THEN b.team_id END) as home_teams,
    COUNT(DISTINCT CASE WHEN b.team_id = g.away_team_id THEN b.team_id END) as away_teams
    
FROM boxscore b
INNER JOIN games g ON b.game_id = g.game_id
WHERE g.game_date > '2025-08-15'
GROUP BY g.game_date
ORDER BY g.game_date;

-- =====================================================
-- DATA QUALITY CHECKS
-- =====================================================

-- Missing or Zero Values Check
SELECT 
    'Data Quality After 8/15/2025' as section,
    COUNT(*) as total_records,
    
    -- Missing data counts
    SUM(CASE WHEN b.at_bats IS NULL THEN 1 ELSE 0 END) as null_at_bats,
    SUM(CASE WHEN b.hits IS NULL THEN 1 ELSE 0 END) as null_hits,
    SUM(CASE WHEN b.home_runs IS NULL THEN 1 ELSE 0 END) as null_home_runs,
    SUM(CASE WHEN b.rbi IS NULL THEN 1 ELSE 0 END) as null_rbi,
    
    -- Zero values (normal for some stats)
    SUM(CASE WHEN b.at_bats = 0 THEN 1 ELSE 0 END) as zero_at_bats,
    SUM(CASE WHEN b.hits = 0 THEN 1 ELSE 0 END) as zero_hits,
    SUM(CASE WHEN b.home_runs = 0 THEN 1 ELSE 0 END) as zero_home_runs,
    
    -- Records with activity
    SUM(CASE WHEN b.at_bats > 0 THEN 1 ELSE 0 END) as active_records,
    
    -- Percentage with activity
    FORMAT(
        CAST(SUM(CASE WHEN b.at_bats > 0 THEN 1 ELSE 0 END) AS DECIMAL(10,2)) / COUNT(*) * 100,
        'N1'
    ) + '%' as pct_active_records
    
FROM boxscore b
INNER JOIN games g ON b.game_id = g.game_id
WHERE g.game_date > '2025-08-15';

-- =====================================================
-- TEAM ACTIVITY SUMMARY
-- =====================================================

-- Team boxscore activity after 8/15/2025
SELECT 
    t.team_name,
    t.abbreviation,
    COUNT(*) as total_boxscore_records,
    COUNT(DISTINCT g.game_id) as games_played,
    
    -- Home vs Away games
    COUNT(DISTINCT CASE WHEN b.team_id = g.home_team_id THEN g.game_id END) as home_games,
    COUNT(DISTINCT CASE WHEN b.team_id = g.away_team_id THEN g.game_id END) as away_games,
    
    -- Statistical totals
    SUM(b.hits) as total_hits,
    SUM(b.home_runs) as total_home_runs,
    SUM(b.rbi) as total_rbi,
    SUM(b.runs) as total_runs,
    
    -- Team batting average
    CASE 
        WHEN SUM(b.at_bats) > 0 
        THEN FORMAT(CAST(SUM(b.hits) AS DECIMAL(10,3)) / SUM(b.at_bats), 'N3')
        ELSE 'N/A'
    END as team_avg
    
FROM boxscore b
INNER JOIN games g ON b.game_id = g.game_id
INNER JOIN teams t ON b.team_id = t.team_id
WHERE g.game_date > '2025-08-15'
GROUP BY t.team_id, t.team_name, t.abbreviation
ORDER BY total_boxscore_records DESC;

-- =====================================================
-- RECENT ACTIVITY CHECK
-- =====================================================

-- Last 5 days of activity
SELECT 
    'Last 5 Days Activity' as section,
    g.game_date,
    COUNT(*) as boxscore_records,
    COUNT(DISTINCT g.game_id) as games,
    MIN(g.game_id) as min_game_id,
    MAX(g.game_id) as max_game_id
FROM boxscore b
INNER JOIN games g ON b.game_id = g.game_id
WHERE g.game_date >= DATEADD(DAY, -5, GETDATE())
GROUP BY g.game_date
ORDER BY g.game_date DESC;

-- =====================================================
-- QUICK VALIDATION QUERIES
-- =====================================================

-- Check for duplicate boxscore records
SELECT 
    'Duplicate Check' as check_type,
    COUNT(*) as total_records,
    COUNT(DISTINCT CONCAT(b.game_id, '-', b.player_id, '-', b.team_id)) as unique_combinations,
    CASE 
        WHEN COUNT(*) = COUNT(DISTINCT CONCAT(b.game_id, '-', b.player_id, '-', b.team_id))
        THEN '✅ No Duplicates'
        ELSE '⚠️ Duplicates Found'
    END as status
FROM boxscore b
INNER JOIN games g ON b.game_id = g.game_id
WHERE g.game_date > '2025-08-15';

-- Check team ID population
SELECT 
    'Team ID Population' as check_type,
    COUNT(*) as total_games,
    SUM(CASE WHEN home_team_id IS NOT NULL THEN 1 ELSE 0 END) as games_with_home_team_id,
    SUM(CASE WHEN away_team_id IS NOT NULL THEN 1 ELSE 0 END) as games_with_away_team_id,
    FORMAT(
        CAST(SUM(CASE WHEN home_team_id IS NOT NULL AND away_team_id IS NOT NULL THEN 1 ELSE 0 END) AS DECIMAL(10,2)) / COUNT(*) * 100,
        'N1'
    ) + '%' as pct_complete_team_ids
FROM games
WHERE game_date > '2025-08-15';

-- =====================================================
-- PERFORMANCE METRICS
-- =====================================================

-- Top performing games by total hits
SELECT TOP 10
    g.game_id,
    g.game_date,
    ht.team_name as home_team,
    at.team_name as away_team,
    COUNT(*) as boxscore_records,
    SUM(b.hits) as total_hits,
    SUM(b.home_runs) as total_home_runs,
    SUM(b.runs) as total_runs
FROM boxscore b
INNER JOIN games g ON b.game_id = g.game_id
INNER JOIN teams ht ON g.home_team_id = ht.team_id
INNER JOIN teams at ON g.away_team_id = at.team_id
WHERE g.game_date > '2025-08-15'
GROUP BY g.game_id, g.game_date, ht.team_name, at.team_name
ORDER BY total_hits DESC;
