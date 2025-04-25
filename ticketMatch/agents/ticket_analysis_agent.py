from typing import List, Optional
from core.data_models import Ticket

class TicketAnalysisAgent:
    def __init__(self):
        self.unassigned_tickets: List[Ticket] = []

    def analyze_tickets(self, tickets: List[Ticket]) -> List[Ticket]:
        """Analyze all tickets and return unassigned ones."""
        self.unassigned_tickets = [ticket for ticket in tickets if not ticket.assigned]
        return self.unassigned_tickets

    def get_unassigned_tickets(self) -> List[Ticket]:
        """Return the list of unassigned tickets."""
        return self.unassigned_tickets

    def analyze_ticket(self, ticket_text: str) -> dict:
        prompt = [
            {"role": "system", "content": (
                "You are an assistant that extracts metadata from support tickets. "
                "Given a user message, return a JSON with: "
                "'topic' (the main issue area), 'urgency' (low/medium/high), "
                "and 'sentiment' (positive/neutral/negative)."
            )},
            {"role": "user", "content": f"Ticket: {ticket_text}"}
        ]

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=prompt,
            temperature=0.2,
            max_tokens=200
        )

        import json
        try:
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            return {
                "topic": "unknown",
                "urgency": "medium",
                "sentiment": "neutral",
                "error": f"Could not parse response: {str(e)}"
            }