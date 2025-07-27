# MLB API Statistical Codes Documentation

## Overview
This document captures the statistical codes used by the MLB Stats API for walks and strikeouts, as implemented in our data pipeline.

## Walks and Strikeouts Statistical Codes

### Walks (Base on Balls)
| **API Field Name** | **Database Column** | **Description** | **Data Type** |
|-------------------|-------------------|-----------------|---------------|
| `baseOnBalls` | `walks` | Total walks (base on balls) | Integer |
| `intentionalWalks` | Not stored | Intentional walks subset | Integer |
| `walksPer9Inn` | Not stored | Walks per 9 innings (pitching stat) | String/Float |

**Example from MLB API JSON:**
```json
{
  "baseOnBalls": 3,
  "intentionalWalks": 1,
  "walksPer9Inn": "4.50"
}
```

### Strikeouts
| **API Field Name** | **Database Column** | **Description** | **Data Type** |
|-------------------|-------------------|-----------------|---------------|
| `strikeOuts` | `strikeouts` | Total strikeouts | Integer |
| `strikeoutsPer9Inn` | Not stored | Strikeouts per 9 innings (pitching stat) | String/Float |

**Example from MLB API JSON:**
```json
{
  "strikeOuts": 16,
  "strikeoutsPer9Inn": "9.45"
}
```

## Data Pipeline Implementation

### JSON to Database Mapping
Our pipeline maps these API fields as follows:

```python
# From src/database/json_to_sql_loader.py
batting_stats_mapping = {
    'walks': batting_stats.get('baseOnBalls', 0),      # API: baseOnBalls -> DB: walks
    'strikeouts': batting_stats.get('strikeOuts', 0)   # API: strikeOuts -> DB: strikeouts
}
```

### Database Schema
```sql
-- From src/database/connection.py
CREATE TABLE boxscore (
    game_id INT,
    player_id INT,
    team_id INT,
    -- ... other fields ...
    walks INT DEFAULT 0,
    strikeouts INT DEFAULT 0,
    -- ... other fields ...
);
```

## Additional Statistical Context

### Related Batting Statistics Available
The MLB API provides these related offensive statistics in the same data structure:

| **API Field** | **Description** |
|---------------|-----------------|
| `atBats` | At bats |
| `runs` | Runs scored |
| `hits` | Hits |
| `doubles` | Doubles |
| `triples` | Triples |
| `homeRuns` | Home runs |
| `rbi` | Runs batted in |
| `hitByPitch` | Hit by pitch |
| `stolenBases` | Stolen bases |
| `caughtStealing` | Caught stealing |

### Per-9-Innings Statistics (Pitching)
For pitching statistics, the API provides rate stats:
- `walksPer9Inn`: Walks allowed per 9 innings
- `strikeoutsPer9Inn`: Strikeouts per 9 innings

## API Data Sources
These statistics are extracted from:
1. **Game-level team stats**: Aggregated team totals
2. **Player-level batting stats**: Individual player performance
3. **Boxscore data**: Detailed game-by-game breakdowns

## Usage Examples

### Extracting Walk/Strikeout Data
```python
# Player batting stats from API response
player_stats = boxscore_data['teams']['home']['players'][player_id]['stats']['batting']

walks = player_stats.get('baseOnBalls', 0)
strikeouts = player_stats.get('strikeOuts', 0)
intentional_walks = player_stats.get('intentionalWalks', 0)
```

### Database Query Examples
```sql
-- Get player walk and strikeout totals
SELECT 
    player_id,
    SUM(walks) as total_walks,
    SUM(strikeouts) as total_strikeouts,
    COUNT(*) as games_played
FROM boxscore 
GROUP BY player_id;

-- Calculate walk and strikeout rates
SELECT 
    player_id,
    SUM(walks) * 1.0 / SUM(at_bats) as walk_rate,
    SUM(strikeouts) * 1.0 / SUM(at_bats) as strikeout_rate
FROM boxscore 
WHERE at_bats > 0
GROUP BY player_id;
```

## Notes
- **Case Sensitivity**: The API uses camelCase (`baseOnBalls`, `strikeOuts`)
- **Default Values**: Our pipeline defaults to 0 for missing values
- **Data Types**: All counting stats are integers in our database
- **API Reliability**: These fields are consistently available across all game data
- **Historical Data**: Available for all seasons from 2015+ through our extraction pipeline

## Last Updated
July 27, 2025 - Based on analysis of MLB Stats API data structure and pipeline implementation.
