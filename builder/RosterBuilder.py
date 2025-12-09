def build_roster_skeleton(league_config):
    """
    Builds a roster skeleton to track drafting
    :param league_config: basic league information
    :return: an empty roster
    """
    roster = {}
    for pos, n in league_config["starters_per_pos"].items():
        roster[pos] = n

    roster["FLEX"] = league_config["flex_spots"]
    roster["BENCH"] = league_config["bench_spots"]

    return roster