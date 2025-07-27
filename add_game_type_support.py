#!/usr/bin/env python3
"""
Add Game Type Support to MLB Data Pipeline
Adds game_type and series_description columns to the games table and updates the data processing.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection

def add_game_type_support():
    """Add game type fields to the games table."""
    db = DatabaseConnection()
    
    # SQL commands to add game type columns
    updates = [
        # Add game_type column
        """
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
                       WHERE TABLE_NAME = 'games' AND COLUMN_NAME = 'game_type')    
        BEGIN
            ALTER TABLE games ADD game_type NVARCHAR(10) DEFAULT NULL;
            PRINT 'Added game_type column to games table';
        END
        ELSE
        BEGIN
            PRINT 'Game_type column already exists in games table';
        END
        """,
        
        # Add series_description column
        """
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS
                       WHERE TABLE_NAME = 'games' AND COLUMN_NAME = 'series_description')    
        BEGIN
            ALTER TABLE games ADD series_description NVARCHAR(100) DEFAULT NULL;
            PRINT 'Added series_description column to games table';
        END
        ELSE
        BEGIN
            PRINT 'Series_description column already exists in games table';
        END
        """,
        
        # Add official_date column
        """
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS
                       WHERE TABLE_NAME = 'games' AND COLUMN_NAME = 'official_date')    
        BEGIN
            ALTER TABLE games ADD official_date DATE DEFAULT NULL;
            PRINT 'Added official_date column to games table';
        END
        ELSE
        BEGIN
            PRINT 'Official_date column already exists in games table';
        END
        """
    ]
    
    try:
        print("Adding game type support to games table...")
        
        for i, update_sql in enumerate(updates, 1):
            print(f"Executing update {i}/3...")
            db.execute_query(update_sql)
        
        # Verify the schema
        verify_sql = """
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'games'
        ORDER BY ORDINAL_POSITION
        """
        
        print("\nVerifying updated schema:")
        result = db.fetch_results(verify_sql)
        
        print("\nGames table columns:")
        print("-" * 70)
        print(f"{'Column Name':<20} {'Data Type':<15} {'Nullable':<10} {'Default':<15}")
        print("-" * 70)
        
        for row in result:
            column_name = row[0]
            data_type = row[1]
            is_nullable = row[2]
            column_default = row[3] if row[3] else ''
            print(f"{column_name:<20} {data_type:<15} {is_nullable:<10} {column_default:<15}")
        
        print(f"\nSchema update completed successfully!")
        print(f"Total columns in games table: {len(result)}")
        
        # Show game type mappings
        print("\n📋 GAME TYPE CODES:")
        print("-" * 70)
        print("S = Spring Training / Preseason")
        print("R = Regular Season")  
        print("F = Wild Card / First Round")
        print("D = Division Series")
        print("L = League Championship Series")
        print("W = World Series")
        print("A = All-Star Game")
        
    except Exception as e:
        print(f"Error updating schema: {e}")
        return False
    
    finally:
        db.disconnect()
    
    return True

if __name__ == "__main__":
    success = add_game_type_support()
    if success:
        print("\n✅ Game type support added successfully!")
    else:
        print("\n❌ Failed to add game type support!")
