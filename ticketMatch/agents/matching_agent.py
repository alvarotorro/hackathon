class MatchingAgent:
    def __init__(self):
        pass

    def match_ticket(self, ticket_info: dict, ambassador_profiles: list) -> dict:
        # Placeholder: Select ambassador with "Teams" skill
        for profile in ambassador_profiles:
            if "Teams" in profile.get("skills", []):
                return {
                    "matched_ambassador": profile["id"],
                    "score": 0.95,
                    "reason": "Strong skill match on topic 'Teams'"
                }
        return {
            "matched_ambassador": None,
            "score": 0,
            "reason": "No suitable ambassador found"
        }