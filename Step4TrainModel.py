"""
Step 4: Train the draft prediction model.
Run this after Step3ConsolidateData.py completes successfully.
"""
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib


def create_position_rankings(df):
    """Create rankings within each position based on fantasy points."""
    rankings = []

    for season in df['season'].unique():
        season_data = df[df['season'] == season]
        for position in season_data['position'].unique():
            pos_data = season_data[season_data['position'] == position].copy()
            # Rank by points per game (desc)
            pos_data['position_rank'] = pos_data['points_per_game'].rank(
                ascending=False, method='min'
            )
            # Calculate percentile within position ([0-1] higher is better)
            pos_data['position_percentile'] = pos_data['points_per_game'].rank(
                pct=True
            )
            rankings.append(pos_data)

    return pd.concat(rankings, ignore_index=True)


def prepare_features(df):
    """Prepare features for model training."""
    data = df.copy()
    # Encode position
    le = LabelEncoder()
    data['position_encoded'] = le.fit_transform(data['position'])
    # Sort by position and season for lag features
    data = data.sort_values(['position', 'season'])
    # Create lag features
    data['prev_season_points'] = data.groupby('position')['fantasy_points'].shift(1)
    data['prev_season_ppg'] = data.groupby('position')['points_per_game'].shift(1)
    # Position avg per season
    data['position_avg_points'] = data.groupby(['position', 'season'])['fantasy_points'].transform('mean')
    data['position_avg_ppg'] = data.groupby(['position', 'season'])['points_per_game'].transform('mean')
    # Player's dev from position avg
    data['points_vs_position_avg'] = data['fantasy_points'] - data['position_avg_points']
    data['ppg_vs_position_avg'] = data['points_per_game'] - data['position_avg_ppg']
    # Fill NaN values for first season (no data available in prev year)
    data['prev_season_points'] = data['prev_season_points'].fillna(data['position_avg_points'])
    data['prev_season_ppg'] = data['prev_season_ppg'].fillna(data['position_avg_ppg'])

    return data, le


def main():
    """Main training function."""
    print("="*60)
    print("  STEP 4: TRAINING DRAFT PREDICTION MODEL")
    print("="*60)
    # Load consolidated data
    print("\nLoading consolidated data...")
    try:
        df = pd.read_csv("data/processed/consolidated_player_data.csv")
        print(f"  Loaded {len(df)} player-season records")
    except FileNotFoundError:
        print("   Error: consolidated_player_data.csv not found!")
        print("   Please run Step3ConsolidateData.py first")
        return
    # Create position rankings
    print("\nCreating position rankings...")
    df_ranked = create_position_rankings(df)
    # Save rankings
    rankings_path = "data/processed/player_rankings.csv"
    df_ranked.to_csv(rankings_path, index=False)
    print(f"  Rankings created and saved to {rankings_path}")
    # Prepare features
    print("\nPreparing features for modeling...")
    data, label_encoder = prepare_features(df_ranked)
    feature_columns = [
        'position_encoded',
        'games_played_season',
        'prev_season_points',
        'prev_season_ppg',
        'position_avg_points',
        'position_avg_ppg',
        'points_vs_position_avg',
        'ppg_vs_position_avg'
    ]
    # Remove rows with NaN in features or target
    data_clean = data.dropna(subset=feature_columns + ['points_per_game'])
    print(f"Prepared {len(data_clean)} records for training")
    X = data_clean[feature_columns]
    y = data_clean['points_per_game']
    # Split data into training and test sets (80-20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"   Training set: {len(X_train)} samples")
    print(f"   Test set:     {len(X_test)} samples")

    # Train Random Forest model
    print("\nTraining Random Forest model...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1,
        verbose=0
    )
    model.fit(X_train, y_train)
    print("   Model training complete!")

    # Evaluate model performance
    print("\nEvaluating model performance...")
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)

    train_mae = mean_absolute_error(y_train, train_pred)
    test_mae = mean_absolute_error(y_test, test_pred)
    train_r2 = r2_score(y_train, train_pred)
    test_r2 = r2_score(y_test, test_pred)

    print(f"\n   Train Metrics:")
    print(f"     MAE: {train_mae:.2f} points per game")
    print(f"     R²:  {train_r2:.3f}")

    print(f"\n   Test Metrics:")
    print(f"     MAE: {test_mae:.2f} points per game")
    print(f"     R²:  {test_r2:.3f}")

    # Feature importance
    importance_df = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    print(f"\nFeature Importance:")
    for _, row in importance_df.iterrows():
        bar_length = int(row['importance'] * 50)
        bar = '█' * bar_length
        print(f"     {row['feature']:30s} {bar} {row['importance']:.3f}")

    # Save model
    print("\nSaving model...")
    models_path = Path("models")
    models_path.mkdir(exist_ok=True)

    joblib.dump(model, models_path / 'draft_model.pkl')
    joblib.dump(label_encoder, models_path / 'position_encoder.pkl')
    joblib.dump(feature_columns, models_path / 'feature_columns.pkl')

    print(f"Model saved to {models_path}/")
    print(f"     - draft_model.pkl")
    print(f"     - position_encoder.pkl")
    print(f"     - feature_columns.pkl")

    # Summary
    print("\n" + "="*60)
    print("MODEL TRAINING COMPLETE!")
    print("="*60)

    if test_mae < 5.0:
        print("\nModel looks good! (Test MAE < 5.0)")
    elif test_mae < 8.0:
        print("\nModel is okay. Consider more data/features for improvement.")
    else:
        print("\nModel needs improvement. Consider:")
        print("     - Adding more historical data")
        print("     - Trying a new model")


if __name__ == "__main__":
    main()