class Player:
    def __init__(self, player_id, name):
        self.player_id = player_id
        self.name = name

    @classmethod
    def from_json(cls, json_data):
        return cls(
            player_id=json_data.get('player_id'),
            name=json_data.get('name')
        )