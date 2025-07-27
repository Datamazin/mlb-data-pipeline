-- =====================================================
-- Add Doubles, Triples, and Home Runs to Boxscore Table
-- =====================================================
-- Run this script to add new columns to existing boxscore table

USE mlb_data;
GO

-- Add doubles column if it doesn't exist
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'boxscore' AND COLUMN_NAME = 'doubles')
BEGIN
    ALTER TABLE boxscore ADD doubles INT DEFAULT 0;
    PRINT 'Added doubles column to boxscore table';
END
ELSE
BEGIN
    PRINT 'Doubles column already exists in boxscore table';
END

-- Add triples column if it doesn't exist
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'boxscore' AND COLUMN_NAME = 'triples')
BEGIN
    ALTER TABLE boxscore ADD triples INT DEFAULT 0;
    PRINT 'Added triples column to boxscore table';
END
ELSE
BEGIN
    PRINT 'Triples column already exists in boxscore table';
END

-- Add home_runs column if it doesn't exist
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'boxscore' AND COLUMN_NAME = 'home_runs')
BEGIN
    ALTER TABLE boxscore ADD home_runs INT DEFAULT 0;
    PRINT 'Added home_runs column to boxscore table';
END
ELSE
BEGIN
    PRINT 'Home_runs column already exists in boxscore table';
END

-- Verify the new columns
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'boxscore'
ORDER BY ORDINAL_POSITION;

PRINT 'Boxscore table schema updated successfully!';
