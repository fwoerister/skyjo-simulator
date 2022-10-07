from skyjosimulator import DRAW_LOCATION


class SkyjoGameState:
    def __init__(self, draw_stack, player_grids):
        self.draw_stack = draw_stack
        self.discard_stack = []
        self.player_grids = player_grids

    def initialize_discard_stack(self):
        self.discard_stack.append(self.draw_stack.pop())

    def get_current_state(self):
        revealed_values = dict()

        for player in self.player_grids:
            revealed_values[player] = self.player_grids[player].to_list()

        return revealed_values

    def apply_move(self, player, draw_location, target_location):
        grid = self.player_grids[player]

        if draw_location == DRAW_LOCATION.DRAW_STACK:
            drawn_card = self.draw_stack.pop()
        else:
            drawn_card = self.discard_stack.pop()

        if target_location.replace_card:
            value_to_discard = grid.replace_card((target_location.column, target_location.row), drawn_card)
            self.discard_stack.append(value_to_discard)
        else:
            self.discard_stack.append(drawn_card)
            grid.reveal_card(target_location.column, target_location.row)

    def player_has_finished(self, player):
        grid = self.player_grids[player]
        return grid.all_cards_revealed()

    def draw_n_cards(self, n):
        drawn_cards = self.draw_stack[-n:]
        self.draw_stack = self.draw_stack[:-n]
        return drawn_cards

    def reveal_all_cards(self):
        for player_grid in self.player_grids.values():
            player_grid.reveal_all_cards()

    def flip_cards(self, player, positions):
        grid = self.player_grids[player]
        for position in positions:
            grid.reveal_card(position[0], position[1])

    def remove_columns_with_identical_cards(self, player):
        grid = self.player_grids[player]

        for column in grid.columns:
            if column.is_removeable():
                grid.columns.remove(column)

    def calculate_scores(self):
        scores = dict()
        for player in self.player_grids:
            scores[player] = self.player_grids[player].calculate_current_score()
        return scores


class CardGrid:
    def __init__(self, columns: list):
        self.columns = columns

    def all_cards_revealed(self):
        for column in self.columns:
            if not column.all_cards_revealed():
                return False
        return True

    def reveal_card(self, column_index, row_index):
        column = self.columns[column_index]
        column.reveal_card(row_index)

    def reveal_all_cards(self):
        for column in self.columns:
            column.reveal_all_cards()

    def replace_card(self, position, value):
        column = self.columns[position[0]]
        value_to_discard = column.replace_card(position[1], value)
        return value_to_discard

    def calculate_current_score(self):
        score = 0
        for column in self.columns:
            score += column.calculate_current_score()
        return score

    def to_list(self):
        grid_list = list()

        for col in self.columns:
            grid_list.append(col.to_list())

        return grid_list


class CardColumn:
    def __init__(self, cards: list):
        self.cards = cards

    def is_removeable(self):
        value_of_first_card = None

        for card in self.cards:
            if not value_of_first_card:
                value_of_first_card = card.value
            elif card.value != value_of_first_card or not card.is_revealed:
                return False
        return True

    def all_cards_revealed(self):
        for card in self.cards:
            if not card.is_revealed:
                return False
        return True

    def reveal_card(self, row_index):
        card = self.cards[row_index]
        card.is_revealed = True

    def reveal_all_cards(self):
        for card in self.cards:
            card.is_revealed = True

    def replace_card(self, row_index, value):
        card = self.cards[row_index]
        value_to_discard = card.value
        card.value = value
        card.is_revealed = True
        return value_to_discard

    def calculate_current_score(self):
        score = 0
        for card in self.cards:
            if card.is_revealed:
                score += card.value
        return score

    def to_list(self):
        return [card.get_value() for card in self.cards]


class Card:
    def __init__(self, value, is_revealed=False):
        self.value = value
        self.is_revealed = is_revealed

    def get_value(self):
        if not self.is_revealed:
            return None
        return self.value
