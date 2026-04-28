from enum import Enum
from typing import Optional

from PySide6.QtWidgets import QMainWindow

from stand.server.gui.console.console_window import Ui_ConsoleWindow
from stand.server.gui.main_view import MainView
from stand.server.server_api import AbstractGame, AbstractGameAgent
from stand.server.utils import find_games, find_agents


class MainStates(Enum):
    IDLE = 0
    SELECTING_GAME = 1
    SELECTING_AGENTS = 2

class MainPresenter:
    state: MainStates
    games: list[AbstractGame]
    selected_game: Optional[AbstractGame]

    def __init__(self, main_view: MainView):
        self.main_view = main_view
        self.state = MainStates.IDLE

        self.games = []
        self.selected_game = None
        self.agents = []
        self.selected_agents = []

    def on_selected_game_changed(self, game_id):
        self.selected_game = self.games[game_id]
        self.change_state(MainStates.SELECTING_AGENTS)

    def on_game_unselected(self):
        self.selected_game = None
        self.change_state(MainStates.SELECTING_GAME)

    def on_agent_added(self, agent_id):
        self.selected_agents.append(agent_id)

    def on_agent_removed(self, agent_id):
        self.selected_agents.remove(agent_id)

    def change_state(self, new_state: MainStates):
        if new_state == MainStates.SELECTING_GAME:
            self.selected_game = None
            self.games = find_games()
            self.show_games()
            self.main_view.set_agents_box_enabled(False)
            self.agents = []
            self.show_agents()

        if new_state == MainStates.SELECTING_AGENTS:
            self.agents = [agent
                           for agent in find_agents()
                           if agent.GAME_NAME == self.selected_game.GAME_NAME]
            self.show_agents()
            self.main_view.set_agents_box_enabled(True)

        self.state = new_state

    def show_games(self):
        self.main_view.set_games([
            f"{game.GAME_NAME}: {game.GAME_VERSION}" for game in self.games
        ])

    def show_agents(self):
        self.main_view.set_agents([f"{agent.AGENT_NAME}: {agent.GAME_VERSION}"
                                   for agent in self.agents])
    def start_cli_session(self):
        self.main_view.show_cli_window(
            self.selected_game(), list(map(lambda agent_id: self.agents[agent_id](), self.selected_agents))
        )