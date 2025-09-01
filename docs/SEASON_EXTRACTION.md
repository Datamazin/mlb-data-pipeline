# MLB Season Data Extraction Guide

This guide explains how to extract historical MLB season data using the enhanced extraction capabilities.

## Overview

The MLB data pipeline now supports extracting data for entire seasons, months, weeks, or custom date ranges. This is perfect for building historical datasets for analysis.

## Key Features

- ✅ **Full Season Extraction** - Extract entire MLB seasons (March to November)
- ✅ **Month/Week Extraction** - Extract specific periods
- ✅ **Custom Date Ranges** - Extract any date range you specify
- ✅ **Organized Storage** - Files organized by year/month directories
- ✅ **Progress Tracking** - Real-time progress updates and statistics
- ✅ **API Rate Limiting** - Respectful delays between API calls
- ✅ **Error Handling** - Continues extraction even if some games fail
- ✅ **Comprehensive Reporting** - Detailed statistics and failure logs

## Quick Start Commands

### Extract Recent Data (Testing)
```bash
# Test with last 3 days (no JSON saving for speed)
python extract_season.py test --no-json --test-days 3
```

### Extract Full Season
```bash
# Extract 2024 season
python run.py extract-season 2024

# Or using the advanced script
python extract_season.py season --year 2024
```

### Extract Specific Periods
```bash
# Extract April 2024
python run.py extract-month 2024 04

# Extract a specific week
python run.py extract-week 2024-04-15

# Custom date range
python extract_season.py date-range --start-date 2024-04-01 --end-date 2024-04-30
```

## Advanced Season Extraction Script

The `extract_season.py` script provides more advanced options:

### Basic Usage
```bash
python extract_season.py <mode> [options]
```

### Modes Available

| Mode | Description | Example |
|------|-------------|---------|
| `season` | Extract full season | `python extract_season.py season --year 2024` |
| `month` | Extract specific month | `python extract_season.py month --year 2024 --month 4` |
| `week` | Extract specific week | `python extract_season.py week --week-start 2024-04-15` |
| `date-range` | Custom date range | `python extract_season.py date-range --start-date 2024-04-01 --end-date 2024-04-07` |
| `test` | Test with recent data | `python extract_season.py test --test-days 5` |

### Advanced Options

| Option | Description | Default |
|--------|-------------|---------|
| `--year`, `-y` | Season year | Current year |
| `--delay`, `-d` | Delay between API calls (seconds) | 1.0 |
| `--no-json` | Skip saving JSON files | False |
| `--max-games-per-day` | Limit games per day | None |
| `--output-dir`, `-o` | Output directory | data/json |

### Examples

#### 1. Extract 2023 Season with Custom Settings
```bash
python extract_season.py season --year 2023 --delay 0.5
```

#### 2. Extract June 2024 with Limited Games (Testing)
```bash
python extract_season.py month --year 2024 --month 6 --max-games-per-day 3
```

#### 3. Extract World Series Week 2024
```bash
python extract_season.py week --week-start 2024-10-25 --delay 2.0
```

#### 4. Fast Testing (No JSON, Recent Games)
```bash
python extract_season.py test --no-json --test-days 7 --max-games-per-day 2
```

## File Organization

When extracting seasonal data, files are automatically organized:

```
data/json/
├── 2024/
│   ├── 03-March/
│   │   ├── boxscore_raw_661234_20240328_120000.json
│   │   ├── game_raw_661234_20240328_120000.json
│   │   └── combined_data_661234_20240328.json
│   ├── 04-April/
│   ├── 05-May/
│   └── ...
├── 2023/
│   └── ...
└── extraction_report_20250726_133121.json
```

## Data Types Extracted

For each game, the following data is captured:

### Boxscore Data
- Player statistics (batting, pitching)
- Team totals
- Game officials
- Performance highlights

### Game Data  
- Live scoring updates
- Inning-by-inning details
- Team information
- Game status and timing

### Metadata
- Extraction timestamp
- Game date and teams
- Game status (Final, Live, Preview)

## Typical Season Statistics

A full MLB season extraction typically includes:

- **~183 days** with games (March - October)
- **~2,430 regular season games** (162 games × 15 teams × 2)
- **~40-50 playoff games** (October)
- **~7,500+ JSON files** (3 files per game)
- **~2-4 GB** of raw JSON data

## Performance Considerations

### API Rate Limiting
- Default: 1 second delay between requests
- Recommended: 0.5-2.0 seconds for bulk extraction
- MLB API allows reasonable request rates

### Extraction Time Estimates
- **Single game**: ~3-5 seconds
- **Single day**: ~1-3 minutes (varies by # of games)
- **Full month**: ~30-90 minutes
- **Full season**: ~8-15 hours

### Storage Requirements
- **Single game**: ~50-200 KB JSON
- **Single month**: ~50-200 MB
- **Full season**: ~2-4 GB

## Error Handling

The extraction process is robust and handles:

- **Network timeouts** - Retries and continues
- **Missing games** - Logs and continues
- **API rate limits** - Respects delays
- **Invalid data** - Skips and logs errors

Failed extractions are logged in the final report with details.

## Monitoring Progress

During extraction, you'll see:

```
📅 Processing 2024-04-15...
   Found 15 game(s)
   [1/15] Game 746123: Dodgers @ Padres (Final)
      ✅ Extracted successfully
   [2/15] Game 746124: Yankees @ Red Sox (Final)  
      ✅ Extracted successfully
   ...
   
📊 Progress Update (Day 50):
   Days with games: 45
   Games extracted: 234/250
   JSON files saved: 702
```

## Best Practices

### 1. Start Small
```bash
# Test first
python extract_season.py test --test-days 3
```

### 2. Extract by Month
```bash
# Instead of full season, do monthly extractions
python extract_season.py month --year 2024 --month 4
python extract_season.py month --year 2024 --month 5
# ...
```

### 3. Monitor Storage
- Check disk space before large extractions
- Consider `--no-json` for testing
- Use `--max-games-per-day` for sampling

### 4. Be Respectful to API
- Don't reduce delay below 0.5 seconds
- Run extractions during off-peak hours
- Monitor for any API errors

## Integration with Database

After extracting seasonal data, load it to your database:

```bash
# Load all extracted JSON files to SQL Server
python run.py load-json

# View what was loaded
python run.py view-db
```

## Troubleshooting

### Large Extractions
- Use screen/tmux for long-running extractions
- Monitor disk space during extraction
- Check extraction reports for failures

### API Issues
- Increase delay if getting rate limited
- Check MLB API status for outages
- Some games may not have complete data

### Storage Issues
- Clean up old JSON files periodically
- Consider compressing historical data
- Use database storage for analysis

## Sample Workflows

### Historical Analysis Setup
```bash
# 1. Extract last season
python extract_season.py season --year 2024

# 2. Load to database  
python run.py load-json

# 3. View results
python run.py view-db
```

### Monthly Data Updates
```bash
# Extract current month incrementally
python extract_season.py month --year 2025 --month $(date +%m)
python run.py load-json
```

### Research Dataset Creation
```bash
# Extract specific period for research
python extract_season.py date-range \
    --start-date 2024-07-01 \
    --end-date 2024-09-30 \
    --delay 1.5
```

This seasonal extraction capability transforms your pipeline into a comprehensive historical data collection system! 🎉
