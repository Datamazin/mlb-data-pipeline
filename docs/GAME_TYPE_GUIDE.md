# MLB Game Type Detection and Analysis

## Overview

Your MLB data pipeline now supports comprehensive game type detection to distinguish between regular season games, spring training (preseason), and other game types like playoffs and exhibitions.

## Game Type Categories

### Primary Game Types

| Code | Description | When |
|------|-------------|------|
| `S` | **Spring Training / Preseason** | February - March |
| `R` | **Regular Season** | April - September |
| `E` | **Exhibition** | Special exhibition games |
| `F` | **Wild Card / First Round** | October playoffs |
| `D` | **Division Series** | October playoffs |
| `L` | **League Championship Series** | October playoffs |
| `W` | **World Series** | October/November |
| `A` | **All-Star Game** | July |

## Database Schema Updates

### Games Table Enhancement

The `games` table now includes these new columns:

```sql
-- Game type identification
game_type NVARCHAR(10)          -- 'S', 'R', 'F', 'D', 'L', 'W', 'A', 'E'
series_description NVARCHAR(100) -- 'Spring Training', 'Regular Season', etc.
official_date DATE              -- Official game date from MLB
```

### Current Data Status

✅ **433 March 2025 Games Loaded with Game Types:**
- **355 Spring Training games** (`S`) 
- **67 Regular Season games** (`R`)
- **11 Exhibition games** (`E`)

## Usage Examples

### 1. Basic Game Type Detection

```python
from game_type_analyzer import GameTypeAnalyzer

analyzer = GameTypeAnalyzer()

# Check if a specific game is preseason
is_preseason = analyzer.is_preseason_game(779011)
print(f"Game 779011 is preseason: {is_preseason}")  # True for spring training

# Get all spring training games for 2025
spring_games = analyzer.get_spring_training_games(year=2025)

# Get regular season games
regular_games = analyzer.get_regular_season_games(year=2025)
```

### 2. SQL Queries for Game Type Filtering

```sql
-- Get all spring training games
SELECT * FROM games WHERE game_type = 'S';

-- Get all regular season games  
SELECT * FROM games WHERE game_type = 'R';

-- Get games with team names
SELECT g.game_id, g.game_date, g.game_type, g.series_description,
       ht.team_name as home_team, at.team_name as away_team
FROM games g
LEFT JOIN teams ht ON g.home_team_id = ht.team_id
LEFT JOIN teams at ON g.away_team_id = at.team_id
WHERE g.game_type = 'S'  -- Spring Training only
ORDER BY g.game_date DESC;

-- Count games by type
SELECT game_type, series_description, COUNT(*) as game_count
FROM games 
GROUP BY game_type, series_description
ORDER BY game_type;
```

### 3. Power BI DAX Measures for Game Types

Add these measures to your Power BI model:

```dax
-- Total Spring Training Games
Spring Training Games = 
CALCULATE(
    DISTINCTCOUNT(games[game_id]),
    games[game_type] = "S"
)

-- Total Regular Season Games  
Regular Season Games = 
CALCULATE(
    DISTINCTCOUNT(games[game_id]),
    games[game_type] = "R"
)

-- Game Type Filter
Game Type Description = 
SWITCH(
    SELECTEDVALUE(games[game_type]),
    "S", "Spring Training",
    "R", "Regular Season", 
    "E", "Exhibition",
    "F", "Wild Card",
    "D", "Division Series",
    "L", "Championship Series",
    "W", "World Series",
    "A", "All-Star Game",
    "Unknown"
)

-- Is Preseason Game
Is Preseason = 
IF(SELECTEDVALUE(games[game_type]) = "S", "Yes", "No")
```

### 4. Filtering in Analysis

```python
# Example: Analyze only regular season batting performance
analyzer = GameTypeAnalyzer()

# Get regular season games for analysis
regular_games = analyzer.get_regular_season_games(year=2025)
regular_game_ids = [game[0] for game in regular_games]

# In your Power BI or analysis, filter by these game IDs
# This ensures spring training stats don't skew regular season analysis
```

## API Integration

### Automatic Game Type Detection

The system automatically detects game types when processing schedule data:

```python
# The MLB API returns game type in schedule data
{
  "gamePk": 779011,
  "gameType": "S",                    # Spring Training
  "seriesDescription": "Spring Training",
  "teams": {
    "away": {
      "springLeague": {
        "name": "Cactus League",      # Indicates spring training
        "abbreviation": "CL"
      }
    }
  }
}
```

### Data Processing

The `JSONToSQLLoader` class automatically extracts and stores:
- `gameType` → `games.game_type`
- `seriesDescription` → `games.series_description`  
- `officialDate` → `games.official_date`

## Scripts and Utilities

### Available Scripts

1. **`game_type_analyzer.py`** - Main analysis utility
   - Query games by type
   - Generate summaries
   - Check individual game types

2. **`test_game_types.py`** - Test different game types from MLB API
   - Compare spring training vs regular season
   - Show game type patterns

3. **`update_march_game_types.py`** - Update existing data
   - Backfill game type information
   - Refresh schedule data

4. **`add_game_type_support.py`** - Database schema updates
   - Add game type columns
   - Update table structure

### Running the Analysis

```bash
# Show game type summary
python game_type_analyzer.py

# Update game types for a date range  
python update_march_game_types.py

# Test API game type detection
python test_game_types.py
```

## Benefits for Analysis

### 1. **Accurate Performance Metrics**
- Separate spring training stats from regular season
- Focus analysis on games that "count"
- Compare preseason vs regular season performance

### 2. **Seasonal Analysis**
- Track team improvement from spring to regular season
- Identify players who perform differently in different contexts
- Analyze coaching decisions by game importance

### 3. **Power BI Filtering**
- Create separate dashboards for different game types
- Filter measures by season type
- Build comparative analysis views

### 4. **Data Quality**
- Ensures proper context for all statistics
- Prevents mixing exhibition and competitive game data
- Maintains data integrity across different game contexts

## Future Enhancements

- **Playoff Analysis**: Automatically detect and analyze playoff performance
- **All-Star Integration**: Special handling for All-Star Game data  
- **International Games**: Detect special international series
- **Doubleheader Detection**: Track split-squad and doubleheader games

---

Your MLB data pipeline now provides complete game type awareness, enabling accurate analysis that properly separates preseason exhibition games from regular season competition!
