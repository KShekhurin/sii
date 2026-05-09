from stand.games.bid_game.bid_game import BidGame
from stand.games.bid_game.events import AgentBidEvent, NewBidEvent, BidResult, ErrorEvent, AgentOptOutEvent
from stand.server.server_api import AbstractWCLIRenderer, AbstractCLIDisplay, game


class BidWCLIRenderer(AbstractWCLIRenderer):
    def __init__(self, cli_display: AbstractCLIDisplay, game: BidGame):
        super().__init__(cli_display)
        self.game = game
        self.event_chain_len = 0

    def sub_display(self) -> None:
        if self.event_chain_len == len(self.game.event_chain):
            return

        for event in self.game.event_chain[self.event_chain_len:]:
            self.match_events(event)

        self.event_chain_len = len(self.game.event_chain)

    def get_agent_name_by_id(self, id: int):
        return self.game.agents[id].AGENT_NAME

    def match_events(self, event):
        match event:
            case AgentBidEvent(agent_id=id, value=value):
                self.cli_display.print_line(
                    f"Agent {self.get_agent_name_by_id(id)}({id}) put {value}")
            case AgentOptOutEvent(agent_id=id):
                self.cli_display.print_line(
                    f"Agent {self.get_agent_name_by_id(id)}({id}) opted out"
                )
            case NewBidEvent(round=round):
                self.cli_display.print_line(f"ROUND: {round}")
            case BidResult(winner_id=id, value_bet=value, prize=prize):
                self.cli_display.print_line(
                    f"Agent {self.get_agent_name_by_id(id)}({id}) paid {value} and won {prize}"
                )
            case ErrorEvent(agent_id=id, message=message):
                self.cli_display.print_line(f"ERROR({id}): {message}")
