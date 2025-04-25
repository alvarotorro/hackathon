import pandas as pd
from datetime import datetime, time
from typing import List, Tuple
from .data_models import Ticket, Ambassador, Shift

class DataLoader:
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.tickets_df = None
        self.ambassadors_df = None
        self.shifts_df = None

    def load_data(self) -> Tuple[List[Ticket], List[Ambassador], List[Shift]]:
        """Load and parse data from Excel file."""
        try:
            # Read Excel sheets
            self.tickets_df = pd.read_excel(self.excel_path, sheet_name='Tickets')
            self.ambassadors_df = pd.read_excel(self.excel_path, sheet_name='Ambassador History')
            self.shifts_df = pd.read_excel(self.excel_path, sheet_name='Shift Schedule')

            # Convert to data models
            tickets = self._parse_tickets()
            ambassadors = self._parse_ambassadors()
            shifts = self._parse_shifts()

            return tickets, ambassadors, shifts
        except Exception as e:
            raise Exception(f"Error loading data from Excel: {str(e)}")

    def _parse_time(self, time_str: str) -> time:
        """Parse time string to time object."""
        try:
            # Try parsing as time string (HH:MM:SS)
            return datetime.strptime(str(time_str), "%H:%M:%S").time()
        except ValueError:
            try:
                # Try parsing as datetime
                return pd.to_datetime(time_str).time()
            except:
                # Return default time if parsing fails
                return time(9, 0)  # Default to 9:00 AM

    def _parse_tickets(self) -> List[Ticket]:
        tickets = []
        for _, row in self.tickets_df.iterrows():
            ticket = Ticket(
                case_number=str(row['Case Number']),
                line_of_business=str(row['Line of Business']),
                primary_product=str(row['Primary Product']),
                primary_feature=str(row['Primary Feature']),
                specific_primary_driver=str(row['Spesific Primary Driver']),
                secondary_product=str(row['Secondary Product']) if pd.notna(row['Secondary Product']) else None,
                specific_secondary_feature=str(row['Spesific Secondary Feature']) if pd.notna(row['Spesific Secondary Feature']) else None,
                issue_summary=str(row['Issue Summary']),
                technical_proficiency=str(row['Technical Proficeny']),
                detailed_description=str(row['Detailed Description']),
                urgency=str(row['Urgency']),
                language=str(row['Language'])
            )
            tickets.append(ticket)
        return tickets

    def _parse_ambassadors(self) -> List[Ambassador]:
        ambassadors = []
        for _, row in self.ambassadors_df.iterrows():
            # Get unique line of business and case numbers for this ambassador
            ambassador_shifts = self.shifts_df[self.shifts_df['Ambassador ID'] == row['Ambassador ID']]
            lines_of_business = ambassador_shifts['Line of Business'].unique().tolist()
            
            ambassador = Ambassador(
                id=str(row['Ambassador ID']),
                name=str(row['Name']),
                line_of_business=lines_of_business,
                languages=str(row['Language(s)']).split(','),
                csat_score=float(row['CSAT']),
                case_history=str(row['Case Number']).split(',') if pd.notna(row['Case Number']) else []
            )
            ambassadors.append(ambassador)
        return ambassadors

    def _parse_shifts(self) -> List[Shift]:
        shifts = []
        for _, row in self.shifts_df.iterrows():
            # Parse shift times
            shift_start = self._parse_time(row['Shift Start'])
            shift_end = self._parse_time(row['Shift End'])
            
            shift = Shift(
                ambassador_id=str(row['Ambassador ID']),
                name=str(row['Name']),
                line_of_business=str(row['Line of Business']),
                working_days=str(row['Working Days']),
                shift_start=shift_start,
                shift_end=shift_end
            )
            shifts.append(shift)
        return shifts 