#!/usr/bin/env python3
"""
MLB Data Export to CSV for Fabric Import
=========================================

Since table creation is restricted, this script exports today's MLB data
to CSV files that can be imported into Fabric manually.
"""

import os
import sys
import csv
import json
from datetime import datetime, date
from pathlib import Path

# Add src to path
sys.path.append('src')

from etl.extract import get_games_for_date
from api.mlb_client import MLBClient

def export_todays_games_to_csv():
    """Export today's MLB games to CSV files for Fabric import."""
    print("📊 MLB Data Export for Fabric Import")
    print("=" * 50)
    
    # Create export directory
    export_dir = Path("fabric_export")
    export_dir.mkdir(exist_ok=True)
    
    # Initialize client
    client = MLBClient()
    
    # Get today's date
    today = date.today()
    print(f"📅 Extracting games for: {today}")
    
    try:
        # Extract today's games
        games_data = []
        games_schedule = get_games_for_date(today)
        
        if not games_schedule:
            print("❌ No games found for today")
            return False
        
        print(f"🎯 Found {len(games_schedule)} games scheduled")
        
        # Get detailed data for each game
        for game_info in games_schedule:
            game_id = game_info['gamePk']
            print(f"   Fetching data for Game {game_id}...")
            
            try:
                boxscore_data = client.fetch_boxscore(game_id)
                game_data = client.fetch_game_data(game_id)
                
                if boxscore_data and game_data:
                    # Combine the data
                    combined_game_data = {
                        'game': game_data,
                        'liveData': {'boxscore': boxscore_data}
                    }
                    games_data.append(combined_game_data)
                    print(f"   ✅ Game {game_id} data extracted")
                else:
                    print(f"   ⚠️  Game {game_id} data incomplete")
            except Exception as e:
                print(f"   ❌ Error extracting Game {game_id}: {e}")
        
        if not games_data:
            print("❌ No complete game data extracted")
            return False
        
        # Prepare data containers
        teams_data = {}
        players_data = {}
        games_rows = []
        boxscore_rows = []
        raw_json_rows = []
        
        # Process each game
        for game_data in games_data:
            # Get game info from boxscore (which has the detailed team info)
            boxscore = game_data.get('liveData', {}).get('boxscore', {})
            if not boxscore:
                continue
                
            # Get game ID and date from schedule info
            schedule_info = games_schedule[games_data.index(game_data)]
            game_id = schedule_info['gamePk']
            game_date = schedule_info.get('officialDate', today.isoformat())
            
            # Store raw JSON with enhanced metadata
            raw_json_rows.append({
                'game_id': game_id,
                'game_date': game_date,  # Added game_date
                'data_type': 'boxscore',
                'json_data': json.dumps(game_data),
                'extraction_timestamp': datetime.now().isoformat()
            })
            
            # Extract teams from boxscore
            home_team = boxscore['teams']['home']['team']
            away_team = boxscore['teams']['away']['team']
            
            for team in [home_team, away_team]:
                if team['id'] not in teams_data:
                    teams_data[team['id']] = {
                        'team_id': team['id'],
                        'team_name': team['name'],
                        'abbreviation': team['abbreviation'],
                        'league': team.get('league', {}).get('name', ''),
                        'division': team.get('division', {}).get('name', ''),
                        'game_id': game_id,  # Added game_id to track which game this team data came from
                        'game_date': game_date,  # Added game_date
                        'created_at': datetime.now().isoformat()
                    }
            
            # Extract game info with consistent date handling
            games_rows.append({
                'game_id': game_id,
                'game_date': game_date,  # Use consistent game_date from schedule
                'home_team_id': home_team['id'],
                'away_team_id': away_team['id'],
                'home_score': schedule_info.get('home_score', 0),
                'away_score': schedule_info.get('away_score', 0),
                'inning': 9,  # Default for completed games
                'inning_state': 'Final',
                'game_status': schedule_info.get('status', 'Final'),
                'game_type': schedule_info.get('gameType', 'R'),
                'series_description': schedule_info.get('seriesDescription', ''),
                'official_date': game_date,  # Consistent with game_date
                'created_at': datetime.now().isoformat()
            })
            
            # Extract boxscore data
            for team_type in ['home', 'away']:
                team_id = boxscore['teams'][team_type]['team']['id']
                team_players = boxscore.get('teams', {}).get(team_type, {}).get('players', {})
                
                for player_key, player_data in team_players.items():
                    if not player_key.startswith('ID'):
                        continue
                    
                    player_id = int(player_key.replace('ID', ''))
                    person = player_data.get('person', {})
                    stats = player_data.get('stats', {}).get('batting', {})
                    
                    # Store player info with game context
                    if player_id not in players_data:
                        players_data[player_id] = {
                            'player_id': player_id,
                            'player_name': person.get('fullName', ''),
                            'team_id': team_id,
                            'position': player_data.get('position', {}).get('abbreviation', ''),
                            'game_id': game_id,  # Added game_id to track which game this player data came from
                            'game_date': game_date,  # Added game_date
                            'created_at': datetime.now().isoformat()
                        }
                    
                    # Store boxscore stats with enhanced fields and consistent game info
                    if stats:  # Only if batting stats exist
                        boxscore_rows.append({
                            'game_id': game_id,  # Explicitly included
                            'player_id': player_id,
                            'team_id': team_id,
                            'at_bats': stats.get('atBats', 0),
                            'runs': stats.get('runs', 0),
                            'hits': stats.get('hits', 0),
                            'doubles': stats.get('doubles', 0),
                            'triples': stats.get('triples', 0),
                            'home_runs': stats.get('homeRuns', 0),
                            'rbi': stats.get('rbi', 0),
                            'walks': stats.get('baseOnBalls', 0),
                            'strikeouts': stats.get('strikeOuts', 0),
                            'stolen_bases': stats.get('stolenBases', 0),  # Enhanced field
                            'caught_stealing': stats.get('caughtStealing', 0),  # Enhanced field
                            'hit_by_pitch': stats.get('hitByPitch', 0),
                            'sacrifice_flies': stats.get('sacFlies', 0),
                            'sacrifice_bunts': stats.get('sacBunts', 0),
                            'game_date': game_date,  # Explicitly included with consistent date
                            'created_at': datetime.now().isoformat()
                        })
        
        # Write CSV files
        csv_files = []
        
        # Teams CSV
        teams_file = export_dir / "teams.csv"
        with open(teams_file, 'w', newline='', encoding='utf-8') as f:
            if teams_data:
                writer = csv.DictWriter(f, fieldnames=list(teams_data.values())[0].keys())
                writer.writeheader()
                writer.writerows(teams_data.values())
        csv_files.append(teams_file)
        
        # Players CSV
        players_file = export_dir / "players.csv"
        with open(players_file, 'w', newline='', encoding='utf-8') as f:
            if players_data:
                writer = csv.DictWriter(f, fieldnames=list(players_data.values())[0].keys())
                writer.writeheader()
                writer.writerows(players_data.values())
        csv_files.append(players_file)
        
        # Games CSV
        games_file = export_dir / "games.csv"
        with open(games_file, 'w', newline='', encoding='utf-8') as f:
            if games_rows:
                writer = csv.DictWriter(f, fieldnames=games_rows[0].keys())
                writer.writeheader()
                writer.writerows(games_rows)
        csv_files.append(games_file)
        
        # Boxscore CSV
        boxscore_file = export_dir / "boxscore.csv"
        with open(boxscore_file, 'w', newline='', encoding='utf-8') as f:
            if boxscore_rows:
                writer = csv.DictWriter(f, fieldnames=boxscore_rows[0].keys())
                writer.writeheader()
                writer.writerows(boxscore_rows)
        csv_files.append(boxscore_file)
        
        # Raw JSON CSV
        raw_json_file = export_dir / "raw_json_data.csv"
        with open(raw_json_file, 'w', newline='', encoding='utf-8') as f:
            if raw_json_rows:
                writer = csv.DictWriter(f, fieldnames=raw_json_rows[0].keys())
                writer.writeheader()
                writer.writerows(raw_json_rows)
        csv_files.append(raw_json_file)
        
        # Print results
        print(f"\n✅ Successfully exported data to {len(csv_files)} CSV files:")
        for file_path in csv_files:
            file_size = file_path.stat().st_size
            print(f"   📄 {file_path.name} ({file_size:,} bytes)")
        
        print(f"\n📊 Data Summary:")
        print(f"   - Teams: {len(teams_data)}")
        print(f"   - Players: {len(players_data)}")
        print(f"   - Games: {len(games_rows)}")
        print(f"   - Boxscore entries: {len(boxscore_rows)}")
        print(f"   - Enhanced fields: stolen_bases, caught_stealing included")
        
        print(f"\n📁 Files location: {export_dir.absolute()}")
        print("\n💡 Import options:")
        print("   1. Upload CSV files to Fabric via web interface")
        print("   2. Use Fabric's data import tools")
        print("   3. Share with admin to bulk load into tables")
        
        return True
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")
        return False

if __name__ == "__main__":
    success = export_todays_games_to_csv()
    if success:
        print("\n🎯 Ready for Fabric import!")
    else:
        print("\n❌ Export failed")
