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
import argparse

# Initialize colorama
init()

def print_step(step: str, message: str):
    print(f"\n{Fore.CYAN}[{step}]{Style.RESET_ALL} {message}")

def print_success(message: str):
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_warning(message: str):
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")

def print_error(message: str):
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def main(excel_file_path: str):
    print(f"\n{Fore.BLUE}🚀 Ticket Matchmaker - Azure AI Powered{Style.RESET_ALL}\n")

    try:
        # 1. Azure Connection
        print_step("AZURE", "Initializing Azure AI connection...")
        azure_connection = AzureConnection()
        print_success("Azure connection established")

        # 2. Load Excel
        print_step("DATA", f"Loading data from {excel_file_path} ...")
        data_loader = DataLoader(excel_file_path)
        tickets, ambassadors, shifts = data_loader.load_data()

        # Filter only unassigned ones
        unassigned_tickets = [ticket for ticket in tickets if not ticket.assigned]
        print_success(f"Loaded {len(unassigned_tickets)} unassigned tickets out of {len(tickets)} total")

        print("\nExamples:")
        for ticket in unassigned_tickets[:3]:
            print(f"  - Case {ticket.case_number}: {ticket.line_of_business}, {ticket.primary_product}")

        # 3. Initialize agents
        print_step("AGENTS", "Initializing agents...")
        ticket_agent = TicketAnalysisAgent()
        ambassador_agent = AmbassadorProfilingAgent()
        availability_agent = AvailabilityAgent()
        matching_agent = MatchingAgent(azure_connection)
        print_success("Agents ready")

        # 4. Process tickets
        print_step("PROCESSING", f"Processing {len(unassigned_tickets)} tickets...")
        unassigned_tickets = ticket_agent.analyze_tickets(tickets)
        ambassador_profiles = ambassador_agent.analyze_conversation_history(ambassadors)
        results = []

        for ticket in unassigned_tickets:
            print(f"\n{Fore.MAGENTA}📋 Processing Ticket {ticket.case_number}{Style.RESET_ALL}")
            available_ambassadors = availability_agent.check_availability(ticket, ambassadors, shifts)

            if not available_ambassadors:
                print_warning(f"No ambassadors available for ticket {ticket.case_number}")
                results.append({
                    'ticket_id': ticket.case_number,
                    'assigned_ambassador': None,
                    'matching_reason': 'No available ambassadors',
                    'status': 'Unassigned'
                })
                continue

            # Convert dictionary to list of Ambassador objects
            available_ids = list(available_ambassadors.keys())
            available_objects = [a for a in ambassadors if a.id in available_ids]

            # Azure Matching
            print_step("MATCHING", "Finding best match with Azure AI...")
            match_result = matching_agent.process_ticket_with_azure(ticket, available_objects)

            if match_result:
                ambassador_id, explanation, confidence = match_result
                ambassador = next((a for a in ambassadors if a.id == ambassador_id), None)
                ambassador_name = ambassador.name if ambassador else ambassador_id
                print_success(f"Match: {ambassador_name} (Confidence: {confidence:.2f})")
                print(f"  {Fore.CYAN}Reason:{Style.RESET_ALL} {explanation}")

                results.append({
                    'ticket_id': ticket.case_number,
                    'assigned_ambassador': ambassador_name,
                    'matching_reason': explanation,
                    'confidence_score': confidence,
                    'status': 'Assigned'
                })
            else:
                print_warning(f"No match found for ticket {ticket.case_number}")
                results.append({
                    'ticket_id': ticket.case_number,
                    'assigned_ambassador': None,
                    'matching_reason': "No suitable match",
                    'confidence_score': 0.0,
                    'status': 'Unassigned'
                })

        # 5. Save results
        print_step("SAVING", "Saving results to Excel...")
        try:
            os.makedirs("output", exist_ok=True)
            df = pd.DataFrame(results)
            df.to_excel("output/assigned_tickets.xlsx", index=False)
            print_success("Results saved to output/assigned_tickets.xlsx")

            with open("output/assignment_details.json", "w") as f:
                json.dump(results, f, indent=2)
            print_success("Detailed results saved to assignment_details.json")

        except Exception as e:
            print_error(f"Error saving results: {str(e)}")

        print_success("\nAll tickets processed successfully.")

    except Exception as e:
        print_error(f"General error: {str(e)}")

# CLI Argument
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ticket Matcher")
    parser.add_argument("excel_file", type=str, help="Path to input Excel file")
    args = parser.parse_args()
    main(args.excel_file)
