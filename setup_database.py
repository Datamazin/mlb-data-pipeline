#!/usr/bin/env python3
"""
Setup MLB Database
This script creates the mlb_data database and sets up the initial schema.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import pyodbc
from sqlalchemy import create_engine, text

def create_database():
    """Create the mlb_data database if it doesn't exist."""
    print("Creating MLB database...")
    
    try:
        # Connect to SQL Server without specifying a database (use master)
        connection_string = (
            "mssql+pyodbc://localhost/master?"
            "driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
        )
        
        engine = create_engine(connection_string, isolation_level="AUTOCOMMIT")
        connection = engine.connect()
        
        print("✅ Connected to SQL Server")
        
        # Check if database exists
        result = connection.execute(text("SELECT name FROM sys.databases WHERE name = 'mlb_data'"))
        exists = result.fetchone()
        
        if exists:
            print("✅ Database 'mlb_data' already exists")
        else:
            # Create the database
            connection.execute(text("CREATE DATABASE mlb_data"))
            print("✅ Database 'mlb_data' created successfully")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def setup_tables():
    """Setup the database tables."""
    from src.database.connection import DatabaseConnection
    
    print("Setting up database tables...")
    db = DatabaseConnection()
    
    if db.connect():
        try:
            db.create_tables()
            print("✅ Database tables created successfully")
            return True
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
        finally:
            db.disconnect()
    else:
        print("❌ Failed to connect to mlb_data database")
        return False

def main():
    """Main setup function."""
    print("MLB Database Setup")
    print("=" * 50)
    
    # Step 1: Create database
    if not create_database():
        print("❌ Database creation failed")
        return
    
    # Step 2: Create tables
    if not setup_tables():
        print("❌ Table creation failed")
        return
    
    print("=" * 50)
    print("✅ Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Run: python run.py extract")
    print("2. Run: python run.py load-json")
    print("Or run: python run.py extract-and-load")

if __name__ == "__main__":
    main()
