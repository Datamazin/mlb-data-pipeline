def load_data(transformed_data):
    from database.connection import DatabaseConnection

    db_connection = DatabaseConnection()
    connection = db_connection.connect()

    try:
        # Load boxscore data
        for boxscore in transformed_data['boxscores']:
            query = """
            INSERT INTO boxscore (game_id, home_team, away_team)
            VALUES (%s, %s, %s)
            """
            cursor = connection.cursor()
            cursor.execute(query, (boxscore['game_id'], boxscore['home_team'], boxscore['away_team']))
        
        # Load game data
        for game in transformed_data['games']:
            query = """
            INSERT INTO game (game_id, date)
            VALUES (%s, %s)
            """
            cursor.execute(query, (game['game_id'], game['date']))

        # Load player data
        for player in transformed_data['players']:
            query = """
            INSERT INTO player (player_id, name)
            VALUES (%s, %s)
            """
            cursor.execute(query, (player['player_id'], player['name']))

        # Load team data
        for team in transformed_data['teams']:
            query = """
            INSERT INTO team (team_id, name)
            VALUES (%s, %s)
            """
            cursor.execute(query, (team['team_id'], team['name']))

        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        db_connection.disconnect()