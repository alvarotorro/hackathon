#holaaafrom core.azure_connection import AzureConnection
from agents.ticket_analysis_agent import TicketAnalysisAgent
from agents.ambassador_profiling_agent import AmbassadorProfilingAgent
from agents.availability_agent import AvailabilityAgent
from agents.matching_agent import MatchingAgent

def main():
    print("🚀 Ticket Matchmaker - Multi-Agent System Starting...\n")

    # 1. Initialize Azure OpenAI
    connection = AzureConnection()
    if not connection.initialize():
        print("❌ Failed to connect to Azure OpenAI.")
        return

    client = connection.get_client()

    # 2. Initialize Agents
    ticket_agent = TicketAnalysisAgent(client)
    ambassador_agent = AmbassadorProfilingAgent(ambassador_data={})  # Replace with actual data
    availability_agent = AvailabilityAgent(schedule_data={})         # Replace with actual data
    matching_agent = MatchingAgent()

    # 3. Mock ticket input
    ticket = {
        "id": "TICKET-001",
        "text": "Teams is crashing every time I try to share my screen. Please help!"
    }
    print(f"[Ticket Received] {ticket['id']}: {ticket['text']}")

    # 4. Analyze ticket
    ticket_info = ticket_agent.analyze_ticket(ticket["text"])
    print(f"[Ticket Analysis] → Topic: {ticket_info['topic']} | Urgency: {ticket_info['urgency']} | Sentiment: {ticket_info['sentiment']}")

    # 5. Get mock ambassador profiles
    ambassador_ids = ["ambassador_1", "ambassador_2"]
    ambassador_profiles = []

    for aid in ambassador_ids:
        profile = ambassador_agent.get_profile(aid)
        if availability_agent.check_availability(aid):
            ambassador_profiles.append(profile)
            print(f"[Ambassador Available] {aid} → Skills: {profile['skills']} | CSAT: {profile['csat_score']}")
        else:
            print(f"[Ambassador Unavailable] {aid}")

    # 6. Match ticket
    result = matching_agent.match_ticket(ticket_info, ambassador_profiles)
    print(f"[Matching Result] → Matched Ambassador: {result['matched_ambassador']} | Score: {result['score']} | Reason: {result['reason']}")

    print("\n✅ Flow completed.")

if __name__ == "__main__":
    main()