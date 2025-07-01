"""
Parking systems
"""

import json
import os
from datetime import datetime
import validators
from calculator import PricingCalculator


class ParkingSystem:
    def __init__(self, data_folder="data"):
        self.data_folder = data_folder
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

        self.parked_cars_file = os.path.join(
            self.data_folder, "parked_cars.json")
        self.credits_file = os.path.join(self.data_folder, "credits.json")
        self.history_file = os.path.join(self.data_folder, "history.json")

        self.parked_cars = self._load_json(self.parked_cars_file, {})
        self.credits = self._load_json(self.credits_file, {})
        self.history = self._load_json(self.history_file, {})

    def _load_json(self, file_path, default_data):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default_data

    def _save_json(self, data, file_path):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def _save_all_data(self):
        self._save_json(self.parked_cars, self.parked_cars_file)
        self._save_json(self.credits, self.credits_file)
        self._save_json(self.history, self.history_file)

    def park(self):
        print("\n--- Park a Car ---")
        while True:
            car_id = input(
                "Enter car identity (e.g., 59C-12345): ").strip().upper()
            if validators.validate_car_id(car_id):
                if car_id in self.parked_cars:
                    print("Error: This car is already parked.")
                else:
                    break
            else:
                print("Invalid car identity format. Please try again.")

        while True:
            arrival_time_str = input(
                "Enter arrival time (YYYY-MM-DD HH:MM): ").strip()
            if validators.validate_arrival_time(arrival_time_str):
                break
            else:
                print("Invalid datetime format. Please try again.")

        fpn = input(
            "Enter frequent parking number (5 digits, optional, press Enter to skip): ").strip()
        is_fpn_valid = fpn and validators.validate_frequent_parking_number(fpn)
        if fpn and not is_fpn_valid:
            print(
                "Invalid frequent parking number. Car will be registered without FPN benefits.")
            fpn = None
        elif not fpn:
            fpn = None

        self.parked_cars[car_id] = {
            "arrival_time": arrival_time_str,
            "frequent_parking_number": fpn
        }
        self._save_all_data()
        print(f"\nSuccessfully parked car {car_id} at {arrival_time_str}.")

    def pickup(self):
        print("\n--- Pick up a Car ---")
        car_id = input("Enter car identity to pick up: ").strip().upper()

        if car_id not in self.parked_cars:
            print("Error: This car was not found in the parking lot.")
            return

        car_info = self.parked_cars[car_id]
        arrival_dt = datetime.strptime(
            car_info["arrival_time"], '%Y-%m-%d %H:%M')

        # To facilitate testing according to the assignment, we will input the leave time.
        # In a real-world scenario, this could be datetime.now().
        while True:
            leave_time_str = input(
                f"Enter leave time for car {car_id} (YYYY-MM-DD HH:MM): ").strip()
            if validators.validate_arrival_time(leave_time_str):
                leave_dt = datetime.strptime(leave_time_str, '%Y-%m-%d %H:%M')
                if leave_dt > arrival_dt:
                    break
                else:
                    print("Leave time must be after arrival time.")
            else:
                print("Invalid datetime format.")

        is_frequent = bool(car_info.get("frequent_parking_number"))
        calculator = PricingCalculator(is_frequent_parker=is_frequent)

        fee = calculator.calculate_fee(arrival_dt, leave_dt)
        print(f"Total parking fee: ${fee:.2f}")

        available_credit = self.credits.get(car_id, 0.0)
        if available_credit > 0:
            print(f"You have ${available_credit:.2f} in credits.")
            if fee <= available_credit:
                self.credits[car_id] -= fee
                print(
                    f"Fee paid using credits. Remaining credit: ${self.credits[car_id]:.2f}")
                fee = 0
            else:
                fee -= available_credit
                self.credits[car_id] = 0
                print(f"Used all credits. Amount to pay: ${fee:.2f}")

        final_fee = fee
        if final_fee > 0:
            while True:
                try:
                    payment_str = input(
                        f"Enter payment amount (>= {final_fee:.2f}): ")
                    payment = float(payment_str)
                    if payment >= final_fee:
                        break
                    else:
                        print(
                            f"Payment must be greater than or equal to ${final_fee:.2f}")
                except (ValueError, TypeError):
                    print("Please enter a valid number.")

            overpaid = payment - final_fee
            if overpaid > 0:
                self.credits[car_id] = self.credits.get(car_id, 0.0) + overpaid
                print(
                    f"Payment successful. Change of ${overpaid:.2f} has been saved as credit.")

        # Log to history
        if car_id not in self.history:
            self.history[car_id] = []

        self.history[car_id].append({
            "arrival": car_info["arrival_time"],
            "leave": leave_dt.strftime('%Y-%m-%d %H:%M'),
            "fee_paid": final_fee
        })

        # Remove car from lot and save all data
        del self.parked_cars[car_id]
        self._save_all_data()
        print(f"Car {car_id} has left the parking lot.")

    def show_history(self):
        print("\n--- View History ---")
        car_id = input("Enter car identity to view history: ").strip().upper()

        if car_id not in self.history and car_id not in self.credits:
            print(f"No history or credits found for car {car_id}.")
            return

        total_payments = sum(item['fee_paid']
                             for item in self.history.get(car_id, []))
        available_credits = self.credits.get(car_id, 0.0)

        file_name = f"{car_id}.txt"
        try:
            with open(file_name, 'w') as f:
                f.write(f"Total payment: ${total_payments:.2f}\n")
                f.write(f"Available credits: ${available_credits:.2f}\n")
                f.write("Parked Dates:\n")

                car_history = self.history.get(car_id, [])
                for record in car_history:
                    # To display the full cost of each stay in the history file as per the example format.
                    arrival = datetime.strptime(
                        record['arrival'], '%Y-%m-%d %H:%M')
                    leave = datetime.strptime(
                        record['leave'], '%Y-%m-%d %H:%M')

                    # For this display, we need the original fee without discounts.
                    # This calculation might differ from what was actually paid if discounts/credits were used.
                    # We can get the paid amount from the record directly.
                    # For consistency with the prompt's example output, let's just display the paid amount.
                    stay_time_str = f"{record['arrival']} - {record['leave']}"
                    f.write(f"{stay_time_str} ${record['fee_paid']:.2f}\n")

            print(f"History has been exported to file: {file_name}")
        except IOError as e:
            print(f"Error writing to file: {e}")
