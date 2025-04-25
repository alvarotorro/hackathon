from typing import List, Dict
from datetime import datetime
from core.data_models import Ambassador, Shift, Ticket

class AvailabilityAgent:
    def __init__(self):
        self.available_ambassadors: Dict[str, Dict] = {}

    def check_availability(self, ticket: Ticket, ambassadors: List[Ambassador], shifts: List[Shift]) -> Dict[str, Dict]:
        """Check which ambassadors are available for the ticket based on their shifts."""
        current_time = datetime.now()
        self.available_ambassadors = {}

        for ambassador in ambassadors:
            # Check if ambassador has reached their ticket limit
            if ambassador.current_tickets >= ambassador.max_active_tickets:
                continue

            # Find ambassador's active shifts
            active_shifts = [
                shift for shift in shifts
                if shift.ambassador_id == ambassador.id
                and shift.is_active
                and shift.shift_start <= current_time.time() <= shift.shift_end
            ]

            if active_shifts:
                availability = {
                    'ambassador_id': ambassador.id,
                    'name': ambassador.name,
                    'current_tickets': ambassador.current_tickets,
                    'max_active_tickets': ambassador.max_active_tickets,
                    'active_shifts': active_shifts,
                    'is_available': True
                }
                self.available_ambassadors[ambassador.id] = availability

        return self.available_ambassadors

    def get_available_ambassadors(self) -> Dict[str, Dict]:
        """Return the list of available ambassadors."""
        return self.available_ambassadors

    def is_ambassador_available(self, ambassador_id: str) -> bool:
        """Check if a specific ambassador is available."""
        return ambassador_id in self.available_ambassadors and self.available_ambassadors[ambassador_id]['is_available']