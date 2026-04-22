from stand.games.test_game.echo_game import EchoWCLIRenderer
from stand.server.utils import find_games, find_agents, ConsoleDisplay, run
from prompt_toolkit.shortcuts import radiolist_dialog, checkboxlist_dialog


def run_server():
    games = find_games()

    game_index = radiolist_dialog(
        title="Select a game",
        text="Games found",
        values=[(i, f"{game.GAME_NAME}, ver. {game.GAME_VERSION}")
                for i, game in enumerate(games)]
    ).run()
    game_cls = games[game_index]

    agents = find_agents()

    agents_types = checkboxlist_dialog(
        title="Select agents",
        text="Agents found",
        values=[(agent, f"{agent.AGENT_NAME}")
                for agent in agents if game_cls.GAME_NAME == agent.GAME_NAME]
    ).run()

    game = game_cls()
    for agent_type in agents_types:
        game.agents.append(agent_type())

    game.setup()

    renderer = EchoWCLIRenderer(ConsoleDisplay(), game)

    run(game, renderer)

    input("PRESS ENTER TO FINISH")