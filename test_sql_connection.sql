-- Test SQL Server connection with Windows Authentication
-- This file tests the connection to localhost SQL Server

SELECT 
    @@SERVERNAME as ServerName,
    DB_NAME() as CurrentDatabase,
    SYSTEM_USER as WindowsUser,
    GETDATE() as CurrentDateTime;

-- Show available databases
SELECT name as DatabaseName 
FROM sys.databases 
WHERE database_id > 4  -- Exclude system databases
ORDER BY name;

-- Show basic mlb_data statistics
SELECT 
    'games' as TableName,
    COUNT(*) as RecordCount
FROM games
UNION ALL
SELECT 
    'boxscore' as TableName,
    COUNT(*) as RecordCount  
FROM boxscore
UNION ALL
SELECT 
    'players' as TableName,
    COUNT(*) as RecordCount
FROM players
ORDER BY TableName;
