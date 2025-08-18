import requests


class MLBClient:
    def __init__(self, base_url="https://statsapi.mlb.com/api/v1"):
        self.base_url = base_url

    def fetch_boxscore(self, game_id):
        # MLB Stats API endpoint for boxscore
        response = requests.get(f"{self.base_url}/game/{game_id}/boxscore")
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def fetch_game_data(self, game_id):
        # MLB Stats API endpoint for linescore (contains game summary data)
        response = requests.get(f"{self.base_url}/game/{game_id}/linescore")
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
            
    def fetch_game_feed(self, game_id):
        # MLB Stats API endpoint for complete game feed
        response = requests.get(f"{self.base_url}/game/{game_id}/feed/live")
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    def fetch_schedule(self, start_date, end_date, sport_id=1):
        """
        Fetch MLB schedule for a date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format  
            sport_id: Sport ID (1 for MLB)
        """
        url = f"{self.base_url}/schedule"
        params = {
            'startDate': start_date,
            'endDate': end_date,
            'sportId': sport_id,
            'hydrate': 'team,linescore'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    def fetch_game_metadata(self, game_id):
        """
        Fetch game metadata from the schedule API for a specific game.
        This provides gameType, seriesDescription, and other metadata missing from linescore.
        
        Args:
            game_id: MLB game ID (gamePk)
            
        Returns:
            Dict with game metadata or None if not found
        """
        try:
            url = f"{self.base_url}/schedule"
            params = {
                'gamePk': game_id,
                'hydrate': 'game'
            }
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if 'dates' in data and data['dates']:
                    for date_entry in data['dates']:
                        if 'games' in date_entry:
                            for game in date_entry['games']:
                                if game.get('gamePk') == game_id:
                                    return {
                                        'game_type': game.get('gameType'),
                                        'series_description': game.get('seriesDescription'),
                                        'official_date': game.get('officialDate'),
                                        'season': game.get('season'),
                                        'game_number': game.get('gameNumber'),
                                        'double_header': game.get('doubleHeader'),
                                        'series_game_number': game.get('seriesGameNumber'),
                                        'games_in_series': game.get('gamesInSeries'),
                                        'day_night': game.get('dayNight'),
                                        'scheduled_innings': game.get('scheduledInnings', 9)
                                    }
            return None
            
        except Exception as e:
            print(f"❌ Error fetching game metadata for game {game_id}: {e}")
            return None