#!/usr/bin/env python3
"""
Test SQL Server Database Connection
This script tests the connection to your localhost SQL Server database.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.connection import DatabaseConnection

def test_connection():
    """Test the database connection."""
    print("Testing SQL Server connection...")
    
    # Test with Windows Authentication (default)
    db = DatabaseConnection()
    
    print(f"Connection String: {db.get_connection_string()}")
    print("Attempting to connect...")
    
    if db.connect():
        print("✅ Connection successful!")
        
        # Test a simple query
        try:
            result = db.fetch_results("SELECT @@VERSION as version")
            if result:
                print(f"SQL Server Version: {result[0][0][:100]}...")
            
            # List existing databases
            databases = db.fetch_results("SELECT name FROM sys.databases WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb')")
            print(f"User Databases: {[db[0] for db in databases]}")
            
        except Exception as e:
            print(f"❌ Error running test queries: {e}")
        
        db.disconnect()
    else:
        print("❌ Connection failed!")
        print("\nTroubleshooting:")
        print("1. Ensure SQL Server is running on localhost")
        print("2. Check if Windows Authentication is enabled")
        print("3. Try creating the database 'mlb_data' manually")
        print("4. Update .env file with correct credentials if using SQL Auth")

if __name__ == "__main__":
    test_connection()
