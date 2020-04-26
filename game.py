"""Game manages the poker game and the state of the players."""

import enum
import random

import cards
import deck

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


def _none_or_func(f, x):
    """Return None if x is None, f(x) otherwise"""
    if x is None:
        return None
    return f(x)


class Configuration:
    """Data class for configuration of the game.

    Attributes:
      max_players: number of spots in the game
    """
    def __init__(self, max_players=10, ante=0):
        self.max_players = max_players
        self.ante = ante
    
    
class Player:
    """Player represents the state of of the player.

    Note that this does not cover the state inside of a hand.
    See HandPlayer for that.
    """

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
    WAITING_FOR_START = 2
    HAND_STARTED = 3
    ANTE = 4
    HOLE_CARDS_DEALT = 5
    FLOP_DEALT = 6
    TURN_DEALT = 7
    RIVER_DEALT = 8
    SHOWDOWN = 9
    PAYING_OUT = 10
    

class Event:
    """Events are for communicating out what has happened in the game.

    In order to keep a clean interface between the Manager and the
    parts of the system that need to respond to changes in the game,
    objects can subscribe as listeners in a Manager and be passed
    Event objects telling them when things happen in the game.

    If the listener is going to keep a reference to the data passed in
    the Event, they should make a copy because the underlying objects may be
    updated.

    Attributes:
      event_type: the type of event (one of the enum EventType)
      args: a dictionary with the arguments for this event. The expected contents
            are documented below

    Expected arguments by type:
      PLAYER_ADDED: player(of type Player)
      PLAYER_REMOVED: player(of type Player)
      WAITING_TO_START: None
      GAME_STARTED: players (array of HandPlayer)
      HOLE_CARDS_DEALT: cards (array of cards.PlayerCards)
      FLOP_DEALT: cards (cards.PlayerCards)
      TURN_DEALT: card (deck.Card)
      RIVER_DEALT: card (deck.Card)
      SHOWDOWN: ranks (array of array (as returned by cards.PlayerCards.hand_rank))
                winners (array of int)
      PAYING_OUT: pot_winnings (array of int (config.max_players size))
                  net_profit (array of int (config.max_players size))

    """
    def __init__(self, event_type, **kwargs):
        self.event_type = event_type
        self.args = kwargs

    def __str__(self):
        args_strs = []
        for key in sorted(self.args.keys()):
            args_strs.append("{}={}".format(key, self.args[key]))
        return "Event({}, {})".format(self.event_type, ", ".join(args_strs))


def _shuffled_deck_factory():
    d = deck.Deck()
    d.shuffle
    return d

class HandPlayer:
    """Controls the state of a player for one deal/pot."""
    def __init__(self, player):
        """Initialize HandPlayer

        Args:
          player: Player
        """
        self.base_player = player
        self.initial_stack = player.stack
        self.stack = player.stack
        self.hole_cards = None

    def __str__(self):
        return "HandPlayer({}, {}, {}, {})".format(
            self.base_player.name, self.initial_stack, self.stack,
            self.hole_cards is not None)


class Hand:
    """Hand controls the state for one hand/deal.

    Attributes:
      config: Configuration
      deck: deck.Deck
      players: array of None or HandPlayer
      button_pos: button position
      pot: amount in the pot
      board: cards.PlayerCards for the comunity cards
      ranks: ranks of all hands present at showdown
      winners: list of winners
    """
    def __init__(self, config, players, button_pos, deck_factory):
        """Creates the hand.

        Args:
          config: Configuration
          players: array of Player
          button_pos: integer button postion
          deck_factory: function which returns a deck.Deck (for injection during 
            unittests, normally it's shuffled_deck_factory)
        """
        self.config = config
        self.deck = deck_factory()
        self.players = [_none_or_func(HandPlayer, p) for p in players]
        self.button_pos = button_pos
        if self.players[button_pos] is None:
            raise ValueError("No player on button {}".format(button_pos))
        self.pot = 0
        self.board = cards.PlayerCards()
        self.ranks = None
        self.winners = None
        self.net_winnings = None

    def ante(self):
        if self.config.ante == 0:
            return None
        num_players = sum(1 for p in self.players if p is not None)
        self.pot += num_players * self.config.ante
        players_who_anted = []
        for pos, player in enumerate(self.players):
            if player is None:
                continue
            player.stack -= self.config.ante
            players_who_anted.append(pos)
        return players_who_anted
        
    def deal_hole_cards(self):
        for p in self.players:
            if p is None:
                continue
            p.hole_cards = cards.PlayerCards(self.deck.deal(2))

    def deal_flop(self):
        self.board.cards.extend(self.deck.deal(3))

    def deal_turn(self):
        self.board.cards.extend(self.deck.deal(1))

    def deal_river(self):
        self.board.cards.extend(self.deck.deal(1))

    def showdown(self):
        self.ranks = []
        for p in self.players:
            if p is None or p.hole_cards is None:
                self.ranks.append([cards.HandRank.NO_HAND])
                continue
            self.ranks.append(p.hole_cards.combine(self.board).hand_rank())
        best_hand = max(self.ranks)
        self.winners = [i for i, rank in enumerate(self.ranks) if rank == best_hand]
        for idx in self.winners:
            self.players[idx].stack += self.pot / len(self.winners)

        
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

    The manager has a core concept of a current state. The state
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

    def __init__(self, config):
        """Initializes Manager.

        Args:
          config: Configuration
        """
        self.config = config
        self.players = [None] * self.config.max_players
        self.button_pos = None
        self.state= GameState.WAITING_FOR_START
        self.current_hand = None
        self._listeners = []
        # Can be overridden for unittests
        self._deck_factory = _shuffled_deck_factory

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
        for idx in range(self.config.max_players):
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
        events = self._create_hand()
        self.state = GameState.PRE_DEAL
        for e in events:
            self._notify(e)

    def proceed(self):
        if self.state == GameState.WAITING_FOR_START:
            raise WaitingForStartError()

        elif self.state == GameState.PRE_DEAL:
            self.current_hand.deal_hole_cards()
            self.state = GameState.HOLE_CARDS_DEALT
            self._notify(Event(
                EventType.HOLE_CARDS_DEALT,
                cards=[_none_or_func(lambda p: p.hole_cards, p)
                       for p in self.current_hand.players]))

        elif self.state == GameState.HOLE_CARDS_DEALT:
            self.current_hand.deal_flop()
            self.state = GameState.FLOP_DEALT
            self._notify(Event(
                EventType.FLOP_DEALT,
                cards=self.current_hand.board))

        elif self.state == GameState.FLOP_DEALT:
            self.current_hand.deal_turn()
            self.state = GameState.TURN_DEALT
            self._notify(Event(
                EventType.TURN_DEALT,
                card=self.current_hand.board.cards[-1]))

        elif self.state == GameState.TURN_DEALT:
            self.current_hand.deal_river()
            self.state = GameState.RIVER_DEALT
            self._notify(Event(
                EventType.RIVER_DEALT,
                card=self.current_hand.board.cards[-1]))

        elif self.state == GameState.RIVER_DEALT:
            self.current_hand.showdown()
            self.state = GameState.SHOWDOWN
            self._notify(Event(
                EventType.SHOWDOWN,
                ranks=self.current_hand.ranks,
                winners=self.current_hand.winners))

        elif self.state == GameState.SHOWDOWN:
            self.state = GameState.PAYING_OUT
            # TODO: we obviously aren't dealing with any pot now
            self._notify(Event(
                EventType.PAYING_OUT,
                net_profit=[0] * self.config.max_players,
                pot_winnings=[0] * self.config.max_players))
            
        elif self.state == GameState.PAYING_OUT:
            self.current_hand = None
            if self.num_players() > 1:
                events = self._create_hand()
                self.state = GameState.PRE_DEAL
                for e in events:
                    self._notify(e)
            else:
                self.state = GameState.WAITING_FOR_START
                self._notify(Event(EventType.WAITING_FOR_START))
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
            for offset in range(1, self.config.max_players + 1):
                try_pos = (self.button_pos + offset) % self.config.max_players
                if self.players[try_pos] is not None:
                    chosen_button = try_pos
                    break
            if chosen_button is None:
                self.button_pos = None
                raise NotEnoughPlayersError()
            self.button_pos = chosen_button

    def _create_hand(self):
        events = []
        if self.current_hand is not None:
            raise ValueError("Can not create hand while one in progress")
        self.current_hand = Hand(
            self.config, self.players, self.button_pos, self._deck_factory)
        events.append(Event(EventType.HAND_STARTED, players=self.current_hand.players))
        players_who_anted = self.current_hand.ante()
        if players_who_anted:
            events.append(Event(EventType.ANTE, player_indices=players_who_anted))
        return events

        
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
