import random

from builder.RosterBuilder import build_roster_skeleton
from config.LeagueConfig import league_teams_default_config
from recommender.DraftRecommender import DraftRecommender

def view_position_analysis():
    """Show tier breakdowns and scarcity analysis for each position."""
    print("\n" + "=" * 60)
    print("  POSITION ANALYSIS")
    print("=" * 60)

    try:
        # Initialize the recommender to access player data
        recommender = DraftRecommender()

        # Show position scarcity overview
        print("\n" + "-" * 60)
        print("  POSITION SCARCITY RANKING")
        print("-" * 60)
        print("\n  (Higher scarcity = Prioritize early in draft)\n")

        scarcity = recommender.get_position_scarcity()
        print(scarcity.to_string(index=False))

        input("\nPress Enter to see detailed tier breakdowns...")

        # List of positions to analyze
        positions = ['QB', 'RB', 'WR', 'TE', 'K', 'IDP']

        for position in positions:
            print("\n" + "=" * 60)
            print(f"  {position} TIER BREAKDOWN")
            print("=" * 60)

            # Get tier data for this position
            tiers = recommender.get_tier_breakdowns(position)

            if not tiers:
                print(f"\n  No data available for {position}")
                continue

            # Display each tier
            for tier_name, stats in tiers.items():
                print(f"\n  {tier_name}:")
                print(f"    Players:  {stats['count']}")
                print(f"    Avg PPG:  {stats['avg_ppg']:.2f}")
                print(f"    Range:    {stats['min_ppg']:.2f} - {stats['max_ppg']:.2f}")

        print("\n" + "=" * 60)
        input("\nPress Enter to return to main menu...")

    except FileNotFoundError:
        print("\nError: Player rankings not found!")
        print("\nPlease run data processing first:")
        print("  1. py Step3ConsolidateData.py")
        print("  2. py Step4TrainModel.py")
        input("\nPress Enter to continue...")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        input("\nPress Enter to continue...")


def run_draft():
    """Interactive snake draft simulator with AI opponents."""
    print("\n" + "=" * 60)
    print("  FANTASY FOOTBALL DRAFT SIMULATOR")
    print("=" * 60)

    try:
        recommender = DraftRecommender()
        recommender.reset_draft()

        # Get user's draft position
        print("Draft Type: Snake Draft\nIn a Snake Draft, the order reverses each round.")
        print("Ex: Round 1 goes 1→10, Round 2 goes 10→1")

        while True:
            try:
                user_position = int(
                    input(f"\nEnter your draft position (1-{league_teams_default_config['league_size']}): ").strip())
                if 1 <= user_position <= league_teams_default_config['league_size']:
                    break
                print(f"Error: Please enter a number between 1 and {league_teams_default_config['league_size']}")
            except ValueError:
                print("Error: Please enter a valid number")

        print(f"\nYou are drafting from position #{user_position}")
        print(f"  League size: {league_teams_default_config['league_size']} teams")
        input("\nPress Enter to start the draft...")

        # Initialize rosters for all teams
        num_teams = league_teams_default_config['league_size']
        all_rosters = {}
        for i in range(1, num_teams + 1):
            roster_skeleton = build_roster_skeleton(league_teams_default_config)
            all_rosters[i] = {pos: 0 for pos in roster_skeleton.keys()}

        # Calculate total picks needed
        roster_size = sum(build_roster_skeleton(league_teams_default_config).values())
        total_rounds = roster_size

        # Snake draft order
        draft_complete = False
        current_round = 1

        while not draft_complete:
            # Determine pick order for this round (snake draft)
            if current_round % 2 == 1:  # Odd rounds: normal order
                pick_order = list(range(1, num_teams + 1))
            else:  # Even rounds: backwards draft order
                pick_order = list(range(num_teams, 0, -1))

            print("\n" + "=" * 60)
            print(f"  ROUND {current_round}")
            print("=" * 60)

            for drafter_position in pick_order:
                # Calculate overall pick number
                if current_round % 2 == 1:
                    overall_pick = (current_round - 1) * num_teams + drafter_position
                else:
                    overall_pick = (current_round - 1) * num_teams + (num_teams - drafter_position + 1)

                # Check if draft is complete
                user_roster_full = all(
                    all_rosters[user_position][pos] >= build_roster_skeleton(league_teams_default_config)[pos]
                    for pos in all_rosters[user_position].keys()
                )
                if user_roster_full:
                    draft_complete = True
                    break

                if drafter_position == user_position:
                    # USER'S TURN
                    print("\n" + "█" * 60)
                    print(f"  YOUR TURN - Pick #{overall_pick}")
                    print("█" * 60)

                    # Show user's roster
                    print("\nYour Current Roster:")
                    roster_skeleton = build_roster_skeleton(league_teams_default_config)
                    for pos, count in all_rosters[user_position].items():
                        needed = roster_skeleton[pos]
                        status = "F" if count >= needed else "o"
                        max_allowed = league_teams_default_config['max_per_position'].get(pos, needed)
                        print(f"  [{status}] {pos:6s}: {count}/{needed} (max: {max_allowed})")

                    # Get top 3 recommendations
                    recommendations = recommender.get_recommendations(
                        all_rosters[user_position],
                        league_teams_default_config,
                        top_n=25 # this gets the top 25, making sure we get 3 distinct positions to draft
                    )

                    if recommendations.empty:
                        print("\nYour roster is full!")
                        draft_complete = True
                        break

                    # Display top 3 positions to draft
                    print("\n" + "~" * 60)
                    print("  RECOMMENDED 3 POSITIONS TO DRAFT")
                    print("~" * 60)

                    top_positions = []
                    seen_positions = set()

                    for idx, row in recommendations.iterrows():
                        pos = row['position']
                        if pos not in seen_positions:
                            top_positions.append({
                                'position': pos,
                                'ppg': row['points_per_game'],
                                'rank': int(row['position_rank']),
                                'value': row['value_score'],
                                'index': idx
                            })
                            seen_positions.add(pos)
                            if len(top_positions) == 3:
                                break

                    for i, pos_info in enumerate(top_positions, 1):
                        print(
                            f"  {i}. {pos_info['position']:5s} - {pos_info['ppg']:.1f} PPG (Rank #{pos_info['rank']}, Value: {pos_info['value']:.1f})")

                    # Simple input prompt to get user's draft choice
                    print("\n" + "-" * 60)
                    valid_positions = [p['position'] for p in top_positions]
                    print(f"  Enter position to draft: {' / '.join(valid_positions)}")
                    print(f"  (or press ENTER to draft {valid_positions[0]})")

                    print("-" * 60)

                    while True:
                        choice = input("\nDraft position: ").strip().upper()
                        # handle default first choice
                        if choice == "":
                            choice = valid_positions[0]

                        if choice in valid_positions:
                            # Find the player to draft
                            selected_pos_info = next(p for p in top_positions if p['position'] == choice)
                            player_idx = selected_pos_info['index']

                            # Get the actual best available player at that position
                            best_at_pos = recommender.get_best_available_by_position(choice, n=1)
                            if best_at_pos.empty:
                                print(f"No available players at {choice}")
                                continue

                            # Find the index of this player in the rankings
                            player_to_draft = best_at_pos.index[0]

                            # Draft the player
                            recommender.mark_player_drafted(player_to_draft)

                            # Update roster
                            if not update_roster(all_rosters[user_position], choice, league_teams_default_config):
                                print(f"ERRORThat position {choice} is full!")
                                recommender.drafted_players.remove(player_to_draft)
                                continue

                            drafted_player = best_at_pos.iloc[0]
                            print(f"\nYOU DRAFTED: {choice}")
                            print(f"PPG: {drafted_player['points_per_game']:.2f} | Position Rank: #{int(drafted_player['position_rank'])}")
                            break
                        else:
                            print(f"Please enter one of: {' / '.join(valid_positions)}")

                else:
                    # Sim other drafters for speed of testing
                    computer_recommendations = recommender.get_recommendations(
                        all_rosters[drafter_position],
                        league_teams_default_config,
                        top_n=15 # more options for random picking
                    )

                    if not computer_recommendations.empty:
                        # Get top 3 unique positions (like user sees)
                        comp_top_positions = []
                        seen_positions = set()

                        for idx, row in computer_recommendations.iterrows():
                            pos = row['position']
                            if pos not in seen_positions:
                                comp_top_positions.append({
                                    'position': pos,
                                    'index': idx
                                })
                                seen_positions.add(pos)
                                if len(comp_top_positions) == 3:
                                    break

                        comp_position = None
                        comp_player = None
                        # Randomly select from top 3 positions (simulating drafter bias)
                        if comp_top_positions:
                            selected = random.choice(comp_top_positions)
                            comp_position = selected['position']

                            # Draft best available at selected position
                            best_at_pos = recommender.get_best_available_by_position(comp_position, n=1)
                            if not best_at_pos.empty:
                                comp_idx = best_at_pos.index[0]
                                comp_player = best_at_pos.iloc[0]

                                recommender.mark_player_drafted(comp_idx)
                                update_roster(all_rosters[drafter_position], comp_position, league_teams_default_config)
                        print(
                            f"  Pick #{overall_pick}: Drafter {drafter_position} → {comp_position} ({comp_player['points_per_game']:.1f} PPG)")

            if not draft_complete:
                current_round += 1

        # Draft complete
        print("\n" + "=" * 60)
        print("  DRAFT COMPLETE!")
        print("=" * 60)
        print("\nYour Final Roster:")
        for pos, count in all_rosters[user_position].items():
            needed = build_roster_skeleton(league_teams_default_config)[pos]
            status = "✓" if count >= needed else "✗"
            print(f"  [{status}] {pos:6s}: {count}/{needed}")

        input("\nPress Enter to return to main menu...")

    except FileNotFoundError:
        print("\nError: Required data files not found!")
        print("\nPlease run the data pipeline first:")
        print("  1. py Step3ConsolidateData.py")
        print("  2. py Step4TrainModel.py")
        input("\nPress Enter to continue...")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to continue...")


def update_roster(roster, position, league_config):
    """
    Update roster with drafted player.
    Returns True if successful, False if no spot available.
    """

    max_allowed = league_config['max_per_position'].get(position, 99)
    current_at_position = roster.get(position, 0)

    if current_at_position >= max_allowed:
        return False  # reached max number of players for this position

    starter_needed = league_config['starters_per_pos'].get(position, 0)
    if roster[position] < starter_needed:
        roster[position] += 1
        return True
    elif (position in league_config['flex_eligible'] and
          roster['FLEX'] < league_config['flex_spots']):
        roster['FLEX'] += 1
        return True
    elif roster['BENCH'] < league_config['bench_spots']:
        roster['BENCH'] += 1
        return True

    return False


def main_menu():
    """
    Shows the home menu and route to the selected option.
    This runs in a loop until the user chooses to quit.
    """
    run = True

    print("\n" + "=" * 50)
    print("  FANTASY FOOTBALL DRAFT ASSISTANT")
    print("=" * 50)
    print("\n  Data-driven draft recommendations")
    print("  to help you dominate your league!\n")
    input("Press Enter to continue...")

    while run:
        print("\n" + "=" * 50)
        print("  FANTASY FOOTBALL DRAFT ASSISTANT")
        print("=" * 50)
        print("\n1. View position analysis")
        print("2. Start draft")
        print("3. Quit")
        print("\n" + "=" * 50)

        choice = input("\nSelect an option (1-3): ").strip()

        if choice == "1":
            view_position_analysis()
        elif choice == "2":
            run_draft()
        elif choice == "3":
            run = False
            print("\n" + "=" * 50)
            print("  Thank you for using Draft Assistant!")
            print("  Good luck this season!")
            print("=" * 50 + "\n")
        else:
            print("\nInvalid choice - please enter 1-3")


if __name__ == "__main__":
    main_menu()