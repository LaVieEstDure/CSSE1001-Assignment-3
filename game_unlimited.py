"""Modelling classes for Unlimited Lolo game mode."""

import math

import game_regular

__author__ = "Benjamin Martin and Brae Webb"
__copyright__ = "Copyright 2017, The University of Queensland"
__license__ = "MIT"
__version__ = "1.0.0"


class UnlimitedGame(game_regular.RegularGame):
    """Unlimited Lolo game.

    The goal of the game is to form the largest possible tile."""

    def __init__(self, size=(8, 8), types=4, min_group=3,
                 animation=True):
        """Constructor

        Parameters:
            size (tuple<int, int>): The number of (rows, columns) in the game.
            types (int): The number of tiles.
            min_group (int): The minimum number of tiles required for a
                             connected group to be joinable.
            animation (bool): If True, animation will be enabled.
        """

        super().__init__(size=size, types=types, min_group=min_group,
                         animation=animation)

    def _construct_tile(self, type, position):
        """(RegularTile) Returns a randomly generated tile."""
        return game_regular.RegularTile(type, max_value=math.inf)

    def update_score_on_activate(self, current, connections):
        if current.get_value() > self._score:
            # Update score
            score = current.get_value()
            self._score = score

            self.increase_score(score)
