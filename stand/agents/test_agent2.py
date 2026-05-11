from stand.games.test_game.echo_game import EchoGameAgent, Handle
from stand.server.server_api import agent, AbstractInput


@agent
class CrazyAgent(EchoGameAgent):
    AGENT_NAME = "CrazyAgent"
    GAME_VERSION = "1"

    def __init__(self, inpt: AbstractInput):
        super().__init__(inpt)

    def respond(self, text: str, handle: Handle):
        handle.respond_with_text("aasdfsadf")