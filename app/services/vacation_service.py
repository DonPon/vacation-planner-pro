import holidays
from datetime import date, timedelta

class HolidayService:
    @staticmethod
    def get_holidays(country: str, subdivision: str = None, year: int = 2026):
        try:
            h = holidays.country_holidays(country, subdiv=subdivision, years=year)
            return h
        except Exception:
            # Fallback to empty if country not found
            return {}

    @staticmethod
    def is_holiday(dt: date, country: str, subdivision: str = None):
        h = HolidayService.get_holidays(country, subdivision, dt.year)
        return dt in h

class VacationService:
    @staticmethod
    def calculate_business_days(start: date, end: date, country: str, subdivision: str = None, working_days_per_week: int = 5):
        """
        Calculates business days between start and end (inclusive),
        excluding weekends and public holidays.
        """
        if start > end:
            return 0
        
        h = HolidayService.get_holidays(country, subdivision, start.year)
        # If the range spans across years, we might need more years, but for MVP let's assume same year or handle carefully
        if end.year != start.year:
            h.update(HolidayService.get_holidays(country, subdivision, end.year))
            
        count = 0
        curr = start
        while curr <= end:
            # Weekday: 0=Mon, 1=Tue, ..., 5=Sat, 6=Sun
            # If working_days_per_week is 5, we assume Mon-Fri are working days.
            # If 6, we assume Mon-Sat.
            is_weekend = False
            if working_days_per_week == 5:
                if curr.weekday() >= 5: # Sat, Sun
                    is_weekend = True
            elif working_days_per_week == 6:
                if curr.weekday() == 6: # Sun
                    is_weekend = True
            
            if not is_weekend and curr not in h:
                count += 1
            curr += timedelta(days=1)
            
        return count
