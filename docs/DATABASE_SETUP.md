# SQL Server Database Setup Guide

## Prerequisites

1. **SQL Server LocalDB or SQL Server Express** installed on your machine
2. **ODBC Driver 17 for SQL Server** (usually comes with SQL Server)

## Quick Setup Steps

### 1. Test Database Connection
```bash
python test_db_connection.py
```

### 2. Setup Database Tables
```bash
python run.py setup-db
```

### 3. Extract Data and Load to Database
```bash
python run.py extract-and-load
```

## Manual Database Setup

If you prefer to create the database manually:

### 1. Connect to SQL Server Management Studio (SSMS)
- Server: `localhost` or `(localdb)\MSSQLLocalDB`
- Authentication: Windows Authentication

### 2. Create Database
```sql
CREATE DATABASE mlb_data;
```

### 3. Use the Database
```sql
USE mlb_data;
```

### 4. Run the Setup Command
```bash
python run.py setup-db
```

## Configuration Options

### Windows Authentication (Default)
In `.env` file:
```
DB_SERVER=localhost
DB_NAME=mlb_data
DB_USERNAME=
DB_PASSWORD=
```

### SQL Server Authentication
In `.env` file:
```
DB_SERVER=localhost
DB_NAME=mlb_data
DB_USERNAME=your_username
DB_PASSWORD=your_password
```

## Database Schema

The following tables will be created:

- **teams**: Team information (ID, name, league, division)
- **games**: Game information (ID, date, teams, scores)
- **players**: Player information (ID, name, team, position)
- **boxscore**: Player statistics for each game
- **raw_json_data**: Backup of original JSON data

## Troubleshooting

### Connection Issues
1. Ensure SQL Server is running:
   ```bash
   services.msc
   ```
   Look for "SQL Server" services

2. Check if SQL Server Browser is running

3. Verify SQL Server configuration:
   - TCP/IP enabled
   - Named Pipes enabled
   - Mixed Mode Authentication (if using SQL Auth)

### Driver Issues
If you get ODBC driver errors:
1. Download "ODBC Driver 17 for SQL Server" from Microsoft
2. Install and restart your application

### Permission Issues
1. Ensure your Windows user has access to SQL Server
2. Add your user to `sysadmin` role if needed
3. Check database permissions

## Available Commands

| Command | Description |
|---------|-------------|
| `python run.py extract` | Extract data and save JSON |
| `python run.py setup-db` | Create database tables |
| `python run.py load-json` | Load existing JSON to database |
| `python run.py extract-and-load` | Extract and load in one step |
| `python test_db_connection.py` | Test database connection |

## Data Flow

1. **Extract**: MLB API → JSON files (`data/json/`)
2. **Load**: JSON files → SQL Server database
3. **Backup**: Original JSON stored in `raw_json_data` table
4. **Transform**: Data normalized into relational tables

## Viewing Data

Connect to your database and query:

```sql
-- View teams
SELECT * FROM teams;

-- View recent games
SELECT g.*, 
       ht.team_name as home_team_name,
       at.team_name as away_team_name
FROM games g
JOIN teams ht ON g.home_team_id = ht.team_id
JOIN teams at ON g.away_team_id = at.team_id
ORDER BY g.created_at DESC;

-- View player stats
SELECT p.player_name, t.team_name, b.*
FROM boxscore b
JOIN players p ON b.player_id = p.player_id
JOIN teams t ON b.team_id = t.team_id
ORDER BY b.runs DESC, b.hits DESC;
```
