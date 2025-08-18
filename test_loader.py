from src.database.json_to_sql_loader import JSONToSQLLoader
from src.database.connection import DatabaseConnection

try:
    db = DatabaseConnection()
    db.connect()
    loader = JSONToSQLLoader(db)
    
    print('🔍 Loader status:')
    print(f'  _fetch_game_metadata_if_needed: {hasattr(loader, "_fetch_game_metadata_if_needed")}')
    print(f'  _extract_game_id_from_filename: {hasattr(loader, "_extract_game_id_from_filename")}')
    
    game_id = loader._extract_game_id_from_filename('boxscore_raw_776762.json')
    print(f'  Filename extraction: {game_id}')
    
    db.disconnect()
    print('✅ Methods working')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
