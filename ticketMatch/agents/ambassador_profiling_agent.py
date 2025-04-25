from typing import Dict, List
from core.data_models import Ambassador

class AmbassadorProfilingAgent:
    def __init__(self, ambassadors: List[Ambassador]):
        self.ambassadors = {a.id: a for a in ambassadors}

    def get_profile(self, ambassador_id: str) -> Dict:
        """Get ambassador profile with scoring."""
        ambassador = self.ambassadors.get(ambassador_id)
        if not ambassador:
            raise ValueError(f"Ambassador {ambassador_id} not found")

        return {
            "id": ambassador.id,
            "name": ambassador.name,
            "line_of_business": ambassador.line_of_business,
            "languages": ambassador.languages,
            "csat_score": ambassador.csat_score,
            "case_history": ambassador.case_history,
            "current_tickets": ambassador.current_tickets,
            "max_active_tickets": ambassador.max_active_tickets
        }

    def score_match(self, ambassador_id: str, ticket: Dict) -> float:
        """Score how well an ambassador matches a ticket."""
        ambassador = self.ambassadors.get(ambassador_id)
        if not ambassador:
            return 0.0

        # Line of Business match (0-0.4)
        lob_score = 0.4 if ticket['line_of_business'] in ambassador.line_of_business else 0.0

        # Language match (0-0.3)
        language_score = 0.3 if ticket['language'] in ambassador.languages else 0.0

        # CSAT score normalized to 0-0.3 range
        csat_score = (ambassador.csat_score / 5.0) * 0.3

        # Calculate total score
        total_score = lob_score + language_score + csat_score

        return total_score

    def get_expertise_score(self, ambassador_id: str, product: str) -> float:
        """Calculate expertise score based on case history."""
        ambassador = self.ambassadors.get(ambassador_id)
        if not ambassador or not ambassador.case_history:
            return 0.0

        # Count cases related to the product
        product_cases = sum(1 for case in ambassador.case_history if product.lower() in case.lower())
        
        # Normalize score (0-1)
        expertise_score = min(1.0, product_cases / 10)  # Cap at 10 cases
        
        return expertise_score