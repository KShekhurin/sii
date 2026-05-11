from stand.games.test_game.echo_game import Handle, EchoGameAgent
from stand.server.server_api import agent, AbstractInput


@agent
class ResponsiveAgent(EchoGameAgent):
    AGENT_NAME = "ResponsiveAgent"
    GAME_VERSION = "1"

    def __init__(self, inpt: AbstractInput):
        super().__init__(inpt)

    def respond(self, text: str, handle: Handle):
        handle.respond_with_text(text)