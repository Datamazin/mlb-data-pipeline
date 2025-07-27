def transform_data(boxscore_data, game_data, player_data, team_data):
    transformed_data = {
        "boxscore": [],
        "games": [],
        "players": [],
        "teams": []
    }

    for boxscore in boxscore_data:
        transformed_data["boxscore"].append({
            "game_id": boxscore["game_id"],
            "home_team": boxscore["home_team"],
            "away_team": boxscore["away_team"],
            "home_score": boxscore["home_score"],
            "away_score": boxscore["away_score"]
        })

    for game in game_data:
        transformed_data["games"].append({
            "game_id": game["game_id"],
            "date": game["date"],
            "status": game["status"]
        })

    for player in player_data:
        transformed_data["players"].append({
            "player_id": player["player_id"],
            "name": player["name"],
            "team_id": player["team_id"]
        })

    for team in team_data:
        transformed_data["teams"].append({
            "team_id": team["team_id"],
            "name": team["name"],
            "league": team["league"]
        })

    return transformed_data