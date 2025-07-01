# main.py
from parking_system import ParkingSystem


def main_menu():
    print("\n==============================")
    print("  CONSOLE PARKING SYSTEM")
    print("==============================")
    print("1. Park a car")
    print("2. Pick up a car")
    print("3. View history")
    print("4. Exit")
    choice = input("Please select an option: ")
    return choice


def main():
    system = ParkingSystem()

    while True:
        choice = main_menu()
        if choice == '1' or choice.lower() == 'park':
            system.park()
        elif choice == '2' or choice.lower() == 'pickup':
            system.pickup()
        elif choice == '3' or choice.lower() == 'history':
            system.show_history()
        elif choice == '4' or choice.lower() == 'exit':
            print("Thank you for using the system. Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
