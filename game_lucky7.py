"""Modelling classes for Lucky 7 Lolo game mode."""

import game_regular
import game_make13

__author__ = "Benjamin Martin and Brae Webb"
__copyright__ = "Copyright 2017, The University of Queensland"
__license__ = "MIT"
__version__ = "1.0.2"


class LuckyTile(game_make13.LevelTile):
    """Tile whose value & type are equal, incrementing by one when joined."""

    def __init__(self, value=1, lucky=7):
        """Constructor

        Parameters:
             value (int): The tile's value.
             lucky (int): The value of a lucky (exploding) tile.
        """
        super().__init__(value)
        self._lucky = lucky

    def is_max(self):
        return self.get_value() == self._lucky

    def is_combo_max(self):
        return self.is_max()


class Lucky7Game(game_make13.Make13Game):
    """Lucky7 Lolo game.

    Groups of three or more can be combined to increase tile's value by one.

    When lucky 7 tiles are formed, they explode, removing surrounding tiles.
    """

    GAME_NAME = "Lucky 7"

    def __init__(self, size=(6, 6), initial_tiles=4, lucky_value=7, min_group=3,
                 animation=True, autofill=True):
        """Constructor

        Parameters:
            size (tuple<int, int>): The number of (rows, columns) in the game.
            initial_tiles (int): The number of tiles.
            lucky_value (int): The value of the lucky tile.
            min_group (int): The minimum number of tiles required for a
                             connected group to be joinable.
            animation (bool): If True, animation will be enabled.
            autofill (bool): Automatically fills the grid iff True.
        """

        self.lucky_value = lucky_value

        super().__init__(size=size, initial_tiles=initial_tiles,
                         goal_value=lucky_value + 1, min_group=min_group,
                         animation=animation, autofill=autofill)

    def reset(self):
        # super().reset()
        weights = {i: self.get_tile_weight(i) for i in
                   range(1, self.initial_tiles + 1)}
        self._selector.update(weights, clear=True)

    def _construct_tile(self, type, position):
        """(LuckyTile) Returns a randomly generated tile."""
        return LuckyTile(type, lucky=self.lucky_value)

    def update_score_on_activate(self, current, connections):
        value = current.get_value()

        if value == 1:
            score = 5
        elif value == self.lucky_value:
            score = (value - 2) * 20
        else:
            score = (value - 1) * 10

        self.set_score(self.get_score() + score)

    def activate(self, position):
        return game_regular.RegularGame.activate(self, position)
