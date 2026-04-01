from datetime import datetime

class TimeOfDay:
    def __init__(self):
        self.current_hour = datetime.now().hour

    def time_of_day(self) -> str:
        if 5 <= self.current_hour < 12:
            return "Good morning sir!"
        elif 12 <= self.current_hour < 17:
            return "Good afternoon sir!"
        elif 17 <= self.current_hour < 21:
            return "Good evening sir!"
        else:
            return "Good night sir!"
