#!/usr/bin/env python3
"""
Fabric Configuration Helper

This script helps you configure and test your Microsoft Fabric connection.
It provides guidance on finding your Fabric workspace details and offers local testing.
"""

import os
import sys
import sqlite3
from datetime import datetime, date
from pathlib import Path

def show_fabric_setup_guide():
    """Show step-by-step guide for setting up Fabric."""
    print("🎯 Microsoft Fabric Setup Guide")
    print("=" * 50)
    
    print("\n📋 Steps to get your Fabric SQL Endpoint:")
    print("1. 🌐 Go to https://fabric.microsoft.com")
    print("2. 🏢 Select or create a workspace")
    print("3. 📊 Create a Data Warehouse (if you don't have one)")
    print("4. ⚙️  In your Data Warehouse, go to Settings")
    print("5. 🔗 Copy the 'SQL Connection String' endpoint")
    print("6. 📝 It should look like: your-workspace.datawarehouse.fabric.microsoft.com")
    
    print("\n🔧 Configuration Options:")
    print("Option 1: Integrated Authentication (Easiest)")
    print("   - Uses your current Windows/Azure credentials")
    print("   - Leave FABRIC_USERNAME and FABRIC_PASSWORD blank")
    print("   - Make sure you're signed into Azure/Microsoft 365")
    
    print("\nOption 2: Username/Password Authentication")
    print("   - Set FABRIC_USERNAME to your Azure AD email")
    print("   - Set FABRIC_PASSWORD to your password")
    print("   - Less secure but works if integrated auth fails")

def check_current_config():
    """Check the current .env configuration."""
    print("\n🔍 Current Configuration Check")
    print("=" * 50)
    
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        print("💡 Run: copy .env.fabric.template .env")
        return False
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed")
    
    fabric_server = os.getenv('FABRIC_SERVER', '').strip()
    fabric_database = os.getenv('FABRIC_DATABASE', 'mlb_data')
    fabric_username = os.getenv('FABRIC_USERNAME', '').strip()
    fabric_password = os.getenv('FABRIC_PASSWORD', '').strip()
    
    print(f"📊 Current Settings:")
    print(f"   Server: {fabric_server}")
    print(f"   Database: {fabric_database}")
    print(f"   Username: {fabric_username or '(integrated auth)'}")
    print(f"   Password: {'***' if fabric_password else '(integrated auth)'}")
    
    # Check if server is still placeholder
    if not fabric_server or 'your-' in fabric_server or 'example' in fabric_server:
        print("\n❌ FABRIC_SERVER needs to be configured")
        print("💡 Replace with your actual Fabric SQL Endpoint")
        return False
    
    if fabric_username and not fabric_password:
        print("\n⚠️  Username set but password is blank")
        print("💡 Either set both username/password or leave both blank for integrated auth")
        return False
    
    print("\n✅ Configuration looks valid")
    return True

def test_connection_prereqs():
    """Test connection prerequisites."""
    print("\n🔧 Testing Connection Prerequisites")
    print("=" * 50)
    
    # Test pyodbc import
    try:
        import pyodbc
        print("✅ pyodbc installed")
        
        # List ODBC drivers
        drivers = [d for d in pyodbc.drivers() if 'SQL Server' in d]
        if drivers:
            print(f"✅ SQL Server ODBC drivers found: {', '.join(drivers)}")
        else:
            print("❌ No SQL Server ODBC drivers found")
            print("💡 Install ODBC Driver 17 for SQL Server")
            return False
    except ImportError:
        print("❌ pyodbc not installed")
        print("💡 Run: pip install pyodbc")
        return False
    
    # Test SQLAlchemy
    try:
        import sqlalchemy
        print("✅ SQLAlchemy installed")
    except ImportError:
        print("❌ SQLAlchemy not installed")
        print("💡 Run: pip install sqlalchemy")
        return False
    
    # Test dotenv
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv installed")
    except ImportError:
        print("⚠️  python-dotenv not installed (optional)")
        print("💡 Run: pip install python-dotenv")
    
    return True

def create_test_connection():
    """Create a simple test connection without full setup."""
    print("\n🧪 Testing Basic Connection (Mock)")
    print("=" * 50)
    
    print("Creating a test connection to demonstrate the flow...")
    
    # Add src to path for imports
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from database.fabric_connection import FabricConnection
        
        # Create connection object (won't actually connect with mock server)
        fabric_db = FabricConnection(
            server="test-workspace.datawarehouse.fabric.microsoft.com",
            database="mlb_data"
        )
        
        # Show what the connection string would look like
        connection_string = fabric_db.get_connection_string()
        print("✅ Connection object created successfully")
        print(f"📝 Connection string pattern: {connection_string[:60]}...")
        
        print("\n💡 To actually connect, you need:")
        print("   1. A real Fabric workspace SQL endpoint")
        print("   2. Valid Azure AD credentials")
        print("   3. Access permissions to the workspace")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test connection: {e}")
        return False

def main():
    """Main configuration helper."""
    print("🚀 Microsoft Fabric Configuration Helper")
    print("=" * 60)
    
    # Show setup guide
    show_fabric_setup_guide()
    
    # Check current config
    config_ok = check_current_config()
    
    # Test prerequisites
    prereqs_ok = test_connection_prereqs()
    
    # Test mock connection
    test_ok = create_test_connection()
    
    print(f"\n📊 Summary:")
    print(f"   Configuration: {'✅' if config_ok else '❌'}")
    print(f"   Prerequisites: {'✅' if prereqs_ok else '❌'}")
    print(f"   Test Connection: {'✅' if test_ok else '❌'}")
    
    if not config_ok:
        print(f"\n🔧 Next Steps:")
        print(f"   1. Get your Fabric SQL Endpoint from fabric.microsoft.com")
        print(f"   2. Update FABRIC_SERVER in your .env file")
        print(f"   3. Run: python setup_fabric.py")
    elif prereqs_ok and test_ok:
        print(f"\n🎉 Ready to connect!")
        print(f"   Run: python setup_fabric.py")
    else:
        print(f"\n🔧 Fix the issues above and try again")

if __name__ == "__main__":
    main()
