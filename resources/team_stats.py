from dataclasses import dataclass, field

@dataclass
class TeamStats:

    # Comparison function to check wheter is the same or other team. For stats calculation team
    # is considered different if it's group has changed.
    def __eq__(self, other):
        return self.team_id+self.group_name == other.team_id+other.group_name

    team_id = 0
    team_name: str = ""
    wins: int = 0
    ties: int = 0
    losses: int = 0
    points: int = 0
    goals: int = 0
    goals_allowed: int = 0
    group_name: str = ""
    lost_teams: list = field(default_factory=list)


