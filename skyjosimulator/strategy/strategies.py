import random

from skyjosimulator import DRAW_LOCATION, CARD_FREQUENCIES
from skyjosimulator.game.logic import SkyjoGameMove


def calculate_expected_card_value(player_grids, discard_stack):
    revealed_cards_statistic = create_card_statistic(discard_stack, player_grids)

    hidden_cards_no = 0
    hidden_cards_value_sum = 0

    for value in CARD_FREQUENCIES.keys():
        remaining_hidden_cards = CARD_FREQUENCIES[value] - zero_if_none(revealed_cards_statistic.get(value))
        hidden_cards_no += remaining_hidden_cards
        hidden_cards_value_sum += value * remaining_hidden_cards

    return float(hidden_cards_value_sum) / float(hidden_cards_no)


def create_card_statistic(discard_stack, player_grids):
    revealed_cards_statistic = dict()
    apply_cards_to_statistic(discard_stack, revealed_cards_statistic)
    apply_card_grids_to_statistic(player_grids, revealed_cards_statistic)
    return revealed_cards_statistic


def apply_card_grids_to_statistic(player_grids, revealed_cards_statistic):
    for player_grid in player_grids.values():
        grid_values = player_grid.to_list()
        for column in grid_values:
            apply_cards_to_statistic(column, revealed_cards_statistic)


def apply_cards_to_statistic(discard_stack, revealed_cards):
    for value in discard_stack:
        add_value_to_statistic(value, revealed_cards)


def add_value_to_statistic(value, statistic):
    if value is None:
        return
    elif value in statistic.keys():
        statistic[value] += 1
    else:
        statistic[value] = 1


def calculate_possible_card_positions(columns, rows):
    positions = []
    for c in range(columns):
        for r in range(rows):
            positions.append((c, r))
    return positions


def zero_if_none(value):
    return value or 0


class Strategy:
    def __init__(self, name):
        self.name = name

    def get_position_of_initial_card_flips(self):
        """
        This method decides which of the 12 initial cards are revealed before the game starts.
        """
        raise NotImplementedError()

    def decide_draw_location(self, player_grids, discard_stack):
        """
        This method decides wether to draw from the draw-stack or the discard-stack.

        :param player_grids:
        :param discard_stack:
        :return:
        """
        raise NotImplementedError()

    def get_target_location(self, player_grids, discard_stack, new_card):
        """
        This method decides which position of the player grid should be affected by the current move.

        :param player_grids:
        :param discard_stack:
        :param new_card:
        :return:
        """
        raise NotImplementedError()


class RandomStrategy(Strategy):
    def __init__(self, player_name):
        super(RandomStrategy, self).__init__(player_name)

    def get_position_of_initial_card_flips(self):
        card_positions = calculate_possible_card_positions(4, 3)
        return random.choices(card_positions, k=2)

    def decide_draw_location(self, player_grids, discard_stack):
        return random.choice([DRAW_LOCATION.DRAW_STACK, DRAW_LOCATION.DISCARD_STACK])

    def get_target_location(self, player_grids, discard_stack, new_card):
        own_grid = player_grids[self.name]
        column_count = len(own_grid.columns)
        position = random.choice(calculate_possible_card_positions(column_count, 3))
        replace_card = random.choice([True, False])
        return SkyjoGameMove(position[0], position[1], replace_card)


class ManualStrategy(Strategy):

    def get_position_of_initial_card_flips(self):
        print("Which cards do you wish to start with?")
        # TODO: Read and parse user input!

    def decide_draw_location(self, player_grids, discard_stack):
        print("Where do you want to draw a card? (draw stack or discard stack)")
        # TODO: Read and parse user input!

    def get_target_location(self, player_grids, discard_stack, new_card):
        print("Which card do you want to replace with the card drawn card?")
        # TODO: Read and parse user input!


class LocalOptimumStrategy(Strategy):

    def get_position_of_initial_card_flips(self):
        return [(1, 1), (2, 1)]

    def decide_draw_location(self, player_grids, discard_stack):
        expected_card_value = calculate_expected_card_value(player_grids, discard_stack)

        if discard_stack[-1] < expected_card_value:
            return DRAW_LOCATION.DISCARD_STACK
        else:
            return DRAW_LOCATION.DRAW_STACK

    def get_target_location(self, player_grids, discard_stack, new_card):
        own_grid = player_grids[self.name]
        expected_card_value = calculate_expected_card_value(player_grids, discard_stack + [new_card])

        hidden_location = None

        first_card = own_grid.columns[0].cards[0]

        best_move = (0, 0)
        if first_card.is_revealed:
            best_score = first_card.value - new_card
        else:
            best_score = expected_card_value - new_card

        for column_index in range(len(own_grid.columns)):
            for row_index in range(3):
                card = own_grid.columns[column_index].cards[row_index]
                location = (column_index, row_index)
                if card.is_revealed:
                    score = card.value - new_card
                else:
                    hidden_location = (column_index, row_index)
                    score = expected_card_value - new_card

                if score > best_score:
                    best_score = score
                    best_move = location

        if best_score > 0:
            return SkyjoGameMove(best_move[0], best_move[1], replace_card=True)
        return SkyjoGameMove(hidden_location[0], hidden_location[1], replace_card=False)


class ColumnFirstStrategy(Strategy):
    def __init__(self):
        self.columns_in_progress = [None, None, None, None]

    def get_position_of_initial_card_flips(self):
        return [(1, 1), (2, 1)]

    def decide_draw_location(self, player_grids, discard_stack):
        own_grid = player_grids[self.name]
        discard_stack_card = discard_stack[-1]
        revealed_cards_statistics = create_card_statistic(discard_stack, player_grids)
        expected_card_value = calculate_expected_card_value(player_grids, discard_stack)

        if discard_stack_card <= 0:
            return DRAW_LOCATION.DISCARD_STACK

        values = []

        for column in own_grid.columns:
            for card in column.cards:
                if card.get_value() is not None:
                    values.append(card.value)

        if discard_stack_card in values and revealed_cards_statistics[discard_stack_card] <= 5:
            return DRAW_LOCATION.DISCARD_STACK

        if discard_stack_card < expected_card_value:
            return DRAW_LOCATION.DISCARD_STACK

        return DRAW_LOCATION.DRAW_STACK

    def get_target_location(self, player_grids, discard_stack, new_card):
        # TODO: find possible columns
        # TODO: if found: find best position (local optimum)
        # TODO: else: calculate local optimum
        return SkyjoGameMove(0, 0, True)
