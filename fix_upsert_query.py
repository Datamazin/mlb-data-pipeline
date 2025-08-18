# Quick fix script to update the UPSERT query in _insert_game
import re

# Read the current file
with open(r'src\database\json_to_sql_loader.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the specific UPDATE statement in _insert_game method (first occurrence)
# We'll look for the pattern in the first _insert_game method specifically

# Split by method definitions to isolate the first _insert_game method
methods = content.split('def _insert_game(')

if len(methods) >= 2:
    # Get the first _insert_game method content
    first_method = methods[1]
    
    # Find the next method start to know where this method ends
    next_def_pos = first_method.find('\n    def ')
    if next_def_pos == -1:
        # If no next method found, look for class end or file end
        method_content = first_method
    else:
        method_content = first_method[:next_def_pos]
    
    # Replace the UPDATE statement in this method
    old_update = """        UPDATE games SET 
            game_date = :game_date,
            home_score = :home_score,"""
    
    new_update = """        UPDATE games SET 
            game_date = :game_date,
            home_team_id = :home_team_id,
            away_team_id = :away_team_id,
            home_score = :home_score,"""
    
    if old_update in method_content:
        method_content = method_content.replace(old_update, new_update)
        print("✅ Found and updated the UPSERT query")
        
        # Reconstruct the file
        methods[1] = method_content
        new_content = 'def _insert_game('.join(methods)
        
        # Write back to file
        with open(r'src\database\json_to_sql_loader.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ File updated successfully")
    else:
        print("❌ UPDATE pattern not found in method")
        print("Method content preview:", method_content[:500])
else:
    print("❌ Could not find _insert_game method")
