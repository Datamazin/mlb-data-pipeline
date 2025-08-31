#!/usr/bin/env python3
"""
Microsoft Fabric Migration Setup Script

This script helps you migrate your MLB data pipeline from SQL Server to Microsoft Fabric.
It validates your Fabric connection, creates the necessary tables, and provides migration guidance.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.fabric_connection import FabricConnection
from database.fabric_json_loader import FabricJSONLoader

def test_fabric_connection():
    """Test connection to Microsoft Fabric."""
    print("🔗 Testing Microsoft Fabric Connection...")
    print("=" * 50)
    
    # Check environment variables
    fabric_server = os.getenv('FABRIC_SERVER')
    fabric_database = os.getenv('FABRIC_DATABASE', 'mlb_data')
    fabric_username = os.getenv('FABRIC_USERNAME')
    fabric_password = os.getenv('FABRIC_PASSWORD')
    
    print(f"Configuration:")
    print(f"  Server: {fabric_server or '❌ NOT SET'}")
    print(f"  Database: {fabric_database}")
    print(f"  Username: {fabric_username or '(Using integrated auth)'}")
    print(f"  Password: {'***' if fabric_password else '(Using integrated auth)'}")
    
    if not fabric_server:
        print("\n❌ FABRIC_SERVER environment variable is required!")
        print("💡 Set it to your Fabric SQL Endpoint:")
        print("   FABRIC_SERVER=xyz-workspace.datawarehouse.fabric.microsoft.com")
        return False
    
    # Test connection
    try:
        fabric_db = FabricConnection()
        connection = fabric_db.connect()
        
        if connection:
            print("\n✅ Successfully connected to Microsoft Fabric!")
            
            # Test a simple query
            result = fabric_db.fetch_results("SELECT @@VERSION")
            if result:
                version = result[0][0]
                print(f"📊 SQL Server Version: {version[:100]}...")
            
            fabric_db.disconnect()
            return True
        else:
            print("\n❌ Failed to connect to Microsoft Fabric")
            return False
            
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check your Fabric SQL Endpoint URL")
        print("   2. Verify Azure AD credentials")
        print("   3. Ensure you have access to the Fabric workspace")
        print("   4. Check if ODBC Driver 17 for SQL Server is installed")
        return False

def setup_fabric_tables():
    """Create tables in Fabric if they don't exist."""
    print("\n🗃️  Setting up Fabric Tables...")
    print("=" * 50)
    
    try:
        fabric_db = FabricConnection()
        if not fabric_db.connect():
            print("❌ Cannot connect to Fabric to create tables")
            return False
        
        # Create tables
        fabric_db.create_tables()
        
        # Verify tables were created
        tables_result = fabric_db.fetch_results("""
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE' 
        ORDER BY TABLE_NAME
        """)
        
        if tables_result:
            print("✅ Tables created/verified in Fabric:")
            for table in tables_result:
                table_name = table[0]
                count = fabric_db.get_table_count(table_name)
                print(f"   - {table_name}: {count} records")
        else:
            print("❌ No tables found in Fabric database")
            return False
        
        fabric_db.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up tables: {e}")
        return False

def show_migration_guide():
    """Show migration guide and next steps."""
    print("\n📋 Migration Guide")
    print("=" * 50)
    
    print("Next Steps:")
    print("1. 🔄 Use the new Fabric loading script:")
    print("   python load_fabric_date_range_data.py --start 2025-08-31 --end 2025-08-31")
    
    print("\n2. 🚀 Load historical data to Fabric:")
    print("   # Load all 2025 season data")
    print("   python load_fabric_date_range_data.py --start 2025-03-01 --end 2025-08-31")
    
    print("\n3. ⚖️  Compare data between SQL Server and Fabric:")
    print("   # Check record counts match between systems")
    
    print("\n4. 🎯 Update your scheduled tasks to use Fabric loader:")
    print("   # Replace load_dynamic_date_range_data.py with load_fabric_date_range_data.py")
    
    print("\n📚 Key Differences:")
    print("   - Connection: fabric_connection.py instead of connection.py")
    print("   - Loader: fabric_json_loader.py instead of json_to_sql_loader.py")
    print("   - Authentication: Azure AD instead of Windows Authentication")
    print("   - Endpoint: Fabric SQL Endpoint instead of local SQL Server")

def main():
    """Main setup function."""
    print("🚀 Microsoft Fabric Migration Setup")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path('.env')
    env_template = Path('.env.fabric.template')
    
    if not env_file.exists():
        print("📄 .env file not found")
        if env_template.exists():
            print("💡 Found .env.fabric.template - copy it to .env and configure your Fabric details")
            print(f"   Copy: {env_template} -> {env_file}")
        else:
            print("💡 Create a .env file with your Fabric configuration")
        print()
    
    # Load environment variables from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded from .env")
    except ImportError:
        print("⚠️  python-dotenv not installed - environment variables must be set manually")
    except Exception as e:
        print(f"⚠️  Error loading .env file: {e}")
    
    # Test connection
    if not test_fabric_connection():
        print("\n❌ Cannot proceed without valid Fabric connection")
        print("💡 Fix the connection issues above and try again")
        return
    
    # Setup tables
    if not setup_fabric_tables():
        print("\n❌ Cannot proceed without valid Fabric tables")
        return
    
    # Show migration guide
    show_migration_guide()
    
    print("\n🎉 Fabric setup completed successfully!")
    print("✅ You can now load MLB data to Microsoft Fabric")

if __name__ == "__main__":
    main()
