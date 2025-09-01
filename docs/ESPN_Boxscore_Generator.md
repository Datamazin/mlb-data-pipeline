# ESPN-Style MLB Boxscore Generator

A professional baseball boxscore generator that produces clean, newspaper-style statistical displays matching traditional MLB format.

## Overview

The ESPN-style boxscore generator (`espn_style_boxscore.py`) creates formatted baseball game statistics that closely match traditional sports media presentations. It pulls data from the MLB data pipeline database and formats it into readable tables with essential batting statistics.

## Features

### 📊 **Core Statistics**
- **AB** - At Bats
- **R** - Runs
- **H** - Hits  
- **RBI** - Runs Batted In
- **HR** - Home Runs
- **BB** - Walks (Base on Balls)
- **K** - Strikeouts
- **AVG** - Batting Average
- **OBP** - On-Base Percentage
- **SLG** - Slugging Percentage

### 🎯 **Advanced Features**
- Automatic team grouping by team_id
- Professional player name + position formatting
- Team totals with calculated averages
- Clean, compact table layout
- Database-driven data retrieval

## Usage

### Command Line Interface

```bash
# Generate boxscore for specific game ID
python espn_style_boxscore.py --game-id 776518

# Generate boxscore for the latest game with statistics
python espn_style_boxscore.py --latest

# Show help and usage information
python espn_style_boxscore.py --help
```

### Example Output

```
============================================================
MLB BOXSCORE
============================================================
Date: 2025-08-31
Status: Live

TEAM 113
HITTERS          AB  R  H RBI HR BB  K AVG OBP SLG
Austin Hays       3  1  1   2  1  0  1 0.333 0.333 1.333
Elly De La Cruz   4  1  1   0  0  0  1 0.250 0.250 0.500
TJ Friedl         4  0  3   2  0  0  1 0.750 0.750 0.750
TEAM             25  5  7   5  1  5  8

TEAM 138
HITTERS          AB  R  H RBI HR BB  K AVG OBP SLG
Jimmy Crooks      3  1  1   1  1  0  1 0.333 0.333 1.333
Lars Nootbaar     4  2  2   0  0  0  1 0.500 0.500 1.000
TEAM             25  4  6   4  1  0  9
============================================================
```

## Technical Implementation

### Database Schema Requirements

The generator requires the following database tables and fields:

#### Games Table
- `game_id` - Unique game identifier
- `game_date` - Date of the game
- `game_status` - Current game status (Live, Final, etc.)

#### Boxscore Table
- `game_id` - Links to games table
- `player_id` - Links to players table
- `team_id` - Team identifier
- `at_bats` - At-bats count
- `runs` - Runs scored
- `hits` - Hits count
- `rbi` - RBIs count
- `doubles` - Doubles count
- `triples` - Triples count
- `home_runs` - Home runs count
- `walks` - Walks count
- `strikeouts` - Strikeouts count
- `hit_by_pitch` - Hit by pitch count

#### Players Table
- `player_id` - Unique player identifier
- `player_name` - Player's name
- `position` - Player's position

### Statistical Calculations

#### Batting Average (AVG)
```
AVG = Hits / At-Bats
```

#### On-Base Percentage (OBP)
```
OBP = (Hits + Walks + Hit By Pitch) / (At-Bats + Walks + Hit By Pitch)
```

#### Slugging Percentage (SLG)
```
Total Bases = Singles + (Doubles × 2) + (Triples × 3) + (Home Runs × 4)
SLG = Total Bases / At-Bats
```

Where:
```
Singles = Hits - Doubles - Triples - Home Runs
```

## Code Structure

### Main Classes

#### ESPNStyleBoxscore
The primary class that handles all boxscore generation functionality.

**Key Methods:**
- `generate_boxscore(game_id)` - Main entry point for boxscore generation
- `get_team_batting_stats(game_id, team_id=None)` - Retrieves batting statistics
- `get_team_totals(game_id, team_id=None)` - Calculates team totals
- `format_batting_stats(team_name, batting_stats, team_totals)` - Formats output
- `get_latest_game()` - Finds most recent game with statistics

### Database Integration

The generator uses the `DatabaseConnection` class from the MLB data pipeline:

```python
from database.connection import DatabaseConnection

db = DatabaseConnection()
db.connect()
# Execute queries...
db.disconnect()
```

### Error Handling

The generator includes comprehensive error handling for:
- Database connection failures
- Missing game data
- Invalid game IDs
- Statistical calculation errors

## Installation & Setup

### Prerequisites
- Python 3.8+
- Access to MLB data pipeline database
- Required Python packages (see requirements.txt)

### Dependencies
```python
import sys
import os
import argparse
from database.connection import DatabaseConnection
```

### Database Connection
Ensure your database connection is configured in `src/database/connection.py` with proper credentials for the MLB data pipeline database.

## Performance Considerations

### Query Optimization
- Uses parameterized queries to prevent SQL injection
- Efficient JOINs between games, boxscore, and players tables
- Indexes on game_id and team_id recommended for optimal performance

### Memory Usage
- Processes statistics in memory for formatting
- Suitable for individual game processing
- Consider batching for bulk operations

## Troubleshooting

### Common Issues

#### "Game X not found"
- Verify the game_id exists in the games table
- Check that the game has associated boxscore data

#### "No batting statistics found"
- Confirm boxscore records exist for the specified game
- Verify player_id relationships are properly established

#### "Could not find team information"
- This is handled gracefully - the generator will group by team_id from boxscore data
- Team names may display as "Team X" if team metadata is unavailable

### Debug Mode
Add debug logging by modifying the database queries to include result counts:

```python
print(f"Found {len(batting_stats)} batting records")
print(f"Found {len(team_totals)} team records")
```

## Future Enhancements

### Planned Features
- Pitching statistics integration
- Game situation context (inning, score)
- Historical comparison metrics
- Export to different formats (CSV, JSON, HTML)

### Customization Options
- Configurable stat columns
- Team name display preferences  
- Formatting style options
- Filtering by player position

## Contributing

When contributing to the boxscore generator:

1. **Maintain Statistical Accuracy** - Ensure all baseball calculations follow official MLB standards
2. **Preserve Formatting** - Keep the clean, professional table layout
3. **Test with Real Data** - Verify with actual game scenarios
4. **Document Changes** - Update this documentation for any new features

## License

Part of the MLB Data Pipeline project. See main project license for details.

---

*Generated from MLB data pipeline - Professional baseball statistics for data analysis and reporting*
