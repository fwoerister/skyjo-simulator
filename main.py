from skyjosimulator.game import SkyjoGame
from skyjosimulator.strategy import create_strategy

ROUND_COUNT = 10000

player_stat = {
    'player1': 0,
    'player2': 0,
    'player3': 0,
}

for game_round in range(ROUND_COUNT):
    game = SkyjoGame([
        create_strategy('player1', 'local'),
        create_strategy('player2', 'random'),
        create_strategy('player3', 'local'),
    ])

    game.prepare_game()
    result = game.start()

    for player in result:
        player_stat[player] += result[player]

for player in player_stat:
    player_stat[player] /= ROUND_COUNT

print(player_stat)
