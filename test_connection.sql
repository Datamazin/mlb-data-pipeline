-- =====================================================
-- MLB DATABASE CONNECTION TEST
-- =====================================================
-- Run this file in VS Code to test your connection

-- Basic server and database info
SELECT 
    @@SERVERNAME AS ServerName,
    DB_NAME() AS DatabaseName,
    GETDATE() AS CurrentDateTime;

-- Database tables overview
SELECT 
    TABLE_NAME,
    TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES
ORDER BY TABLE_NAME;

-- Quick data sample
SELECT TOP 5
    p.player_name,
    t.team_name,
    COUNT(b.game_id) as games_played
FROM boxscore b
INNER JOIN players p ON b.player_id = p.player_id
INNER JOIN teams t ON b.team_id = t.team_id
GROUP BY p.player_name, t.team_name
ORDER BY games_played DESC;

-- Database statistics
SELECT 
    'Teams' as TableName, COUNT(*) as RecordCount FROM teams
UNION ALL
SELECT 'Players', COUNT(*) FROM players
UNION ALL  
SELECT 'Games', COUNT(*) FROM games
UNION ALL
SELECT 'Boxscore Records', COUNT(*) FROM boxscore;
