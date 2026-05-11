from stand.games.test_game.echo_game import EchoGame
from stand.server.server_api import AbstractWCLIRenderer, AbstractCLIDisplay


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