from typing import Dict, List, Optional, Tuple
from core.data_models import Ticket, Ambassador, Shift
from agents.ticket_analysis_agent import TicketAnalysisAgent
from agents.ambassador_profiling_agent import AmbassadorProfilingAgent
from agents.availability_agent import AvailabilityAgent

class MatchingAgent:
    def __init__(self):
        self.ticket_agent = TicketAnalysisAgent()
        self.profiling_agent = AmbassadorProfilingAgent()
        self.availability_agent = AvailabilityAgent()
        self.assigned_tickets: Dict[str, Tuple[str, str]] = {}  # ticket_id -> (ambassador_id, explanation)

    def process_tickets(self, tickets: List[Ticket], ambassadors: List[Ambassador], shifts: List[Shift]) -> Dict[str, Tuple[str, str]]:
        """Process all tickets and make assignment decisions.
        Returns a dict of ticket_id -> (ambassador_id, explanation)"""
        # Analyze tickets (they are already filtered for unassigned only)
        unassigned_tickets = self.ticket_agent.analyze_tickets(tickets)
        
        # Get ambassador profiles
        ambassador_profiles = self.profiling_agent.analyze_conversation_history(ambassadors)

        for ticket in unassigned_tickets:
            # Get available ambassadors
            available_ambassadors = self.availability_agent.check_availability(ticket, ambassadors, shifts)
            
            if not available_ambassadors:
                self.assigned_tickets[ticket.case_number] = (None, "No available ambassadors")
                continue

            # Find best match
            best_match, explanation = self._find_best_match(ticket, available_ambassadors, ambassador_profiles)
            
            if best_match:
                self._assign_ticket(ticket, best_match)
                self.assigned_tickets[ticket.case_number] = (best_match, explanation)
            else:
                self.assigned_tickets[ticket.case_number] = (None, explanation)

        return self.assigned_tickets

    def _find_best_match(self, ticket: Ticket, available_ambassadors: Dict[str, Dict], 
                        ambassador_profiles: Dict[str, Dict]) -> Tuple[Optional[str], str]:
        """Find the best matching ambassador for a ticket.
        Returns a tuple of (ambassador_id, explanation)"""
        best_score = 0.0
        best_ambassador_id = None
        best_explanation = "No suitable match found"

        for ambassador_id, availability in available_ambassadors.items():
            if not availability['is_available']:
                continue

            profile = ambassador_profiles.get(ambassador_id)
            if not profile:
                continue

            # Calculate match score and get explanation
            score, explanation = self._calculate_match_score(ticket, profile)
            
            if score > best_score:
                best_score = score
                best_ambassador_id = ambassador_id
                best_explanation = f"Match score: {score:.2%} - {explanation}"

        return best_ambassador_id, best_explanation

    def _calculate_match_score(self, ticket: Ticket, profile: Dict) -> Tuple[float, str]:
        """Calculate a match score between ticket and ambassador profile.
        Returns a tuple of (score, explanation)"""
        score = 0.0
        explanations = []

        # Language match (30%)
        if ticket.language in profile['languages']:
            score += 0.3
            explanations.append(f"Language match: {ticket.language}")
        else:
            explanations.append(f"Language mismatch: {ticket.language} not in {profile['languages']}")

        # Line of business match (25%)
        if ticket.line_of_business in profile['line_of_business']:
            score += 0.25
            explanations.append(f"Line of business match: {ticket.line_of_business}")
        else:
            explanations.append(f"Line of business mismatch: {ticket.line_of_business} not in {profile['line_of_business']}")

        # Technical proficiency match (20%)
        if ticket.technical_proficiency.lower() in ['expert', 'advanced']:
            # Prefer ambassadors with high CSAT for complex tickets
            performance = profile['performance_metrics']
            score += 0.2 * (performance['customer_satisfaction'] / 5.0)
            explanations.append(f"Technical ticket matched with high CSAT ambassador ({performance['customer_satisfaction']}/5)")
        else:
            # For basic tickets, consider workload more
            workload_ratio = profile['current_tickets'] / profile['max_active_tickets']
            score += 0.2 * (1 - workload_ratio)
            explanations.append(f"Basic ticket matched with available ambassador (workload: {workload_ratio:.2%})")

        # Urgency handling (15%)
        if ticket.urgency.lower() == 'high':
            # For high urgency, prioritize success rate
            score += 0.15 * profile['performance_metrics']['success_rate']
            explanations.append(f"High urgency matched with high success rate ({profile['performance_metrics']['success_rate']:.2%})")
        else:
            # For normal urgency, consider balanced workload
            workload_ratio = profile['current_tickets'] / profile['max_active_tickets']
            score += 0.15 * (1 - workload_ratio)
            explanations.append(f"Normal urgency matched with balanced workload ({workload_ratio:.2%})")

        # Past experience (10%)
        if ticket.primary_product in profile.get('past_products', []):
            score += 0.1
            explanations.append(f"Past experience with product: {ticket.primary_product}")

        return score, " | ".join(explanations)

    def _assign_ticket(self, ticket: Ticket, ambassador_id: str):
        """Assign a ticket to an ambassador."""
        ticket.assigned = True
        ticket.assigned_ambassador_id = ambassador_id