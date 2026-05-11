from dataclasses import dataclass
from typing import Optional


@dataclass
class AgentBidEvent:
    agent_id: int
    value: int

@dataclass
class AgentOptOutEvent:
    agent_id: int

@dataclass
class NewBidEvent:
    round: int

@dataclass
class BidResult:
    round_number: int
    winner_id: Optional[int]
    value_bet: Optional[int]
    prize: Optional[int]

@dataclass
class GameResult:
    winner_id: Optional[int]

@dataclass
class ErrorEvent:
    agent_id: int
    message: str