"""
Validators
"""

import re
from datetime import datetime

def validate_car_id(car_id: str) -> bool:
    """Validates the car ID format (e.g., 59C-12345)."""
    pattern = re.compile(r'^\d{2}[A-Z]-\d{4,5}$')
    return bool(pattern.match(car_id))


def validate_arrival_time(time_str: str) -> bool:
    """Validates the time format (YYYY-MM-DD HH:MM)."""
    try:
        datetime.strptime(time_str, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False


def validate_frequent_parking_number(number_str: str) -> bool:
    """
    Validates the frequent parking number using the Modulo 11 algorithm.
    The number must be 5 digits long.
    """
    if not number_str.isdigit() or len(number_str) != 5:
        return False

    digits = [int(d) for d in number_str]
    # Calculation: S = d1*2 + d2*3 + d3*4 + d4*5
    s = digits[0] * 2 + digits[1] * 3 + digits[2] * 4 + digits[3] * 5
    r = s % 11

    # The check digit is the remainder R.
    return r == digits[4]
