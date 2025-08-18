#!/usr/bin/env python3

# Fix the UPSERT query in the first _insert_game method only
import re

def fix_first_insert_game_method():
    # Read file
    with open('src/database/json_to_sql_loader.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the first _insert_game method (the main one we want to fix)
    pattern = r'(def _insert_game\(self, game_id, game_data, home_team, away_team.*?)(UPDATE games SET\s+game_date = :game_date,\s+home_score = :home_score,)(.*?WHERE game_id = :game_id)'
    
    def replacement(match):
        prefix = match.group(1)
        old_update_start = match.group(2)
        suffix = match.group(3)
        
        new_update_start = """UPDATE games SET 
            game_date = :game_date,
            home_team_id = :home_team_id,
            away_team_id = :away_team_id,
            home_score = :home_score,"""
        
        return prefix + new_update_start + suffix
    
    # Apply the replacement only to the first match
    new_content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
    
    if new_content != content:
        with open('src/database/json_to_sql_loader.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Successfully updated the first _insert_game method")
        return True
    else:
        print("❌ No changes made - pattern not found")
        return False

if __name__ == "__main__":
    fix_first_insert_game_method()
