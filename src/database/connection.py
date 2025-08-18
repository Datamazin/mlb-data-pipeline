import pyodbc
import sqlalchemy
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConnection:
    def __init__(self, server=None, database=None, username=None, password=None):
        """
        Initialize database connection for SQL Server.
        
        Args:
            server: SQL Server instance (default: localhost)
            database: Database name (default: mlb_data)
            username: Username (optional for Windows Authentication)
            password: Password (optional for Windows Authentication)
        """
        self.server = server or os.getenv('DB_SERVER', 'localhost')
        self.database = database or os.getenv('DB_NAME', 'mlb_data')
        self.username = username or os.getenv('DB_USERNAME')
        self.password = password or os.getenv('DB_PASSWORD')
        self.connection = None
        self.engine = None

    def get_connection_string(self):
        """Create SQL Server connection string."""
        if self.username and self.password:
            # SQL Server Authentication
            connection_string = (
                f"mssql+pyodbc://{self.username}:{self.password}@"
                f"{self.server}/{self.database}?"
                f"driver=ODBC+Driver+17+for+SQL+Server"
            )
        else:
            # Windows Authentication
            connection_string = (
                f"mssql+pyodbc://{self.server}/{self.database}?"
                f"driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
            )
        return connection_string

    def connect(self):
        """Establish a database connection."""
        try:
            connection_string = self.get_connection_string()
            # For SQLAlchemy 2.0, we need to handle transactions differently
            self.engine = create_engine(connection_string)
            self.connection = self.engine.connect()
            print(f"✅ Connected to SQL Server: {self.server}/{self.database}")
            return self.connection
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            return None

    def disconnect(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")

    def commit(self):
        """Commit the current transaction."""
        if self.connection:
            try:
                # For SQLAlchemy, we need to commit on the engine or use transactions explicitly
                # Since we're using autocommit by default, this might not be needed
                # But for explicit transaction control, we should use begin()
                pass
            except Exception as e:
                print(f"❌ Error committing transaction: {e}")
                raise

    def rollback(self):
        """Rollback the current transaction."""
        if self.connection:
            try:
                # For SQLAlchemy, rollback is handled by the transaction context
                pass
            except Exception as e:
                print(f"❌ Error rolling back transaction: {e}")
                raise

    def execute_query(self, query, params=None):
        """Execute a database query."""
        try:
            if not self.connection:
                self.connect()
            
            # Just execute the query - let the caller handle transaction management
            result = self.connection.execute(text(query), params or {})
            return result
        except Exception as e:
            print(f"❌ Error executing query: {e}")
            raise

    def execute_with_transaction(self, query, params=None):
        """Execute a database query with automatic transaction management."""
        try:
            if not self.connection:
                self.connect()
            
            with self.connection.begin():
                result = self.connection.execute(text(query), params or {})
                return result
        except Exception as e:
            print(f"❌ Error executing query with transaction: {e}")
            raise

    def execute_transaction(self, queries):
        """Execute multiple queries in a single transaction."""
        try:
            if not self.connection:
                self.connect()
            
            # For safety, let's close and reopen the connection to ensure clean state
            if self.connection:
                self.connection.close()
            self.connection = self.engine.connect()
            
            trans = self.connection.begin()
            try:
                results = []
                for query in queries:
                    if isinstance(query, tuple):
                        # Query with parameters
                        sql, params = query
                        result = self.connection.execute(text(sql), params)
                    else:
                        # Simple query
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
        """Create the necessary tables for MLB data."""
        tables_sql = """
        -- Create Teams table
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='teams' AND xtype='U')
        CREATE TABLE teams (
            team_id INT PRIMARY KEY,
            team_name NVARCHAR(100),
            abbreviation NVARCHAR(10),
            league NVARCHAR(50),
            division NVARCHAR(50),
            created_at DATETIME DEFAULT GETDATE()
        );

        -- Create Games table
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='games' AND xtype='U')
        CREATE TABLE games (
            game_id INT PRIMARY KEY,
            game_date DATE,
            home_team_id INT,
            away_team_id INT,
            home_score INT,
            away_score INT,
            inning INT,
            inning_state NVARCHAR(20),
            game_status NVARCHAR(50),
            game_type NVARCHAR(10),
            series_description NVARCHAR(100),
            official_date DATE,
            created_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
            FOREIGN KEY (away_team_id) REFERENCES teams(team_id)
        );

        -- Create Players table  
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='players' AND xtype='U')
        CREATE TABLE players (
            player_id INT PRIMARY KEY,
            player_name NVARCHAR(100),
            team_id INT,
            position NVARCHAR(50),
            created_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (team_id) REFERENCES teams(team_id)
        );

        -- Create Boxscore table
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='boxscore' AND xtype='U')
        CREATE TABLE boxscore (
            id INT IDENTITY(1,1) PRIMARY KEY,
            game_id INT,
            player_id INT,
            team_id INT,
            at_bats INT DEFAULT 0,
            runs INT DEFAULT 0,
            hits INT DEFAULT 0,
            doubles INT DEFAULT 0,
            triples INT DEFAULT 0,
            home_runs INT DEFAULT 0,
            rbi INT DEFAULT 0,
            walks INT DEFAULT 0,
            strikeouts INT DEFAULT 0,
            created_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (game_id) REFERENCES games(game_id),
            FOREIGN KEY (player_id) REFERENCES players(player_id),
            FOREIGN KEY (team_id) REFERENCES teams(team_id)
        );

        -- Create Raw JSON Data table for backup
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='raw_json_data' AND xtype='U')
        CREATE TABLE raw_json_data (
            id INT IDENTITY(1,1) PRIMARY KEY,
            game_id INT,
            data_type NVARCHAR(50), -- 'boxscore' or 'game_data'
            json_data NVARCHAR(MAX),
            extraction_timestamp DATETIME DEFAULT GETDATE()
        );
        """
        
        try:
            # Split and execute each statement
            statements = tables_sql.split(';\n\n')
            for statement in statements:
                if statement.strip():
                    self.execute_query(statement)
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            raise