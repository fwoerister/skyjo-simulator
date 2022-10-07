from random import shuffle

from skyjosimulator import CARD_FREQUENCIES, DRAW_LOCATION
from skyjosimulator.game import CardGridFactory
from skyjosimulator.game.model import SkyjoGameState


def generate_draw_stack():
    draw_stack = []
    for card in CARD_FREQUENCIES:
        draw_stack += [card] * CARD_FREQUENCIES[card]
    shuffle(draw_stack)
    return draw_stack


class SkyjoGame:
    def __init__(self, player_strategies):
        draw_stack = generate_draw_stack()
        self.state = SkyjoGameState(draw_stack, {})
        self.player_strategies = player_strategies

        self.current_player_index = 0
        self.current_player = None
        self.last_round = False

    def prepare_game(self):
        player_grids = dict()
        for player in self.player_strategies:
            cards = self.state.draw_n_cards(12)
            player_grids[player.name] = CardGridFactory.create_grid(cards)
        self.state.player_grids = player_grids

    def start(self):
        remaining_turns = None

        self.flip_starting_cards()
        self.state.initialize_discard_stack()
        self.set_next_player_as_current()

        while remaining_turns is None or remaining_turns > 0:
            self.execute_current_players_move()
            self.state.remove_columns_with_identical_cards(self.current_player.name)

            if len(self.state.draw_stack) == 0:
                self.reshuffle_cards()

            if not self.last_round and self.state.player_has_finished(self.current_player.name):
                self.last_round = True
                remaining_turns = len(self.player_strategies) - 1

            if self.last_round:
                remaining_turns -= 1

            self.set_next_player_as_current()

        return self.evaluate_scores()

    def execute_current_players_move(self):
        draw_location = self.current_player.decide_draw_location(self.state.player_grids,
                                                                 self.state.discard_stack)
        new_card = self.get_drawn_card(draw_location)
        target_location = self.current_player.get_target_location(self.state.player_grids,
                                                                  self.state.discard_stack,
                                                                  new_card)
        self.state.apply_move(self.current_player.name, draw_location, target_location)

    def reshuffle_cards(self):
        self.state.draw_stack += self.state.discard_stack
        shuffle(self.state.draw_stack)
        self.state.discard_stack = [self.state.draw_stack.pop()]

    def get_drawn_card(self, draw_location):
        if draw_location == DRAW_LOCATION.DRAW_STACK:
            new_card = self.state.draw_stack[-1]
        else:
            new_card = self.state.discard_stack[-1]
        return new_card

    def flip_starting_cards(self):
        for strategy in self.player_strategies:
            positions = strategy.get_position_of_initial_card_flips()
            self.state.flip_cards(strategy.name, positions)

    def set_next_player_as_current(self):
        if self.current_player is None:
            scores = self.state.calculate_scores()
            starting_player = None

            for player in scores:
                if scores[player] == max(scores.values()):
                    starting_player = player

            self.current_player_index = 0
            self.current_player = self.player_strategies[self.current_player_index]
            while self.current_player.name != starting_player:
                self.current_player_index += 1
                self.current_player = self.player_strategies[self.current_player_index]
        else:
            self.current_player_index = (self.current_player_index + 1) % len(self.player_strategies)
            self.current_player = self.player_strategies[self.current_player_index]

    def evaluate_scores(self):
        self.state.reveal_all_cards()
        scores = self.state.calculate_scores()

        if scores[self.current_player.name] != min(scores.values()) and scores[self.current_player.name] > 0:
            scores[self.current_player.name] *= 2

        return scores


class SkyjoGameMove:
    def __init__(self, target_column, target_row, replace_card):
        """
        Instances of this class represent a move of a single player.

        :param target_column: column of the card that should be affected by this move
        :param target_row: row of the card that should be affected by this move
        :param replace_card: if this flag is true, the card specified by this move is replaced by the drawn card.
                             otherwise, the drawn card is discarded and the card specified by this move is revealed.
                             (remark: if this flag is True, the target card must not be revealed)
        """
        self.column = target_column
        self.row = target_row
        self.replace_card = replace_card
