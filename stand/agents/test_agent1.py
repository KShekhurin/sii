from stand.games.test_game.echo_game import Handle, EchoGameAgent
from stand.server.server_api import agent

@agent
class ResponsiveAgent(EchoGameAgent):
    AGENT_NAME = "ResponsiveAgent"
    GAME_VERSION = "1"

    def __init__(self):
        super().__init__()

    def respond(self, text: str, handle: Handle):
        handle.respond_with_text(text)