class Boxscore:
    def __init__(self, game_id, home_team, away_team):
        self.game_id = game_id
        self.home_team = home_team
        self.away_team = away_team

    @classmethod
    def from_json(cls, json_data):
        game_id = json_data.get('game_id')
        home_team = json_data.get('home_team')
        away_team = json_data.get('away_team')
        return cls(game_id, home_team, away_team)

    def to_dict(self):
        return {
            'game_id': self.game_id,
            'home_team': self.home_team,
            'away_team': self.away_team
        }