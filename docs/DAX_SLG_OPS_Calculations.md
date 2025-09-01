# MLB Slugging Percentage (SLG) and OPS Calculations in DAX

This document provides DAX formulas for calculating advanced baseball statistics including Slugging Percentage (SLG) and On-Base Plus Slugging (OPS) using MLB data pipeline data.

## Overview

**Slugging Percentage (SLG)** measures a player's power by calculating total bases per at-bat.

**On-Base Plus Slugging (OPS)** combines a player's ability to get on base with their power hitting ability.

## Data Requirements

These calculations require data from the `boxscore` table with the following fields:
- `at_bats` - Official at-bats
- `hits` - Total hits
- `doubles` - Two-base hits
- `triples` - Three-base hits
- `home_runs` - Home runs
- `walks` - Bases on balls
- `hit_by_pitch` - Times hit by pitch
- `sacrifice_flies` - Sacrifice flies (if available)

## DAX Measures

### 1. Total Bases

Total bases considers the base value of each hit type:
- Singles = 1 base
- Doubles = 2 bases  
- Triples = 3 bases
- Home runs = 4 bases

```dax
Total Bases = 
VAR Singles = SUM(boxscore[hits]) - SUM(boxscore[doubles]) - SUM(boxscore[triples]) - SUM(boxscore[home_runs])
VAR Doubles = SUM(boxscore[doubles]) * 2
VAR Triples = SUM(boxscore[triples]) * 3
VAR HomeRuns = SUM(boxscore[home_runs]) * 4
RETURN
    Singles + Doubles + Triples + HomeRuns
```

### 2. Slugging Percentage (SLG)

SLG = Total Bases ÷ At-Bats

```dax
SLG = 
VAR TotalBases = [Total Bases]
VAR AtBats = SUM(boxscore[at_bats])
RETURN
    IF(AtBats > 0, TotalBases / AtBats, BLANK())
```

### 3. On-Base Percentage (OBP)

OBP = (Hits + Walks + HBP) ÷ (At-Bats + Walks + HBP + SF)

```dax
OBP = 
VAR Hits = SUM(boxscore[hits])
VAR Walks = SUM(boxscore[walks])
VAR HBP = SUM(boxscore[hit_by_pitch])
VAR AtBats = SUM(boxscore[at_bats])
VAR SacFlies = SUM(boxscore[sacrifice_flies]) -- Use 0 if not available
VAR PlateAppearances = AtBats + Walks + HBP + SacFlies
RETURN
    IF(PlateAppearances > 0, (Hits + Walks + HBP) / PlateAppearances, BLANK())
```

### 4. On-Base Plus Slugging (OPS)

OPS = OBP + SLG

```dax
OPS = 
VAR OnBasePercentage = [OBP]
VAR SluggingPercentage = [SLG]
RETURN
    IF(NOT ISBLANK(OnBasePercentage) && NOT ISBLANK(SluggingPercentage),
       OnBasePercentage + SluggingPercentage,
       BLANK())
```

## Alternative Simplified Formulas

### Simplified SLG (if sacrifice flies data not available)

```dax
SLG Simplified = 
DIVIDE(
    (SUM(boxscore[hits]) - SUM(boxscore[doubles]) - SUM(boxscore[triples]) - SUM(boxscore[home_runs])) +
    (SUM(boxscore[doubles]) * 2) +
    (SUM(boxscore[triples]) * 3) +
    (SUM(boxscore[home_runs]) * 4),
    SUM(boxscore[at_bats])
)
```

### Simplified OBP (assuming SF = 0)

```dax
OBP Simplified = 
DIVIDE(
    SUM(boxscore[hits]) + SUM(boxscore[walks]) + SUM(boxscore[hit_by_pitch]),
    SUM(boxscore[at_bats]) + SUM(boxscore[walks]) + SUM(boxscore[hit_by_pitch])
)
```

## Player-Level Calculations

### Individual Player SLG

```dax
Player SLG = 
VAR PlayerAtBats = 
    CALCULATE(
        SUM(boxscore[at_bats]),
        FILTER(boxscore, boxscore[player_id] = SELECTEDVALUE(players[player_id]))
    )
VAR PlayerTotalBases = 
    CALCULATE(
        [Total Bases],
        FILTER(boxscore, boxscore[player_id] = SELECTEDVALUE(players[player_id]))
    )
RETURN
    DIVIDE(PlayerTotalBases, PlayerAtBats)
```

### Season-to-Date Player OPS

```dax
Player Season OPS = 
VAR PlayerFilter = FILTER(boxscore, boxscore[player_id] = SELECTEDVALUE(players[player_id]))
VAR SeasonFilter = FILTER(PlayerFilter, YEAR(boxscore[game_date]) = YEAR(TODAY()))
VAR PlayerOBP = 
    CALCULATE(
        [OBP],
        SeasonFilter
    )
VAR PlayerSLG = 
    CALCULATE(
        [SLG],
        SeasonFilter
    )
RETURN
    PlayerOBP + PlayerSLG
```

## Team-Level Calculations

### Team Slugging Percentage

```dax
Team SLG = 
CALCULATE(
    [SLG],
    FILTER(boxscore, boxscore[team_id] = SELECTEDVALUE(teams[team_id]))
)
```

### Team OPS by Game Type

```dax
Team Regular Season OPS = 
CALCULATE(
    [OPS],
    FILTER(games, games[game_type] = "R"),
    FILTER(boxscore, boxscore[team_id] = SELECTEDVALUE(teams[team_id]))
)
```

## Performance Categories

### OPS Rating Categories

```dax
OPS Rating = 
VAR PlayerOPS = [OPS]
RETURN
    SWITCH(TRUE(),
        PlayerOPS >= 1.000, "Excellent (1.000+)",
        PlayerOPS >= 0.900, "Great (0.900-0.999)",
        PlayerOPS >= 0.800, "Very Good (0.800-0.899)",
        PlayerOPS >= 0.700, "Above Average (0.700-0.799)",
        PlayerOPS >= 0.600, "Below Average (0.600-0.699)",
        "Poor (< 0.600)"
    )
```

### SLG Rating Categories

```dax
SLG Rating = 
VAR PlayerSLG = [SLG]
RETURN
    SWITCH(TRUE(),
        PlayerSLG >= 0.600, "Excellent Power (0.600+)",
        PlayerSLG >= 0.500, "Good Power (0.500-0.599)",
        PlayerSLG >= 0.450, "Average Power (0.450-0.499)",
        PlayerSLG >= 0.400, "Below Average (0.400-0.449)",
        "Poor Power (< 0.400)"
    )
```

## Advanced Calculations

### Isolated Power (ISO)

ISO = SLG - Batting Average

```dax
ISO = 
VAR SluggingPct = [SLG]
VAR BattingAvg = DIVIDE(SUM(boxscore[hits]), SUM(boxscore[at_bats]))
RETURN
    SluggingPct - BattingAvg
```

### Extra Base Hit Percentage

```dax
Extra Base Hit % = 
VAR ExtraBaseHits = SUM(boxscore[doubles]) + SUM(boxscore[triples]) + SUM(boxscore[home_runs])
VAR TotalHits = SUM(boxscore[hits])
RETURN
    DIVIDE(ExtraBaseHits, TotalHits)
```

## Usage Examples

### Power BI Table Visual
Create a table with these columns:
- Player Name: `players[player_name]`
- At-Bats: `SUM(boxscore[at_bats])`
- Hits: `SUM(boxscore[hits])`
- SLG: `[SLG]`
- OBP: `[OBP]`
- OPS: `[OPS]`
- OPS Rating: `[OPS Rating]`

### Power BI Card Visuals
- **Team OPS**: Display `[OPS]` filtered by team
- **League Leader OPS**: `MAXX(ALL(players), [OPS])`
- **Season High SLG**: `MAXX(ALL(boxscore), [SLG])`

## Data Quality Considerations

1. **Null Handling**: All formulas use `DIVIDE()` or conditional logic to handle division by zero
2. **Minimum At-Bats**: Consider filtering players with minimum at-bats for meaningful statistics
3. **Game Type Filtering**: Use `games[game_type] = "R"` for regular season only
4. **Date Ranges**: Apply date filters for current season or specific periods

## Formula Validation

### Expected Ranges
- **SLG**: Typically 0.300-0.700 (elite players may exceed 0.600)
- **OBP**: Typically 0.250-0.450 (elite players may exceed 0.400)  
- **OPS**: Typically 0.550-1.150 (elite players may exceed 1.000)

### Test Cases
```dax
-- Babe Ruth 1927: .772 SLG, 1.258 OPS
-- Modern elite: .600+ SLG, 1.000+ OPS
-- League average: ~.430 SLG, ~.740 OPS
```

## Related Documentation

- [MLB API Statistical Codes](./MLB_API_Statistical_Codes.md)
- [Power BI Baseball Dashboard Guide](./PowerBI_Baseball_Dashboard.md)
- [DAX Batting Statistics](./DAX_Batting_Statistics.md)

---

*Last Updated: August 31, 2025*
*MLB Data Pipeline Documentation*
