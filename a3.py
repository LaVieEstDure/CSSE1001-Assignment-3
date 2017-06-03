"""
CSSE1001 Assignment 3.

Semester 1, 2017
"""

import tkinter as tk
from tkinter import font
from tkinter import messagebox
import highscores
import view
from game_regular import RegularGame
import random
from time import sleep
from tkinter import Label
from game_make13 import Make13Game
from game_lucky7 import Lucky7Game
from game_unlimited import UnlimitedGame

__author__ = "Raghav Mishra"
__email__ = "r.mishra@uqconnect.edu.au"

__version__ = "1.0.2"

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
                hell = IndexError("Cannot activate position {}".format(position))
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
                                                          self._game.get_score()))
        print("Don't forget to override the score method!")

class LoloApp(BaseLoloApp):
    """GUI class for Lolo."""
    def __init__(self, master, status, playername, game=None, grid_view=None):
        """Constructor

        Parameters:
            master (tk.Tk|tk.Frame): The parent widget.
            status (StatusBar): The StatusBar instance the game is linked to
            game (model.AbstractGame): The game to play. Defaults to a
                                       game_regular.RegularGame.
            playername (str): Name of player
            grid_view (view.GridView): The view to use for the game. Optional.

        Raises:
            ValueError: If grid_view is supplied, but game is not.
        """
        super().__init__(master, game, grid_view)
        self.master = master
        self._status = status
        self.playername = playername
        self._status.set_gamemode(game.get_name())
        self._grid_view.config(bg="white")
        self.num_lights = tk.IntVar()
        self.num_lights.set(1)
        self.lightning_on = False
        self.counter = 0
        self.cant_acivate_error = messagebox.Message(
            message="Cannot activate position!")
        self.game_over_error = messagebox.Message(
            message="Game over!")

    def score(self, points):
        """Handles increase in score.
        Parameters:
        points (int) - Number of points"""

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
        self.num_lights.set(1)

    def activate(self, position):
        """Activates tile at position
        position (tuple) - position on grid
        """
        if self.lightning_on:
            super().remove(position)
            self.lightning_on = False
            self._master.config(cursor="")
            self.num_lights.set(self.num_lights.get()-1)
            print(self.num_lights.get())
        else:
            try:
                super().activate(position)
                self.counter += 1
                if self.counter > 5:
                    self.num_lights.set(self.num_lights.get()+1)
                    counter = 0
            except IndexError:
                self.cant_acivate_error.show()

    def quit(self, *args):
        self.master.destroy()

    def game_over(self):
        hs_manager = highscores.HighScoreManager()
        data = hs_manager.data
        gameoverdata = self._game.serialize()
        if hs_manager.get_sorted_data()[-1]["score"] < self._game.get_score:
            hs_manager.record(self._game.get_score(),
                              gameoverdata, name=self.playername)
        self.game_over_error.show()


class AutoPlayingGame(BaseLoloApp):
    """Autoplaying game. Plays itself by choosing random tile"""
    def __init__(self, master, **kwargs):
        """
        Parameters:
        master(Tk,Tk|Tk.Frame) - master window
        """
        super().__init__(master, **kwargs)
        self.activate_random()
        self._grid_view.pack(side="right")

    def bind_events(self):
        self._game.on('game_over', self.reset)
        self._game.on('resolve', lambda: self._master.after(1000,
                                                        self.activate_random))

    def activate_random(self, *args):
        # *args needed to fix unexplainable tkinter callback argument errors
        try:
            list = []
            for i in self._game.find_groups():
                list.append(i)
            randomtile = random.sample(random.choice(list), 1)
            self.activate(randomtile[0])
        except IndexError:
            print("No moves left!")

    def reset(self):
        self._game.reset()
        self._grid_view.draw(self._game.grid, self._game.find_connections())


class LightningButton(tk.Button):
    """Lightning button class. Takes care of the lightning button
    """
    def __init__(self, master, game):
        """
        Parameters:
        master (Tk|Tk.Frame) - master window
        game (AbstractGame) - Game mode
        """
        super().__init__(master, text=f"Lighting[{game.num_lights.get()}]",
                         command=self.press)
        self.game = game
        self.pack()
        self.game.num_lights.trace("w", self.update)

    def press(self, *args):
        self.game.lightning_on = not self.game.lightning_on
        if self.master["cursor"] == "":
            self.master.config(cursor="X_cursor")
        else:
            self.master.config(cursor="")

    def update(self, *args):
        self.config(text=f"Lighting[{self.game.num_lights.get()}]")
        if self.game.num_lights.get() == 0:
            self.config(state="disabled")
        else:
            self.config(state="active")

class HomeScreen(tk.Tk):
    """GUI class for Home screen for Lolo."""

    def __init__(self, game):
        """Initialise Homescreen Tk Frameself.
        Parameters:
        game (AbstractGame) - Game mode"""
        super().__init__()
        self.game = game
        self.minsize(700, 600)
        self.wm_title('LOLO')

        LoloLogo(self)
        auto = AutoPlayingGame(self)

        play_game = tk.Button(self, text="Play game",
                              command=self.play_game)
        play_game.place(relx=0.15, rely=0.3, anchor=tk.CENTER)

        highscores = tk.Button(self, text="Highscores", command=self.hs)
        highscores.place(relx=0.15, rely=0.4, anchor=tk.CENTER)

        exit = tk.Button(self, text="Exit", command=self.exit)
        exit.place(relx=0.15, rely=0.5, anchor=tk.CENTER)

        self.name = tk.StringVar()
        self.name.set("Anon")
        name_entry = tk.Entry(self, textvariable=self.name)
        name_entry.pack()


        self.gamemode = tk.StringVar()
        self.gamemode.set("Regular")
        gamemodeselect = tk.OptionMenu(self, self.gamemode, "Regular",
                                       "Lucky 7", "Make 13", "Unlimited")
        gamemodeselect.place(anchor=tk.NW)
        self.mainloop()

    def play_game(self):
        self.destroy()
        self.game(self.gamemode, self.name.get())

    def hs(self):
        self.destroy()
        hs = HighScore()

    def exit(self):
        self.after_cancel()
        self.destroy()

class HighScore(tk.Tk):
    def __init__(self):
        """
        Creates the high score window
        """
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.wm_title('LOLO - High scores')
        self.title = tk.Label(self, text="Highscores", font=("Helvetica",
                                                             20, "bold"))
        self.title.pack()
        self.hs_manager = highscores.HighScoreManager()
        self.data = self.hs_manager.get_sorted_data()

        self.highest = self.data[0]
        self.highestname = self.highest["name"]
        self.highestscore = self.highest["score"]
        self.grid = self.highest["grid"]
        self.best_player = tk.Label(self, text=f"The best player {self.highestname} is with {self.highestscore} points!")
        self.game = RegularGame.deserialize(self.grid)

        highest_score_frame = tk.Frame(self)
        highest_score_frame.pack()

        leaderboard = tk.Label(highest_score_frame, text="Leaderboard")
        leaderboard.pack(side="bottom")


        high_score_lists = tk.Frame(self)
        high_score_lists.pack(fill=tk.BOTH)

        self.static_grid = AutoPlayingGame(highest_score_frame, game=self.game)


        name_list = ""
        score_list = ""
        for i in range(10):
            name_list += self.data[i]["name"] + "\n"
            score_list += str(self.data[i]["score"]) + "\n"

        names = Label(high_score_lists, text=name_list)
        scores = Label(high_score_lists, text=score_list)
        names.pack(side="left")
        scores.pack(side="right")
        self.mainloop()

    def quit(self):
        self.destroy()
        HomeScreen(Game)


class StatusBar(tk.Frame):
    """GUI class for Status bar for Lolol."""

    def __init__(self, master):
        """Constructor

        Parameters:
            master (tk.Tk|tk.Frame): Parent widget
            game (mode.AbstractGame): Game to play
        """
        super().__init__(master, height=20, bg="white", relief='flat', borderwidth=0)
        self.score = 0

        helv36 = font.Font(size=15)
        font.families()

        self.score_label = tk.Label(self, text=f"Score: {self.score}",
                                    font=helv36, bg="white")
        self.score_label.pack(side="right")
        self.gamemode_label = tk.Label(self, text="Game",
                                       font=helv36, bg="white")
        self.gamemode_label.pack(side="left")

        self.pack(side=tk.TOP, fill=tk.BOTH)

    def set_score(self, score):
        self.score_label["text"] = f"Score: {score}"


    def set_gamemode(self, gamemode):
        self.gamemode_label["text"] = gamemode


class MenuBar(tk.Menu):
    def __init__(self, master, loloobj):
        """
        Menubar for root window
        Parameters:
        master (Tk) - root window
        loloobj (LoloApp) - Associated game
        """
        super().__init__(master)
        filemenu = tk.Menu(self, tearoff=0)
        filemenu.add_command(label="New Game", command=loloobj.reset)
        filemenu.add_command(label="Exit", command=master.destroy)
        self.add_cascade(label="File", menu=filemenu)


class LoloLogo(tk.Canvas):
    """docstring for LoloLogo."""
    def __init__(self, master):
        """Lolo logo

        Parameters:
            master (tk.Tk|tk.Frame): Parent widget
        """
        super().__init__(width=460, height=100, bg="white", relief='flat', borderwidth=0)
        self.pack()
        self.create_rectangle(115, 15, 140, 90, fill='red', width=0)
        self.create_rectangle(115, 65, 175, 90, fill='red', width=0)
        self.create_oval(190, 37, 235, 82, width=15, outline="red")
        self.create_rectangle(260, 15, 285, 90, fill='red', width=0)
        self.create_rectangle(260, 65, 320, 90, fill='red', width=0)
        self.create_oval(335, 37, 380, 82, width=15, outline="red")
        self.pack(side=tk.TOP, fill=tk.BOTH)

class Game:
    """Game class. Contains game code"""
    def __init__(self, game_name, player_name):
        """
        Parameters:
        game_name (str) - name of game_name
        player_name (str) - name of player
        """
        gamemode = {
            "Regular": RegularGame,
            "Make 13": Make13Game,
            "Unlimited": UnlimitedGame,
            "Lucky 7": Lucky7Game
        }
        game_instance = gamemode[game_name.get()]()

        game_window = tk.Tk()
        game_window.config(background="white")
        game_window.resizable(width=False, height=False)
        game_window.wm_title(f"LOLO - " + game_instance.get_name() + " Game")

        status = StatusBar(game_window)

        logo = LoloLogo(game_window)


        lolo = LoloApp(game_window, status, player_name, game=game_instance)

        menubar = MenuBar(game_window, lolo)
        game_window.config(menu=menubar)
        lightning = LightningButton(game_window, lolo)

        game_window.bind('<Control-l>', lightning.press)
        game_window.bind('<Control-q>', lolo.quit)

        game_window.mainloop()

def main():
        home = HomeScreen(Game)



if __name__ == "__main__":
    main()
