#!/usr/bin/env python3
"""
Microsoft Fabric Setup Helper
=============================

This script provides multiple options for setting up your MLB data pipeline
with Microsoft Fabric based on your current permissions.

Current Status: ✅ Connection Working, ❌ Table Creation Denied
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append('src')

from database.fabric_connection import FabricConnection

def generate_table_creation_sql():
    """Generate the SQL statements needed to create tables."""
    print("📋 Fabric Table Creation SQL")
    print("=" * 50)
    print("Copy the following SQL statements to create tables in Fabric:")
    print("(You can run these in the Fabric SQL Analytics endpoint or ask an admin)")
    
    sql_statements = [
        """-- Teams table
CREATE TABLE teams (
    team_id INT NOT NULL,
    team_name VARCHAR(100),
    abbreviation VARCHAR(10),
    league VARCHAR(50),
    division VARCHAR(50),
    created_at DATETIME2(6)
);""",
        
        """-- Games table  
CREATE TABLE games (
    game_id INT NOT NULL,
    game_date DATE,
    home_team_id INT,
    away_team_id INT,
    home_score INT,
    away_score INT,
    inning INT,
    inning_state VARCHAR(20),
    game_status VARCHAR(50),
    game_type VARCHAR(10),
    series_description VARCHAR(100),
    official_date DATE,
    created_at DATETIME2(6)
);""",
        
        """-- Players table
CREATE TABLE players (
    player_id INT NOT NULL,
    player_name VARCHAR(100),
    team_id INT,
    position VARCHAR(50),
    created_at DATETIME2(6)
);""",
        
        """-- Boxscore table with enhanced statistics
CREATE TABLE boxscore (
    id INT IDENTITY(1,1),
    game_id INT,
    player_id INT,
    team_id INT,
    at_bats INT,
    runs INT,
    hits INT,
    doubles INT,
    triples INT,
    home_runs INT,
    rbi INT,
    walks INT,
    strikeouts INT,
    stolen_bases INT,
    caught_stealing INT,
    hit_by_pitch INT,
    sacrifice_flies INT,
    sacrifice_bunts INT,
    game_date DATE,
    created_at DATETIME2(6)
);""",
        
        """-- Raw JSON backup table
CREATE TABLE raw_json_data (
    id INT IDENTITY(1,1),
    game_id INT,
    data_type VARCHAR(50),
    json_data VARCHAR(MAX),
    extraction_timestamp DATETIME2(6)
);"""
    ]
    
    for i, sql in enumerate(sql_statements, 1):
        print(f"\n-- Statement {i}/{len(sql_statements)}")
        print(sql)
    
    print(f"\n✅ Generated {len(sql_statements)} table creation statements")
    print("\n💡 To create these tables:")
    print("   1. Copy the SQL above")
    print("   2. Go to your Fabric workspace")
    print("   3. Open SQL Analytics endpoint")
    print("   4. Run each CREATE TABLE statement")
    print("   5. Or ask your workspace admin to run them")

def test_existing_tables():
    """Test if we can work with any existing tables."""
    print("\n🔍 Checking for Existing Tables")
    print("=" * 50)
    
    fabric_conn = FabricConnection()
    
    try:
        if not fabric_conn.connect():
            return False
        
        # Check what tables exist
        result = fabric_conn.fetch_results("""
            SELECT 
                t.TABLE_SCHEMA,
                t.TABLE_NAME,
                COUNT(c.COLUMN_NAME) as column_count
            FROM INFORMATION_SCHEMA.TABLES t
            LEFT JOIN INFORMATION_SCHEMA.COLUMNS c ON t.TABLE_NAME = c.TABLE_NAME
            WHERE t.TABLE_TYPE = 'BASE TABLE'
            GROUP BY t.TABLE_SCHEMA, t.TABLE_NAME
            ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME
        """)
        
        if result:
            print(f"📊 Found {len(result)} existing tables:")
            for row in result:
                print(f"   - {row[0]}.{row[1]} ({row[2]} columns)")
            
            # Check if our target tables exist
            table_names = [row[1].lower() for row in result]
            required_tables = ['teams', 'games', 'players', 'boxscore', 'raw_json_data']
            
            existing_required = [table for table in required_tables if table in table_names]
            missing_required = [table for table in required_tables if table not in table_names]
            
            if existing_required:
                print(f"\n✅ Found {len(existing_required)} required tables:")
                for table in existing_required:
                    print(f"   - {table}")
            
            if missing_required:
                print(f"\n❌ Missing {len(missing_required)} required tables:")
                for table in missing_required:
                    print(f"   - {table}")
                    
        else:
            print("   No tables found in workspace")
            
        fabric_conn.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False

def show_next_steps():
    """Show what to do next based on current permissions."""
    print("\n🚀 Next Steps")
    print("=" * 50)
    print("Based on your current permissions, here are your options:")
    print("\n📋 Option 1: Request Table Creation Permissions")
    print("   - Contact your Fabric workspace administrator")
    print("   - Request 'Contributor' role or 'SQL Admin' permissions")
    print("   - Once granted, run: python setup_fabric.py")
    
    print("\n📋 Option 2: Manual Table Creation")
    print("   - Use the SQL statements generated above")
    print("   - Run them in Fabric SQL Analytics endpoint")
    print("   - Or ask an admin to create the tables for you")
    
    print("\n📋 Option 3: Use Existing Tables (if available)")
    print("   - If tables already exist, you can start loading data")
    print("   - Run: python load_fabric_date_range_data.py --start 2025-08-31 --end 2025-08-31")
    
    print("\n📋 Option 4: Alternative Data Loading")
    print("   - Export data to CSV files")
    print("   - Upload CSV files to Fabric via the web interface")
    print("   - Import data using Fabric's data import tools")

if __name__ == "__main__":
    print("🚀 Microsoft Fabric Setup Helper")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Check current status
    test_existing_tables()
    
    # Generate SQL for manual creation
    generate_table_creation_sql()
    
    # Show next steps
    show_next_steps()
    
    print("\n✅ Fabric setup analysis complete!")
    print("💡 Choose the option that works best for your permissions.")
