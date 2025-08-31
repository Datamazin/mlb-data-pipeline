#!/usr/bin/env python3
"""
Check Microsoft Fabric permissions and existing tables.
This script helps determine what permissions you have in the Fabric workspace.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append('src')

from database.fabric_connection import FabricConnection

def check_fabric_permissions():
    """Check what permissions we have in Fabric."""
    print("🔍 Microsoft Fabric Permissions Check")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Fabric connection
    fabric_conn = FabricConnection()
    
    try:
        # Test connection
        if not fabric_conn.connect():
            print("❌ Cannot connect to Fabric")
            return False
        
        print("✅ Connected to Fabric successfully")
        
        # Check existing tables
        print("\n📋 Checking existing tables...")
        try:
            result = fabric_conn.fetch_results("""
                SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_SCHEMA, TABLE_NAME
            """)
            
            if result:
                print(f"📊 Found {len(result)} existing tables:")
                for row in result:
                    print(f"   - {row[0]}.{row[1]} ({row[2]})")
            else:
                print("   No tables found")
                
        except Exception as e:
            print(f"❌ Cannot read table information: {e}")
        
        # Test if we can create a simple test table
        print("\n🧪 Testing table creation permissions...")
        try:
            fabric_conn.execute_query("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='test_permissions')
                CREATE TABLE test_permissions (
                    id INT,
                    test_value VARCHAR(50)
                )
            """)
            print("✅ Table creation permission: ALLOWED")
            
            # Clean up test table
            try:
                fabric_conn.execute_query("DROP TABLE test_permissions")
                print("✅ Table deletion permission: ALLOWED")
            except:
                print("⚠️  Table deletion permission: UNKNOWN")
                
        except Exception as e:
            print(f"❌ Table creation permission: DENIED")
            print(f"   Error: {e}")
            print("\n💡 To resolve this, you need:")
            print("   1. 'Contributor' role in the Fabric workspace")
            print("   2. 'SQL Admin' permissions in the warehouse")
            print("   3. Ask your Fabric workspace admin to grant these permissions")
        
        # Test insert permissions on existing tables (if any)
        print("\n📝 Testing data insertion permissions...")
        try:
            # Try a simple SELECT to test read permissions
            result = fabric_conn.fetch_results("SELECT 1 as test_select")
            print("✅ SELECT permission: ALLOWED")
        except Exception as e:
            print(f"❌ SELECT permission: DENIED - {e}")
        
        fabric_conn.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Error checking permissions: {e}")
        return False

def show_fabric_requirements():
    """Show what's needed for Fabric access."""
    print("\n🔑 Microsoft Fabric Permission Requirements")
    print("=" * 50)
    print("To create and load data into Fabric tables, you need:")
    print("\n1. Workspace Access:")
    print("   - Member or Contributor role in the Fabric workspace")
    print("   - Access to the specific SQL Endpoint (lakehouse/warehouse)")
    print("\n2. SQL Permissions:")
    print("   - CREATE TABLE permission")
    print("   - INSERT/UPDATE/DELETE permissions")
    print("   - SELECT permissions for data validation")
    print("\n3. Azure AD Authentication:")
    print("   - Valid Azure AD account")
    print("   - Account must be in the same tenant as the Fabric workspace")
    print("\n4. How to get permissions:")
    print("   - Contact your Fabric workspace administrator")
    print("   - Request 'Contributor' role in the workspace")
    print("   - Ensure your account is added to the workspace members")
    print("\n📚 Learn more:")
    print("   https://docs.microsoft.com/en-us/fabric/data-warehouse/security")

if __name__ == "__main__":
    success = check_fabric_permissions()
    if not success:
        show_fabric_requirements()
