from src.api.mlb_client import MLBClient
from src.utils.json_handler import save_raw_api_data, save_to_json
import requests
from datetime import datetime, timedelta, date
import time
import os

def get_current_games():
    """Get today's games to find a valid game ID"""
    today = datetime.now().strftime('%Y-%m-%d')
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('dates') and len(data['dates']) > 0 and data['dates'][0].get('games'):
                return [game['gamePk'] for game in data['dates'][0]['games']]
    except:
        pass
    return []

def get_games_for_date(target_date):
    """Get all games for a specific date"""
    if isinstance(target_date, date):
        date_str = target_date.strftime('%Y-%m-%d')
    else:
        date_str = target_date
    
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date_str}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('dates') and len(data['dates']) > 0 and data['dates'][0].get('games'):
                games = []
                for game in data['dates'][0]['games']:
                    games.append({
                        'gamePk': game['gamePk'],
                        'gameDate': game['gameDate'],
                        'gameType': game.get('gameType'),  # Include game type
                        'officialDate': game.get('officialDate'),  # Include official date
                        'seriesDescription': game.get('seriesDescription'),  # Include series description
                        'status': game['status']['abstractGameState'],
                        'home_team': game['teams']['home']['team']['name'],
                        'away_team': game['teams']['away']['team']['name']
                    })
                return games
    except Exception as e:
        print(f"Error fetching games for {date_str}: {e}")
    return []

def get_season_date_range(year=None):
    """Get the typical MLB season date range for a given year"""
    if year is None:
        year = datetime.now().year
    
    # MLB season typically runs from late March/early April to late September/early October
    # Playoffs can extend into November
    season_start = date(year, 3, 20)  # Conservative start date
    season_end = date(year, 11, 15)   # Conservative end date including playoffs
    
    return season_start, season_end

def extract_season_data(year=None, start_date=None, end_date=None, 
                       save_json=True, delay_seconds=1, max_games_per_day=None):
    """
    Extract data for an entire MLB season by iterating through each day.
    
    Args:
        year: Season year (default: current year)
        start_date: Custom start date (YYYY-MM-DD string or date object)
        end_date: Custom end date (YYYY-MM-DD string or date object)
        save_json: Whether to save JSON files
        delay_seconds: Delay between API calls to be respectful
        max_games_per_day: Limit games per day (useful for testing)
    
    Returns:
        Dictionary with extraction statistics
    """
    if year is None:
        year = datetime.now().year
    
    # Determine date range
    if start_date and end_date:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        start_date, end_date = get_season_date_range(year)
    
    print(f"🏟️  Extracting MLB {year} season data from {start_date} to {end_date}")
    
    # Statistics tracking
    stats = {
        'total_days': 0,
        'days_with_games': 0,
        'total_games_found': 0,
        'games_extracted': 0,
        'games_failed': 0,
        'json_files_saved': 0,
        'start_date': start_date,
        'end_date': end_date,
        'extraction_start_time': datetime.now(),
        'failed_games': []
    }
    
    current_date = start_date
    client = MLBClient()
    
    while current_date <= end_date:
        stats['total_days'] += 1
        date_str = current_date.strftime('%Y-%m-%d')
        
        print(f"\n📅 Processing {date_str}...")
        
        # Get games for this date
        games = get_games_for_date(current_date)
        
        if games:
            stats['days_with_games'] += 1
            stats['total_games_found'] += len(games)
            
            # Limit games per day if specified (useful for testing)
            if max_games_per_day:
                games = games[:max_games_per_day]
            
            print(f"   Found {len(games)} game(s)")
            
            for i, game in enumerate(games, 1):
                game_id = game['gamePk']
                status = game['status']
                
                print(f"   [{i}/{len(games)}] Game {game_id}: {game['away_team']} @ {game['home_team']} ({status})")
                
                # Only extract data for completed games or games in progress
                if status in ['Final', 'Live', 'In Progress']:
                    try:
                        # Extract game data
                        boxscore_data = client.fetch_boxscore(game_id)
                        game_data = client.fetch_game_data(game_id)
                        
                        if boxscore_data and game_data:
                            stats['games_extracted'] += 1
                            
                            # Save to JSON files if requested
                            if save_json:
                                # Create date-specific directory
                                date_dir = f"data/json/{year}/{current_date.strftime('%m-%B')}"
                                
                                saved_files = save_raw_api_data(boxscore_data, game_data, game_id, date_dir)
                                stats['json_files_saved'] += len(saved_files)
                                
                                # Save combined file with additional metadata
                                combined_data = {
                                    "game_id": game_id,
                                    "game_date": date_str,
                                    "extraction_timestamp": datetime.now().isoformat(),
                                    "home_team": game['home_team'],
                                    "away_team": game['away_team'],
                                    "game_status": status,
                                    "game_type": game.get('gameType'),  # Include game type from schedule
                                    "official_date": game.get('officialDate'),  # Include official date
                                    "series_description": game.get('seriesDescription'),  # Include series description
                                    "boxscore": boxscore_data,
                                    "game_data": game_data
                                }
                                
                                combined_path = save_to_json(combined_data, f"combined_data_{game_id}_{date_str.replace('-', '')}", date_dir)
                                if combined_path:
                                    stats['json_files_saved'] += 1
                            
                            print(f"      ✅ Extracted successfully")
                        else:
                            stats['games_failed'] += 1
                            stats['failed_games'].append({'game_id': game_id, 'date': date_str, 'reason': 'No data returned'})
                            print(f"      ❌ No data returned")
                    
                    except Exception as e:
                        stats['games_failed'] += 1
                        stats['failed_games'].append({'game_id': game_id, 'date': date_str, 'reason': str(e)})
                        print(f"      ❌ Error: {e}")
                else:
                    print(f"      ⏭️  Skipped (status: {status})")
                
                # Be respectful to the API
                if delay_seconds > 0:
                    time.sleep(delay_seconds)
        else:
            print(f"   No games found")
        
        # Move to next day
        current_date += timedelta(days=1)
        
        # Progress update every 10 days
        if stats['total_days'] % 10 == 0:
            print(f"\n📊 Progress Update (Day {stats['total_days']}):")
            print(f"   Days with games: {stats['days_with_games']}")
            print(f"   Games extracted: {stats['games_extracted']}/{stats['total_games_found']}")
            print(f"   JSON files saved: {stats['json_files_saved']}")
    
    # Final statistics
    stats['extraction_end_time'] = datetime.now()
    stats['total_duration'] = stats['extraction_end_time'] - stats['extraction_start_time']
    
    print(f"\n🎉 Season extraction completed!")
    print(f"📊 Final Statistics:")
    print(f"   Total days processed: {stats['total_days']}")
    print(f"   Days with games: {stats['days_with_games']}")
    print(f"   Games found: {stats['total_games_found']}")
    print(f"   Games extracted: {stats['games_extracted']}")
    print(f"   Games failed: {stats['games_failed']}")
    print(f"   JSON files saved: {stats['json_files_saved']}")
    print(f"   Total duration: {stats['total_duration']}")
    
    if stats['failed_games']:
        print(f"\n❌ Failed games:")
        for failed in stats['failed_games'][:10]:  # Show first 10 failures
            print(f"   Game {failed['game_id']} on {failed['date']}: {failed['reason']}")
        if len(stats['failed_games']) > 10:
            print(f"   ... and {len(stats['failed_games']) - 10} more")
    
    return stats

def extract_data(game_id=None, save_json=True):
    client = MLBClient()
    
    # Get a current game ID if none provided
    if game_id is None:
        current_games = get_current_games()
        if current_games:
            game_id = current_games[0]
            print(f"Using current game ID: {game_id}")
        else:
            # Fallback to a known working game ID
            game_id = "746790"  # Example from 2024 season
            print(f"Using fallback game ID: {game_id}")
    
    try:
        boxscore_data = client.fetch_boxscore(game_id)
        game_data = client.fetch_game_data(game_id)
        
        # Save to JSON files if requested
        if save_json and boxscore_data and game_data:
            print("Saving raw API data to JSON files...")
            saved_files = save_raw_api_data(boxscore_data, game_data, game_id)
            print(f"Saved {len(saved_files)} JSON files")
            
            # Also save a combined file
            combined_data = {
                "game_id": game_id,
                "extraction_timestamp": datetime.now().isoformat(),
                "boxscore": boxscore_data,
                "game_data": game_data
            }
            save_to_json(combined_data, f"combined_data_{game_id}")
        
        return boxscore_data, game_data
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print("This might be because the game ID doesn't exist or the game hasn't occurred yet.")
        return None, None

if __name__ == "__main__":
    # Test the extract function when run directly
    print("Extracting MLB data...")
    try:
        boxscore, game = extract_data(save_json=True)
        if boxscore and game:
            print("Data extraction successful!")
            print(f"Boxscore keys: {list(boxscore.keys()) if isinstance(boxscore, dict) else 'Not a dict'}")
            print(f"Game data keys: {list(game.keys()) if isinstance(game, dict) else 'Not a dict'}")
        else:
            print("No data extracted - check game ID or API endpoints")
    except Exception as e:
        print(f"Error during extraction: {e}")