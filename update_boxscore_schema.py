#!/usr/bin/env python3
"""
Update Boxscore Schema
Adds doubles, triples, and home_runs columns to the existing boxscore table.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection

def update_boxscore_schema():
    """Add new columns to boxscore table if they don't exist."""
    db = DatabaseConnection()
    
    # SQL commands to add columns
    updates = [
        # Add doubles column
        """
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
        """,
        
        # Add triples column
        """
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
        """,
        
        # Add home_runs column
        """
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
        """
    ]
    
    try:
        print("Updating boxscore table schema...")
        
        for i, update_sql in enumerate(updates, 1):
            print(f"Executing update {i}/3...")
            db.execute_query(update_sql)
        
        # Verify the schema
        verify_sql = """
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'boxscore'
        ORDER BY ORDINAL_POSITION
        """
        
        print("\nVerifying updated schema:")
        result = db.fetch_results(verify_sql)
        
        print("\nBoxscore table columns:")
        print("-" * 60)
        print(f"{'Column Name':<15} {'Data Type':<12} {'Nullable':<10} {'Default':<10}")
        print("-" * 60)
        
        for row in result:
            column_name = row[0]
            data_type = row[1]
            is_nullable = row[2]
            column_default = row[3] if row[3] else ''
            print(f"{column_name:<15} {data_type:<12} {is_nullable:<10} {column_default:<10}")
        
        print(f"\nSchema update completed successfully!")
        print(f"Total columns in boxscore table: {len(result)}")
        
    except Exception as e:
        print(f"Error updating schema: {e}")
        return False
    
    finally:
        db.disconnect()
    
    return True

if __name__ == "__main__":
    success = update_boxscore_schema()
    if success:
        print("\n✅ Boxscore schema update completed!")
    else:
        print("\n❌ Schema update failed!")
