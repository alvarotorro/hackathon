from typing import Dict, List, Optional
from core.data_models import Ambassador

class AmbassadorProfilingAgent:
    def __init__(self):
        self.ambassador_profiles: Dict[str, Dict] = {}

    def analyze_conversation_history(self, ambassadors: List[Ambassador]) -> Dict[str, Dict]:
        """Analyze conversation history and create profiles for each ambassador."""
        for ambassador in ambassadors:
            profile = {
                'id': ambassador.id,
                'name': ambassador.name,
                'languages': ambassador.languages,
                'line_of_business': ambassador.line_of_business,
                'csat_score': ambassador.csat_score,
                'current_tickets': ambassador.current_tickets,
                'max_active_tickets': ambassador.max_active_tickets,
                'performance_metrics': self._calculate_performance_metrics(ambassador)
            }
            self.ambassador_profiles[ambassador.id] = profile
        return self.ambassador_profiles

    def _calculate_performance_metrics(self, ambassador: Ambassador) -> Dict:
        """Calculate performance metrics based on conversation history."""
        return {
            'average_resolution_time': self._calculate_average_resolution_time(ambassador),
            'success_rate': self._calculate_success_rate(ambassador),
            'customer_satisfaction': ambassador.csat_score
        }

    def _calculate_average_resolution_time(self, ambassador: Ambassador) -> float:
        """Calculate average resolution time from case history."""
        # Implementation would depend on actual case history data structure
        return 0.0  # Placeholder

    def _calculate_success_rate(self, ambassador: Ambassador) -> float:
        """Calculate success rate from case history."""
        # Implementation would depend on actual case history data structure
        return 0.0  # Placeholder

    def get_ambassador_profile(self, ambassador_id: str) -> Optional[Dict]:
        """Get the profile for a specific ambassador."""
        return self.ambassador_profiles.get(ambassador_id)

    def get_profile(self, ambassador_id: str) -> Dict:
        """Get ambassador profile with scoring."""
        ambassador = self.ambassador_profiles.get(ambassador_id)
        if not ambassador:
            raise ValueError(f"Ambassador {ambassador_id} not found")

        return {
            "id": ambassador.get('id'),
            "name": ambassador.get('name'),
            "line_of_business": ambassador.get('line_of_business'),
            "languages": ambassador.get('languages'),
            "csat_score": ambassador.get('csat_score'),
            "case_history": ambassador.get('case_history'),
            "current_tickets": ambassador.get('current_tickets'),
            "max_active_tickets": ambassador.get('max_active_tickets'),
            "performance_metrics": ambassador.get('performance_metrics')
        }

    def score_match(self, ambassador_id: str, ticket: Dict) -> float:
        """Score how well an ambassador matches a ticket."""
        ambassador = self.ambassador_profiles.get(ambassador_id)
        if not ambassador:
            return 0.0

        # Line of Business match (0-0.4)
        lob_score = 0.4 if ticket['line_of_business'] in ambassador.get('line_of_business', []) else 0.0

        # Language match (0-0.3)
        language_score = 0.3 if ticket['language'] in ambassador.get('languages', []) else 0.0

        # CSAT score normalized to 0-0.3 range
        csat_score = (ambassador.get('csat_score', 0) / 5.0) * 0.3

        # Calculate total score
        total_score = lob_score + language_score + csat_score

        return total_score

    def get_expertise_score(self, ambassador_id: str, product: str) -> float:
        """Calculate expertise score based on case history."""
        ambassador = self.ambassador_profiles.get(ambassador_id)
        if not ambassador or not ambassador.get('case_history'):
            return 0.0

        # Count cases related to the product
        product_cases = sum(1 for case in ambassador.get('case_history', []) if product.lower() in case.lower())
        
        # Normalize score (0-1)
        expertise_score = min(1.0, product_cases / 10)  # Cap at 10 cases
        
        return expertise_score