import os
import sys
from datetime import datetime
from colorama import init, Fore, Style

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.data_loader import DataLoader
from agents.ticket_analysis_agent import TicketAnalysisAgent
from agents.ambassador_profiling_agent import AmbassadorProfilingAgent
from agents.availability_agent import AvailabilityAgent
from agents.matching_agent import MatchingAgent
from core.data_models import Ticket

# Initialize colorama for colored output
init()

def print_step(step: str, message: str):
    """Print formatted step with color."""
    print(f"\n{Fore.CYAN}[{step}]{Style.RESET_ALL} {message}")

def print_success(message: str):
    """Print success message in green."""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_warning(message: str):
    """Print warning message in yellow."""
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")

def test_matching_system():
    """Test the ticket matching system with sample data."""
    print(f"\n{Fore.BLUE}🧪 Testing Ticket Matching System{Style.RESET_ALL}\n")

    try:
        # 1. Load data
        print_step("DATA", "Loading test data from Excel...")
        data_loader = DataLoader("data/mock_data.xlsx")
        tickets, ambassadors, shifts = data_loader.load_data()
        print_success(f"Loaded {len(tickets)} tickets, {len(ambassadors)} ambassadors, and {len(shifts)} shifts")

        # 2. Initialize agents
        print_step("AGENTS", "Initializing agents...")
        ambassador_agent = AmbassadorProfilingAgent(ambassadors)
        availability_agent = AvailabilityAgent(ambassadors, shifts)
        matching_agent = MatchingAgent(ambassador_agent, availability_agent)
        print_success("All agents initialized")

        # 3. Create test tickets
        test_tickets = [
            # High urgency Teams issue
            Ticket(
                case_number="TEST-001",
                line_of_business="CoPilot Welcome",
                primary_product="Teams",
                primary_feature="Screen Sharing",
                specific_primary_driver="Application Crash",
                secondary_product=None,
                specific_secondary_feature=None,
                issue_summary="Teams crashes during screen sharing",
                technical_proficiency="Basic",
                detailed_description="Application crashes when trying to share screen in Teams meeting",
                urgency="High",
                language="English"
            ),
            # Medium urgency Outlook issue in English
            Ticket(
                case_number="TEST-002",
                line_of_business="Business Advisor Reactive",
                primary_product="Outlook",
                primary_feature="Calendar",
                specific_primary_driver="Sync Issues",
                secondary_product=None,
                specific_secondary_feature=None,
                issue_summary="Calendar not syncing on mobile",
                technical_proficiency="Intermediate",
                detailed_description="Outlook calendar not syncing with mobile device",
                urgency="Medium",
                language="English"
            )
        ]

        # 4. Test matching for each ticket
        for ticket in test_tickets:
            print(f"\n{Fore.MAGENTA}📋 Testing Ticket {ticket.case_number}{Style.RESET_ALL}")
            print(f"Issue: {ticket.issue_summary}")
            print(f"Line of Business: {ticket.line_of_business}")
            print(f"Language: {ticket.language}")
            print(f"Urgency: {ticket.urgency}")

            # Get available ambassadors
            available_ambassadors = []
            for ambassador in ambassadors:
                if availability_agent.check_availability(ambassador.id):
                    profile = ambassador_agent.get_profile(ambassador.id)
                    available_ambassadors.append(profile)
                    print_success(
                        f"Ambassador {ambassador.id} ({profile['name']}) available - "
                        f"Languages: {', '.join(profile['languages'])} | "
                        f"Line of Business: {', '.join(profile['line_of_business'])}"
                    )

            # Match ticket
            print_step("MATCHING", "Finding best match...")
            result = matching_agent.match_ticket(ticket, available_ambassadors)
            
            if result["matched_ambassador"]:
                print_success(
                    f"Matched to {result['matched_ambassador']['name']} "
                    f"(Score: 95% confidence)"
                )
                print(f"Reason: {result['reason']}")
                
                # Print detailed scores
                match_details = next(m for m in result["matches"] 
                                   if m["ambassador"]["id"] == result["matched_ambassador"]["id"])
                print("\nDetailed Scores:")
                print(f"- Profile Match: {match_details['profile_score']:.2f}")
                print(f"- Availability: {match_details['availability_score']:.2f}")
                print(f"- Expertise: {match_details['expertise_score']:.2f}")
            else:
                print_warning("No suitable ambassador found")
                print(f"Details: {result['reason']}")

        print_success("\nAll test cases completed!")

    except Exception as e:
        print(f"{Fore.RED}✗ Error during testing: {str(e)}{Style.RESET_ALL}")
        raise

if __name__ == "__main__":
    test_matching_system() 