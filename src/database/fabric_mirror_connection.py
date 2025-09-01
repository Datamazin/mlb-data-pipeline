"""
Microsoft Fabric Connection Module for Database Mirroring
========================================================

Enhanced Fabric connection specifically designed for database mirroring operations.
Includes optimized settings for bulk operations and schema management.
"""

import pyodbc
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

class FabricMirrorConnection:
    def __init__(self):
        # Fabric SQL Endpoint configuration
        self.server = "niagdix6nenejo5yletqutjpae-apygryrrgdhupeevwhp3xhozjy.datawarehouse.fabric.microsoft.com"
        self.database = "mlb_data_fabric"
        self.connection = None
        self.logger = logging.getLogger(__name__)
        
        # Optimized connection string for bulk operations
        self.connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"Authentication=ActiveDirectoryInteractive;"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout=60;"
            f"Command Timeout=300;"  # 5 minutes for bulk operations
            f"MultipleActiveResultSets=True;"
        )
    
    def connect(self) -> bool:
        """Establish connection to Fabric SQL Endpoint."""
        try:
            self.logger.info(f"🔌 Connecting to Fabric: {self.server}")
            self.connection = pyodbc.connect(self.connection_string)
            self.connection.autocommit = True  # For DDL operations
            self.logger.info("✅ Connected to Fabric SQL Endpoint")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Fabric connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close Fabric connection."""
        if self.connection:
            try:
                self.connection.close()
                self.logger.info("✅ Fabric connection closed")
            except Exception as e:
                self.logger.error(f"⚠️  Error closing Fabric connection: {e}")
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> bool:
        """Execute query in Fabric (DDL/DML operations)."""
        if not self.connection:
            self.logger.error("❌ No Fabric connection available")
            return False
        
        try:
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Get affected rows for DML operations
            if cursor.rowcount >= 0:
                self.logger.info(f"✅ Query executed: {cursor.rowcount} rows affected")
            
            cursor.close()
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Query execution failed: {e}")
            self.logger.error(f"📝 Query: {query[:200]}...")
            return False
    
    def fetch_results(self, query: str, params: Optional[Dict] = None) -> List[Any]:
        """Fetch query results from Fabric."""
        if not self.connection:
            self.logger.error("❌ No Fabric connection available")
            return []
        
        try:
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            cursor.close()
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Query fetch failed: {e}")
            return []
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in Fabric."""
        query = """
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = ? AND TABLE_TYPE = 'BASE TABLE'
        """
        
        try:
            result = self.fetch_results(query, [table_name])
            return result[0][0] > 0 if result else False
        except:
            return False
    
    def get_table_count(self, table_name: str) -> int:
        """Get row count for a Fabric table."""
        if not self.table_exists(table_name):
            return 0
        
        try:
            query = f"SELECT COUNT(*) FROM {table_name}"
            result = self.fetch_results(query)
            return result[0][0] if result else 0
        except:
            return 0
    
    def create_table_from_ddl(self, table_name: str, ddl: str) -> bool:
        """Create table in Fabric from DDL statement."""
        try:
            # Drop table if exists
            drop_query = f"DROP TABLE IF EXISTS {table_name};"
            self.execute_query(drop_query)
            
            # Create table
            success = self.execute_query(ddl)
            
            if success:
                self.logger.info(f"✅ Created Fabric table: {table_name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create table {table_name}: {e}")
            return False
    
    def bulk_insert_from_csv(self, table_name: str, csv_file_path: str, has_header: bool = True) -> bool:
        """Perform bulk insert from CSV file."""
        # Note: Direct BULK INSERT may not be available in Fabric
        # This is a placeholder for the actual implementation
        self.logger.warning(f"⚠️  Bulk insert not directly supported in Fabric")
        self.logger.info(f"💡 Use Fabric notebook to load CSV: {csv_file_path}")
        return False
    
    def validate_connection(self) -> Dict[str, Any]:
        """Validate Fabric connection and capabilities."""
        if not self.connection:
            return {'connected': False, 'error': 'No connection'}
        
        try:
            # Test basic connectivity
            test_query = "SELECT GETDATE() as current_time, @@VERSION as version"
            result = self.fetch_results(test_query)
            
            if result:
                return {
                    'connected': True,
                    'server_time': result[0][0],
                    'version': result[0][1][:100] + "..." if len(result[0][1]) > 100 else result[0][1],
                    'database': self.database
                }
            else:
                return {'connected': False, 'error': 'Query failed'}
                
        except Exception as e:
            return {'connected': False, 'error': str(e)}

# Test the connection
if __name__ == "__main__":
    print("🧪 Testing Fabric Mirror Connection")
    print("=" * 40)
    
    fabric = FabricMirrorConnection()
    
    if fabric.connect():
        validation = fabric.validate_connection()
        
        if validation['connected']:
            print(f"✅ Connection successful!")
            print(f"📅 Server time: {validation['server_time']}")
            print(f"🗄️  Database: {validation['database']}")
            print(f"🖥️  Version: {validation['version']}")
        else:
            print(f"❌ Validation failed: {validation['error']}")
        
        fabric.disconnect()
    else:
        print("❌ Connection failed")
