"""
Draft recommendation system that suggests the best available position
based on roster needs and value.
"""
import pandas as pd


class DraftRecommender:
    """Recommends players based on roster needs and player value."""

    def __init__(self, player_rankings_path="data/summary/player_rankings.csv"):
        """Initialize with player rankings data."""
        self.rankings = pd.read_csv(player_rankings_path)
        self.drafted_players = set()

    @staticmethod
    def get_position_needs(roster, league_config):
        """
        Determine which positions still need to be filled.

        Args:
            roster: Dict with filled position counts
            league_config: League configuration dict

        Returns:
            Dict of position: remaining_spots_needed
        """
        needs = {}

        # Check starter positions
        for pos, required in league_config['starters_per_pos'].items():
            filled = roster.get(pos, 0)
            if filled < required:
                needs[pos] = required - filled

        # Check flex spots
        flex_filled = roster.get('FLEX', 0)
        if flex_filled < league_config['flex_spots']:
            for pos in league_config['flex_eligible']:
                needs[pos] = needs.get(pos, 0) + 1

        # Always consider bench
        bench_filled = roster.get('BENCH', 0)
        if bench_filled < league_config['bench_spots']:
            # All positions can fill bench
            for pos in league_config['starters_per_pos'].keys():
                needs[pos] = needs.get(pos, 0) + 1

        return needs

    @staticmethod
    def calculate_player_value(player_row, position_needs):
        """
        Calculate value score for a player based on:
        - Position scarcity
        - Performance vs position average
        - Roster needs

        Args:
            player_row: DataFrame row with player stats
            position_needs: Dict of position needs

        Returns:
            Float value score
        """
        position = player_row['position']

        # Base value from performance
        base_value = player_row['points_per_game']

        # Bonus for being above position average
        position_diff = player_row.get('ppg_vs_position_avg', 0)
        value_score = base_value + (position_diff * 0.5)

        # Apply need multiplier
        need_multiplier = position_needs.get(position, 0)
        if need_multiplier > 0:
            # Boost value if we need this position
            value_score *= (1 + (need_multiplier * 0.2))
        else:
            # Penalize if we don't need this position
            value_score *= 0.5

        # Bonus for elite players (top 20% in their position)
        if player_row.get('position_percentile', 0) >= 0.8:
            value_score *= 1.3

        return value_score

    def get_recommendations(self, roster, league_config, season=2024, top_n=10):
        """
        Get top N player recommendations based on current roster.

        Args:
            roster: Dict showing filled positions
            league_config: League configuration dict
            season: Season to get recommendations for
            top_n: Number of recommendations to return

        Returns:
            DataFrame of recommended players with value scores
        """
        # Get position needs
        position_needs = self.get_position_needs(roster, league_config)

        if not position_needs:
            return pd.DataFrame()  # Roster is full

        # Filter to most recent season and available players
        available = self.rankings[
            (self.rankings['season'] == season) &
            (~self.rankings.index.isin(self.drafted_players))
            ].copy()

        if available.empty:
            return pd.DataFrame()

        # Calculate value for each player
        available['value_score'] = available.apply(
            lambda row: self.calculate_player_value(row, position_needs),
            axis=1
        )

        # Sort by value and get top N
        recs = available.nlargest(top_n, 'value_score')

        # Format output
        output_cols = [
            'position', 'points_per_game', 'fantasy_points',
            'position_rank', 'position_percentile', 'value_score'
        ]

        return recs[output_cols].round(2)

    def mark_player_drafted(self, player_index):
        """Mark a player as drafted (no longer available)."""
        self.drafted_players.add(player_index)

    def reset_draft(self):
        """Reset the draft (clear all drafted players)."""
        self.drafted_players = set()

    def get_best_available_by_position(self, position, season=2024, n=5):
        """
        Get the N-best available players at a specific position.

        Args:
            position: Position code (QB, RB, WR, etc.)
            season: Season to filter by
            n: Number of players to return

        Returns:
            DataFrame of top N available players at position
        """
        available = self.rankings[
            (self.rankings['season'] == season) &
            (self.rankings['position'] == position) &
            (~self.rankings.index.isin(self.drafted_players))
            ].copy()

        if available.empty:
            return pd.DataFrame()

        return available.nlargest(n, 'points_per_game')[[
            'position', 'points_per_game', 'fantasy_points',
            'position_rank', 'position_percentile'
        ]].round(2)

    def get_tier_breakdowns(self, position, season=2024):
        """
        Get tier breakdown for a position (useful for identifying
        when to draft that position).

        Args:
            position: Position code
            season: Season to analyze

        Returns:
            Dict with tier statistics
        """
        pos_data = self.rankings[
            (self.rankings['season'] == season) &
            (self.rankings['position'] == position)
            ].sort_values('points_per_game', ascending=False)

        if pos_data.empty:
            return {}

        # Define tiers based on percentiles
        tiers = {
            'Elite (Top 10%)': pos_data[pos_data['position_percentile'] >= 0.9],
            'Tier 1 (Top 25%)': pos_data[
                (pos_data['position_percentile'] >= 0.75) &
                (pos_data['position_percentile'] < 0.9)
                ],
            'Tier 2 (Top 50%)': pos_data[
                (pos_data['position_percentile'] >= 0.5) &
                (pos_data['position_percentile'] < 0.75)
                ],
            'Tier 3 (Top 75%)': pos_data[
                (pos_data['position_percentile'] >= 0.25) &
                (pos_data['position_percentile'] < 0.5)
                ],
            'Tier 4 (Bottom 25%)': pos_data[pos_data['position_percentile'] < 0.25]
        }

        tier_summary = {}
        for tier_name, tier_data in tiers.items():
            if not tier_data.empty:
                tier_summary[tier_name] = {
                    'count': len(tier_data),
                    'avg_ppg': tier_data['points_per_game'].mean(),
                    'min_ppg': tier_data['points_per_game'].min(),
                    'max_ppg': tier_data['points_per_game'].max()
                }

        return tier_summary

    def get_position_scarcity(self, season=2024):
        """
        Calculate position scarcity - helps identify which positions
        to prioritize in the draft.

        Returns:
            DataFrame with scarcity metrics by position
        """
        season_data = self.rankings[self.rankings['season'] == season]

        scarcity = []
        for position in season_data['position'].unique():
            pos_data = season_data[season_data['position'] == position]

            # Calculate drop-off from best to average
            if len(pos_data) > 0:
                top_10_pct = pos_data.nlargest(max(1, len(pos_data) // 10), 'points_per_game')
                median_ppg = pos_data['points_per_game'].median()
                top_10_ppg = top_10_pct['points_per_game'].mean()

                scarcity.append({
                    'position': position,
                    'total_players': len(pos_data),
                    'top_10_avg_ppg': round(top_10_ppg, 2),
                    'median_ppg': round(median_ppg, 2),
                    'drop_off': round(top_10_ppg - median_ppg, 2),
                    'scarcity_score': round((top_10_ppg - median_ppg) / median_ppg, 2)
                })

        return pd.DataFrame(scarcity).sort_values('scarcity_score', ascending=False)


# Example usage / testing
# Example usage / testing
if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Add parent directory to path
    parent_dir = str(Path(__file__).parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    from config.LeagueConfig import league_teams_default_config

    try:
        # Initialize recommender
        recommender = DraftRecommender()

        # Example roster early in draft
        current_roster = {
            "QB": 1,
            "RB": 0,
            "WR": 0,
            "TE": 0,
            "DP": 0,
            "D/ST": 0,
            "K": 0,
            "FLEX": 0,
            "BENCH": 0
        }

        print("=" * 60)
        print("  DRAFT RECOMMENDER TEST")
        print("=" * 60)

        print("\nCurrent Roster:")
        for pos, count in current_roster.items():
            needed = league_teams_default_config['starters_per_pos'].get(pos, 0)
            if pos == 'FLEX':
                needed = league_teams_default_config['flex_spots']
            elif pos == 'BENCH':
                needed = league_teams_default_config['bench_spots']
            status = "✓" if count >= needed else " "
            print(f"  [{status}] {pos:6s}: {count}/{needed}")

        # Get recommendations
        recommendations = recommender.get_recommendations(
            current_roster,
            league_teams_default_config,
            top_n=10
        )

        print("\n" + "=" * 60)
        print("  TOP 10 RECOMMENDATIONS")
        print("=" * 60)
        print(recommendations.to_string())

        # Position scarcity
        print("\n" + "=" * 60)
        print("  POSITION SCARCITY ANALYSIS")
        print("=" * 60)
        scarcity = recommender.get_position_scarcity()
        print(scarcity.to_string(index=False))

        print("\nRecommender test complete!")

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nPlease run the following first:")
        print("  1. py Step1DataProcessing.py")
        print("  2. py Step2CleanData.py")
        print("  3. py Step3ConsolidateData.py")
        print("  4. py Step4TrainModel.py")