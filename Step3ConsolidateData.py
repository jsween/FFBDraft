"""
Step 3: Consolidate all processed data and calculate fantasy points.
Run this after Step1DataProcessing.ipynb and Step2CleanData.ipynb.
"""
import pandas as pd
from pathlib import Path
from config.ScoringConfig import league_default_scoring_config as scoring


def calculate_offensive_points(row):
    """Calculate fantasy points for offensive players."""
    points = 0

    # Passing
    points += row.get('passing_yards', 0) * scoring['passing']['py']
    points += row.get('pass_touchdown', 0) * scoring['passing']['ptd']
    points += row.get('interception', 0) * scoring['passing']['int']

    # Rushing
    points += row.get('rushing_yards', 0) * scoring['rushing']['ry']
    points += row.get('rush_touchdown', 0) * scoring['rushing']['rtd']

    # Receiving
    points += row.get('receiving_yards', 0) * scoring['receiving']['rey']

    # Total TDs (for receiving TDs)
    if pd.notna(row.get('total_tds', 0)):
        # Receiving TDs = total_tds - rush_touchdown - pass_touchdown
        receiving_tds = row.get('total_tds', 0) - row.get('rush_touchdown', 0)
        points += receiving_tds * scoring['receiving']['retd']

    # Fumbles
    points += row.get('fumble', 0) * scoring['misc']['fuml']

    return points


def calculate_defensive_points(row):
    """Calculate fantasy points for defensive players."""
    points = 0

    points += row.get('sack', 0) * scoring['def_plyr']['sk']
    points += row.get('solo_tackle', 0) * scoring['def_plyr']['tk']
    points += row.get('assist_tackle', 0) * scoring['def_plyr']['tka']
    points += row.get('tackle_with_assist', 0) * scoring['def_plyr']['tks']
    points += row.get('interception', 0) * scoring['def_plyr']['int']
    points += row.get('fumble_forced', 0) * scoring['def_plyr']['ff']
    points += row.get('def_touchdown', 0) * 6  # Simplified for PM project
    points += row.get('safety', 0) * scoring['def_plyr']['sf']

    return points


def calculate_team_defense_points(row):
    """Calculate fantasy points for team defense/special teams."""
    points = 0

    # Defensive actions
    points += row.get('sack', 0) * scoring['tm_df_sp_tm']['sk']
    points += row.get('interception', 0) * scoring['tm_df_sp_tm']['int']
    points += row.get('fumble', 0) * scoring['tm_df_sp_tm']['fr']
    points += row.get('def_touchdown', 0) * scoring['tm_df_sp_tm']['inttd']
    points += row.get('safety', 0) * scoring['tm_df_sp_tm']['sf']

    # Points allowed (based on your scoring config)
    pts_allowed = row.get('Pts/G', 0)
    if pts_allowed == 0:
        points += scoring['tm_df_sp_tm']['pa0']
    elif pts_allowed <= 6:
        points += scoring['tm_df_sp_tm']['pa1']
    elif pts_allowed <= 13:
        points += scoring['tm_df_sp_tm']['pa7']
    elif pts_allowed <= 17:
        points += scoring['tm_df_sp_tm']['pa14']
    elif pts_allowed <= 21:
        points += scoring['tm_df_sp_tm']['pa18']
    elif pts_allowed <= 27:
        points += scoring['tm_df_sp_tm']['pa22']
    elif pts_allowed <= 34:
        points += scoring['tm_df_sp_tm']['pa35']
    else:
        points += scoring['tm_df_sp_tm']['pa46']

    return points


def calculate_kicking_points(row):
    """Calculate fantasy points for kickers."""
    points = 0

    # Field goals by distance
    points += row.get('fg_made_0_19', 0) * scoring['kicking']['fg0']
    points += row.get('fg_made_20_29', 0) * scoring['kicking']['fg0']
    points += row.get('fg_made_30_39', 0) * scoring['kicking']['fg0']
    points += row.get('fg_made_40_49', 0) * scoring['kicking']['fg40']
    points += row.get('fg_made_50_59', 0) * scoring['kicking']['fg50']
    points += row.get('fg_made_60_', 0) * scoring['kicking']['fg60']

    # PATs and misses
    points += row.get('pat_made', 0) * scoring['kicking']['pat']
    points += row.get('pat_missed', 0) * scoring['kicking']['patm']
    points += row.get('fg_missed', 0) * scoring['kicking']['fgm']

    return points


def main():
    """Main consolidation function."""
    cleaned_path = Path("data/cleaned/")

    print("=" * 60)
    print("CONSOLIDATING PLAYER DATA")
    print("=" * 60)

    # Read cleaned data
    print("\n1. Loading cleaned data...")
    try:
        off_df = pd.read_csv(cleaned_path / "off_position_year_summary.csv")
        print(f"Loaded {len(off_df)} offensive records")
    except FileNotFoundError:
        print("off_position_year_summary.csv not found!")
        return None

    try:
        def_df = pd.read_csv(cleaned_path / "def_position_year_summary.csv")
        print(f"Loaded {len(def_df)} defensive records")
    except FileNotFoundError:
        print("def_position_year_summary.csv not found!")
        return None

    try:
        team_def_df = pd.read_csv(cleaned_path / "team_defense_summary.csv")
        print(f"Loaded {len(team_def_df)} team defense records")
    except FileNotFoundError:
        print("Error: team_defense_summary.csv not found! Skipping team defense...")
        return None

    try:
        kick_df = pd.read_csv(cleaned_path / "kicking_position_summary.csv")
        print(f"Loaded {len(kick_df)} kicking records")
    except FileNotFoundError:
        print("kicking_position_summary.csv not found!")
        return None

    # Calculate fantasy points
    print("\nCalculating fantasy points...")
    off_df['fantasy_points'] = off_df.apply(calculate_offensive_points, axis=1)
    def_df['fantasy_points'] = def_df.apply(calculate_defensive_points, axis=1)
    kick_df['fantasy_points'] = kick_df.apply(calculate_kicking_points, axis=1)
    if team_def_df is not None:
        team_def_df['fantasy_points'] = team_def_df.apply(calculate_team_defense_points, axis=1)
        print("Fantasy points calculated for all players (including D/ST)")
    else:
        print("Fantasy points calculated for offensive, defensive, and kicking players")

    # Add player type identifier
    off_df['player_type'] = 'offensive'
    def_df['player_type'] = 'defensive'
    team_def_df['player_type'] = 'team_defense'
    kick_df['player_type'] = 'kicker'

    # Standardize columns
    print("\n3. Standardizing columns...")

    # Offensive players
    off_cols = ['position', 'season', 'games_played_season', 'fantasy_points', 'player_type']
    off_final = off_df[off_cols].copy()

    # Defensive players
    def_cols = ['position', 'season', 'games_played_season', 'fantasy_points', 'player_type']
    def_final = def_df[def_cols].copy()

    # Team Defense
    team_def_df = team_def_df.rename(columns={'Gms': 'games_played_season'})
    team_def_df['position'] = 'D/ST'
    team_def_cols = ['position', 'season', 'games_played_season', 'fantasy_points', 'player_type']
    team_def_final = team_def_df[team_def_cols].copy()

    # Kickers - check if 'week' column exists and rename
    if 'week' in kick_df.columns:
        kick_df = kick_df.rename(columns={'week': 'games_played_season'})
    kick_df['position'] = 'K'
    kick_cols = ['position', 'season', 'games_played_season', 'fantasy_points', 'player_type']
    kick_final = kick_df[kick_cols].copy()

    print("Columns standardized across all datasets")

    # Combine all datasets
    print("\nCombining datasets...")
    combined_df = pd.concat([off_final, def_final, kick_final, team_def_final], ignore_index=True)
    print(f"  Combined into {len(combined_df)} total player-seasons")

    # Calculate points per game
    combined_df['points_per_game'] = (
            combined_df['fantasy_points'] / combined_df['games_played_season']
    ).round(2)

    # Filter out players with few games (< 4 games)
    original_count = len(combined_df)
    combined_df = combined_df[combined_df['games_played_season'] >= 4]
    filtered_count = original_count - len(combined_df)
    print(f"Filtered {filtered_count} records with < 4 games played")

    # Save consolidated dataset
    output_path = cleaned_path / "consolidated_player_data.csv"
    combined_df.to_csv(output_path, index=False)
    print(f"\n✓ Saved consolidated data to: {output_path}")

    # Print summary statistics
    print("\n" + "=" * 60)
    print("  Summary Stats")
    print("=" * 60)
    print(f"\nTotal player-seasons: {len(combined_df):,}")

    print(f"\nPlayers by position:")
    pos_counts = combined_df['position'].value_counts().sort_index()
    for pos, count in pos_counts.items():
        print(f"  {pos:6s}: {count:4d}")

    print(f"\nPlayers by season:")
    season_counts = combined_df['season'].value_counts().sort_index()
    for season, count in season_counts.items():
        print(f"  {season}: {count:4d}")

    print(f"\nFantasy points statistics:")
    print(f"  Mean:   {combined_df['fantasy_points'].mean():.2f}")
    print(f"  Median: {combined_df['fantasy_points'].median():.2f}")
    print(f"  Std:    {combined_df['fantasy_points'].std():.2f}")
    print(f"  Min:    {combined_df['fantasy_points'].min():.2f}")
    print(f"  Max:    {combined_df['fantasy_points'].max():.2f}")

    print(f"\nPoints per game statistics:")
    print(f"  Mean:   {combined_df['points_per_game'].mean():.2f}")
    print(f"  Median: {combined_df['points_per_game'].median():.2f}")
    print(f"  Std:    {combined_df['points_per_game'].std():.2f}")
    print(f"  Min:    {combined_df['points_per_game'].min():.2f}")
    print(f"  Max:    {combined_df['points_per_game'].max():.2f}")

    print("\n" + "=" * 60)
    print("DATA CONSOLIDATION COMPLETE!")
    print("=" * 60)

    return combined_df


if __name__ == "__main__":
    df = main()
    if df is not None:
        print("\nReady for Step 4: Model Training")
        print("   Run: python Step4TrainModel.py")