"""
CSSE1001 Assignment 3
Semester 1, 2017
"""

import tkinter as tk
from tkinter import messagebox

import model
import view
from game_regular import RegularGame

__author__ = "<Your name here>"
__email__ = "<Your student email here>"

__version__ = "1.0.0"


# Once you have created your basic gui (LoloApp), you can delete this class
# and replace it with the following:
# from base import BaseLoloApp
class BaseLoloApp:
    """Base class for a simple Lolo game."""

    def __init__(self, master, game=None, grid_view=None):
        """Constructor

        Parameters:
            master (tk.Tk|tk.Frame): The parent widget.
            game (model.AbstractGame): The game to play. Defaults to a
                                       game_regular.RegularGame.
            grid_view (view.GridView): The view to use for the game. Optional.

        Raises:
            ValueError: If grid_view is supplied, but game is not.
        """
        self._master = master

        # Game
        if game is None:
            game = RegularGame(types=3)

        self._game = game

        # Grid View
        if grid_view is None:
            if game is None:
                raise ValueError("A grid view cannot be given without a game.")
            grid_view = view.GridView(master, self._game.grid.size())

        self._grid_view = grid_view
        self._grid_view.pack()

        self._grid_view.draw(self._game.grid, self._game.find_connections())

        # Events
        self.bind_events()

    def bind_events(self):
        """Binds relevant events."""
        self._grid_view.on('select', self.activate)
        self._game.on('game_over', self.game_over)
        self._game.on('score', self.score)

    def create_animation(self, generator, delay=200, func=None, callback=None):
        """Creates a function which loops through a generator using the tkinter
        after method to allow for animations to occur

        Parameters:
            generator (generator): The generator yielding animation steps.
            delay (int): The delay (in milliseconds) between steps.
            func (function): The function to call after each step.
            callback (function): The function to call after all steps.

        Return:
            (function): The animation runner function.
        """

        def runner():
            try:
                value = next(generator)
                self._master.after(delay, runner)
                if func is not None:
                    func()
            except StopIteration:
                if callback is not None:
                    callback()

        return runner

    def activate(self, position):
        """Attempts to activate tile at a given position.

        Parameters:
            position (tuple<int, int>): Row-column position of the tile.
            """
        if position is None:
            return

        if self._game.is_resolving():
            return

        if position in self._game.grid:

            if not self._game.can_activate(position):
                return messagebox.showwarning("Can't Activate",
                                              "Cannot activate position {}"
                                              .format(position))

            def finish_move():
                self._grid_view.draw(self._game.grid,
                                     self._game.find_connections())

            def draw_grid():
                self._grid_view.draw(self._game.grid)

            animation = self.create_animation(self._game.activate(position),
                                              func=draw_grid,
                                              callback=finish_move)
            animation()

    def reset(self):
        """Resets the game."""
        raise NotImplementedError("Abstract method")

    def game_over(self):
        """Handles the game ending."""
        raise NotImplementedError("Abstract method")

    def score(self, points):
        """Handles increase in score."""

        # Normally, this should raise the following error:
        # raise NotImplementedError("Abstract method")
        # But so that the game can work prior to this method being implemented,
        # we'll just print some information.
        print("Scored {} points. Score is now {}.".format(points,
                                                          self._game.get_score()))
        print("Don't forget to override the score method!")


# Define your classes here


def main():
    pass
    # Your GUI instantiation code here


if __name__ == "__main__":
    main()
