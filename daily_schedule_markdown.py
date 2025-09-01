#!/usr/bin/env python3
"""
Daily MLB Schedule Markdown Generator

Fetches today's MLB schedule and formats it as a clean Markdown document.
Shows game times, matchups, and status information.
"""

import sys
import os
import argparse
from datetime import datetime, date
import requests
import json

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from api.mlb_client import MLBClient

class MLBScheduleMarkdown:
    def __init__(self):
        self.mlb_client = MLBClient()
        
    def get_daily_schedule(self, target_date=None, save_json=True):
        """Get MLB schedule for a specific date."""
        if target_date is None:
            target_date = date.today()
        
        # Format date for MLB API (YYYY-MM-DD)
        date_str = target_date.strftime('%Y-%m-%d')
        
        try:
            # Use MLB Stats API for schedule
            url = f"https://statsapi.mlb.com/api/v1/schedule"
            params = {
                'date': date_str,
                'sportId': 1,  # MLB
                'hydrate': 'team,linescore,flags,liveLookin,review,broadcasts(all),decisions,person,probablePitcher,stats,homeRuns,previousPlay,game(content(media(epg)),color,contentDescriptors,highlights)'
            }
            
            print(f"🔍 Fetching MLB schedule for {date_str}...")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Save JSON response to file if requested
            if save_json:
                json_filename = f"data/schedule_response_{date_str.replace('-', '')}.json"
                os.makedirs(os.path.dirname(json_filename), exist_ok=True)
                
                try:
                    with open(json_filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"💾 Saved API response to {json_filename}")
                except Exception as e:
                    print(f"⚠️  Warning: Could not save JSON file: {e}")
            
            if 'dates' not in data or not data['dates']:
                return []
            
            games = []
            for date_info in data['dates']:
                if 'games' in date_info:
                    games.extend(date_info['games'])
            
            print(f"✅ Found {len(games)} games for {date_str}")
            return games
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching schedule: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return []
    
    def format_game_time(self, game_data):
        """Format game time in a readable format."""
        try:
            if 'gameDate' in game_data:
                game_datetime = datetime.fromisoformat(game_data['gameDate'].replace('Z', '+00:00'))
                # Convert to local time (assuming Eastern for MLB)
                local_time = game_datetime.strftime('%I:%M %p ET')
                return local_time
            return "TBD"
        except:
            return "TBD"
    
    def get_game_status(self, game_data):
        """Get formatted game status."""
        try:
            status = game_data.get('status', {})
            detailed_state = status.get('detailedState', 'Unknown')
            
            # Map common statuses to cleaner display
            status_map = {
                'Scheduled': 'Scheduled',
                'Pre-Game': 'Pre-Game',
                'Warmup': 'Warmup',
                'In Progress': 'Live',
                'Game Over': 'Final',
                'Final': 'Final',
                'Postponed': 'Postponed',
                'Cancelled': 'Cancelled',
                'Suspended': 'Suspended'
            }
            
            return status_map.get(detailed_state, detailed_state)
        except:
            return "Unknown"
    
    def get_score_info(self, game_data):
        """Get score information if available."""
        try:
            if 'linescore' in game_data:
                linescore = game_data['linescore']
                if 'teams' in linescore:
                    away_score = linescore['teams']['away'].get('runs', 0)
                    home_score = linescore['teams']['home'].get('runs', 0)
                    return f"{away_score}-{home_score}"
            return None
        except:
            return None
    
    def get_probable_pitchers(self, game_data):
        """Get probable starting pitchers."""
        try:
            pitchers = {}
            if 'teams' in game_data:
                # Away pitcher
                away_team = game_data['teams'].get('away', {})
                if 'probablePitcher' in away_team and away_team['probablePitcher']:
                    pitcher = away_team['probablePitcher']
                    pitchers['away'] = pitcher.get('fullName', 'TBD')
                
                # Home pitcher
                home_team = game_data['teams'].get('home', {})
                if 'probablePitcher' in home_team and home_team['probablePitcher']:
                    pitcher = home_team['probablePitcher']
                    pitchers['home'] = pitcher.get('fullName', 'TBD')
            
            return pitchers
        except:
            return {}
    
    def generate_markdown(self, target_date=None, save_json=True):
        """Generate complete MLB schedule in Markdown format."""
        if target_date is None:
            target_date = date.today()
        
        games = self.get_daily_schedule(target_date, save_json=save_json)
        
        if not games:
            return self.generate_no_games_markdown(target_date)
        
        # Sort games by game time
        games.sort(key=lambda g: g.get('gameDate', ''))
        
        markdown_lines = []
        
        # Header
        date_formatted = target_date.strftime('%B %d, %Y')
        weekday = target_date.strftime('%A')
        
        markdown_lines.extend([
            f"# MLB Schedule - {weekday}, {date_formatted}",
            "",
            f"*Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*",
            "",
            f"## Games Today ({len(games)} games)",
            ""
        ])
        
        # Group games by status
        scheduled_games = []
        live_games = []
        completed_games = []
        
        for game in games:
            status = self.get_game_status(game)
            if status in ['Live', 'In Progress']:
                live_games.append(game)
            elif status in ['Final', 'Game Over']:
                completed_games.append(game)
            else:
                scheduled_games.append(game)
        
        # Live Games Section
        if live_games:
            markdown_lines.extend([
                "### 🔴 Live Games",
                ""
            ])
            
            for game in live_games:
                markdown_lines.extend(self.format_game_markdown(game))
            
            markdown_lines.append("")
        
        # Completed Games Section
        if completed_games:
            markdown_lines.extend([
                "### ✅ Completed Games",
                ""
            ])
            
            for game in completed_games:
                markdown_lines.extend(self.format_game_markdown(game))
            
            markdown_lines.append("")
        
        # Scheduled Games Section
        if scheduled_games:
            markdown_lines.extend([
                "### ⏰ Scheduled Games",
                ""
            ])
            
            for game in scheduled_games:
                markdown_lines.extend(self.format_game_markdown(game))
        
        # Summary section
        markdown_lines.extend([
            "",
            "---",
            "",
            "## Summary",
            "",
            f"- **Total Games**: {len(games)}",
            f"- **Live Games**: {len(live_games)}",
            f"- **Completed Games**: {len(completed_games)}",
            f"- **Scheduled Games**: {len(scheduled_games)}",
            "",
            "*Data provided by MLB Stats API*"
        ])
        
        return "\n".join(markdown_lines)
    
    def format_game_markdown(self, game):
        """Format a single game as Markdown."""
        lines = []
        
        try:
            # Get team information
            away_team = game['teams']['away']['team']
            home_team = game['teams']['home']['team']
            
            away_name = away_team.get('name', 'Unknown')
            home_name = home_team.get('name', 'Unknown')
            
            # Get game details
            game_time = self.format_game_time(game)
            status = self.get_game_status(game)
            score_info = self.get_score_info(game)
            probable_pitchers = self.get_probable_pitchers(game)
            
            # Format matchup
            if score_info:
                matchup = f"**{away_name}** @ **{home_name}** - {score_info} ({status})"
            else:
                matchup = f"**{away_name}** @ **{home_name}** - {game_time} ({status})"
            
            lines.append(f"#### {matchup}")
            
            # Add probable pitchers if available
            if probable_pitchers:
                lines.append("")
                if 'away' in probable_pitchers and 'home' in probable_pitchers:
                    lines.append(f"**Probable Pitchers**: {probable_pitchers['away']} vs {probable_pitchers['home']}")
                elif 'away' in probable_pitchers:
                    lines.append(f"**Away Pitcher**: {probable_pitchers['away']}")
                elif 'home' in probable_pitchers:
                    lines.append(f"**Home Pitcher**: {probable_pitchers['home']}")
            
            # Add venue if available
            if 'venue' in game and game['venue']:
                venue_name = game['venue'].get('name', '')
                if venue_name:
                    lines.append(f"**Venue**: {venue_name}")
            
            lines.append("")
            
        except Exception as e:
            lines.extend([
                f"#### Game (Error formatting)",
                f"*Error: {e}*",
                ""
            ])
        
        return lines
    
    def generate_no_games_markdown(self, target_date):
        """Generate Markdown for days with no games."""
        date_formatted = target_date.strftime('%B %d, %Y')
        weekday = target_date.strftime('%A')
        
        return f"""# MLB Schedule - {weekday}, {date_formatted}

*Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*

## No Games Scheduled

There are no MLB games scheduled for today.

---

*Data provided by MLB Stats API*"""

def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Generate MLB schedule in Markdown format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate today's schedule (saves JSON response automatically)
  python daily_schedule_markdown.py

  # Generate schedule for specific date with JSON saved
  python daily_schedule_markdown.py --date 2025-09-01

  # Save to file and JSON response
  python daily_schedule_markdown.py --output schedule.md

  # Generate without saving JSON response
  python daily_schedule_markdown.py --no-save-json

  # Generate for specific date and save both markdown and JSON
  python daily_schedule_markdown.py --date 2025-09-01 --output schedule_090125.md
        """
    )
    
    parser.add_argument(
        '--date', 
        help='Date for schedule (YYYY-MM-DD format, default: today)'
    )
    
    parser.add_argument(
        '--output', 
        help='Output file path (default: print to console)'
    )
    
    parser.add_argument(
        '--no-save-json',
        action='store_true',
        help='Do not save API response to JSON file'
    )
    
    args = parser.parse_args()
    
    # Parse date
    target_date = date.today()
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print(f"❌ Error: Invalid date format '{args.date}'. Use YYYY-MM-DD")
            sys.exit(1)
    
    # Generate markdown
    generator = MLBScheduleMarkdown()
    markdown_content = generator.generate_markdown(target_date, save_json=not args.no_save_json)
    
    # Output
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"✅ Schedule saved to {args.output}")
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            sys.exit(1)
    else:
        print("\n" + markdown_content)

if __name__ == "__main__":
    main()
