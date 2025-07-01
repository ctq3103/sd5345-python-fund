"""
Calculators
"""

from datetime import datetime, timedelta, time


class PricingCalculator:
    """
    Calculates parking fees based on arrival time, departure time, 
    and frequent parker status.
    """
    RATES = {
        # Monday to Friday (0-4)
        **{i: {
            "08:00-16:59": {"max_stay": 2, "price_per_hour": 10.00},
            "17:00-23:59": {"max_stay": "Up to midnight", "price_per_hour": 5.00},
            "00:00-07:59": {"price_one_time": 20.00}
        } for i in range(5)},
        # # Friday (4)
        # 4: {
        #     "08:00-16:59": {"max_stay": 2, "price_per_hour": 10.00},
        #     "17:00-23:59": {"max_stay": "Up to midnight", "price_per_hour": 5.00},
        #     "00:00-07:59": {"price_one_time": 20.00}
        # },
        # Saturday (5)
        5: {
            "08:00-16:59": {"max_stay": 4, "price_per_hour": 3.00},
            "17:00-23:59": {"max_stay": "Up to midnight", "price_per_hour": 5.00},
            "00:00-07:59": {"price_one_time": 20.00}
        },
        # Sunday (6)
        6: {
            "08:00-16:59": {"max_stay": 8, "price_per_hour": 2.00},
            "17:00-23:59": {"max_stay": "Up to midnight", "price_per_hour": 5.00},
            "00:00-07:59": {"price_one_time": 20.00}
        }
    }

    def __init__(self, is_frequent_parker: bool):
        self.is_frequent_parker = is_frequent_parker

    def _apply_discount(self, price: float, current_time: datetime) -> float:
        """Applies discounts based on the time and frequent parker status."""
        if not self.is_frequent_parker:
            return price

        # 50% discount for parking time: 17:00 - Midnight, Midnight - 08:00.
        if time(17, 0) <= current_time.time() or current_time.time() < time(8, 0):
            return price * 0.5
        # 10% for other parking time.
        else:
            return price * 0.9

    def calculate_fee(self, arrival_dt: datetime, leave_dt: datetime) -> float:
        """Calculates the total parking fee by iterating through each day."""
        total_fee = 0.0

        current_day = arrival_dt.date()
        while current_day <= leave_dt.date():
            day_of_week = current_day.weekday()
            rates_for_day = self.RATES[day_of_week]

            start_of_day = datetime.combine(current_day, time.min)
            end_of_day = datetime.combine(current_day, time.max)

            day_start_dt = max(arrival_dt, start_of_day)
            day_end_dt = min(leave_dt, end_of_day)

            # Slot 1: 00:00 - 07:59 (Flat Fee)
            slot1_start, slot1_end = time(0, 0), time(7, 59)
            if max(day_start_dt.time(), slot1_start) <= min(day_end_dt.time(), slot1_end):
                fee = rates_for_day["00:00-07:59"]["price_one_time"]
                total_fee += self._apply_discount(fee,
                                                  datetime.combine(current_day, time(1, 0)))

            # Slot 2: 08:00 - 16:59 (Hourly Rate)
            slot2_start_dt = datetime.combine(current_day, time(8, 0))
            slot2_end_dt = datetime.combine(current_day, time(16, 59))

            overlap_start = max(day_start_dt, slot2_start_dt)
            overlap_end = min(day_end_dt, slot2_end_dt)

            if overlap_end > overlap_start:
                hours_in_slot = round(
                    (overlap_end - overlap_start).total_seconds() / 3600)
                if hours_in_slot > 0:
                    rate_info = rates_for_day["08:00-16:59"]
                    price_per_hour = rate_info["price_per_hour"]
                    max_stay = rate_info["max_stay"]

                    if hours_in_slot <= max_stay:
                        fee = hours_in_slot * price_per_hour
                    else:  # Apply double price for exceeded hours
                        fee = (max_stay * price_per_hour) + \
                              ((hours_in_slot - max_stay) * price_per_hour * 2)

                    total_fee += self._apply_discount(fee, slot2_start_dt)

            # Slot 3: 17:00 - 23:59 (Hourly Rate)
            slot3_start_dt = datetime.combine(current_day, time(17, 0))
            slot3_end_dt = datetime.combine(current_day, time(23, 59, 59))

            overlap_start = max(day_start_dt, slot3_start_dt)
            overlap_end = min(day_end_dt, slot3_end_dt)

            if overlap_end > overlap_start:
                hours_in_slot = round(
                    (overlap_end - overlap_start).total_seconds() / 3600)
                if hours_in_slot > 0:
                    rate_info = rates_for_day["17:00-23:59"]
                    price_per_hour = rate_info["price_per_hour"]
                    fee = hours_in_slot * price_per_hour
                    total_fee += self._apply_discount(fee, slot3_start_dt)

            current_day += timedelta(days=1)

        return round(total_fee, 2)
