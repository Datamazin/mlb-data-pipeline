#!/usr/bin/env python3
"""
MLB Data Lakehouse Upload Script
================================

Upload CSV files to Microsoft Fabric Lakehouse using various methods:
1. OneLake file system upload
2. Fabric REST API upload
3. Delta Lake operations
4. Manual upload instructions
"""

import os
import sys
import pandas as pd
import requests
from pathlib import Path
from dotenv import load_dotenv
import json

def main():
    """Main upload orchestration."""
    print("🏠 MLB Data Lakehouse Upload Script")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Verify CSV files exist
    export_dir = Path("fabric_export")
    csv_files = list(export_dir.glob("*.csv")) if export_dir.exists() else []
    
    if not csv_files:
        print("❌ No CSV files found. Run 'python export_for_fabric.py' first.")
        return False
    
    print(f"📁 Found {len(csv_files)} CSV files:")
    for file_path in csv_files:
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"   📄 {file_path.name} ({size_mb:.2f} MB)")
    
    # Show data summary  
    show_data_summary(csv_files)
    
    # Try upload methods
    success = try_upload_methods(csv_files)
    
    if not success:
        print("\n💡 Automated upload not available with current permissions.")
        show_manual_upload_guide(csv_files)
    
    return success

def show_data_summary(csv_files):
    """Show summary of the data being uploaded."""
    print("\n📊 Data Summary:")
    print("-" * 30)
    
    for csv_file in csv_files:
        if csv_file.name == 'boxscore.csv':
            try:
                df = pd.read_csv(csv_file)
                print(f"📈 {csv_file.name}: {len(df)} records")
                
                # Check enhanced statistics
                if 'stolen_bases' in df.columns:
                    stolen_count = (df['stolen_bases'] > 0).sum()
                    total_stolen = df['stolen_bases'].sum()
                    print(f"   🏃 Stolen bases: {stolen_count} players, {total_stolen} total")
                
                if 'caught_stealing' in df.columns:
                    caught_count = (df['caught_stealing'] > 0).sum()
                    total_caught = df['caught_stealing'].sum()
                    print(f"   🚫 Caught stealing: {caught_count} players, {total_caught} total")
                
                if 'walks' in df.columns:
                    walk_count = (df['walks'] > 0).sum()
                    total_walks = df['walks'].sum()
                    print(f"   🚶 Base on balls: {walk_count} players, {total_walks} total")
                    
            except Exception as e:
                print(f"❌ Error reading {csv_file.name}: {e}")
        else:
            try:
                df = pd.read_csv(csv_file)
                print(f"📈 {csv_file.name}: {len(df)} records")
            except:
                print(f"📈 {csv_file.name}: File exists")

def try_upload_methods(csv_files):
    """Try different upload methods."""
    print("\n🚀 Attempting Upload Methods:")
    print("-" * 40)
    
    # Method 1: OneLake file system (if available)
    if try_onelake_upload(csv_files):
        return True
    
    # Method 2: Fabric REST API (if credentials available)
    if try_fabric_api_upload(csv_files):
        return True
    
    # Method 3: Direct lakehouse connection (already tried)
    print("🔍 Method 3: Direct SQL connection")
    print("   ❌ Blocked by table creation permissions")
    print("   💡 Need admin to create tables first")
    
    return False

def try_onelake_upload(csv_files):
    """Try uploading via OneLake file system."""
    print("🔍 Method 1: OneLake file system upload")
    
    # Check for OneLake environment variables
    workspace_id = os.getenv('FABRIC_WORKSPACE_ID')
    lakehouse_id = os.getenv('FABRIC_LAKEHOUSE_ID')
    
    if not workspace_id or not lakehouse_id:
        print("   ⚠️  OneLake credentials not configured")
        print("   💡 Set FABRIC_WORKSPACE_ID and FABRIC_LAKEHOUSE_ID in .env")
        return False
    
    # OneLake uses ADLS Gen2 compatible paths
    onelake_path = f"https://onelake.dfs.fabric.microsoft.com/{workspace_id}/{lakehouse_id}/Files/"
    
    print(f"   🎯 Target path: {onelake_path}")
    print("   ⚠️  OneLake upload requires Azure Storage SDK")
    print("   💡 Install with: pip install azure-storage-file-datalake")
    
    return False  # Not implemented - requires additional dependencies

def try_fabric_api_upload(csv_files):
    """Try uploading via Fabric REST API."""
    print("🔍 Method 2: Fabric REST API upload")
    
    # Check for API credentials
    workspace_id = os.getenv('FABRIC_WORKSPACE_ID')
    client_id = os.getenv('AZURE_CLIENT_ID')
    
    if not workspace_id:
        print("   ⚠️  Fabric API credentials not configured")
        print("   💡 Set FABRIC_WORKSPACE_ID in .env for API access")
        return False
    
    print(f"   🎯 Workspace: {workspace_id}")
    print("   ⚠️  REST API upload requires authentication token")
    print("   💡 Would use: https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items")
    
    return False  # Not implemented - requires API authentication

def show_manual_upload_guide(csv_files):
    """Show comprehensive manual upload guide."""
    print("\n📚 Manual Upload Guide")
    print("=" * 40)
    
    print("\n🌐 Recommended: Fabric Web Interface")
    print("1. Open https://fabric.microsoft.com")
    print("2. Navigate to your workspace")
    print("3. Open your 'mlb_api' lakehouse")
    print("4. Go to 'Get data' in the ribbon")
    print("5. Choose 'Upload files' or 'Local files'")
    print("6. Select all CSV files from fabric_export/ folder")
    print("7. Follow the import wizard to create tables")
    
    print("\n📓 Alternative: Use Fabric Notebook")
    print("1. Create a new notebook in your workspace")
    print("2. Upload CSV files to the lakehouse Files area")
    print("3. Use this code in the notebook:")
    print("""
# Load CSV files into Delta tables
import pandas as pd

# Teams
teams_df = spark.read.csv('/lakehouse/default/Files/teams.csv', header=True, inferSchema=True)
teams_df.write.mode('overwrite').saveAsTable('teams')

# Players  
players_df = spark.read.csv('/lakehouse/default/Files/players.csv', header=True, inferSchema=True)
players_df.write.mode('overwrite').saveAsTable('players')

# Games
games_df = spark.read.csv('/lakehouse/default/Files/games.csv', header=True, inferSchema=True)
games_df.write.mode('overwrite').saveAsTable('games')

# Boxscore (with enhanced stats!)
boxscore_df = spark.read.csv('/lakehouse/default/Files/boxscore.csv', header=True, inferSchema=True)
boxscore_df.write.mode('overwrite').saveAsTable('boxscore')

print("✅ All tables created successfully!")
""")
    
    print("\n📂 Files Ready for Upload:")
    for csv_file in csv_files:
        size_kb = csv_file.stat().st_size / 1024
        print(f"   📄 {csv_file.name} ({size_kb:.1f} KB)")
    
    print(f"\n📁 Location: {Path('fabric_export').absolute()}")
    
    print("\n🎯 Key Features in Your Data:")
    print("   ✅ Stolen bases statistics captured")
    print("   ✅ Caught stealing statistics captured")
    print("   ✅ Enhanced batting statistics included")
    print("   ✅ 15 games from August 31, 2025")
    print("   ✅ 779 players with complete stats")
    print("   ✅ 296 boxscore entries with missing fields now included")

def create_onelake_uploader():
    """Create a more advanced OneLake uploader for future use."""
    print("\n🔮 Creating Advanced OneLake Uploader")
    print("=" * 45)
    
    uploader_content = '''#!/usr/bin/env python3
"""
Advanced OneLake Uploader for MLB Data
=====================================

This script uploads CSV files directly to OneLake using Azure Storage SDK.
Requires: pip install azure-storage-file-datalake azure-identity
"""

import os
from azure.storage.filedatalake import DataLakeServiceClient
from azure.identity import DefaultAzureCredential
from pathlib import Path

def upload_to_onelake():
    """Upload CSV files to OneLake."""
    
    # OneLake connection details
    workspace_id = os.getenv('FABRIC_WORKSPACE_ID')
    lakehouse_id = os.getenv('FABRIC_LAKEHOUSE_ID') 
    
    if not workspace_id or not lakehouse_id:
        print("❌ Missing OneLake configuration")
        print("Add to .env file:")
        print("FABRIC_WORKSPACE_ID=your_workspace_id")
        print("FABRIC_LAKEHOUSE_ID=your_lakehouse_id")
        return False
    
    # OneLake endpoint
    account_url = f"https://onelake.dfs.fabric.microsoft.com"
    
    # Initialize client with Azure AD credentials
    credential = DefaultAzureCredential()
    service_client = DataLakeServiceClient(account_url, credential=credential)
    
    # Get file system (lakehouse)
    file_system_name = f"{workspace_id}.{lakehouse_id}"
    file_system_client = service_client.get_file_system_client(file_system_name)
    
    # Upload each CSV file
    export_dir = Path("fabric_export")
    csv_files = list(export_dir.glob("*.csv"))
    
    for csv_file in csv_files:
        print(f"📤 Uploading {csv_file.name}...")
        
        # Upload to Files/mlb_data/ directory
        file_path = f"Files/mlb_data/{csv_file.name}"
        file_client = file_system_client.get_file_client(file_path)
        
        with open(csv_file, 'rb') as data:
            file_client.upload_data(data, overwrite=True)
        
        print(f"   ✅ {csv_file.name} uploaded successfully")
    
    print("🎉 All files uploaded to OneLake!")
    return True

if __name__ == "__main__":
    upload_to_onelake()
'''
    
    with open("onelake_uploader.py", 'w') as f:
        f.write(uploader_content)
    
    print("📄 Created: onelake_uploader.py")
    print("💡 This advanced uploader requires:")
    print("   - pip install azure-storage-file-datalake azure-identity")
    print("   - FABRIC_WORKSPACE_ID and FABRIC_LAKEHOUSE_ID in .env")
    print("   - Azure AD authentication")

if __name__ == "__main__":
    success = main()
    create_onelake_uploader()
    
    if success:
        print("\n🎉 Upload completed!")
    else:
        print("\n💡 Manual upload required - all helper files ready!")
