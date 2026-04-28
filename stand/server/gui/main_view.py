from abc import ABC, abstractmethod
from typing import Optional

from stand.server.server_api import AbstractGame, AbstractGameAgent


class MainView(ABC):
    @abstractmethod
    def get_selected_game_id(self) -> Optional[int]:
        pass

    @abstractmethod
    def set_games(self, texts: list[str]):
        pass

    @abstractmethod
    def get_selected_agents_ids(self) -> list[int]:
        pass

    @abstractmethod
    def set_agents(self, texts: list[str]):
        pass

    @abstractmethod
    def set_agents_box_enabled(self, enabled: bool):
        pass

    @abstractmethod
    def set_cli_btn_enabled(self, enabled: bool):
        pass

    @abstractmethod
    def set_gui_btn_enabled(self, enabled: bool):
        pass

    @abstractmethod
    def show_cli_window(self, game: AbstractGame, agents: list[AbstractGameAgent]):
        pass