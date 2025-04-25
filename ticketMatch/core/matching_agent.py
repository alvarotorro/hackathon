from typing import Tuple, Optional
from datetime import datetime
from ticketMatch.core.data_loader import DataLoader
from ticketMatch.core.ticket import Ticket
from ticketMatch.core.ambassador import Ambassador

class MatchingAgent:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.ambassadors = data_loader.load_ambassadors()
        self.tickets = data_loader.load_tickets()
        self.shifts = data_loader.load_shifts()

    def calculate_match_score(self, ticket: Ticket, ambassador: Ambassador) -> Tuple[float, str]:
        score = 0.0
        reasons = []

        # Language match (highest priority)
        if ticket.language.lower() in [lang.lower() for lang in ambassador.languages]:
            score += 0.3
            reasons.append("Language match")

        # Line of business match
        if ticket.line_of_business.lower() in [lob.lower() for lob in ambassador.lines_of_business]:
            score += 0.2
            reasons.append("Line of business match")

        # Product expertise match
        if ticket.primary_product.lower() in [product.lower() for product in ambassador.product_expertise]:
            score += 0.2
            reasons.append("Product expertise match")

        # Technical proficiency match
        if ticket.technical_proficiency.lower() == ambassador.technical_proficiency.lower():
            score += 0.15
            reasons.append("Technical proficiency match")

        # Urgency handling capability
        if ticket.urgency.lower() in [urgency.lower() for urgency in ambassador.urgency_handling]:
            score += 0.15
            reasons.append("Urgency handling capability")

        return score, ", ".join(reasons)

    def find_best_match(self, ticket: Ticket) -> Optional[Tuple[Ambassador, float, str]]:
        if ticket.assigned:
            return None

        best_match = None
        best_score = 0.0
        best_reasons = ""

        for ambassador in self.ambassadors:
            # Check if ambassador is available (has active shifts)
            is_available = any(
                shift.ambassador_id == ambassador.ambassador_id and 
                shift.start_time <= datetime.now() <= shift.end_time
                for shift in self.shifts
            )

            if not is_available:
                continue

            score, reasons = self.calculate_match_score(ticket, ambassador)
            
            if score > best_score:
                best_match = ambassador
                best_score = score
                best_reasons = reasons

        if best_match and best_score > 0:
            return best_match, best_score, best_reasons
        return None

    def assign_ticket(self, ticket: Ticket) -> Optional[Tuple[Ambassador, float, str]]:
        match = self.find_best_match(ticket)
        if match:
            ambassador, score, reasons = match
            ticket.assigned = True
            ticket.assignment_datetime = datetime.now()
            ticket.assigned_ambassador_id = ambassador.ambassador_id
            return ambassador, score, reasons
        return None 