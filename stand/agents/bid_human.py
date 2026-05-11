from stand.games.bid_game.bid_agent import BidAgent, Handle
from stand.games.bid_game.states import GameStates
from stand.server.server_api import agent


@agent
class BidAgentHuman(BidAgent):
    AGENT_NAME = "BID Human 1"

    def __init__(self):
        super().__init__()

    def on_state_change(self, state: GameStates):
        pass

    def make_step(self, handle: Handle, info: dict):
        print("-1 — opt out, n — bet:")
        data = int(input())

        if data == -1:
            handle.opt_out()
        else:
            handle.set_bid(data)