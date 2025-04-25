from datetime import datetime, time
from typing import List
from core.data_models import Ambassador, Shift

class AvailabilityAgent:
    def __init__(self, ambassadors: List[Ambassador], shifts: List[Shift]):
        self.ambassadors = {a.id: a for a in ambassadors}
        self.shifts = {s.ambassador_id: s for s in shifts}

    def check_availability(self, ambassador_id: str) -> bool:
        """Check if ambassador is currently available based on shift and ticket load."""
        ambassador = self.ambassadors.get(ambassador_id)
        shift = self.shifts.get(ambassador_id)
        
        if not ambassador or not shift:
            return False

        # Check if ambassador has reached max ticket limit
        if ambassador.current_tickets >= ambassador.max_active_tickets:
            return False

        # Check if current time is within shift hours
        current_time = datetime.now().time()
        if not (shift.shift_start <= current_time <= shift.shift_end):
            return False

        # Check if today is a working day
        current_day = datetime.now().strftime("%a")
        working_days = shift.working_days.lower()
        
        if "mon to fri" in working_days and current_day in ["Sat", "Sun"]:
            return False

        return True

    def get_availability_score(self, ambassador_id: str) -> float:
        """Calculate availability score based on current ticket load and shift timing."""
        ambassador = self.ambassadors.get(ambassador_id)
        if not ambassador:
            return 0.0

        # Base score on current ticket load (0.0 to 0.6)
        ticket_ratio = ambassador.current_tickets / ambassador.max_active_tickets
        load_score = 0.6 * (1 - ticket_ratio)

        # Add shift timing score (0.0 to 0.4)
        if self.check_availability(ambassador_id):
            timing_score = 0.4
        else:
            # If ambassador will be available soon (within next hour), give partial score
            timing_score = 0.2
        
        return load_score + timing_score