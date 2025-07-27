# MLB Data Pipeline

This project is designed to extract, transform, and load (ETL) Major League Baseball (MLB) data from the MLB Stats API into both JSON files and a SQL Server database. The pipeline captures live boxscore data, game information, player statistics, and team details, creating a comprehensive dataset suitable for analysis and reporting in Power BI.

## Features

- ✅ **Live MLB Data Extraction** - Fetches real-time data from MLB Stats API
- ✅ **JSON File Storage** - Saves raw data to timestamped JSON files
- ✅ **SQL Server Integration** - Loads data into normalized database tables
- ✅ **Data Backup** - Preserves original JSON in database for audit trail
- ✅ **Virtual Environment Support** - Isolated Python environment setup
- ✅ **Windows Authentication** - Seamless localhost SQL Server connection

## Project Structure

```
mlb-data-pipeline
├── src
│   ├── main.py                # Entry point for the application
│   ├── api                    # Contains API client for fetching data
│   │   ├── __init__.py
│   │   └── mlb_client.py      # MLBClient for interacting with the MLB Stats API
│   ├── models                 # Data models for the application
│   │   ├── __init__.py
│   │   ├── boxscore.py        # Boxscore data model
│   │   ├── game.py            # Game data model
│   │   ├── player.py          # Player data model
│   │   └── team.py            # Team data model
│   ├── etl                    # ETL processes
│   │   ├── __init__.py
│   │   ├── extract.py         # Data extraction logic
│   │   ├── transform.py       # Data transformation logic
│   │   └── load.py            # Data loading logic
│   ├── database               # Database connection management
│   │   ├── __init__.py
│   │   ├── connection.py      # SQL Server connection handling
│   │   └── json_to_sql_loader.py # JSON to SQL Server data loader
│   └── utils                  # Utility functions
│       ├── __init__.py
│       └── json_handler.py    # JSON file operations
├── config                     # Configuration settings
│   └── settings.py            # API keys and database connection strings
├── data                       # Data storage
│   └── json                   # JSON files with timestamped data
├── requirements.txt           # Project dependencies
├── .env                       # Environment variables
├── run.py                     # Main runner script with multiple commands
├── setup_database.py          # Database setup script
├── test_db_connection.py      # Database connection tester
├── view_database.py           # Database content viewer
├── DATABASE_SETUP.md          # Detailed database setup guide
└── README.md                  # Project documentation
```

## Setup Instructions

### Prerequisites
- Python 3.7+ installed
- SQL Server LocalDB or SQL Server Express on localhost
- ODBC Driver 17 for SQL Server (usually comes with SQL Server)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/mlb-data-pipeline.git
cd mlb-data-pipeline
```

### 2. Create Virtual Environment
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Database (One-time)
```bash
python setup_database.py
```
This creates the `mlb_data` database and required tables.

### 5. Configure Environment Variables (Optional)
Update the `.env` file if you need custom database settings:
```env
DB_SERVER=localhost
DB_NAME=mlb_data
DB_USERNAME=    # Leave blank for Windows Authentication
DB_PASSWORD=    # Leave blank for Windows Authentication
```

## Quick Start

### Extract Data and Load to Database (Recommended)
```bash
python run.py extract-and-load
```

### View Your Data
```bash
python run.py view-db
```

## Available Commands

| Command | Description |
|---------|-------------|
| `python run.py extract` | Extract MLB data and save to JSON files |
| `python run.py extract-no-json` | Extract data without saving JSON |
| `python run.py setup-db` | Create/update database tables |
| `python run.py load-json` | Load existing JSON files to SQL Server |
| `python run.py extract-and-load` | Extract data and load to database (recommended) |
| `python run.py view-db` | View database contents and statistics |
| `python run.py pipeline` | Run the full ETL pipeline |

### Additional Utilities
```bash
python test_db_connection.py    # Test SQL Server connection
python view_database.py         # View database contents directly
python setup_database.py        # Setup database and tables
```

## Data Storage

### JSON Files
- **Location**: `data/json/` directory
- **Format**: Timestamped files (e.g., `boxscore_raw_777001_20250726_125205.json`)
- **Types**:
  - `boxscore_raw_*.json` - Raw boxscore data from MLB API
  - `game_raw_*.json` - Raw game/linescore data from MLB API
  - `combined_data_*.json` - Combined data with metadata

### SQL Server Database
- **Database**: `mlb_data` on localhost
- **Tables**:
  - `teams` - Team information (ID, name, league, division)
  - `games` - Game details (ID, date, teams, scores, inning status)
  - `players` - Player information (ID, name, team, position)
  - `boxscore` - Player statistics (at-bats, runs, hits, RBI, etc.)
  - `raw_json_data` - Backup of original JSON data

## Data Flow

```
MLB Stats API → JSON Files → SQL Server Database
      ↓              ↓              ↓
  Live Data → Timestamped → Normalized Tables
                Backup       + JSON Backup
```

## Sample Usage

### 1. Extract Today's Game Data
```bash
# Extract current games and save to both JSON and database
python run.py extract-and-load
```

### 2. Load Schedule Data (Recommended First Step)
Load complete MLB schedule for proper game listings:
```bash
# Load current month schedule (March 2025 by default)
python run.py load-schedule

# Load specific month
python run.py load-schedule 2025 4    # April 2025

# Alternative: use standalone script
python load_schedule.py
```

### 3. View What's In Your Database
```bash
python run.py view-db
```
Output example:
```
📊 TEAMS:
  143 | Philadelphia Phillies     | PHI  | National League
  147 | New York Yankees          | NYY  | American League

🏟️ GAMES:
  Game 777001 | 2025-07-26 | Phillies 3 - 2 Yankees
    Inning: 9 Bottom | Status: Live

📈 DATABASE STATISTICS:
  Teams               :     2
  Games               :     1
  Players             :    52
  Boxscore Records    :    60
```

### 3. Load Historical JSON Files
```bash
# If you have existing JSON files, load them to database
python run.py load-json
```

## Usage

## Power BI Integration

The application creates a normalized database structure perfect for Power BI reporting:

### Key Relationships
- `games` ↔ `teams` (home/away team relationships)
- `players` ↔ `teams` (player-team assignments)
- `boxscore` ↔ `games`, `players`, `teams` (statistical relationships)

### Connection String for Power BI
```
Server: localhost
Database: mlb_data
Authentication: Windows Authentication
```

### Sample Queries for Power BI
```sql
-- Team Performance
SELECT t.team_name, 
       COUNT(g.game_id) as games_played,
       AVG(CASE WHEN g.home_team_id = t.team_id THEN g.home_score 
                ELSE g.away_score END) as avg_score
FROM teams t
JOIN games g ON (g.home_team_id = t.team_id OR g.away_team_id = t.team_id)
GROUP BY t.team_name;

-- Player Statistics
SELECT p.player_name, t.team_name,
       SUM(b.hits) as total_hits,
       SUM(b.runs) as total_runs,
       SUM(b.rbi) as total_rbi
FROM boxscore b
JOIN players p ON b.player_id = p.player_id
JOIN teams t ON b.team_id = t.team_id
GROUP BY p.player_name, t.team_name;
```

## Command Reference

### Core Commands
- `python run.py extract` - Extract current game data and save JSON
- `python run.py extract-no-json` - Extract data without saving JSON files
- `python run.py setup-db` - Setup database tables
- `python run.py load-json` - Load existing JSON files to database
- `python run.py load-schedule [year] [month]` - Load MLB schedule data
- `python run.py extract-and-load` - Extract data and load to database
- `python run.py view-db` - View database contents
- `python run.py pipeline` - Run full pipeline process

### Seasonal Data Extraction
- `python run.py extract-season [year] [start-date] [end-date]` - Extract entire season
- `python run.py extract-month YYYY MM` - Extract specific month
- `python run.py extract-week YYYY-MM-DD` - Extract specific week

### Standalone Scripts
- `python load_schedule.py` - Load March 2025 schedule (configurable)
- `python extract_season.py` - Advanced seasonal extraction
- `python view_database.py` - Direct database viewer
- `python test_db_connection.py` - Test SQL Server connection
- `python setup_database.py` - Setup database and tables

### Examples
```bash
# Load current schedule
python run.py load-schedule

# Load April 2025 schedule  
python run.py load-schedule 2025 4

# Extract all March 2025 data
python run.py extract-month 2025 3

# Extract specific date range
python run.py extract-season 2025 2025-03-01 2025-03-31

# Full workflow
python run.py load-schedule     # Load schedule first
python run.py extract-month 2025 3  # Extract game data
python run.py view-db           # View results
```

## Troubleshooting

### Database Connection Issues
1. **Ensure SQL Server is running**:
   ```bash
   python test_db_connection.py
   ```

2. **Check Windows Authentication**:
   - Verify SQL Server allows Windows Authentication
   - Ensure your Windows user has access to SQL Server

3. **Database doesn't exist**:
   ```bash
   python setup_database.py
   ```

### Module Import Errors
If you get `ModuleNotFoundError`, use the full command:
```bash
$env:PYTHONPATH = "C:\Users\metsy\source\repos\mlb-data-pipeline"; python run.py extract
```

### MLB API Issues
- The pipeline automatically finds current games
- Falls back to recent game IDs if no current games
- Check MLB Stats API status if persistent issues

## Dependencies

The application fetches live data from the MLB Stats API and transforms it into a structured format suitable for analysis and reporting. All data is automatically saved to both JSON files (for backup) and a SQL Server database (for analysis).

```
requests>=2.31.0
pandas>=2.0.0
sqlalchemy>=2.0.0
python-dotenv>=1.0.0
pyodbc>=5.0.0
```

## Additional Resources

- **DATABASE_SETUP.md** - Detailed database setup guide
- **MLB Stats API Documentation** - https://statsapi.mlb.com/docs/
- **SQL Server Express Download** - https://www.microsoft.com/en-us/sql-server/sql-server-downloads

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.