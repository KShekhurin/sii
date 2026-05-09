from abc import abstractmethod
from typing import Optional

from stand.games.bid_game.states import GameStates
from stand.games.bid_game.events import AgentBidEvent, NewBidEvent, BidResult, AgentOptOutEvent
from stand.server.server_api import AbstractGameAgent


class Handle:
    transaction: Optional[AgentBidEvent | AgentOptOutEvent]

    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        self.transaction = None

    def opt_out(self):
        self.transaction = AgentOptOutEvent(self.agent_id)

    def set_bid(self, bid_value: int):
        self.transaction = AgentBidEvent(self.agent_id, bid_value)


class BidAgent(AbstractGameAgent):
    GAME_NAME = 'BID'

    @abstractmethod
    def on_state_change(self, state: GameStates):
        pass

    @abstractmethod
    def make_step(self, handle: Handle, info: dict):
        pass