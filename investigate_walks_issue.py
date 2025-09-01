#!/usr/bin/env python3
"""
Investigate walks data issue from April 18th onwards
"""

import sys
import os
from datetime import datetime, timedelta

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection

def investigate_walks_issue():
    """Investigate the walks data issue from April 18th onwards."""
    
    db = DatabaseConnection()
    db.connect()
    
    print("🔍 WALKS ANALYSIS - APRIL 18+ ISSUE")
    print("=" * 60)
    
    # Check walks by date range
    query = """
    SELECT 
        g.game_date,
        COUNT(DISTINCT g.game_id) as games,
        COUNT(b.id) as total_records,
        SUM(CASE WHEN b.walks > 0 THEN 1 ELSE 0 END) as records_with_walks,
        SUM(ISNULL(b.walks, 0)) as total_walks,
        AVG(CAST(ISNULL(b.walks, 0) AS FLOAT)) as avg_walks_per_record
    FROM games g
    LEFT JOIN boxscore b ON g.game_id = b.game_id
    WHERE g.game_date >= :start_date AND g.game_date <= :end_date
    GROUP BY g.game_date
    ORDER BY g.game_date
    """
    
    print("📅 Date        Games  Records  W/Walks  Total  Avg")
    print("-" * 55)
    
    results = db.fetch_results(query, {'start_date': '2025-04-15', 'end_date': '2025-04-25'})
    for row in results:
        date, games, records, with_walks, total, avg = row
        avg_val = avg or 0
        date_str = date.strftime('%Y-%m-%d')
        print(f"{date_str}     {games:2d}     {records:3d}      {with_walks:3d}    {total:3d}  {avg_val:.2f}")
    
    print()
    
    # Check JSON files for April 18th
    print("🔍 Checking JSON files for April 18th, 2025:")
    
    # Get a game from April 18th
    game_query = """
    SELECT TOP 1 g.game_id, g.game_date, g.home_team_id, g.away_team_id
    FROM games g
    WHERE g.game_date = :game_date
    ORDER BY g.game_id
    """
    
    game_results = db.fetch_results(game_query, {'game_date': '2025-04-18'})
    if game_results:
        game_id, game_date, home_team, away_team = game_results[0]
        print(f"   📋 Game {game_id} on {game_date.strftime('%Y-%m-%d')}")
        
        # Check if JSON file exists
        from pathlib import Path
        json_path = Path(f"data/json/2025/04-April/combined_data_{game_id}_20250418.json")
        
        if json_path.exists():
            print(f"   ✅ JSON file exists: {json_path}")
            
            # Check JSON content for baseOnBalls
            import json
            try:
                with open(json_path, 'r') as f:
                    json_data = json.load(f)
                
                # Look for baseOnBalls in the JSON structure
                walks_found = False
                sample_count = 0
                
                def check_for_walks(obj, path=""):
                    nonlocal walks_found, sample_count
                    
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            if 'base' in key.lower() and 'ball' in key.lower():
                                if value and value > 0:
                                    walks_found = True
                                    print(f"      🎯 Found {key}: {value} at {path}.{key}")
                                    sample_count += 1
                                    if sample_count >= 3:  # Show first 3 examples
                                        return
                            elif isinstance(value, (dict, list)):
                                check_for_walks(value, f"{path}.{key}" if path else key)
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            if isinstance(item, (dict, list)):
                                check_for_walks(item, f"{path}[{i}]" if path else f"[{i}]")
                
                check_for_walks(json_data)
                
                if not walks_found:
                    print("      ❌ No baseOnBalls/walks data found in JSON")
                    
                    # Check the structure
                    print("      📋 JSON structure preview:")
                    if 'boxscore' in json_data:
                        boxscore = json_data['boxscore']
                        if 'teams' in boxscore:
                            for team_key in ['away', 'home']:
                                if team_key in boxscore['teams']:
                                    team_data = boxscore['teams'][team_key]
                                    if 'players' in team_data:
                                        print(f"         {team_key} team has {len(team_data['players'])} players")
                                        # Check first player structure
                                        first_player = list(team_data['players'].values())[0]
                                        if 'stats' in first_player and 'batting' in first_player['stats']:
                                            batting_stats = first_player['stats']['batting']
                                            print(f"         Batting stats keys: {list(batting_stats.keys())[:10]}")
                
            except Exception as e:
                print(f"      ❌ Error reading JSON: {e}")
        else:
            print(f"      ❌ JSON file not found: {json_path}")
    
    # Compare with earlier date that has walks
    print("\n🔍 Comparing with April 15th (should have walks):")
    
    early_results = db.fetch_results(game_query, {'game_date': '2025-04-15'})
    if early_results:
        game_id, game_date, home_team, away_team = early_results[0]
        print(f"   📋 Game {game_id} on {game_date.strftime('%Y-%m-%d')}")
        
        json_path = Path(f"data/json/2025/04-April/combined_data_{game_id}_20250415.json")
        if json_path.exists():
            print(f"   ✅ JSON file exists: {json_path}")
            
            import json
            try:
                with open(json_path, 'r') as f:
                    json_data = json.load(f)
                
                walks_found = False
                sample_count = 0
                
                def check_for_walks_early(obj, path=""):
                    nonlocal walks_found, sample_count
                    
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            if 'base' in key.lower() and 'ball' in key.lower():
                                if value and value > 0:
                                    walks_found = True
                                    print(f"      ✅ Found {key}: {value} at {path}.{key}")
                                    sample_count += 1
                                    if sample_count >= 2:
                                        return
                            elif isinstance(value, (dict, list)):
                                check_for_walks_early(value, f"{path}.{key}" if path else key)
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            if isinstance(item, (dict, list)):
                                check_for_walks_early(item, f"{path}[{i}]" if path else f"[{i}]")
                
                check_for_walks_early(json_data)
                
                if not walks_found:
                    print("      ⚠️  Also no walks found in April 15th JSON")
                
            except Exception as e:
                print(f"      ❌ Error reading JSON: {e}")
    
    # Check database for pattern
    print("\n📊 Monthly walks summary:")
    monthly_query = """
    SELECT 
        YEAR(g.game_date) as year,
        MONTH(g.game_date) as month,
        COUNT(DISTINCT g.game_id) as games,
        SUM(CASE WHEN b.walks > 0 THEN 1 ELSE 0 END) as records_with_walks,
        SUM(ISNULL(b.walks, 0)) as total_walks
    FROM games g
    LEFT JOIN boxscore b ON g.game_id = b.game_id
    WHERE g.game_date >= :start_date AND g.game_date <= :end_date
    GROUP BY YEAR(g.game_date), MONTH(g.game_date)
    ORDER BY YEAR(g.game_date), MONTH(g.game_date)
    """
    
    monthly_results = db.fetch_results(monthly_query, {'start_date': '2025-03-01', 'end_date': '2025-08-31'})
    print("📅 Year-Month  Games  Records w/Walks  Total Walks")
    print("-" * 50)
    for row in monthly_results:
        year, month, games, with_walks, total = row
        print(f"   {year}-{month:02d}      {games:4d}       {with_walks:5d}        {total:5d}")
    
    db.disconnect()
    
    print("\n💡 CONCLUSIONS:")
    print("   - Check if JSON structure changed after April 17th")
    print("   - Verify if MLB API response format changed")
    print("   - May need to update JSON parsing logic")

if __name__ == "__main__":
    investigate_walks_issue()
