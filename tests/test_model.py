from unittest import TestCase

from skyjosimulator import DRAW_LOCATION
from skyjosimulator.game.model import Card, CardColumn, CardGrid, SkyjoGameState
from skyjosimulator.game.logic import SkyjoGameMove


class SkyjoGameStateTests(TestCase):
    def test_get_current_state(self):
        card_col1 = CardColumn([Card(value) for value in range(2)])
        card_col2 = CardColumn([Card(value) for value in range(2)])
        card_col3 = CardColumn([Card(value) for value in range(2)])
        card_col4 = CardColumn([Card(value) for value in range(2)])

        card_col1.reveal_card(0)
        card_col2.reveal_card(1)
        card_col3.reveal_card(1)
        card_col4.reveal_card(0)

        card_grid1 = CardGrid([card_col1, card_col2])
        card_grid2 = CardGrid([card_col3, card_col4])

        game = SkyjoGameState([], {
            'player1': card_grid1,
            'player2': card_grid2,
        })

        self.assertEqual(game.get_current_state(), {
            'player1': [[0, None], [None, 1]],
            'player2': [[None, 1], [0, None]],
        })

    def test_apply_discard_drawn_card_move(self):
        card_col1 = CardColumn([Card(value) for value in [1, 5, -3]])
        card_col2 = CardColumn([Card(value) for value in [7, 2, 2]])
        card_col3 = CardColumn([Card(value) for value in [2, 12, 3]])
        card_col4 = CardColumn([Card(value) for value in [8, 4, 0]])

        grid = CardGrid([card_col1, card_col2, card_col3, card_col4])
        game = SkyjoGameState([1, 4, 3, 5, -2], {'player1': grid})

        game.apply_move('player1', DRAW_LOCATION.DRAW_STACK, SkyjoGameMove(0, 0, False))

        self.assertEqual(game.discard_stack.pop(), -2)
        self.assertEqual(game.draw_stack, [1, 4, 3, 5])
        self.assertTrue(card_col1.cards[0].is_revealed)

    def test_apply_replace_card_move(self):
        card_col1 = CardColumn([Card(value) for value in [3, 5, -3]])
        card_col2 = CardColumn([Card(value) for value in [7, 1, 2]])
        card_col3 = CardColumn([Card(value) for value in [12, 2, 3]])
        card_col4 = CardColumn([Card(value) for value in [2, 4, 6]])

        grid = CardGrid([card_col1, card_col2, card_col3, card_col4])
        game = SkyjoGameState([5, 2, 3, 4, 3], {'player1': grid})

        game.apply_move('player1', DRAW_LOCATION.DRAW_STACK, SkyjoGameMove(2, 1, True))

        self.assertEqual(game.discard_stack.pop(), 2)
        self.assertEqual(game.draw_stack, [5, 2, 3, 4])
        self.assertEqual(card_col3.cards[1].value, 3)
        self.assertTrue(card_col3.cards[1].is_revealed)

    def test_player_has_finished(self):
        card_col1 = CardColumn([Card(value) for value in [2, 5, -3]])
        card_col2 = CardColumn([Card(value) for value in [7, 4, 2]])
        card_col3 = CardColumn([Card(value) for value in [11, 2, 3]])
        card_col4 = CardColumn([Card(value) for value in [2, 4, 1]])

        grid = CardGrid([card_col1, card_col2, card_col3, card_col4])
        game = SkyjoGameState([], {'player1': grid})

        grid.reveal_all_cards()

        self.assertTrue(game.player_has_finished('player1'))

    def test_remove_columns_with_identical_values(self):
        card_col1 = CardColumn([Card(value, is_revealed=True) for value in [5, 5, 5]])
        card_col2 = CardColumn([Card(value) for value in [7, 4, 2]])
        card_col3 = CardColumn([Card(value) for value in [2, 2, 2]])
        card_col4 = CardColumn([Card(value) for value in [8, 4, 1]])

        grid = CardGrid([card_col1, card_col2, card_col3, card_col4])
        game = SkyjoGameState([], {'player1': grid})

        game.remove_columns_with_identical_cards('player1')

        self.assertEqual(len(grid.columns), 3)

    def test_calculate_scores(self):
        card_col1 = CardColumn([Card(value, is_revealed=True) for value in [1, 2, 3]])
        card_col2 = CardColumn([Card(value, is_revealed=True) for value in [7, -2, 2]])
        card_col3 = CardColumn([Card(value, is_revealed=True) for value in [-2, 2, 1]])
        card_col4 = CardColumn([Card(value, is_revealed=True) for value in [8, 4, -1]])

        grid = CardGrid([card_col1, card_col2, card_col3, card_col4])
        game = SkyjoGameState([], {'player1': grid})

        self.assertEqual(game.calculate_scores(), {
            'player1': 25,
        })

    def test_flip_cards(self):
        card_col1 = CardColumn([Card(value) for value in [1, 3, 3]])
        card_col2 = CardColumn([Card(value) for value in [7, 1, 2]])
        card_col3 = CardColumn([Card(value) for value in [2, 2, 1]])
        card_col4 = CardColumn([Card(value) for value in [8, 4, 1]])

        grid = CardGrid([card_col1, card_col2, card_col3, card_col4])
        game = SkyjoGameState([], {'player1': grid})

        game.flip_cards('player1', [(0, 0), (1, 1)])

        self.assertTrue(card_col1.cards[0].is_revealed)
        self.assertTrue(card_col2.cards[1].is_revealed)

    def test_reveal_all_cards(self):
        card_col1 = CardColumn([Card(value) for value in [1, 1, 1]])
        card_col2 = CardColumn([Card(value) for value in [1, 1, 1]])

        grid = CardGrid([card_col1, card_col2])
        game = SkyjoGameState([], {'player1': grid})

        game.reveal_all_cards()

        revealed_cards = [
            [c.is_revealed for c in card_col1.cards],
            [c.is_revealed for c in card_col2.cards],
        ]

        self.assertEqual(revealed_cards[0], [True, True, True])
        self.assertEqual(revealed_cards[1], [True, True, True])


class CardGridTests(TestCase):
    def test_get_revealed_values(self):
        card_col1 = CardColumn([Card(value) for value in range(2)])
        card_col2 = CardColumn([Card(value) for value in range(2)])

        card_col1.reveal_card(0)
        card_col2.reveal_card(1)

        card_grid = CardGrid([card_col1, card_col2])
        self.assertEqual(card_grid.to_list(), [[0, None], [None, 1]])

    def test_replace_card(self):
        card_col1 = CardColumn([Card(value) for value in range(2)])
        card_grid = CardGrid([card_col1])

        value_to_discard = card_grid.replace_card((0, 0), -2)

        self.assertEqual(value_to_discard, 0)
        self.assertEqual(card_col1.cards[0].value, -2)

    def test_reveal_all_cards(self):
        card_col1 = CardColumn([Card(value) for value in range(3)])
        card_col2 = CardColumn([Card(value) for value in range(3)])

        card_grid = CardGrid([card_col1, card_col2])
        card_grid.reveal_all_cards()

        cards_revealed = [
            [c.is_revealed for c in card_col1.cards],
            [c.is_revealed for c in card_col2.cards],
        ]

        self.assertEqual(cards_revealed[0], [True, True, True])
        self.assertEqual(cards_revealed[1], [True, True, True])

    def test_get_current_score(self):
        card_col1 = CardColumn([Card(value) for value in range(3)])
        card_col2 = CardColumn([Card(value) for value in range(3)])

        card_col1.cards[0].is_revealed = True
        card_col1.cards[1].is_revealed = True
        card_col2.cards[2].is_revealed = True

        card_grid = CardGrid([card_col1, card_col2])

        self.assertEqual(card_grid.calculate_current_score(), 3)

    def test_all_cards_revealed(self):
        card_col1 = CardColumn([Card(value, is_revealed=True) for value in range(3)])
        card_col2 = CardColumn([Card(value, is_revealed=True) for value in range(3)])

        card_grid = CardGrid([card_col1, card_col2])

        self.assertTrue(card_grid.all_cards_revealed())

    def test_all_cards_revealed_with_one_card_still_hidden(self):
        card_col1 = CardColumn([Card(value, is_revealed=True) for value in range(3)])
        card_col2 = CardColumn([Card(value, is_revealed=True) for value in range(3)])

        card_col1.cards[0].is_revealed = False

        card_grid = CardGrid([card_col1, card_col2])

        self.assertFalse(card_grid.all_cards_revealed())


class CardColumnTests(TestCase):
    def test_all_cards_revealed(self):
        card1 = Card(1)
        card1.is_revealed = True

        card2 = Card(1)
        card2.is_revealed = True

        column = CardColumn([card1, card2])

        self.assertTrue(column.all_cards_revealed())

    def test_all_cards_revealed_with_hidden_cards(self):
        card1 = Card(1)
        card2 = Card(1)
        card3 = Card(1)

        column = CardColumn([card1, card2, card3])

        self.assertFalse(column.all_cards_revealed())

    def test_card_column_to_list_conversion(self):
        card1 = Card(5)
        card2 = Card(2)
        card3 = Card(-1)

        card2.is_revealed = True

        column = CardColumn([card1, card2, card3])

        self.assertEqual(column.to_list(), [None, 2, None])

    def test_is_removeable_on_column(self):
        card1 = Card(1)
        card1.is_revealed = True
        card2 = Card(1)
        card2.is_revealed = True
        card3 = Card(1)
        card3.is_revealed = True

        column = CardColumn([card1, card2, card3])

        self.assertTrue(column.is_removeable())

    def test_is_removeable_on_column_with_different_values(self):
        card1 = Card(2)
        card1.is_revealed = True
        card2 = Card(4)
        card2.is_revealed = True
        card3 = Card(-1)
        card3.is_revealed = True

        column = CardColumn([card1, card2, card3])

        self.assertFalse(column.is_removeable())

    def test_is_removeable_on_column_with_hidden_cards(self):
        card1 = Card(1)
        card2 = Card(1)
        card3 = Card(1)

        column = CardColumn([card1, card2, card3])

        self.assertFalse(column.is_removeable())

    def test_replace_card(self):
        card1 = Card(1)
        card2 = Card(2)
        card3 = Card(3)

        column = CardColumn([card1, card2, card3])

        value_to_discard = column.replace_card(1, -2)

        self.assertEqual(value_to_discard, 2)
        self.assertEqual(card2.value, -2)

    def test_calculate_score(self):
        card1 = Card(1)
        card2 = Card(2)
        card3 = Card(3)

        card1.is_revealed = True
        card3.is_revealed = True

        column = CardColumn([card1, card2, card3])

        self.assertEqual(column.calculate_current_score(), 4)

    def test_reveal_all_cards(self):
        cards = [Card(1), Card(2), Card(3)]
        column = CardColumn(cards)
        column.reveal_all_cards()

        cards_revealed = [c.is_revealed for c in cards]

        self.assertEqual(cards_revealed, [True, True, True])


class CardTests(TestCase):
    def test_retrieve_value_of_hidden_card(self):
        card = Card(1)
        self.assertIsNone(card.get_value())

    def test_retrieve_value_of_revealed_card(self):
        card = Card(1)
        card.is_revealed = True
        self.assertEqual(card.get_value(), 1)
