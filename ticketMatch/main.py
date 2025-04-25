from core.azure_connection import AzureConnection
from core.data_loader import DataLoader
from agents.ticket_analysis_agent import TicketAnalysisAgent
from agents.ambassador_profiling_agent import AmbassadorProfilingAgent
from agents.availability_agent import AvailabilityAgent
from agents.matching_agent import MatchingAgent
from core.data_models import Ticket, Ambassador, Shift
from datetime import datetime
import os
from colorama import init, Fore, Style

# Initialize colorama
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

def print_error(message: str):
    """Print error message in red."""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def main():
    print(f"\n{Fore.BLUE}🚀 Ticket Matchmaker - Multi-Agent System{Style.RESET_ALL}\n")

    try:
        # 1. Load data from Excel
        print_step("DATA", "Loading data from Excel...")
        data_loader = DataLoader("data/mock_data.xlsx")
        tickets, ambassadors, shifts = data_loader.load_data()
        print_success(f"Loaded {len(tickets)} tickets, {len(ambassadors)} ambassadors, and {len(shifts)} shifts")

        # 2. Initialize Azure OpenAI
        print_step("CONNECTION", "Initializing Azure OpenAI...")
        connection = AzureConnection()
        if not connection.initialize():
            print_error("Failed to connect to Azure OpenAI")
            return
        client = connection.get_client()
        print_success("Connected to Azure OpenAI")

        # 3. Initialize Agents
        print_step("AGENTS", "Initializing agents...")
        ticket_agent = TicketAnalysisAgent(client)
        ambassador_agent = AmbassadorProfilingAgent(ambassadors)
        availability_agent = AvailabilityAgent(ambassadors, shifts)
        matching_agent = MatchingAgent(ambassador_agent, availability_agent)
        print_success("All agents initialized")

        # 4. Process tickets
        print_step("PROCESSING", f"Processing {len(tickets)} tickets...")
        for ticket in tickets:
            print(f"\n{Fore.MAGENTA}📋 Processing Ticket {ticket.id}{Style.RESET_ALL}")
            
            # Analyze ticket
            print_step("ANALYSIS", f"Analyzing ticket: {ticket.text[:50]}...")
            ticket_info = ticket_agent.analyze_ticket(ticket.text)
            print_success(f"Topic: {ticket_info['topic']} | Urgency: {ticket_info['urgency']}")

            # Get available ambassadors
            available_ambassadors = []
            for ambassador in ambassadors:
                if availability_agent.check_availability(ambassador.id):
                    profile = ambassador_agent.get_profile(ambassador.id)
                    available_ambassadors.append(profile)
                    print_success(f"Ambassador {ambassador.id} available (Skills: {', '.join(profile['skills'])})")

            # Match ticket
            print_step("MATCHING", "Finding best match...")
            result = matching_agent.match_ticket(ticket_info, available_ambassadors)
            
            if result["matched_ambassador"]:
                print_success(f"Matched to Ambassador {result['matched_ambassador']['id']} (Score: {result['score']:.2f})")
                print(f"Reason: {result['reason']}")
            else:
                print_warning("No suitable ambassador found")
                print(f"Details: {result['reason']}")

        print_success("\nAll tickets processed successfully!")

    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        return

if __name__ == "__main__":
    main()