# Power BI DAX Copy-Paste Guide

## 🎯 How to Use These Measures

### Step 1: Open Power BI Desktop
1. Open your MLB data model in Power BI Desktop
2. Ensure you have these tables with relationships:
   - `boxscore` (fact table with stats)
   - `teams` (dimension table)
   - `players` (dimension table)
   - `games` (fact/dimension table)

### Step 2: Copy Individual Measures
1. Go to **Modeling** tab → **New Measure**
2. Copy ONE measure at a time from `power_bi_dax_measures_ready.dax`
3. Paste into the formula bar
4. Press Enter to save

### Step 3: Adjust Table Names (if needed)
If your table names are different, replace:
- `boxscore` → your boxscore table name
- `teams` → your teams table name  
- `players` → your players table name
- `games` → your games table name

## 📋 Quick Copy Blocks

### Basic Statistics (Copy these first)
```dax
MEASURE 'Measures'[Total At Bats] = SUM(boxscore[at_bats])
MEASURE 'Measures'[Total Runs] = SUM(boxscore[runs])
MEASURE 'Measures'[Total Hits] = SUM(boxscore[hits])
MEASURE 'Measures'[Total RBI] = SUM(boxscore[rbi])
MEASURE 'Measures'[Total Walks] = SUM(boxscore[walks])
MEASURE 'Measures'[Total Strikeouts] = SUM(boxscore[strikeouts])
```

### Key Calculated Metrics
```dax
MEASURE 'Measures'[Batting Average] = 
VAR TotalHits = SUM(boxscore[hits])
VAR TotalAtBats = SUM(boxscore[at_bats])
RETURN 
    IF(TotalAtBats > 0, 
       DIVIDE(TotalHits, TotalAtBats, 0), 
       BLANK())

MEASURE 'Measures'[On Base Percentage] = 
VAR TotalHits = SUM(boxscore[hits])
VAR TotalWalks = SUM(boxscore[walks])
VAR TotalAtBats = SUM(boxscore[at_bats])
VAR PlateAppearances = TotalAtBats + TotalWalks
RETURN 
    IF(PlateAppearances > 0,
       DIVIDE(TotalHits + TotalWalks, PlateAppearances, 0),
       BLANK())
```

### Summary Measure (Copy last)
```dax
MEASURE 'Measures'[Boxscore Summary] = 
VAR Stats = 
    "BATTING STATISTICS" & UNICHAR(10) &
    "=================" & UNICHAR(10) &
    "At Bats: " & FORMAT('Measures'[Total At Bats], "#,0") & UNICHAR(10) &
    "Hits: " & FORMAT('Measures'[Total Hits], "#,0") & UNICHAR(10) &
    "Runs: " & FORMAT('Measures'[Total Runs], "#,0") & UNICHAR(10) &
    "RBI: " & FORMAT('Measures'[Total RBI], "#,0") & UNICHAR(10) &
    "Walks: " & FORMAT('Measures'[Total Walks], "#,0") & UNICHAR(10) &
    "Strikeouts: " & FORMAT('Measures'[Total Strikeouts], "#,0") & UNICHAR(10) &
    UNICHAR(10) &
    "CALCULATED METRICS" & UNICHAR(10) &
    "=================" & UNICHAR(10) &
    "Batting Average: " & FORMAT('Measures'[Batting Average], "0.000") & UNICHAR(10) &
    "On Base %: " & FORMAT('Measures'[On Base Percentage], "0.000") & UNICHAR(10) &
    "Strikeout Rate: " & FORMAT('Measures'[Strikeout Rate], "0.0%") & UNICHAR(10) &
    "Walk Rate: " & FORMAT('Measures'[Walk Rate], "0.0%") & UNICHAR(10) &
    "Runs/Game: " & FORMAT('Measures'[Runs Per Game], "0.00") & UNICHAR(10) &
    "RBI/Game: " & FORMAT('Measures'[RBI Per Game], "0.00")
RETURN Stats
```

## ⚡ Pro Tips

### 1. Create a Measures Table
- Right-click in Fields pane → **New Table**
- Name it "Measures" 
- All measures will be organized under this table

### 2. Test with Sample Data
Start with basic measures first:
1. `Total Hits`
2. `Total At Bats` 
3. `Batting Average`

### 3. Verify Relationships
Ensure these relationships exist:
- `boxscore[team_id]` → `teams[team_id]`
- `boxscore[player_id]` → `players[player_id]`
- `boxscore[game_id]` → `games[game_id]`

### 4. Common Issues
- **BLANK() results**: Check if your data has zeros instead of nulls
- **Wrong calculations**: Verify column names match exactly
- **Performance issues**: Start with basic measures, add complex ones later

## 🎨 Visualization Suggestions

### Player Performance Card
- **Main Value**: `Batting Average`
- **Supporting**: `Total Hits`, `Total RBI`
- **Tooltip**: `Player Season Summary`

### Team Comparison Table
- **Rows**: Team names
- **Values**: `Team Batting Average`, `Team Total Runs`, `Team Strength`
- **Conditional Formatting**: Use `BA Color` measure

### Executive Dashboard
- **Card Visual**: `Executive Summary`
- **Table**: `Boxscore Summary`

Happy analyzing! 🏟️⚾
