from __future__ import annotations
from dataclasses import dataclass
from typing import List

from stand.server.server_api import *

@dataclass
class ResponseEvent:
    agent: EchoGameAgent
    message: str

class Handle:
    transactions: List[ResponseEvent]

    def __init__(self, game: EchoGame, agent: EchoGameAgent):
        self.__game = game
        self.__agent = agent
        self.transactions = []

    def respond_with_text(self, text: str):
        self.transactions.append(
            ResponseEvent(
                agent=self.__agent,
                message=text
            ))


class EchoGameAgent(AbstractGameAgent):
    GAME_NAME = "ECHO"

    @abstractmethod
    def respond(self, text: str, handle: Handle):
        pass

@game
class EchoGame(AbstractGame):
    GAME_NAME = "ECHO"
    GAME_VERSION = "1"

    agents: List[EchoGameAgent]
    events_chain: List[ResponseEvent]

    def __init__(self):
        self.turns_taken = 0
        self.max_turns = 5

        self.agents = []
        self.agent_inx = 0

        self.finished = False

        self.events_chain = []

    def get_agents_cnt(self):
        return len(self.agents)

    def is_finished(self) -> bool:
        return self.finished

    def make_step(self):
        #exit check
        if self.turns_taken >= self.max_turns:
            self.finished = True
            return

        #agent selection
        current_agent = self.agents[self.agent_inx]

        #turn processing
        handle = Handle(self, current_agent)
        current_agent.respond("test", handle)

        #transaction validation
        if len(handle.transactions) != 1 or not isinstance(handle.transactions[0], ResponseEvent):
            self.finished = True
            return

        #application to the event chain
        self.events_chain.append(handle.transactions[0])

        #change to game state
        self.agent_inx = (self.agent_inx + 1) % self.get_agents_cnt()
        if self.agent_inx == 0:
            self.turns_taken += 1

    def setup(self) -> None:
        for i in range(self.get_agents_cnt()):
            self.agents[i].set_id(i)

class EchoWCLIRenderer(AbstractWCLIRenderer):
    def __init__(self, cli_display: AbstractCLIDisplay, game: EchoGame):
        super().__init__(cli_display)
        self.game = game
        self.events_cnt = 0

    def sub_display(self) -> None:
        event_chain = self.game.events_chain
        if self.events_cnt == len(event_chain):
            return

        self.events_cnt = len(event_chain)
        for event in event_chain[self.events_cnt-1:]:
            self.cli_display.print_line(f"Agent {event.agent.AGENT_NAME}({event.agent.get_id()}) responded: {event.message}")