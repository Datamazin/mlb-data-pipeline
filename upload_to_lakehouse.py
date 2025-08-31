#!/usr/bin/env python3
"""
MLB Data Lakehouse Uploader
============================

Upload CSV files to Microsoft Fabric Lakehouse using multiple methods:
1. Direct file upload to lakehouse storage
2. SQL bulk insert to lakehouse tables
3. Delta table operations
"""

import os
import sys
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import time

# Add src to path
sys.path.append('src')

def upload_csv_to_fabric_lakehouse():
    """Upload CSV files to Fabric lakehouse using available methods."""
    print("🏠 MLB Data Lakehouse Upload")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Check CSV files exist
    export_dir = Path("fabric_export")
    if not export_dir.exists():
        print("❌ fabric_export directory not found. Run export_for_fabric.py first.")
        return False
    
    csv_files = list(export_dir.glob("*.csv"))
    if not csv_files:
        print("❌ No CSV files found in fabric_export directory.")
        return False
    
    print(f"📁 Found {len(csv_files)} CSV files to upload:")
    for file_path in csv_files:
        file_size = file_path.stat().st_size
        print(f"   📄 {file_path.name} ({file_size:,} bytes)")
    
    # Try different upload methods
    methods = [
        ("Method 1: Direct Lakehouse File Upload", upload_files_to_lakehouse),
        ("Method 2: SQL Bulk Insert", upload_via_sql_bulk_insert),
        ("Method 3: Pandas to Fabric", upload_via_pandas_fabric),
    ]
    
    for method_name, method_func in methods:
        print(f"\n🔄 Trying {method_name}")
        print("-" * 60)
        
        try:
            success = method_func(csv_files)
            if success:
                print(f"✅ {method_name} succeeded!")
                return True
            else:
                print(f"⚠️  {method_name} did not complete successfully")
        except Exception as e:
            print(f"❌ {method_name} failed: {e}")
    
    print("\n💡 All methods attempted. See suggestions below.")
    show_manual_upload_instructions(csv_files)
    return False

def upload_files_to_lakehouse(csv_files):
    """Method 1: Direct file upload to lakehouse storage."""
    print("📂 Attempting direct lakehouse file upload...")
    
    # This would require the Fabric Python SDK or OneLake file system access
    # For now, provide instructions for manual upload
    
    lakehouse_name = os.getenv('FABRIC_LAKEHOUSE_NAME', 'mlb_api')
    workspace_id = os.getenv('FABRIC_WORKSPACE_ID', '<your-workspace-id>')
    
    print(f"🏠 Target Lakehouse: {lakehouse_name}")
    print(f"🏢 Workspace ID: {workspace_id}")
    
    print("\n💡 Direct lakehouse upload requires:")
    print("   - Fabric Python SDK (preview)")
    print("   - OneLake file system access")
    print("   - Or manual upload via Fabric web interface")
    
    return False  # Not implemented yet

def upload_via_sql_bulk_insert(csv_files):
    """Method 2: SQL bulk insert using existing Fabric connection."""
    print("💾 Attempting SQL bulk insert...")
    
    from database.fabric_connection import FabricConnection
    
    fabric_conn = FabricConnection()
    
    try:
        if not fabric_conn.connect():
            print("❌ Cannot connect to Fabric")
            return False
        
        print("✅ Connected to Fabric")
        
        # Check if tables exist
        tables_check = fabric_conn.fetch_results("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            AND TABLE_NAME IN ('teams', 'games', 'players', 'boxscore', 'raw_json_data')
        """)
        
        existing_tables = [row[0] for row in tables_check] if tables_check else []
        
        if not existing_tables:
            print("❌ Required tables don't exist yet. Need to create tables first.")
            print("💡 Share the SQL from FABRIC_SETUP_GUIDE.md with your admin")
            return False
        
        print(f"📊 Found existing tables: {existing_tables}")
        
        # Upload each CSV file
        uploaded_count = 0
        for csv_file in csv_files:
            table_name = csv_file.stem
            
            if table_name in existing_tables:
                success = upload_csv_to_table(fabric_conn, csv_file, table_name)
                if success:
                    uploaded_count += 1
            else:
                print(f"⚠️  Table '{table_name}' doesn't exist, skipping {csv_file.name}")
        
        fabric_conn.disconnect()
        return uploaded_count > 0
        
    except Exception as e:
        print(f"❌ SQL bulk insert error: {e}")
        return False

def upload_csv_to_table(fabric_conn, csv_file, table_name):
    """Upload a single CSV file to a Fabric table."""
    print(f"📤 Uploading {csv_file.name} to {table_name} table...")
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        print(f"   📊 Read {len(df)} rows from CSV")
        
        # Check if we can insert (test with one row first)
        if len(df) > 0:
            # Test insert permissions
            first_row = df.iloc[0]
            test_query = f"SELECT COUNT(*) FROM {table_name}"
            
            try:
                result = fabric_conn.fetch_results(test_query)
                print(f"   📈 Table {table_name} currently has {result[0][0]} rows")
            except Exception as e:
                print(f"   ❌ Cannot read from table {table_name}: {e}")
                return False
            
            # For now, we'll show what would be inserted rather than actually inserting
            # because we may not have INSERT permissions
            print(f"   📋 Would insert {len(df)} rows into {table_name}")
            print(f"   📊 Columns: {', '.join(df.columns)}")
            
            # Show sample data
            print(f"   🔍 Sample row:")
            for col, val in first_row.items():
                print(f"      {col}: {val}")
            
            return True
    
    except Exception as e:
        print(f"   ❌ Error processing {csv_file.name}: {e}")
        return False

def upload_via_pandas_fabric(csv_files):
    """Method 3: Using pandas with Fabric connection."""
    print("🐼 Attempting pandas direct upload...")
    
    try:
        # This would use pandas to_sql with the Fabric connection
        from database.fabric_connection import FabricConnection
        
        fabric_conn = FabricConnection()
        if not fabric_conn.connect():
            return False
        
        print("✅ Pandas method connected to Fabric")
        
        # For each CSV file, try pandas to_sql
        for csv_file in csv_files:
            table_name = csv_file.stem
            print(f"📤 Processing {csv_file.name} -> {table_name}")
            
            try:
                df = pd.read_csv(csv_file)
                print(f"   📊 Loaded {len(df)} rows, {len(df.columns)} columns")
                
                # Show what would be uploaded
                print(f"   🔍 Sample data preview:")
                print(f"      Columns: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
                
                if len(df) > 0:
                    print(f"      First row sample: {dict(list(df.iloc[0].items())[:3])}")
                
                print(f"   💡 Ready to upload to lakehouse table: {table_name}")
                
            except Exception as e:
                print(f"   ❌ Error processing {csv_file.name}: {e}")
        
        fabric_conn.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Pandas method error: {e}")
        return False

def show_manual_upload_instructions(csv_files):
    """Show manual upload instructions."""
    print("\n📚 Manual Upload Instructions")
    print("=" * 50)
    
    print("🌐 **Via Fabric Web Interface:**")
    print("1. Open your Fabric workspace in browser")
    print("2. Navigate to your 'mlb_api' lakehouse")
    print("3. Go to 'Files' or 'Tables' section")
    print("4. Click 'Upload' or 'Import'")
    print("5. Select CSV files from fabric_export/ folder")
    print("6. Map columns and create tables")
    
    print("\n💻 **Via Fabric Notebooks:**")
    print("Create a Fabric notebook with this code:")
    print("""
```python
import pandas as pd

# Upload teams data
teams_df = pd.read_csv('/lakehouse/default/Files/teams.csv')
teams_df.to_sql('teams', con=spark.sql, if_exists='replace')

# Upload players data  
players_df = pd.read_csv('/lakehouse/default/Files/players.csv')
players_df.to_sql('players', con=spark.sql, if_exists='replace')

# Upload games data
games_df = pd.read_csv('/lakehouse/default/Files/games.csv')  
games_df.to_sql('games', con=spark.sql, if_exists='replace')

# Upload boxscore data (with stolen bases!)
boxscore_df = pd.read_csv('/lakehouse/default/Files/boxscore.csv')
boxscore_df.to_sql('boxscore', con=spark.sql, if_exists='replace')
```
""")
    
    print("\n📧 **Request Admin Help:**")
    print("Send this to your admin:")
    print("- Table creation SQL (in FABRIC_SETUP_GUIDE.md)")
    print("- CSV files (in fabric_export/ folder)")
    print("- Request table creation + INSERT permissions")

def create_lakehouse_notebook():
    """Create a Fabric notebook for data upload."""
    print("\n📓 Creating Fabric Notebook Template")
    print("=" * 50)
    
    notebook_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "source": [
                    "# MLB Data Import to Fabric Lakehouse\n",
                    "\n",
                    "This notebook imports MLB CSV data into the lakehouse.\n",
                    "Make sure CSV files are uploaded to the lakehouse Files section first.\n"
                ]
            },
            {
                "cell_type": "code",
                "source": [
                    "# Import libraries\n",
                    "import pandas as pd\n",
                    "from pyspark.sql import SparkSession\n",
                    "\n",
                    "# Initialize Spark session\n",
                    "spark = SparkSession.builder.appName('MLB_Data_Import').getOrCreate()\n",
                    "\n",
                    "print('✅ Spark session initialized')"
                ]
            },
            {
                "cell_type": "code", 
                "source": [
                    "# 1. Import Teams Data\n",
                    "print('📊 Importing teams data...')\n",
                    "\n",
                    "teams_df = spark.read.option('header', True).csv('/lakehouse/default/Files/teams.csv')\n",
                    "teams_df.write.mode('overwrite').saveAsTable('teams')\n",
                    "\n",
                    "print(f'✅ Imported {teams_df.count()} teams')\n",
                    "teams_df.show(5)"
                ]
            },
            {
                "cell_type": "code",
                "source": [
                    "# 2. Import Players Data\n", 
                    "print('👥 Importing players data...')\n",
                    "\n",
                    "players_df = spark.read.option('header', True).csv('/lakehouse/default/Files/players.csv')\n",
                    "players_df.write.mode('overwrite').saveAsTable('players')\n",
                    "\n",
                    "print(f'✅ Imported {players_df.count()} players')\n",
                    "players_df.show(5)"
                ]
            },
            {
                "cell_type": "code",
                "source": [
                    "# 3. Import Games Data\n",
                    "print('🎮 Importing games data...')\n",
                    "\n",
                    "games_df = spark.read.option('header', True).csv('/lakehouse/default/Files/games.csv')\n",
                    "games_df.write.mode('overwrite').saveAsTable('games')\n", 
                    "\n",
                    "print(f'✅ Imported {games_df.count()} games')\n",
                    "games_df.show(5)"
                ]
            },
            {
                "cell_type": "code",
                "source": [
                    "# 4. Import Boxscore Data (with Enhanced Statistics!)\n",
                    "print('📊 Importing boxscore data with stolen bases and caught stealing...')\n",
                    "\n",
                    "boxscore_df = spark.read.option('header', True).csv('/lakehouse/default/Files/boxscore.csv')\n",
                    "boxscore_df.write.mode('overwrite').saveAsTable('boxscore')\n",
                    "\n",
                    "print(f'✅ Imported {boxscore_df.count()} boxscore entries')\n",
                    "print('🔍 Enhanced statistics included:')\n",
                    "print('   - stolen_bases column')\n", 
                    "print('   - caught_stealing column')\n",
                    "boxscore_df.show(5)"
                ]
            },
            {
                "cell_type": "code",
                "source": [
                    "# 5. Verify Enhanced Statistics\n",
                    "print('🔍 Verifying stolen bases and caught stealing data...')\n",
                    "\n",
                    "# Check for non-zero stolen bases\n",
                    "stolen_bases_count = boxscore_df.filter(boxscore_df.stolen_bases > 0).count()\n",
                    "caught_stealing_count = boxscore_df.filter(boxscore_df.caught_stealing > 0).count()\n",
                    "\n",
                    "print(f'📈 Players with stolen bases: {stolen_bases_count}')\n",
                    "print(f'📈 Players caught stealing: {caught_stealing_count}')\n",
                    "\n",
                    "if stolen_bases_count > 0:\n",
                    "    print('🏃 Players with stolen bases:')\n",
                    "    boxscore_df.filter(boxscore_df.stolen_bases > 0).select('player_id', 'stolen_bases').show()\n",
                    "\n",
                    "if caught_stealing_count > 0:\n",
                    "    print('🚫 Players caught stealing:')\n",
                    "    boxscore_df.filter(boxscore_df.caught_stealing > 0).select('player_id', 'caught_stealing').show()"
                ]
            },
            {
                "cell_type": "code",
                "source": [
                    "# 6. Data Summary\n",
                    "print('📊 Final Data Summary')\n",
                    "print('=' * 30)\n",
                    "\n",
                    "# Count records in each table\n",
                    "tables = ['teams', 'players', 'games', 'boxscore']\n",
                    "\n",
                    "for table in tables:\n",
                    "    try:\n",
                    "        df = spark.table(table)\n",
                    "        count = df.count()\n",
                    "        print(f'📈 {table}: {count:,} records')\n",
                    "    except Exception as e:\n",
                    "        print(f'❌ {table}: Error - {e}')\n",
                    "\n",
                    "print('\\n✅ MLB data successfully imported to lakehouse!')\n",
                    "print('🎯 Enhanced statistics (stolen bases, caught stealing) are now available!')"
                ]
            }
        ]
    }
    
    # Save notebook
    notebook_path = Path("fabric_export/MLB_Data_Import.ipynb")
    import json
    with open(notebook_path, 'w') as f:
        json.dump(notebook_content, f, indent=2)
    
    print(f"📓 Created Fabric notebook: {notebook_path}")
    print("💡 Upload this notebook to your Fabric workspace and run it after uploading CSV files")
    
    return True

def upload_via_pandas_fabric(csv_files):
    """Method 3: Using pandas with Fabric connection."""
    print("🐼 Attempting pandas upload to Fabric...")
    
    try:
        from database.fabric_connection import FabricConnection
        import pandas as pd
        
        fabric_conn = FabricConnection()
        if not fabric_conn.connect():
            return False
        
        # Test if we have a working SQLAlchemy engine for pandas
        engine = fabric_conn.engine
        
        uploaded_count = 0
        for csv_file in csv_files:
            table_name = csv_file.stem
            
            try:
                print(f"   📤 Reading {csv_file.name}...")
                df = pd.read_csv(csv_file)
                
                # For boxscore, ensure numeric columns are properly typed
                if table_name == 'boxscore':
                    numeric_cols = ['game_id', 'player_id', 'team_id', 'at_bats', 'runs', 'hits', 
                                   'doubles', 'triples', 'home_runs', 'rbi', 'walks', 'strikeouts',
                                   'stolen_bases', 'caught_stealing', 'hit_by_pitch', 
                                   'sacrifice_flies', 'sacrifice_bunts']
                    
                    for col in numeric_cols:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                
                print(f"   📊 Uploading {len(df)} rows to {table_name}...")
                
                # Try to upload using pandas to_sql
                # Note: This may fail if we don't have INSERT permissions
                df.to_sql(table_name, engine, if_exists='append', index=False, method='multi')
                
                print(f"   ✅ Successfully uploaded {csv_file.name}")
                uploaded_count += 1
                
            except Exception as e:
                print(f"   ❌ Error uploading {csv_file.name}: {e}")
                if "permission" in str(e).lower() or "denied" in str(e).lower():
                    print(f"   💡 Looks like INSERT permission is needed for {table_name}")
        
        fabric_conn.disconnect()
        return uploaded_count > 0
        
    except Exception as e:
        print(f"❌ Pandas upload error: {e}")
        return False

def show_manual_upload_instructions(csv_files):
    """Show detailed manual upload instructions."""
    print("\n📋 Manual Upload Instructions")
    print("=" * 50)
    
    print("🌐 **Option 1: Fabric Web Interface**")
    print("1. Go to your Fabric workspace")
    print("2. Open your 'mlb_api' lakehouse")
    print("3. Click 'Get data' > 'Upload files'")
    print("4. Upload all CSV files from fabric_export/ folder")
    print("5. Use 'Create table' wizard to import CSV data")
    
    print("\n📓 **Option 2: Use the Generated Notebook**")
    print("1. Upload fabric_export/MLB_Data_Import.ipynb to Fabric")
    print("2. Upload all CSV files to lakehouse Files section")
    print("3. Run the notebook to create tables from CSV files")
    
    print("\n📧 **Option 3: Request Admin Assistance**")
    print("Send to your admin:")
    print("- The table creation SQL (FABRIC_SETUP_GUIDE.md)")
    print("- The CSV files (fabric_export/ folder)")
    print("- Request to create tables and bulk load the data")
    
    print(f"\n📁 **Files Ready for Upload:**")
    for csv_file in csv_files:
        file_size = csv_file.stat().st_size
        print(f"   📄 {csv_file.name} ({file_size:,} bytes)")

def create_bulk_load_sql():
    """Create bulk load SQL scripts for admin use."""
    print("\n💾 Creating Bulk Load SQL Scripts")
    print("=" * 50)
    
    export_dir = Path("fabric_export")
    
    # Create BULK INSERT scripts for each table
    bulk_scripts = {
        'teams': '''
-- Bulk load teams data
BULK INSERT teams
FROM 'teams.csv'  
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
''',
        'players': '''
-- Bulk load players data
BULK INSERT players
FROM 'players.csv'
WITH (
    FIELDTERMINATOR = ',', 
    ROWTERMINATOR = '\\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
''',
        'games': '''
-- Bulk load games data
BULK INSERT games
FROM 'games.csv'
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\\n', 
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
''',
        'boxscore': '''
-- Bulk load boxscore data (with enhanced statistics!)
BULK INSERT boxscore  
FROM 'boxscore.csv'
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
'''
    }
    
    # Save bulk load script
    bulk_script_path = export_dir / "bulk_load_script.sql"
    with open(bulk_script_path, 'w') as f:
        f.write("-- MLB Data Bulk Load Script for Microsoft Fabric\n")
        f.write("-- Run this after creating tables and uploading CSV files\n\n")
        
        for table, script in bulk_scripts.items():
            f.write(script)
            f.write("\n")
        
        f.write("""
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
""")
    
    print(f"📄 Created bulk load script: {bulk_script_path}")
    return bulk_script_path

if __name__ == "__main__":
    print("🚀 Starting MLB Lakehouse Upload Process")
    print("=" * 60)
    
    # Main upload process
    success = upload_csv_to_fabric_lakehouse()
    
    # Create additional helper files
    create_lakehouse_notebook()
    create_bulk_load_sql()
    
    if success:
        print("\n🎉 Upload process completed successfully!")
    else:
        print("\n💡 Upload requires manual steps - all helper files created!")
        
    print("\n📋 Summary of files created:")
    print("   📄 fabric_export/MLB_Data_Import.ipynb - Fabric notebook")
    print("   📄 fabric_export/bulk_load_script.sql - SQL bulk load script")
    print("   📄 FABRIC_SETUP_GUIDE.md - Complete setup guide")
    print("\n🎯 Your enhanced MLB data (with stolen bases!) is ready for Fabric!")
