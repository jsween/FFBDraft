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
            # TODO: Draft
            # run_draft()
            pass
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