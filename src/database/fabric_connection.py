import pyodbc
import sqlalchemy
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FabricConnection:
    def __init__(self, server=None, database=None, username=None, password=None):
        """
        Initialize database connection for Microsoft Fabric SQL Endpoint.
        
        Args:
            server: Fabric SQL Endpoint (e.g., xyz-workspace.datawarehouse.fabric.microsoft.com)
            database: Database/Warehouse name (default: mlb_data)
            username: Azure AD username or service principal
            password: Password or service principal secret
        """
        self.server = server or os.getenv('FABRIC_SERVER')
        self.database = database or os.getenv('FABRIC_DATABASE', 'mlb_data')
        self.username = username or os.getenv('FABRIC_USERNAME')
        self.password = password or os.getenv('FABRIC_PASSWORD')
        self.connection = None
        self.engine = None

    def get_connection_string(self):
        """Create Fabric SQL Endpoint connection string."""
        if self.username and self.password:
            # Azure AD Authentication with username/password
            connection_string = (
                f"mssql+pyodbc://{self.username}:{self.password}@"
                f"{self.server}/{self.database}?"
                f"driver=ODBC+Driver+17+for+SQL+Server&"
                f"Authentication=ActiveDirectoryPassword&"
                f"Encrypt=yes&TrustServerCertificate=no"
            )
        else:
            # Azure AD Interactive - will prompt for authentication
            # Using a cleaner connection string format
            connection_string = (
                f"mssql+pyodbc:///?odbc_connect="
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"Authentication=ActiveDirectoryInteractive;"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no"
            )
        return connection_string

    def connect(self):
        """Establish a database connection to Fabric."""
        try:
            connection_string = self.get_connection_string()
            print(f"🔗 Attempting connection with: {connection_string[:80]}...")
            
            self.engine = create_engine(connection_string)
            self.connection = self.engine.connect()
            print(f"✅ Connected to Fabric SQL Endpoint: {self.server}/{self.database}")
            return self.connection
        except Exception as e:
            print(f"❌ Error connecting to Fabric: {e}")
            print("💡 Make sure you have:")
            print("   - Valid Azure AD credentials")
            print("   - Access to the Fabric workspace")
            print("   - ODBC Driver 17 for SQL Server installed")
            print("   - Signed into Azure AD (for interactive auth)")
            return None

    def disconnect(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("✅ Fabric connection closed")

    def execute_query(self, query, params=None):
        """Execute a database query."""
        try:
            if not self.connection:
                self.connect()
            
            result = self.connection.execute(text(query), params or {})
            return result
        except Exception as e:
            print(f"❌ Error executing query: {e}")
            raise

    def execute_transaction(self, queries):
        """Execute multiple queries in a single transaction."""
        try:
            if not self.connection:
                self.connect()
            
            # Close and reopen connection for clean state
            if self.connection:
                self.connection.close()
            self.connection = self.engine.connect()
            
            trans = self.connection.begin()
            try:
                results = []
                for query in queries:
                    if isinstance(query, tuple):
                        sql, params = query
                        result = self.connection.execute(text(sql), params)
                    else:
                        result = self.connection.execute(text(query))
                    results.append(result)
                trans.commit()
                return results
            except Exception as e:
                trans.rollback()
                raise
        except Exception as e:
            print(f"❌ Error executing transaction: {e}")
            raise

    def fetch_results(self, query, params=None):
        """Fetch results from a database query."""
        try:
            if not self.connection:
                self.connect()
            
            result = self.connection.execute(text(query), params or {})
            return result.fetchall()
        except Exception as e:
            print(f"❌ Error fetching results: {e}")
            raise

    def create_tables(self):
        """Create the necessary tables for MLB data in Fabric."""
        tables_sql = [
            # Create Teams table (simplified for Fabric)
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='teams')
            CREATE TABLE teams (
                team_id INT NOT NULL,
                team_name VARCHAR(100),
                abbreviation VARCHAR(10),
                league VARCHAR(50),
                division VARCHAR(50),
                game_id INT,
                game_date DATE,
                created_at DATETIME2(6)
            )
            """,
            
            # Create Games table
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='games')
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
            )
            """,
            
            # Create Players table
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='players')
            CREATE TABLE players (
                player_id INT NOT NULL,
                player_name VARCHAR(100),
                team_id INT,
                position VARCHAR(50),
                game_id INT,
                game_date DATE,
                created_at DATETIME2(6)
            )
            """,
            
            # Create Boxscore table with stolen base stats
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='boxscore')
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
            )
            """,
            
            # Create Raw JSON Data table for backup
            """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='raw_json_data')
            CREATE TABLE raw_json_data (
                id INT IDENTITY(1,1),
                game_id INT,
                game_date DATE,
                data_type VARCHAR(50),
                json_data VARCHAR(MAX),
                extraction_timestamp DATETIME2(6)
            )
            """
        ]
        
        try:
            # Execute each statement separately
            for i, statement in enumerate(tables_sql, 1):
                if statement.strip():
                    print(f"   Creating table {i}/{len(tables_sql)}...")
                    self.execute_query(statement)
            print("✅ Fabric tables created successfully")
        except Exception as e:
            print(f"❌ Error creating Fabric tables: {e}")
            raise

    def get_table_count(self, table_name):
        """Get count of records in a table."""
        try:
            result = self.fetch_results(f"SELECT COUNT(*) as count FROM {table_name}")
            return result[0][0] if result else 0
        except Exception as e:
            print(f"❌ Error getting count for {table_name}: {e}")
            return 0
