from config.LeagueConfig import league_teams_default_config
from builder import RosterBuilder

def test_build_roster_skeleton():
    expected = {
        "QB": 1,
        "RB": 2,
        "WR": 2,
        "TE": 1,
        "DP": 1,
        "D/ST": 1,
        "K": 1,
        "FLEX": 2,
        "BENCH": 3
    }

    assert RosterBuilder.build_roster_skeleton(league_teams_default_config) == expected