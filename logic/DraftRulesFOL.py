"""
First-Order Logic rules for draft decision-making.

Predicates:
- NeedsPosition(roster, position): True if roster needs this position
- IsElite(player): True if player is in top 20% at position
- IsScarce(position): True if position has high scarcity (>1.5)
- AtMax(roster, position): True if position is at maximum capacity
- HasStarterAt(roster, position): True if it has starter at this position
"""


class DraftRules:
    """Simple First-Order Logic predicates for draft decisions."""

    def __init__(self, league_config):
        self.league_config = league_config


    def needs_position(self, roster, position):
        """NeedsPosition(roster, position) - Roster needs this position."""
        filled = roster.get(position, 0)
        required = self.league_config['starters_per_pos'].get(position, 0)
        max_allowed = self.league_config['max_per_position'].get(position, 99)

        # Need if no starter or num pos < max and have slots on bench
        return (filled < required or
                (filled < max_allowed and
                 roster.get('BENCH', 0) < self.league_config['bench_spots']))


    @staticmethod
    def is_elite(player_row):
        """IsElite(player) - Player is in top 20% at their position."""
        return player_row.get('position_percentile', 0) >= 0.8


    @staticmethod
    def is_scarce(position, scarcity_data):
        """IsScarce(position) - Position has high scarcity score (>1.5)."""
        if scarcity_data is None:
            return False
        pos_scarcity = scarcity_data[scarcity_data['position'] == position]
        if pos_scarcity.empty:
            return False

        return pos_scarcity.iloc[0]['scarcity_score'] > 1.5


    def at_max(self, roster, position):
        """AtMax(roster, position) - Roster at maximum for this position."""
        filled = roster.get(position, 0)
        max_allowed = self.league_config['max_per_position'].get(position, 99)
        return filled >= max_allowed


    def has_starter_at(self, roster, position):
        """HasStarterAt(roster, position) - Has starter filled at position."""
        filled = roster.get(position, 0)
        required = self.league_config['starters_per_pos'].get(position, 0)
        return filled >= required

    # ==================== First Order Logic ====================

    def should_recommend(self, roster, player_row, scarcity_data):
        """
        FOL Rule:
        Recommend(player) ← NeedsPosition(r, p) ∧ ¬AtMax(r, p) ∧
                           (IsElite(player) ∨ IsScarce(p))

        Recommend IF we need the position & not at max &
                    (player is elite OR position is scarce)
        """
        position = player_row['position']

        # Must satisfy basic constraints
        needs = self.needs_position(roster, position)
        not_at_max = not self.at_max(roster, position)

        # Should recommend if elite OR scarce
        elite = self.is_elite(player_row)
        scarce = self.is_scarce(position, scarcity_data)

        # Combine with AND/OR logic
        return needs and not_at_max and (elite or scarce)