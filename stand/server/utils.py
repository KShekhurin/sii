import importlib.util
from stand import games
from stand.games.test_game.echo_game import EchoWCLIRenderer
from stand.server.server_api import *
from pkgutil import walk_packages

class ConsoleDisplay(AbstractCLIDisplay):
    def print_line(self, text) -> None:
        print(text)

    def read_line(self, text) -> str:
        return input(text)

def load_module_from_path(path: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def load_all_submodules(package):
    modules = []

    for module_info in walk_packages(package.__path__, package.__name__ + "."):
        module = importlib.import_module(module_info.name)
        modules.append(module)

    return modules

def find_games() -> list[type]:
    games = []
    modules = load_all_submodules(importlib.import_module("stand.games"))

    for module in modules:
        for name in dir(module):
            obj = getattr(module, name)

            if (isinstance(obj, type)
                    and hasattr(obj, "__IS_GAME__")
                    and issubclass(obj, AbstractGame)
                    and obj is not AbstractGame
                    and obj not in games):
                games.append(obj)
    return games

def find_agents() -> list[type]:
    agents = []
    modules = load_all_submodules(importlib.import_module("stand.agents"))

    for module in modules:
        for name in dir(module):
            obj = getattr(module, name)

            if (isinstance(obj, type)
                    and hasattr(obj, "__IS_GAME_AGENT__")
                    and issubclass(obj, AbstractGameAgent)
                    and obj is not AbstractGameAgent):
                agents.append(obj)

    return agents

def run(game: AbstractGame, renderer: AbstractRenderer):
    while not game.is_finished():
        if renderer.is_ready():
            game.make_step()
        renderer.display()