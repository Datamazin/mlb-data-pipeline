-- MLB Data Bulk Load Script for Microsoft Fabric
-- Run this after creating tables and uploading CSV files


-- Bulk load teams data
BULK INSERT teams
FROM 'teams.csv'  
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);


-- Bulk load players data
BULK INSERT players
FROM 'players.csv'
WITH (
    FIELDTERMINATOR = ',', 
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);


-- Bulk load games data
BULK INSERT games
FROM 'games.csv'
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n', 
    FIRSTROW = 2,
    FIRE_TRIGGERS
);


-- Bulk load boxscore data (with enhanced statistics!)
BULK INSERT boxscore  
FROM 'boxscore.csv'
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);


-- Verify data loaded correctly
SELECT 'teams' as table_name, COUNT(*) as record_count FROM teams
UNION ALL
SELECT 'players', COUNT(*) FROM players  
UNION ALL
SELECT 'games', COUNT(*) FROM games
UNION ALL  
SELECT 'boxscore', COUNT(*) FROM boxscore;

-- Check enhanced statistics
SELECT 
    'Stolen Bases' as stat_type,
    COUNT(*) as players_with_stat,
    SUM(stolen_bases) as total_stat
FROM boxscore 
WHERE stolen_bases > 0
UNION ALL
SELECT 
    'Caught Stealing' as stat_type,
    COUNT(*) as players_with_stat, 
    SUM(caught_stealing) as total_stat
FROM boxscore
WHERE caught_stealing > 0;
