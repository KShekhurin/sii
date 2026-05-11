from abc import ABC, abstractmethod

def agent(cls):
    cls.__IS_GAME_AGENT__ = True
    return cls

def game(cls):
    cls.__IS_GAME__ = True
    return cls

#server interfaces for module implementation
class AbstractGameAgent(ABC):
    '''any modular game agent must inherit this class and overwrite params below'''
    AGENT_NAME: str = None
    GAME_NAME: str = None
    GAME_VERSION: str = None

    def __init__(self):
        self.id = -1

    def set_id(self, id: int) -> None:
        self.id = id

    def get_id(self) -> int:
        return self.id

class AbstractRenderer(ABC):
    '''!FOR INNER USAGE, DO NOT USE!
    Abstraction for wcli and gui renderers
    '''
    @abstractmethod
    def display(self) -> None:
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        pass

class AbstractCLIDisplay(ABC):
    '''!FOR INNER USAGE, DO NOT USE!
    Abstraction for the real console and a virtual one
    '''
    def __init__(self) -> None:
        pass

    @abstractmethod
    def print_line(self, text) -> None:
        pass

    @abstractmethod
    def read_line(self, prefix) -> str:
        pass

class AbstractWCLIRenderer(AbstractRenderer):
    '''Any modular renderer must inherit this class and overwrite params below
    Is in charge of the text representation of the game
    Communication ONLY via AbstractCLIDisplay
    '''
    def __init__(self, cli_display: AbstractCLIDisplay) -> None:
        self.cli_display = cli_display
        self.ready = True
        self.is_first_msg = True

    def display(self) -> None:
        if self.is_first_msg:
            self.cli_display.print_line("[To go to next step press Next step]")
            self.is_first_msg = False

        self.sub_display()

    @abstractmethod
    def sub_display(self) -> None:
        pass

    def is_ready(self) -> bool: #the virtual console displays in one cycle so no need to wait
        return self.ready

class AbstractGame(ABC):
    '''any game implementation must inherit this class and overwrite params below'''
    GAME_NAME: str = None
    GAME_VERSION: str = None

    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def make_step(self) -> None:
        pass

    @abstractmethod
    def is_finished(self) -> bool:
        pass

    @abstractmethod
    def add_agents(self, agents: list[AbstractGameAgent]):
        pass

    @abstractmethod
    def build_cli_requirements(self, cli_display: AbstractCLIDisplay) -> AbstractWCLIRenderer:
        pass