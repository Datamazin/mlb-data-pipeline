#!/usr/bin/env python3
"""
Debug why boxscore data isn't populating after 8/18/2025
"""

import sys
import os
sys.path.append('src')

from database.connection import DatabaseConnection

def main():
    db = DatabaseConnection()
    try:
        db.connect()
        
        print('🔍 INVESTIGATING GAMES vs BOXSCORE MISMATCH AFTER 8/18/2025')
        print('=' * 70)
        
        # Check games table
        games_result = db.fetch_results('''
            SELECT 
                COUNT(*) as game_count,
                MIN(game_date) as min_date,
                MAX(game_date) as max_date
            FROM games 
            WHERE game_date > '2025-08-18'
        ''')
        
        if games_result:
            print(f'📊 GAMES TABLE after 8/18/2025:')
            print(f'   Count: {games_result[0][0]:,}')
            print(f'   Date range: {games_result[0][1]} to {games_result[0][2]}')
        
        # Check boxscore table
        boxscore_result = db.fetch_results('''
            SELECT 
                COUNT(*) as boxscore_count
            FROM boxscore b
            INNER JOIN games g ON b.game_id = g.game_id
            WHERE g.game_date > '2025-08-18'
        ''')
        
        if boxscore_result:
            print(f'\n📊 BOXSCORE TABLE after 8/18/2025:')
            print(f'   Count: {boxscore_result[0][0]:,}')
        
        # Check specific games that have no boxscore data
        orphan_games = db.fetch_results('''
            SELECT TOP 5
                g.game_id,
                g.game_date,
                g.home_team_id,
                g.away_team_id
            FROM games g
            LEFT JOIN boxscore b ON g.game_id = b.game_id
            WHERE g.game_date > '2025-08-18'
            AND b.game_id IS NULL
            ORDER BY g.game_date DESC
        ''')
        
        print(f'\n🔍 GAMES WITHOUT BOXSCORE DATA (sample):')
        if orphan_games:
            print(f'   Found games without boxscore data:')
            for row in orphan_games:
                print(f'     Game {row[0]} on {row[1]} (Home: {row[2]}, Away: {row[3]})')
        else:
            print('   ✅ All games have boxscore data')
        
        # Check if ALL boxscore data is missing after 8/18
        all_boxscore_count = db.fetch_results('''
            SELECT COUNT(*) as count
            FROM boxscore
        ''')[0][0]
        
        print(f'\n📊 TOTAL BOXSCORE RECORDS IN DATABASE: {all_boxscore_count:,}')
        
        # Check date range of ALL boxscore data
        boxscore_dates = db.fetch_results('''
            SELECT 
                MIN(g.game_date) as min_date,
                MAX(g.game_date) as max_date
            FROM boxscore b
            INNER JOIN games g ON b.game_id = g.game_id
        ''')
        
        if boxscore_dates and boxscore_dates[0][0]:
            print(f'📅 BOXSCORE DATE RANGE: {boxscore_dates[0][0]} to {boxscore_dates[0][1]}')
            
            # This is the key check - if max boxscore date is before 8/19, that's our problem
            if str(boxscore_dates[0][1]) <= '2025-08-18':
                print('🚨 PROBLEM IDENTIFIED: Boxscore data stops at 8/18 or earlier!')
                print('   📋 This suggests the JSON loader is not processing boxscore data for recent games')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        
    finally:
        if hasattr(db, 'disconnect'):
            db.disconnect()

if __name__ == "__main__":
    main()
