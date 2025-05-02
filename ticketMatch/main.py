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
import json

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
    print(f"\n{Fore.BLUE}🚀 Ticket Matchmaker - Azure AI Powered{Style.RESET_ALL}\n")

    try:
        # 1. Initialize Azure Connection
        print_step("AZURE", "Initializing Azure AI connection...")
        azure_connection = AzureConnection()
        print_success("Azure connection established")

        # 2. Load data from Excel
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

        # 3. Initialize Agents
        print_step("AGENTS", "Initializing agents...")
        ticket_agent = TicketAnalysisAgent()
        ambassador_agent = AmbassadorProfilingAgent()
        availability_agent = AvailabilityAgent()
        matching_agent = MatchingAgent(azure_connection)
        print_success("All agents initialized")

        # 4. Process tickets
        print_step("PROCESSING", f"Processing {len(unassigned_tickets)} unassigned tickets...")
        
        # Get unassigned tickets
        unassigned_tickets = ticket_agent.analyze_tickets(tickets)
        print_success(f"Found {len(unassigned_tickets)} unassigned tickets")

        # Get ambassador profiles
        ambassador_profiles = ambassador_agent.analyze_conversation_history(ambassadors)
        print_success(f"Analyzed profiles for {len(ambassador_profiles)} ambassadors")

        # Prepare results DataFrame
        results = []
        
        # Process each unassigned ticket
        for ticket in unassigned_tickets:
            print(f"\n{Fore.MAGENTA}📋 Processing Ticket {ticket.case_number}{Style.RESET_ALL}")
            
            # Get available ambassadors
            available_ambassadors = availability_agent.check_availability(ticket, ambassadors, shifts)
            
            if not available_ambassadors:
                print_warning(f"No available ambassadors for ticket {ticket.case_number}")
                results.append({
                    'ticket_id': ticket.case_number,
                    'assigned_ambassador': None,
                    'matching_reason': 'No available ambassadors',
                    'status': 'Unassigned'
                })
                continue

            # Match ticket using Azure AI
            print_step("MATCHING", "Finding best match using Azure AI...")
            match_result = matching_agent.process_ticket_with_azure(ticket, available_ambassadors)
            
            if match_result:
                ambassador_id, explanation, confidence = match_result
                if ambassador_id:
                    # Find ambassador name
                    ambassador = next((a for a in ambassadors if a.id == ambassador_id), None)
                    ambassador_name = ambassador.name if ambassador else ambassador_id
                    print_success(f"Matched to Ambassador {ambassador_name} (Confidence: {confidence:.2f})")
                    print(f"  {Fore.CYAN}Reason:{Style.RESET_ALL} {explanation}")
                    
                    results.append({
                        'ticket_id': ticket.case_number,
                        'assigned_ambassador': ambassador_name,
                        'matching_reason': explanation,
                        'confidence_score': confidence,
                        'status': 'Assigned'
                    })
                else:
                    print_warning(f"No suitable match found: {explanation}")
                    results.append({
                        'ticket_id': ticket.case_number,
                        'assigned_ambassador': None,
                        'matching_reason': explanation,
                        'confidence_score': 0.0,
                        'status': 'Unassigned'
                    })

        # Save results to Excel
        print_step("SAVING", "Saving assignment results to Excel...")
        try:
            # Create output directory if it doesn't exist
            os.makedirs("output", exist_ok=True)
            
            # Convert results to DataFrame
            results_df = pd.DataFrame(results)
            
            # Save to Excel
            output_path = "output/assigned_tickets.xlsx"
            results_df.to_excel(output_path, index=False)
            
            print_success(f"Results saved to {output_path}")
            
            # Also save detailed results as JSON for debugging
            with open("output/assignment_details.json", "w") as f:
                json.dump(results, f, indent=2)
            
            print_success("Detailed results saved to assignment_details.json")
            
        except Exception as e:
            print_error(f"Error saving results: {str(e)}")

        print_success("\nAll tickets processed successfully!")

    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        return


import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ticket Matcher")
    parser.add_argument("excel_file", type=str, help="Ruta al archivo Excel de entrada")
    args = parser.parse_args()
    excel_file_path = args.excel_file

    main()