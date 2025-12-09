def main_menu():
    """
    Shows the home menu and route to the selected option.
    This runs in a loop until the user chooses to quit.
    """
    run = True
    while run:
        print("\n====================================")
        print(" Fantasy Football Draft Assistant")
        print("====================================")
        print("1. Enter league information")
        print("2. View position analysis")
        print("3. Draft")
        print("4. Quit")
        choice = input("\nSelect an option (1–4): ").strip()
        if choice == "1":
            pass
            # enter_league_information()
        elif choice == "2":
            pass
            # view_position_analysis()
        elif choice == "3":
            pass
            # run_draft()
        elif choice == "4":
            run = False
        else:
            print("Invalid choice, please enter 1–4.")

    print("Thank you for running draft assistant.")

if __name__ == "__main__":
    main_menu()