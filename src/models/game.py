class Game:
    def __init__(self, game_id, date):
        self.game_id = game_id
        self.date = date

    def parse_game_data(self, data):
        self.game_id = data.get('game_id')
        self.date = data.get('date')