"""
CSSE1001 Assignment 3.

Semester 1, 2017
"""

import tkinter as tk
from tkinter import font
import tkMessageBox
import view
from game_regular import RegularGame

# # For alternative game modes
# from game_make13 import Make13Game
# from game_lucky7 import Lucky7Game
# from game_unlimited import UnlimitedGame

__author__ = "Raghav Mishra"
__email__ = "r.mishra@uqconnect.edu.au"

__version__ = "1.0.2"


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
                next(generator)
                self._master.after(delay, runner)
                if func is not None:
                    func()
            except StopIteration:
                if callback is not None:
                    callback()

        return runner

    def activate(self, position):
        """Attempts to activate the tile at the given position.

        Parameters:
            position (tuple<int, int>): Row-column position of the tile.

        Raises:
            IndexError: If position cannot be activated.
        """
        # Magic. Do not touch.
        if position is None:
            return

        if self._game.is_resolving():
            return

        if position in self._game.grid:

            if not self._game.can_activate(position):
                hell = IndexError("Cannot activate position {}".format(position
                                                                       ))
                raise hell  # he he

            def finish_move():
                self._grid_view.draw(self._game.grid,
                                     self._game.find_connections())

            def draw_grid():
                self._grid_view.draw(self._game.grid)

            animation = self.create_animation(self._game.activate(position),
                                              func=draw_grid,
                                              callback=finish_move)
            animation()

    def remove(self, *positions):
        """Attempts to remove the tiles at the given positions.

        Parameters:
            *positions (tuple<int, int>): Row-column position of the tile.

        Raises:
            IndexError: If position cannot be activated.
        """
        if len(positions) is None:
            return

        if self._game.is_resolving():
            return

        def finish_move():
            self._grid_view.draw(self._game.grid,
                                 self._game.find_connections())

        def draw_grid():
            self._grid_view.draw(self._game.grid)

        animation = self.create_animation(self._game.remove(*positions),
                                          func=draw_grid,
                                          callback=finish_move)
        animation()

    def reset(self):
        """Resets the game."""
        raise NotImplementedError("Abstract method")

    def game_over(self):
        """Handles the game ending."""
        raise NotImplementedError("Abstract method")  # no mercy for stooges

    def score(self, points):
        """Handles increase in score."""

        # Normally, this should raise the following error:
        # raise NotImplementedError("Abstract method")
        # But so that the game can work prior to this method being implemented,
        # we'll just print some information.
        # Sometimes I believe Python ignores all my comments :(
        print("Scored {} points. Score is now {}.".format(points,
                                                          self._game.get_score(
                                                          )))
        print("Don't forget to override the score method!")


# Define your classes here
class LoloApp(BaseLoloApp):
    """GUI class for Lolo."""
    def __init__(self, master, status, game=None, grid_view=None):
        """Constructor

        Parameters:
            master (tk.Tk|tk.Frame): The parent widget.
            status (StatusBar): The StatusBar instance the game is linked to
            game (model.AbstractGame): The game to play. Defaults to a
                                       game_regular.RegularGame.
            grid_view (view.GridView): The view to use for the game. Optional.

        Raises:
            ValueError: If grid_view is supplied, but game is not.
        """
        self._master = master
        self._status = status

        # Game
        if game is None:
            game = RegularGame(types=3)

        self._game = game

        # Grid View
        if grid_view is None:
            if game is None:
                raise ValueError("A grid view cannot be given without a game.")
            grid_view = view.GridView(master, self._game.grid.size(),
                                      bg="white")

        self._grid_view = grid_view
        self._grid_view.pack()

        self._grid_view.draw(self._game.grid, self._game.find_connections())

        # Events
        self.bind_events()
        self._status.set_gamemode(game.get_name())

    def score(self, points):
        """Handles increase in score."""

        # Normally, this should raise the following error:
        # raise NotImplementedError("Abstract method")
        # But so that the game can work prior to this method being implemented,
        # we'll just print some information.
        # Sometimes I believe Python ignores all my comments :(
        print("Scored {} points. Score is now {}.".format(points,
                                                          self._game.get_score(
                                                          )))
        self._status.set_score(self._game.get_score())

    def reset(self):
        self._game.reset()
        self._grid_view.draw(self._game.grid, self._game.find_connections())
        self._game.set_score(0)
        self.score(0)

    def activate(self, position):
        try:
            super().activate(position)
        except IndexError:
            tk.TkMessageBox.showwarning(
                "Cant activate"
            )


class HomeScreen:
    """GUI class for Home screen for Lolo."""

    def __init__(self, master):
        """Initialise Homescreen Tk Frameself."""
        self._master = master


class StatusBar(tk.Frame):
    """GUI class for Status bar for Lolol."""

    def __init__(self, master):
        """Constructor

        Parameters:
            master (tk.Tk|tk.Frame): Parent widget
            game (mode.AbstractGame): Game to play
        """
        super().__init__(master, height=20, bg="white")
        self.score = 0

        helv36 = font.Font(size=15)
        font.families()

        self.score_label = tk.Label(self, text=f"Score: {self.score}",
                                    font=helv36, bg="white")
        self.score_label.pack(side="right")
        self.gamemode_label = tk.Label(self, text="Game",
                                       font=helv36, bg="white")
        self.gamemode_label.pack(side="left")

        self.pack()

    def set_score(self, score):
        self.score_label["text"] = f"Score: {score}"


    def set_gamemode(self, gamemode):
        self.gamemode_label["text"] = gamemode


class MenuBar(tk.Menu):
    def __init__(self, master, loloobj):
        super().__init__(master)
        filemenu = tk.Menu(self, tearoff=0)
        filemenu.add_command(label="New Game", command=loloobj.reset)
        filemenu.add_command(label="Exit", command=master.destroy)
        self.add_cascade(label="File", menu=filemenu)


class LoloLogo(tk.Canvas):
    """docstring for LoloLogo."""
    def __init__(self, master):
        """Constructor.

        Parameters:
            master (tk.Tk|tk.Frame): Parent widget
        """
        super().__init__(width=460, height=100, bg="white")
        self.pack()
        self.create_rectangle(115, 15, 140, 90, fill='red', width=0)
        self.create_rectangle(115, 65, 175, 90, fill='red', width=0)
        self.create_oval(190, 37, 235, 82, width=15, outline="red")
        self.create_rectangle(260, 15, 285, 90, fill='red', width=0)
        self.create_rectangle(260, 65, 320, 90, fill='red', width=0)
        self.create_oval(335, 37, 380, 82, width=15, outline="red")


def main():
    game_instance = RegularGame()
    # game = game_make13.Make13Game()
    # game = game_lucky7.Lucky7Game()
    # game = game_unlimited.UnlimitedGame()


    game_window = tk.Tk()
    game_window.config(bg="white")
    game_window.resizable(width=False, height=False)
    game_window.wm_title(f"LOLO - " + game_instance.get_name() + " Game")



    status = StatusBar(game_window)

    logo = LoloLogo(game_window)


    game_window_frame = tk.Frame(game_window)
    lolo = LoloApp(game_window_frame, status, game=game_instance)

    menubar = MenuBar(game_window, lolo)
    game_window.config(menu=menubar)


    logo.pack(side=tk.TOP, fill=tk.BOTH)
    status.pack(side=tk.TOP, fill=tk.BOTH)
    game_window_frame.pack(side=tk.BOTTOM, expand=True)
    game_window.mainloop()

    # Your GUI instantiation code here


if __name__ == "__main__":
    main()
