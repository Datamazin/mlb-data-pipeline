class Team:
    def __init__(self, team_id, name):
        self.team_id = team_id
        self.name = name

    @classmethod
    def from_json(cls, json_data):
        return cls(
            team_id=json_data.get('team_id'),
            name=json_data.get('name')
        )