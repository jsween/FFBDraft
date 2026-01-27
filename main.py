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
            # TODO: Implement position analysis
            # view_position_analysis()
            pass
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