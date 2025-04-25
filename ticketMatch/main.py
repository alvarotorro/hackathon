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
import pandas as pd

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
        
        # Filter only unassigned tickets
        unassigned_tickets = [ticket for ticket in tickets if not ticket.assigned]
        print_success(f"Loaded {len(unassigned_tickets)} unassigned tickets out of {len(tickets)} total tickets")
        
        # Debug: Print some ticket details
        print("\nSample of unassigned tickets:")
        for ticket in unassigned_tickets[:3]:  # Show first 3 unassigned tickets
            print(f"  - Case {ticket.case_number}: {ticket.line_of_business}, {ticket.primary_product}")

        # 2. Initialize Agents
        print_step("AGENTS", "Initializing agents...")
        ticket_agent = TicketAnalysisAgent()
        ambassador_agent = AmbassadorProfilingAgent()
        availability_agent = AvailabilityAgent()
        matching_agent = MatchingAgent()
        print_success("All agents initialized")

        # 3. Process tickets
        print_step("PROCESSING", f"Processing {len(unassigned_tickets)} unassigned tickets...")
        
        # Get unassigned tickets
        unassigned_tickets = ticket_agent.analyze_tickets(tickets)
        print_success(f"Found {len(unassigned_tickets)} unassigned tickets")

        # Get ambassador profiles
        ambassador_profiles = ambassador_agent.analyze_conversation_history(ambassadors)
        print_success(f"Analyzed profiles for {len(ambassador_profiles)} ambassadors")

        # Process each unassigned ticket
        for ticket in unassigned_tickets:
            print(f"\n{Fore.MAGENTA}📋 Processing Ticket {ticket.case_number}{Style.RESET_ALL}")
            
            # Get available ambassadors
            available_ambassadors = availability_agent.check_availability(ticket, ambassadors, shifts)
            
            if not available_ambassadors:
                print_warning(f"No available ambassadors for ticket {ticket.case_number}")
                continue

            # Match ticket
            print_step("MATCHING", "Finding best match...")
            assigned_tickets = matching_agent.process_tickets([ticket], ambassadors, shifts)
            
            if ticket.case_number in assigned_tickets:
                ambassador_id, explanation = assigned_tickets[ticket.case_number]
                if ambassador_id:
                    # Find ambassador name
                    ambassador = next((a for a in ambassadors if a.id == ambassador_id), None)
                    ambassador_name = ambassador.name if ambassador else ambassador_id
                    print_success(f"Matched to Ambassador {ambassador_name}")
                    print(f"  {Fore.CYAN}Reason:{Style.RESET_ALL} {explanation}")
                else:
                    print_warning(f"No suitable match found: {explanation}")

        # Save results to Excel
        print_step("SAVING", "Saving assignment results to Excel...")
        try:
            # Read the original Excel file
            df = pd.read_excel("data/mock_data.xlsx", sheet_name='Tickets')
            
            # Update the assigned column and ambassador column
            for ticket_id, (ambassador_id, _) in matching_agent.assigned_tickets.items():
                if ambassador_id:
                    # Find ambassador name
                    ambassador = next((a for a in ambassadors if a.id == ambassador_id), None)
                    ambassador_name = ambassador.name if ambassador else ambassador_id
                    
                    # Update the row
                    mask = df['Case Number'] == ticket_id
                    df.loc[mask, 'assigned'] = True
                    df.loc[mask, 'ambassador'] = ambassador_name
            
            # Save back to Excel
            with pd.ExcelWriter("data/mock_data.xlsx", engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name='Tickets', index=False)
            
            print_success("Results saved to Excel successfully!")
        except Exception as e:
            print_error(f"Error saving to Excel: {str(e)}")

        print_success("\nAll tickets processed successfully!")

    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        return

if __name__ == "__main__":
    main()