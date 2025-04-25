from typing import Dict, List
from core.data_models import Ambassador, Ticket

class MatchingAgent:
    def __init__(self, ambassador_profiler, availability_agent):
        self.ambassador_profiler = ambassador_profiler
        self.availability_agent = availability_agent

    def match_ticket(self, ticket: Ticket, ambassador_profiles: List[Dict]) -> Dict:
        """Match ticket to best available ambassador using weighted scoring."""
        best_match = None
        best_score = 0.0
        matches = []

        ticket_dict = {
            'line_of_business': ticket.line_of_business,
            'language': ticket.language,
            'primary_product': ticket.primary_product,
            'urgency': ticket.urgency
        }

        for profile in ambassador_profiles:
            # Skip if ambassador is not available
            if not self.availability_agent.check_availability(profile["id"]):
                continue

            # Calculate component scores
            profile_score = self.ambassador_profiler.score_match(profile["id"], ticket_dict)
            availability_score = self.availability_agent.get_availability_score(profile["id"])
            expertise_score = self.ambassador_profiler.get_expertise_score(profile["id"], ticket.primary_product)

            # Calculate total score with weights
            total_score = (
                profile_score * 0.4 +          # 40% weight for profile match
                availability_score * 0.3 +     # 30% weight for availability
                expertise_score * 0.3          # 30% weight for product expertise
            )

            # Urgency boost
            if ticket.urgency.lower() == "high" and total_score > 0.7:
                total_score *= 1.2  # 20% boost for high urgency tickets

            matches.append({
                "ambassador": profile,
                "score": total_score,
                "profile_score": profile_score,
                "availability_score": availability_score,
                "expertise_score": expertise_score
            })

            if total_score > best_score:
                best_score = total_score
                best_match = profile

        if not best_match:
            return {
                "matched_ambassador": None,
                "score": 0.0,
                "reason": "No available ambassadors found",
                "matches": matches
            }

        # Generate detailed reason for the match
        reason_parts = []
        best_match_data = next(m for m in matches if m["ambassador"]["id"] == best_match["id"])
        
        if best_match_data["profile_score"] > 0.3:
            reason_parts.append(f"strong match for {ticket.line_of_business}")
        if best_match_data["availability_score"] > 0.5:
            reason_parts.append("immediately available")
        if best_match_data["expertise_score"] > 0.5:
            reason_parts.append(f"experienced with {ticket.primary_product}")
        
        reason = "Best match based on: " + ", ".join(reason_parts)

        return {
            "matched_ambassador": best_match,
            "score": best_score,
            "reason": reason,
            "matches": matches
        }