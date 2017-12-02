# represents user's context
import datetime

class UserContext:
    def __init__(self, user_id:int):
        self.user_id = user_id
        self.selected_month = datetime.date.today().month
        self.selected_year = datetime.date.today().year
        self.last_calendar_message = None
        self.selected_doctor = None
