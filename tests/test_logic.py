from unittest import TestCase
from unittest.mock import patch

from skyjosimulator.game.logic import SkyjoGame
from skyjosimulator.strategy import create_strategy

STATIC_DRAW_STACK = [7, 8, 0, 8, 11, 12, 6, -2, 0, 1, -1, 10, -1, 8, 9, 10, 1, 9, 7, 6, 7, 11, 2, 2, 12, 9, 5, 4, 0, -1,
                     12, 8, 8, 1, 1, 0, 6, 2, 3, -2, 7, -2, -1, 9, 3, 11, 1, 7, 6, 0, 4, 7, 1, -1, 12, -1, 7, 10, -1, 6,
                     4, 10, 4, 1, 2, 0, 4, 5, 1, 3, 2, 3, -1, 4, 10, 3, 11, 12, 3, 2, -2, 10, 6, 0, 7, 11, 12, -1, 11,
                     2, 7, 5, 11, 10, 5, 8, -1, 3, 4, 6, -1, 1, 4, 9, 9, -1, 11, 9, 8, 0, 5, 0, 0, 6, -1, 10, 12, 9, 8,
                     12, 5, 2, 1, 11, 2, 0, 3, 4, 3, 0, 5, 6, -1, 0, 10, -1, 4, 11, 2, 9, -2, 0, 12, 9, 12, 0, 10, 7, 8,
                     5, 5, 6, 5, 3, 8]


class SkyjoGameTests(TestCase):
    @patch('skyjosimulator.game.logic.generate_draw_stack')
    def test_prepare_game(self, draw_stack_gen):
        draw_stack_gen.return_value = STATIC_DRAW_STACK
        game = SkyjoGame([create_strategy('player1', 'random')])
        game.prepare_game()

        grid = game.state.player_grids['player1']

        self.assertEqual(len(game.state.draw_stack), 143)

        self.assertEqual(grid.columns[0].cards[0].value, 9)
        self.assertEqual(grid.columns[0].cards[1].value, 12)
        self.assertEqual(grid.columns[0].cards[2].value, 0)
        self.assertEqual(grid.columns[1].cards[0].value, 10)
        self.assertEqual(grid.columns[1].cards[1].value, 7)
        self.assertEqual(grid.columns[1].cards[2].value, 8)
        self.assertEqual(grid.columns[2].cards[0].value, 5)
        self.assertEqual(grid.columns[2].cards[1].value, 5)
        self.assertEqual(grid.columns[2].cards[2].value, 6)
        self.assertEqual(grid.columns[3].cards[0].value, 5)
        self.assertEqual(grid.columns[3].cards[1].value, 3)
        self.assertEqual(grid.columns[3].cards[2].value, 8)

    def test_start_game(self):
        game = SkyjoGame([
            create_strategy('player1', 'local'),
            create_strategy('player2', 'random'),
            create_strategy('player3', 'local'),
        ])
        game.prepare_game()
        print(game.start())
