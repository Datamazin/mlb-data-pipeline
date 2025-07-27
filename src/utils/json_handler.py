import json
import os
from datetime import datetime
from pathlib import Path

def save_to_json(data, filename, directory="data/json"):
    """
    Save data to a JSON file in the specified directory.
    
    Args:
        data: The data to save (dict or list)
        filename: Name of the file (without .json extension)
        directory: Directory to save the file in
    """
    # Create directory if it doesn't exist
    Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Add timestamp to filename if not already present
    if not any(char.isdigit() for char in filename[-20:]):  # Check if timestamp already in filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{filename}_{timestamp}.json"
    else:
        full_filename = f"{filename}.json"
    
    file_path = Path(directory) / full_filename
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Data saved to: {file_path}")
        return str(file_path)
    except Exception as e:
        print(f"❌ Error saving JSON file: {e}")
        return None

def load_from_json(file_path):
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
    
    Returns:
        The loaded data or None if error
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Data loaded from: {file_path}")
        return data
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        return None

def save_raw_api_data(boxscore_data, game_data, game_id, directory="data/json"):
    """
    Save raw API data to JSON files.
    
    Args:
        boxscore_data: Raw boxscore data from API
        game_data: Raw game data from API  
        game_id: The game ID for naming
        directory: Directory to save files in
    """
    saved_files = []
    
    if boxscore_data:
        file_path = save_to_json(boxscore_data, f"boxscore_raw_{game_id}", directory)
        if file_path:
            saved_files.append(file_path)
    
    if game_data:
        file_path = save_to_json(game_data, f"game_raw_{game_id}", directory)
        if file_path:
            saved_files.append(file_path)
    
    return saved_files
