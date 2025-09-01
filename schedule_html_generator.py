#!/usr/bin/env python3
"""
MLB Schedule HTML Generator

Creates a beautiful, responsive HTML page displaying the MLB schedule.
Uses modern CSS and includes interactive features.
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

class MLBScheduleHTML:
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
                    return {'away': away_score, 'home': home_score}
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
    
    def get_team_colors(self, team_name):
        """Get team colors for styling."""
        # Basic color mapping for MLB teams
        colors = {
            'New York Yankees': {'primary': '#0C2340', 'secondary': '#C4CED4'},
            'Boston Red Sox': {'primary': '#BD3039', 'secondary': '#0C2340'},
            'Tampa Bay Rays': {'primary': '#092C5C', 'secondary': '#8FBCE6'},
            'Toronto Blue Jays': {'primary': '#134A8E', 'secondary': '#1D2D5C'},
            'Baltimore Orioles': {'primary': '#DF4601', 'secondary': '#000000'},
            'Houston Astros': {'primary': '#002D62', 'secondary': '#EB6E1F'},
            'Los Angeles Angels': {'primary': '#BA0021', 'secondary': '#003263'},
            'Seattle Mariners': {'primary': '#0C2C56', 'secondary': '#005C5C'},
            'Texas Rangers': {'primary': '#003278', 'secondary': '#C0111F'},
            'Oakland Athletics': {'primary': '#003831', 'secondary': '#EFB21E'},
            'Minnesota Twins': {'primary': '#002B5C', 'secondary': '#D31145'},
            'Chicago White Sox': {'primary': '#27251F', 'secondary': '#C4CED4'},
            'Kansas City Royals': {'primary': '#004687', 'secondary': '#BD9B60'},
            'Detroit Tigers': {'primary': '#0C2340', 'secondary': '#FA4616'},
            'Cleveland Guardians': {'primary': '#E31937', 'secondary': '#0C2340'},
            'Atlanta Braves': {'primary': '#CE1141', 'secondary': '#13274F'},
            'New York Mets': {'primary': '#002D72', 'secondary': '#FF5910'},
            'Philadelphia Phillies': {'primary': '#E81828', 'secondary': '#002D72'},
            'Miami Marlins': {'primary': '#00A3E0', 'secondary': '#EF3340'},
            'Washington Nationals': {'primary': '#AB0003', 'secondary': '#14225A'},
            'Milwaukee Brewers': {'primary': '#0A2351', 'secondary': '#B6922E'},
            'Chicago Cubs': {'primary': '#0E3386', 'secondary': '#CC3433'},
            'St. Louis Cardinals': {'primary': '#C41E3A', 'secondary': '#0C2340'},
            'Pittsburgh Pirates': {'primary': '#FDB827', 'secondary': '#27251F'},
            'Cincinnati Reds': {'primary': '#C6011F', 'secondary': '#000000'},
            'Los Angeles Dodgers': {'primary': '#005A9C', 'secondary': '#EF3E42'},
            'San Diego Padres': {'primary': '#2F241D', 'secondary': '#FFC425'},
            'San Francisco Giants': {'primary': '#FD5A1E', 'secondary': '#27251F'},
            'Colorado Rockies': {'primary': '#33006F', 'secondary': '#C4CED4'},
            'Arizona Diamondbacks': {'primary': '#A71930', 'secondary': '#E3D4A7'},
        }
        return colors.get(team_name, {'primary': '#002244', 'secondary': '#69BE28'})
    
    def generate_html(self, target_date=None, save_json=True):
        """Generate complete MLB schedule in HTML format."""
        if target_date is None:
            target_date = date.today()
        
        games = self.get_daily_schedule(target_date, save_json=save_json)
        
        if not games:
            return self.generate_no_games_html(target_date)
        
        # Sort games by game time
        games.sort(key=lambda g: g.get('gameDate', ''))
        
        # Header
        date_formatted = target_date.strftime('%B %d, %Y')
        weekday = target_date.strftime('%A')
        
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
        
        # Generate HTML
        html_content = self.generate_html_template(
            date_formatted, weekday, target_date,
            live_games, completed_games, scheduled_games
        )
        
        return html_content
    
    def generate_html_template(self, date_formatted, weekday, target_date, live_games, completed_games, scheduled_games):
        """Generate the complete HTML template."""
        total_games = len(live_games) + len(completed_games) + len(scheduled_games)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MLB Schedule - {weekday}, {date_formatted}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #333;
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }}
        
        .header h1 {{
            color: #1e3c72;
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        
        .header .date {{
            color: #666;
            font-size: 1.3em;
            font-weight: 300;
        }}
        
        .stats-bar {{
            background: rgba(255, 255, 255, 0.9);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .stat {{
            text-align: center;
            margin: 5px;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: 700;
            color: #1e3c72;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section-title {{
            background: rgba(255, 255, 255, 0.9);
            padding: 15px 25px;
            border-radius: 10px 10px 0 0;
            font-size: 1.4em;
            font-weight: 600;
            color: #1e3c72;
            display: flex;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}
        
        .section-title .icon {{
            margin-right: 10px;
            font-size: 1.2em;
        }}
        
        .games-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 0;
        }}
        
        .game-card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 0 0 15px 15px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            border-left: 5px solid #1e3c72;
        }}
        
        .game-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
        }}
        
        .game-card.live {{
            border-left-color: #e74c3c;
            animation: pulse 2s infinite;
        }}
        
        .game-card.completed {{
            border-left-color: #27ae60;
        }}
        
        @keyframes pulse {{
            0% {{ box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1); }}
            50% {{ box-shadow: 0 8px 25px rgba(231, 76, 60, 0.3); }}
            100% {{ box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1); }}
        }}
        
        .matchup {{
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 15px;
            color: #2c3e50;
        }}
        
        .team {{
            display: inline-block;
            padding: 3px 8px;
            margin: 2px;
            border-radius: 5px;
            background: rgba(30, 60, 114, 0.1);
        }}
        
        .game-details {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 15px;
        }}
        
        .detail-item {{
            background: rgba(52, 73, 94, 0.05);
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .detail-label {{
            font-size: 0.8em;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }}
        
        .detail-value {{
            font-weight: 600;
            color: #2c3e50;
        }}
        
        .status {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .status.scheduled {{ background: #3498db; color: white; }}
        .status.live {{ background: #e74c3c; color: white; }}
        .status.final {{ background: #27ae60; color: white; }}
        .status.postponed {{ background: #f39c12; color: white; }}
        
        .score {{
            font-size: 1.5em;
            font-weight: 700;
            color: #1e3c72;
            text-align: center;
            margin: 10px 0;
        }}
        
        .pitchers {{
            background: rgba(52, 152, 219, 0.1);
            padding: 12px;
            border-radius: 8px;
            margin-top: 10px;
            font-size: 0.95em;
        }}
        
        .venue {{
            color: #7f8c8d;
            font-size: 0.9em;
            font-style: italic;
            margin-top: 10px;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9em;
        }}
        
        .no-games {{
            background: rgba(255, 255, 255, 0.95);
            padding: 60px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .no-games h2 {{
            color: #1e3c72;
            font-size: 2em;
            margin-bottom: 20px;
        }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 15px; }}
            .header h1 {{ font-size: 2em; }}
            .stats-bar {{ flex-direction: column; }}
            .games-grid {{ grid-template-columns: 1fr; }}
            .game-details {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏟️ MLB Schedule</h1>
            <div class="date">{weekday}, {date_formatted}</div>
        </div>
        
        <div class="stats-bar">
            <div class="stat">
                <div class="stat-number">{total_games}</div>
                <div class="stat-label">Total Games</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len(live_games)}</div>
                <div class="stat-label">Live</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len(completed_games)}</div>
                <div class="stat-label">Completed</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len(scheduled_games)}</div>
                <div class="stat-label">Scheduled</div>
            </div>
        </div>
"""
        
        # Live Games Section
        if live_games:
            html += """
        <div class="section">
            <div class="section-title">
                <span class="icon">🔴</span> Live Games
            </div>
            <div class="games-grid">
"""
            for game in live_games:
                html += self.format_game_html(game, "live")
            html += """
            </div>
        </div>
"""
        
        # Completed Games Section
        if completed_games:
            html += """
        <div class="section">
            <div class="section-title">
                <span class="icon">✅</span> Completed Games
            </div>
            <div class="games-grid">
"""
            for game in completed_games:
                html += self.format_game_html(game, "completed")
            html += """
            </div>
        </div>
"""
        
        # Scheduled Games Section
        if scheduled_games:
            html += """
        <div class="section">
            <div class="section-title">
                <span class="icon">⏰</span> Scheduled Games
            </div>
            <div class="games-grid">
"""
            for game in scheduled_games:
                html += self.format_game_html(game, "scheduled")
            html += """
            </div>
        </div>
"""
        
        # Footer
        html += f"""
    </div>
    
    <div class="footer">
        <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | Data provided by MLB Stats API</p>
    </div>
    
    <script>
        // Auto-refresh every 5 minutes for live games
        if ({len(live_games)} > 0) {{
            setTimeout(() => {{
                location.reload();
            }}, 300000); // 5 minutes
        }}
        
        // Add smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({{
                    behavior: 'smooth'
                }});
            }});
        }});
    </script>
</body>
</html>"""
        
        return html
    
    def format_game_html(self, game, section_type):
        """Format a single game as HTML."""
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
            
            # Format venue
            venue_name = ""
            if 'venue' in game and game['venue']:
                venue_name = game['venue'].get('name', '')
            
            # Build HTML
            html = f'''
                <div class="game-card {section_type}">
                    <div class="matchup">
                        <span class="team">{away_name}</span> @ <span class="team">{home_name}</span>
                    </div>
                    
                    <div style="text-align: center; margin: 15px 0;">
                        <span class="status {status.lower()}">{status}</span>
                    </div>
'''
            
            # Add score or time
            if score_info:
                html += f'''
                    <div class="score">
                        {score_info['away']} - {score_info['home']}
                    </div>
'''
            else:
                html += f'''
                    <div class="score" style="font-size: 1.2em; font-weight: 400;">
                        {game_time}
                    </div>
'''
            
            # Add probable pitchers
            if probable_pitchers and ('away' in probable_pitchers or 'home' in probable_pitchers):
                html += '''
                    <div class="pitchers">
                        <div class="detail-label">Probable Pitchers</div>
'''
                if 'away' in probable_pitchers and 'home' in probable_pitchers:
                    html += f'                        <div class="detail-value">{probable_pitchers["away"]} vs {probable_pitchers["home"]}</div>\n'
                elif 'away' in probable_pitchers:
                    html += f'                        <div class="detail-value">Away: {probable_pitchers["away"]}</div>\n'
                elif 'home' in probable_pitchers:
                    html += f'                        <div class="detail-value">Home: {probable_pitchers["home"]}</div>\n'
                
                html += '''
                    </div>
'''
            
            # Add venue
            if venue_name:
                html += f'''
                    <div class="venue">
                        📍 {venue_name}
                    </div>
'''
            
            html += '''
                </div>
'''
            
            return html
            
        except Exception as e:
            return f'''
                <div class="game-card">
                    <div class="matchup">Game (Error formatting)</div>
                    <div style="color: #e74c3c; font-style: italic;">Error: {e}</div>
                </div>
'''
    
    def generate_no_games_html(self, target_date):
        """Generate HTML for days with no games."""
        date_formatted = target_date.strftime('%B %d, %Y')
        weekday = target_date.strftime('%A')
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MLB Schedule - {weekday}, {date_formatted}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .container {{
            max-width: 600px;
            text-align: center;
        }}
        
        .no-games {{
            background: rgba(255, 255, 255, 0.95);
            padding: 60px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .no-games h1 {{
            color: #1e3c72;
            font-size: 2.5em;
            margin-bottom: 20px;
        }}
        
        .no-games h2 {{
            color: #666;
            font-size: 1.5em;
            font-weight: 300;
            margin-bottom: 30px;
        }}
        
        .no-games p {{
            color: #888;
            font-size: 1.1em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="no-games">
            <h1>🏟️ MLB Schedule</h1>
            <h2>{weekday}, {date_formatted}</h2>
            <p>No MLB games scheduled for today.</p>
            <p style="margin-top: 30px; font-size: 0.9em; color: #aaa;">
                Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            </p>
        </div>
    </div>
</body>
</html>"""

def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Generate MLB schedule in HTML format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate today's schedule (saves JSON response automatically)
  python schedule_html_generator.py

  # Generate schedule for specific date with JSON saved
  python schedule_html_generator.py --date 2025-09-01

  # Save to custom HTML file
  python schedule_html_generator.py --output schedule.html

  # Generate without saving JSON response
  python schedule_html_generator.py --no-save-json

  # Generate for specific date and save both HTML and JSON
  python schedule_html_generator.py --date 2025-09-01 --output schedule_090125.html
        """
    )
    
    parser.add_argument(
        '--date', 
        help='Date for schedule (YYYY-MM-DD format, default: today)'
    )
    
    parser.add_argument(
        '--output', 
        help='Output HTML file path (default: auto-generated filename)'
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
    
    # Generate HTML
    generator = MLBScheduleHTML()
    html_content = generator.generate_html(target_date, save_json=not args.no_save_json)
    
    # Determine output filename
    if args.output:
        output_file = args.output
    else:
        date_str = target_date.strftime('%Y%m%d')
        output_file = f"docs/MLB_Schedule_{date_str}.html"
    
    # Save HTML file
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ HTML schedule saved to {output_file}")
        
        # Also suggest opening in browser
        abs_path = os.path.abspath(output_file)
        print(f"🌐 Open in browser: file:///{abs_path.replace(os.sep, '/')}")
        
    except Exception as e:
        print(f"❌ Error saving HTML file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
