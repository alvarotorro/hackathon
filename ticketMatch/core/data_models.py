from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, time

@dataclass
class Ticket:
    case_number: str
    line_of_business: str
    primary_product: str
    primary_feature: str
    specific_primary_driver: str
    secondary_product: Optional[str]
    specific_secondary_feature: Optional[str]
    issue_summary: str
    technical_proficiency: str
    detailed_description: str
    urgency: str
    language: str
    assigned: bool = False
    assignment_datetime: Optional[datetime] = None
    assigned_ambassador_id: Optional[str] = None
    creation_timestamp: Optional[datetime] = None
    current_state: Optional[str] = None
    priority: Optional[str] = None
    complexity: Optional[str] = None

@dataclass
class Ambassador:
    id: str
    name: str
    line_of_business: List[str]
    languages: List[str]
    csat_score: float
    case_history: List[str] = None
    current_tickets: int = 0
    max_active_tickets: int = 3  # Default value
    skills: List[str] = None
    expertise_level: str = "intermediate"
    current_workload: int = 0
    

@dataclass
class Shift:
    ambassador_id: str
    name: str
    line_of_business: str
    working_days: str
    shift_start: time
    shift_end: time
    is_active: bool = True 