from stand.games.bid_game.bid_agent import BidAgent, Handle
from stand.games.bid_game.states import GameStates
from stand.server.server_api import agent, AbstractInput


@agent
class BidAgentHuman(BidAgent):
    AGENT_NAME = "BID Human 1"
    GAME_VERSION = "1"

    def __init__(self, inpt: AbstractInput):
        super().__init__(inpt)

    def on_state_change(self, state: GameStates):
        pass

    def make_step(self, handle: Handle, info: dict):
        data = int(self.input.read_line("-1 — opt out, n — bet:"))

        if data == -1:
            handle.opt_out()
        else:
            handle.set_bid(data)