"""Game manages the poker game and the state of the players."""

import enum
import random

import cards
import deck

MAX_PLAYERS = 10

class GameFullError(Exception):
    pass


class NoSuchPlayerError(Exception):
    def __init__(self, player_idx):
        self.player_idx = player_idx

class NotEnoughPlayersError(Exception):
    pass

class WrongStateError(Exception):
    def __init__(self, expected, actual):
        self.expected_state = expected
        self.actual_state = actual

class NotReadyError(Exception):
    pass

class WaitingForStartError(NotReadyError):
    pass

        
class Player:
    """Player represents the state of of the player.

    Note that this does not cover the state inside of a deal."""

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
    """Events are for communicating out what has happened in the game.

    In order to keep a clean interface between the Manager and the
    parts of the system that need to respond to changes in the game,
    objects can subscribe as listeners in a Manager and be passed
    Event objects telling them when things happen in the game.
    
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

    
class HandPlayer:
    """Controls the state of a player for one deal/pot."""
    def __init__(self, player):
        """Initialize HandPLayer
        
        Args:
          player: Player
        """
        self.base_player = player
        self.initial_stack = player.stack
        self.cards = None
        
        
class Hand:
    """Hnad controls the state for one deal/pot."""
    def __init__(self, players, button_pos):
        self.deck = deck.Deck()
        self.players = [HandPlayer(p) for p in players]
        self.button_pos = button_pos
        self.board = cards.Cards()
        if self.players[button_pos] is None:
            raise ValueError("No player on button {}".format(button_pos))

        
@enum.unique
class GameState(enum.Enum):
    WAITING_FOR_START = 0
    PRE_DEAL = 1
    HOLE_CARDS_DEALT = 2
    FLOP_DEALT = 3
    TURN_DEALT = 4
    RIVER_DEALT = 5
    SHOWDOWN = 6
    PAYING_OUT = 7
    
    
class Manager:
    """Manager is the main class for managing the flow of the game.

    See the Event documention for a discussion of the listener setup.

    Note that the notication should happen as the last possible thing in the
    various functions. The listeners may want to access the state of the Manager
    in response to a notificaiton, so the Manager needs to be in a clean state.

    The manager has a core concept of a current state. THe state
    proceeds under various actions / conditions as below. The main way
    to continue the game is to call proceed(). If the game can
    proceed, an exception derived from NotReadyError will be raised.

    WAITING_FOR_START: to PRE_DEAL on start_game()
    PRE_DEAL: to HOLE_CARDS_DEALT on proceed()
    HOLE_CARDS_DEALT: to FLOP_DEALT on proceed()
    FLOP_DEALT: to TURN_DEALT on proceed()
    RIVER_DEALT: to SHOWDOWN on proceed()
    SHOWDOWN: to PAYING_OUT on proceed()
    PAYING_OUT: to PRE_DEAL or WAITING_FOR_START depending on number of player
        on proceed()
    """

    def __init__(self):
        self.players = [None] * MAX_PLAYERS
        self.button_pos = None
        self.state= GameState.WAITING_FOR_START
        self.current_hand = None
        self._listeners = []

    def add_listener(self, listener):
        """Adds an Event listener.
        
        Args:
          listener: The only requirement on listener is that it has a notify
                    method that accepts one positional Event argument.
        """
        self._listeners.append(listener)
        
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

    def num_players(self):
        return sum(1 for p in self.players if p is not None)
    
    def start_game(self):
        if self.state != GameState.WAITING_FOR_START:
            raise WrongStateError(GameState.WAITING_FOR_START, self.state)
        if self.num_players() <= 1:
            raise NotEnoughPlayersError()
        self._advance_button()
        self._create_hand()
        self.state = GameState.PRE_DEAL

    def proceed(self):
        if self.state == GameState.WAITING_FOR_START:
            raise WaitingForStartError()
        elif self.state == GameState.PRE_DEAL:
            # TODO: create the Hand, deal the cards
            self.state = GameState.HOLE_CARDS_DEALT
        elif self.state == GameState.HOLE_CARDS_DEALT:
            # TODO: deal flop
            self.state = GameState.FLOP_DEALT
        elif self.state == GameState.FLOP_DEALT:
            # TODO: deal turn
            self.state = GameState.TURN_DEALT
        elif self.state == GameState.TURN_DEALT:
            # TODO: deal river
            self.state = GameState.RIVER_DEALT
        elif self.state == GameState.RIVER_DEALT:
            # TODO: rank the hands, pick winner
            self.state = GameState.SHOWDOWN
        elif self.state == GameState.SHOWDOWN:
            self.state = GameState.PAYING_OUT
        elif self.state == GameState.PAYING_OUT:
            # TODO: destroy the Hand, deal with the payout,
            # (maybe) create new Hand
            if self.num_players() > 1:
                self.state = GameState.PRE_DEAL
            else:
                self.state = GameState.WAITING_FOR_START
        else:
            raise ValueError("Unknown state {}".format(self.state))
        
    def _advance_button(self):
        if self.button_pos is None:
            if self.num_players() == 0:
                raise NotEnoughPlayersError()
            self.button_pos = random.choice(
                [i for i, p in enumerate(self.players) if p is not None])
        else:
            chosen_button = None
            for offset in range(1, MAX_PLAYERS + 1):
                try_pos = (self.button_pos + offset) % MAX_PLAYERS
                if self.players[try_pos] is not None:
                    chosen_button = try_pos
                    break
            if chosen_button is None:
                self.button_pos = None
                raise NotEnoughPlayersError()
            self.button_pos = chosen_button
        
    def _create_hand(self):
        if self.current_hand is not None:
            raise ValueError("Can not create hand while one in progress")
        self.current_hand = Hand(self.players, self.button_pos)
            
    def _notify(self, event):
        for listener in self._listeners:
            listener.notify(event)


class RecordingListener:
    """A simple listener that just records all events."""
    def __init__(self):
        self.events = []

    def clear(self):
        self.events.clear()
        
    def notify(self, event):
        self.events.append(event)
