from skyjosimulator.game.model import CardColumn, Card, CardGrid


class CardGridFactory:
    @staticmethod
    def create_grid(values):
        values_column1 = values[0:3]
        values_column2 = values[3:6]
        values_column3 = values[6:9]
        values_column4 = values[9:12]

        column1 = CardColumn([Card(value) for value in values_column1])
        column2 = CardColumn([Card(value) for value in values_column2])
        column3 = CardColumn([Card(value) for value in values_column3])
        column4 = CardColumn([Card(value) for value in values_column4])

        return CardGrid([column1, column2, column3, column4])
