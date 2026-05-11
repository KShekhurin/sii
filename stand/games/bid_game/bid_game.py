import random
import copy

from stand.games.bid_game.bid_agent import BidAgent, Handle
from stand.games.bid_game.events import AgentBidEvent, AgentOptOutEvent, BidResult, ErrorEvent, NewBidEvent
from stand.games.bid_game.states import GameStates
from stand.server.server_api import AbstractGame, game, AbstractGameAgent, AbstractWCLIRenderer, AbstractCLIDisplay


@game
class BidGame(AbstractGame):
    GAME_NAME = "BID"
    GAME_VERSION = "1"

    agents: list[BidAgent]
    is_finished: bool

    state: GameStates
    bidding_agent_id: int
    bidding_lead_id: int
    last_bid: int
    opted_out_ids: list[int]

    info: dict

    def __init__(self):
        #system
        self.event_chain = []
        self.agents = []
        self.finished = False

        #params
        self.rounds = 5
        self.c_round = 0
        self.prize_min = 100
        self.prize_max = 500
        self.starting_total = 1000

        #state
        self.state = GameStates.IDLE
        self.current_prize = 0
        self.bidding_agent_id = 0
        self.bidding_lead_id = -1
        self.last_bid = 0
        self.opted_out_ids = []

        #info
        self.info = {
            "current_round": 0,
            "total_rounds": self.rounds,
            "current_prize": 0,
            "last_bid": 0,
            "prizes": [],  # sequential prize values per round
            "agents": {},  # agent_id -> {"total": int, "last_bid": int}
        }

    def sync_info_header(self):
        self.info["current_round"] = self.c_round
        self.info["total_rounds"] = self.rounds

    def award_prize(self, winner_id: int):
        self.info["agents"][winner_id]["total"] += self.current_prize
        self.info["prizes"].append(self.current_prize)
        self.sync_info_header()

    def deduct_bid(self, agent_id: int, value: int):
        self.info["agents"][agent_id]["total"] -= value

    def add_agents(self, agents: list[AbstractGameAgent]):
        self.agents.extend(agents)

    def build_cli_requirements(self, cli_display: AbstractCLIDisplay) -> AbstractWCLIRenderer:
        from stand.games.bid_game.WCLIRenderer import BidWCLIRenderer
        renderer = BidWCLIRenderer(cli_display, self)

        return renderer

    def setup(self) -> None:
        for i in range(len(self.agents)):
            self.agents[i].set_id(i)

            self.info["agents"][i] = {
                "total": self.starting_total,
                "last_bid": 0,
            }

    def make_step(self) -> None:
        match self.state:
            case GameStates.IDLE:
                self.on_idle()
            case GameStates.NEXT_BID:
                self.on_next_bid()
            case GameStates.BIDDING:
                self.on_bidding()

    def on_idle(self):
        self.state = GameStates.NEXT_BID
        self.make_step()

    def on_next_bid(self):
        if self.c_round >= self.rounds:
            self.is_finished = True
            return

        self.c_round += 1
        for agent in self.agents:
            agent.on_state_change(self.state)

        self.current_prize = random.randint(self.prize_min, self.prize_max)

        self.event_chain.append(NewBidEvent(self.c_round))

        self.state = GameStates.BIDDING

    def on_bidding(self):
        current_agent = self.agents[self.bidding_agent_id]

        handle = Handle(self.bidding_agent_id)
        current_agent.make_step(handle, copy.deepcopy(self.info))

        trans = handle.transaction

        match trans:
            case None:
                self.rise_error("No action was performed",
                                self.bidding_agent_id)
                return
            case AgentBidEvent(agent_id=self.bidding_agent_id, value=value):
                if value <= self.last_bid:
                    self.rise_error("New bid cannot be less then previous one",
                                    self.bidding_agent_id)
                    return
                else:
                    self.last_bid = value
                    self.bidding_lead_id = self.bidding_agent_id

                    self.info["agents"][self.bidding_agent_id]["last_bid"] = value
                    self.event_chain.append(trans)
            case AgentOptOutEvent(agent_id=self.bidding_agent_id):
                self.opted_out_ids.append(self.bidding_agent_id)
                self.event_chain.append(trans)
            case _:
                self.rise_error("Undefined response", self.bidding_agent_id)
                return

        if len(self.opted_out_ids) == len(self.agents) - 1:
            winner_id = (list(set(self.agents) - set(self.opted_out_ids))[0]
                         .get_id())

            self.event_chain.append(BidResult(
                round_number=self.c_round,
                winner_id=winner_id,
                value_bet=self.last_bid,
                prize=self.current_prize
            ))

            self.deduct_bid(winner_id, self.last_bid)
            self.award_prize(winner_id)

            self.clear_state()
        else:
            self.to_next_agent()


    def to_next_agent(self):
        self.bidding_agent_id = (self.bidding_agent_id + 1) % len(self.agents)

        while self.bidding_agent_id in self.opted_out_ids:
            self.bidding_agent_id = (self.bidding_agent_id + 1) % len(self.agents)

    def rise_error(self, msg: str, agent_id: int = -1):
        self.event_chain.append(ErrorEvent(
            agent_id=agent_id,
            message=msg
        ))
        self.is_finished = True

    def clear_state(self):
        self.state = GameStates.NEXT_BID
        self.bidding_agent_id = 0
        self.bidding_lead_id = -1
        self.last_bid = 0
        self.opted_out_ids = []

        self.info["last_bid"] = 0
        for agent_id in self.info["agents"]:
            self.info["agents"][agent_id]["last_bid"] = 0

    def is_finished(self) -> bool:
        return self.finished