from skyjosimulator.strategy.strategies import RandomStrategy, ManualStrategy, LocalOptimumStrategy

STRATEGIES = {
    'random': RandomStrategy,
    'manual': ManualStrategy,
    'local': LocalOptimumStrategy,
}


def create_strategy(player_name, strategy_key):
    return STRATEGIES[strategy_key](player_name)
