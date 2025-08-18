import json

# Test file
test_file = r'data\json\2025\08-August\boxscore_raw_776762.json'

with open(test_file, 'r') as f:
    data = json.load(f)

print('🔍 Boxscore structure analysis:')
print(f'  Top-level keys: {list(data.keys())}')

# Look for game ID in common locations
if 'gamePk' in data:
    print(f'  Found gamePk: {data["gamePk"]}')
if 'game_id' in data:
    print(f'  Found game_id: {data["game_id"]}')
    
# Check nested structures
for key, value in data.items():
    if isinstance(value, dict):
        if 'gamePk' in value:
            print(f'  Found gamePk in {key}: {value["gamePk"]}')

# Extract filename game ID
filename_id = test_file.split('_')[-1].replace('.json', '')
print(f'  Filename game ID: {filename_id}')

# Test the extraction method
from src.database.json_to_sql_loader import JSONToSQLLoader
from src.database.connection import DatabaseConnection

db = DatabaseConnection()
db.connect()
loader = JSONToSQLLoader(db)

extracted_id = loader._extract_game_id_from_data(data)
print(f'  Extracted ID: {extracted_id}')

db.disconnect()
