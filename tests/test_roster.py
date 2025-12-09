from config.LeagueConfig import league_teams_default_config
from builder import RosterBuilder as rb

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

    assert rb.build_roster_skeleton(league_teams_default_config) == expected

def test_zero_bench():
    league_config = league_teams_default_config
    league_config["bench_spots"] = 0

    assert rb.build_roster_skeleton(league_config)["BENCH"] == 0