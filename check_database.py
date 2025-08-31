#!/usr/bin/env python3
"""
Check database connectivity and table contents for SSMS troubleshooting
"""

import sys
import os
sys.path.append('src')

from database.connection import DatabaseConnection

def main():
    db = DatabaseConnection()
    try:
        db.connect()
        
        # Get exact connection details
        print('🔍 Connection Details:')
        print(f'   Server: {db.server}')
        print(f'   Database: {db.database}') 
        print(f'   Username: {db.username or "Windows Auth"}')
        
        # Test basic connectivity
        result = db.fetch_results('SELECT @@SERVERNAME as server_name, DB_NAME() as current_database')
        if result:
            print(f'\n📊 Current Connection:')
            print(f'   Server Name: {result[0][0]}')
            print(f'   Database Name: {result[0][1]}')
        
        # Check if tables exist
        result = db.fetch_results('''
            SELECT 
                TABLE_NAME,
                TABLE_TYPE
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        ''')
        
        print(f'\n📋 Tables in database:')
        if result:
            table_names = []
            for row in result:
                print(f'   - {row[0]}')
                table_names.append(row[0])
                
            # Check row counts for each table
            print(f'\n📊 Row counts:')
            for table_name in table_names:
                try:
                    count_result = db.fetch_results(f'SELECT COUNT(*) FROM {table_name}')
                    if count_result:
                        print(f'   {table_name}: {count_result[0][0]:,} rows')
                except Exception as e:
                    print(f'   {table_name}: Error - {e}')
        else:
            print('   ❌ No tables found!')
            
        # Check database size
        result = db.fetch_results('''
            SELECT 
                DB_NAME() as database_name,
                SUM(size) * 8 / 1024 as size_mb
            FROM sys.database_files
        ''')
        
        if result:
            print(f'\n💾 Database size: {result[0][1]:.1f} MB')
            
    except Exception as e:
        print(f'❌ Error: {e}')
        
    finally:
        if hasattr(db, 'disconnect'):
            db.disconnect()

if __name__ == "__main__":
    main()
