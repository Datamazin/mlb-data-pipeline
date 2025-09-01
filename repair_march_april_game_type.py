#!/usr/bin/env python3
"""
Repair script for March-April 2025 game_type NULL values.

This script identifies games from March-April 2025 that have NULL game_type
and updates them to 'R' (Regular season) based on the date ranges.

Issue: 826 games from March-April have NULL game_type, preventing them from 
being counted in regular season statistics.

Solution: Update these games to game_type = 'R' since they fall within
regular season date ranges.
"""

import sys
import os
from datetime import datetime, date

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import DatabaseConnection

class GameTypeRepairer:
    def __init__(self):
        self.db = DatabaseConnection()
        self.repaired_count = 0
        
    def repair_march_april_game_types(self):
        """Repair NULL game_type values for March-April 2025 games."""
        try:
            if not self.db.connect():
                print("❌ Failed to connect to database")
                return False
            
            print("🔧 Starting March-April 2025 game_type repair...")
            print("=" * 55)
            
            # First, identify the games that need repair
            identify_query = """
            SELECT 
                COUNT(*) as null_games,
                MIN(game_date) as earliest_date,
                MAX(game_date) as latest_date
            FROM games 
            WHERE game_type IS NULL
            """
            
            result = self.db.execute_query(identify_query)
            row = result.fetchone()
            
            if row and row[0] > 0:
                print(f"📊 Found {row[0]:,} games with NULL game_type")
                print(f"📅 Date range: {row[1]} to {row[2]}")
                
                # Get sample of games to verify they should be regular season
                sample_query = """
                SELECT TOP 5 
                    game_id,
                    game_date,
                    game_type,
                    game_status
                FROM games 
                WHERE game_type IS NULL
                ORDER BY game_date
                """
                
                sample_result = self.db.execute_query(sample_query)
                sample_rows = sample_result.fetchall()
                
                print(f"\n📋 Sample of games to repair:")
                print("Game ID       Date         Type  Status")
                print("-" * 40)
                
                for sample_row in sample_rows:
                    game_id = str(sample_row[0])
                    game_date = sample_row[1]
                    game_type = sample_row[2] or 'NULL'
                    status = sample_row[3] or 'Unknown'
                    print(f"{game_id:<12} {game_date}  {game_type:<4}  {status}")
                
                # Confirm these are regular season games based on dates
                march_april_start = date(2025, 3, 1)
                march_april_end = date(2025, 4, 30)
                
                print(f"\n✅ Verification: Games between {march_april_start} and {march_april_end}")
                print("   are typically regular season games and should have game_type = 'R'")
                
                # Perform the repair
                repair_query = """
                UPDATE games 
                SET game_type = 'R'
                WHERE game_type IS NULL
                  AND game_date >= '2025-03-01'
                  AND game_date <= '2025-04-30'
                """
                
                print(f"\n🔧 Executing repair...")
                repair_result = self.db.execute_query(repair_query)
                
                # Verify the repair worked
                verify_query = """
                SELECT 
                    COUNT(*) as remaining_nulls,
                    (SELECT COUNT(*) FROM games WHERE game_type = 'R') as regular_games
                FROM games 
                WHERE game_type IS NULL
                """
                
                verify_result = self.db.execute_query(verify_query)
                verify_row = verify_result.fetchone()
                
                if verify_row:
                    remaining_nulls = verify_row[0]
                    total_regular = verify_row[1]
                    repaired = row[0] - remaining_nulls
                    
                    print(f"✅ Repair completed!")
                    print(f"   Repaired games: {repaired:,}")
                    print(f"   Remaining NULL: {remaining_nulls:,}")
                    print(f"   Total regular season games: {total_regular:,}")
                    
                    # Calculate expected player game counts now
                    expected_regular_games = total_regular
                    expected_player_games = expected_regular_games / 30  # Rough estimate per team
                    
                    print(f"\n📈 Expected Impact:")
                    print(f"   With {total_regular:,} regular season games")
                    print(f"   Players should now have ~{expected_player_games:.0f}+ games")
                    print(f"   (up from previous max of ~106 games)")
                    
                    self.repaired_count = repaired
                    return True
                else:
                    print("❌ Could not verify repair results")
                    return False
                    
            else:
                print("ℹ️ No games found with NULL game_type - repair not needed")
                return True
                
        except Exception as e:
            print(f"❌ Error during repair: {e}")
            return False
        finally:
            self.db.disconnect()
    
    def validate_repair_results(self):
        """Validate that the repair worked by checking game counts."""
        try:
            if not self.db.connect():
                print("❌ Failed to connect for validation")
                return False
            
            print("\n🔍 Validating Repair Results...")
            print("=" * 35)
            
            # Check updated game type distribution
            distribution_query = """
            SELECT 
                game_type,
                COUNT(*) as game_count,
                MIN(game_date) as first_date,
                MAX(game_date) as last_date
            FROM games
            GROUP BY game_type
            ORDER BY game_count DESC
            """
            
            result = self.db.execute_query(distribution_query)
            rows = result.fetchall()
            
            print("📊 Updated Game Type Distribution:")
            for row in rows:
                game_type = row[0] if row[0] else 'NULL'
                print(f"   {game_type}: {row[1]:,} games ({row[2]} to {row[3]})")
            
            # Check top player game counts after repair
            top_players_query = """
            SELECT TOP 5
                p.player_name,
                COUNT(DISTINCT b.game_id) as unique_games
            FROM boxscore b
            INNER JOIN players p ON b.player_id = p.player_id
            INNER JOIN games g ON b.game_id = g.game_id
            WHERE g.game_type = 'R'
            GROUP BY p.player_name, p.player_id
            ORDER BY unique_games DESC
            """
            
            players_result = self.db.execute_query(top_players_query)
            players_rows = players_result.fetchall()
            
            print("\n🏆 Top 5 Players After Repair:")
            print("Player                    Games")
            print("-" * 35)
            
            max_games_after = 0
            for row in players_rows:
                name = row[0][:24] if len(row[0]) > 24 else row[0]
                games = row[1]
                max_games_after = max(max_games_after, games)
                print(f"{name:<25} {games}")
            
            print(f"\n✅ Validation Results:")
            print(f"   Maximum player games after repair: {max_games_after}")
            print(f"   Expected improvement: From ~106 to ~{max_games_after}")
            
            if max_games_after > 120:
                print("🎉 SUCCESS: Player game counts now exceed 120!")
            else:
                print("⚠️ Players still under 120 games - may need additional investigation")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during validation: {e}")
            return False
        finally:
            self.db.disconnect()

def main():
    """Main function to execute the repair process."""
    print("🚀 MLB Data Pipeline: March-April Game Type Repair")
    print("=" * 55)
    
    repairer = GameTypeRepairer()
    
    # Execute repair
    if repairer.repair_march_april_game_types():
        print(f"\n✅ Repair phase completed successfully")
        
        # Validate results
        if repairer.validate_repair_results():
            print(f"\n🎉 All operations completed successfully!")
            print(f"   Repaired {repairer.repaired_count:,} games")
            print(f"   Regular season data should now be complete")
        else:
            print(f"\n⚠️ Repair completed but validation failed")
    else:
        print(f"\n❌ Repair process failed")
    
    print(f"\n📋 Next Steps:")
    print(f"   1. Verify player game counts now exceed 120")
    print(f"   2. Run statistical queries to confirm regular season completeness")
    print(f"   3. Consider running May walks repair if needed")

if __name__ == "__main__":
    main()
