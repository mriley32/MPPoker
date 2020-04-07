"""Game manages the poker game and the state of the players."""

import enum

MAX_PLAYERS = 10

class GameFullError(Exception):
    pass


class NoSuchPlayerError(Exception):
    def __init__(self, player_idx):
        self.player_idx = player_idx

        
class Player:
    """Player represents the state of of the player.

    Note that this does not cover the state inside of a deal"""

    def __init__(self, name, stack):
        self.name = name
        self.stack = stack
        self.position = None

    def __str__(self):
        return "Player({}, {}, {})".format(
            self.name, self.stack, self.position)
        
@enum.unique
class EventType(enum.Enum):
    PLAYER_ADDED = 0
    PLAYER_REMOVED = 1        

class Event:
    """Events are for communicating out what has happened.

    In order to keep a clean interface between the Manager and the
    parts of the system that need to respond to changes in the game,
    objects can subscribe as listeners in a Manager and be passed
    Event objects telling them all the important things in the game.
    
    Attributes:
      event_type: the type of event (one of the enum EventType)
      args: a dictionary with the arguments for this event. The expected contents
            are documented below

    Expected arguments by type:
      PLAYER_ADDED: player(of type Player)
      PLAYER_REMOVED: player(of type Player)
    """

    
    def __init__(self, event_type, **kwargs):
        self.event_type = event_type
        self.args = kwargs

    def __str__(self):
        args_strs = []
        for key in sorted(self.args.keys()):
            args_strs.append("{}={}".format(key, self.args[key]))
        return "Event({}, {})".format(self.event_type, ", ".join(args_strs))

        
class Manager:
    """Manager is the main class for managing the flow of the game.

    See the Event documention for a discussion of the listener setup.

    Note that the notication should happen as the last possible thing in the
    various acitivities. The listeners may want to access the state of the Manager
    in response to a notificaiton, so the Manager needs to be in a clean state.
    """

    def __init__(self):
        self.players = [None] * MAX_PLAYERS
        self.listeners = []

    def add_listener(self, listener):
        """Adds an Event listener.
        
        Args:
          listener: The only requirement on listener is that it has a notify
                    method that accepts one positional Event argument.
        """
        self.listeners.append(listener)
        
    def add_player(self, player):

        """Add a player to the game

        Args:
          player: Player to add

        Returns:
          integer for player position

        Raises:
          GameFullError: if no spots remain
        """
        for idx in range(MAX_PLAYERS):
            if self.players[idx]:
                continue
            player.position = idx
            self.players[idx] = player
            self._notify(Event(EventType.PLAYER_ADDED, player=player))
            return idx
        
        raise GameFullError()

    def remove_player(self, player_idx):
        """Removes a player from the game

        Args:
          player_idx: integer index of player to remove

        Returns:
          Player object

        Raises:
          NoSuchPlayer: if there is no player in that position"""
        try:
            if self.players[player_idx] is None:
                raise NoSuchPlayerError(player_idx)
        except IndexError:
            raise NoSuchPlayerError(player_idx)
        
        removed = self.players[player_idx]
        self.players[player_idx] = None

        self._notify(Event(EventType.PLAYER_REMOVED, player=removed))
        
        return removed

    def _notify(self, event):
        for listener in self.listeners:
            listener.notify(event)


class RecordingListener:
    """A simple listener that just records all events."""
    def __init__(self):
        self.events = []

    def clear(self):
        self.events.clear()
        
    def notify(self, event):
        self.events.append(event)
