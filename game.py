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


class InvalidActionError(Exception):
    pass

class ActionOutOfTurnError(InvalidActionError):
    def __init__(self, player_idx, action_on):
        self.player_idx = player_idx
        self.action_on = action_on

class ActionNotAllowedError(InvalidActionError):
    def __init__(self, action_type):
        self.action_type = action_type

class ActionAmountError(InvalidActionError):
    def __init__(self, amount, min_amount, max_amount):
        self.amount = amount
        self.min_amount = min_amount
        self.max_amount = max_amount


def _none_or_func(f, x):
    """Return None if x is None, f(x) otherwise"""
    if x is None:
        return None
    return f(x)


@enum.unique
class GameType(enum.Enum):
    # Antes are collected, but no betting rounds
    NO_BETTING = 0
    # Standard limit with one size for pre-flop and flop and one for turn and river.
    LIMIT = 1


class Configuration:
    """Data class for configuration of the game.

    Attributes:
      max_players: number of spots in the game
      game_type: of type GameType
      ante: amount of the ante
      blinds: list of amounts of blinds
      limits: if game_type == LIMIT, a 2 tuple of the betting limits
    """
    def __init__(self, max_players=10, game_type=GameType.NO_BETTING, ante=0, blinds=None, limits=None):
        self.max_players = max_players
        self.game_type = game_type
        self.ante = ante
        self.blinds = blinds
        if limits is not None and len(limits) != 2:
            raise ValueError("Invalid limits {}".format(limits))
        self.limits = limits


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
    # Expected args: player(of type Player)
    PLAYER_ADDED = 0
    # Expected args: player(of type Player)
    PLAYER_REMOVED = 1
    # Expected args: None
    WAITING_FOR_START = 2
    # Expected args: players (array of HandPlayer)
    HAND_STARTED = 3
    # Expected args: player_indices (array of int)
    ANTE = 4
    # Expected args: cards (array of cards.PlayerCards)
    HOLE_CARDS_DEALT = 5
    # Expected args: cards (cards.PlayerCards)
    FLOP_DEALT = 6
    # Expected args: card (deck.Card)
    TURN_DEALT = 7
    # Expected args: card (deck.Card)
    RIVER_DEALT = 8
    # Expected args:
    #     ranks (array of array (as returned by cards.PlayerCards.hand_rank))
    #     winners (array of int)
    SHOWDOWN = 9
    # Expected args:
    #     pot_winnings (array of int (config.max_players size))
    #     net_profit (array of int (config.max_players size))
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
      <kwargs>: Everything passed in to kwargs in the constructor are turned into
        attributes on the Event. For example, in the PAYING_OUT events, you can access
        event.pot_winnings and event.net_profit

    The expected attributes are documented in EventType above.
    """
    def __init__(self, event_type, **kwargs):
        self.event_type = event_type
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        args_strs = []
        for key in sorted(self.__dict__.keys()):
            if key == "event_type":
                continue
            args_strs.append("{}={}".format(key, getattr(self, key)))
        return "Event({}, {})".format(self.event_type, ", ".join(args_strs))


def _shuffled_deck_factory():
    d = deck.Deck()
    d.shuffle
    return d


def _next_valid_position(current_pos, valid_players):
    next_pos = None
    for offset in range(1, len(valid_players) + 1):
        try_pos = (current_pos + offset) % len(valid_players)
        if valid_players[try_pos]:
            return try_pos
    raise NotEnoughPlayersError()


@enum.unique
class ActionType(enum.Enum):
    CHECK = 0
    BET = 1
    CALL = 2
    RAISE = 3
    FOLD = 4
    BLIND_BET = 5


class Action:
    def __init__(self, player_idx, action_type, amount=None):
        """Initialize single player's action.

        Args:
          player_idx: index of player acting
          action_type: ActionType
          amount: amount of action, only for BET and RAISE
        """
        self.player_idx = player_idx
        self.action_type = action_type
        if (action_type == ActionType.CHECK or
            action_type == ActionType.CALL or
            action_type == ActionType.FOLD):
            if amount is not None:
                raise ValueError("On action {}, amount must not be specified (got {})"
                                 .format(action_type, amount))
        elif (action_type == ActionType.BET or
              action_type == ActionType.BLIND_BET or
              action_type == ActionType.RAISE):
            if amount is None:
                raise ValueError("On action {}, amount must be specified".format(action_type))
            self.amount = amount
        else:
            raise ValueError("Didn't understand action_type {}".format(action_type))


class AllowedAction:
    """AllowedAction represents the range of valid actions at a specific point."""
    def __init__(self):
        # maps ActionType to (min, max) for BET, RAISE or None for others.
        # only includes actions that are allowed
        self._action_map = {}
        self._player_idx = None

    @property
    def player_idx(self):
        return self._player_idx

    def is_action_type_allowed(self, action_type):
        """Returns whether this type of action is allowed at all.

        Args:
          action_type: ActionType

        Returns:
          boolean
        """
        return action_type in self._action_map

    def range_for_action(self, action_type):
        """Returns the value range for given action_type.

        Only BET and RAISE are valid arguments.

        Args:
          action_type: ActionType

        Returns:
          2 tuple: (min, max). Note that max is *inclusive*.

        Raises:
          ValueError
          ActionNotAllowedError
        """
        if action_type != ActionType.BET and action_type != ActionType.RAISE:
            raise ValueError(action_type)
        try:
            return self._action_map[action_type]
        except KeyError:
            raise ActionNotAllowedError(action_type)

    def check_action(self, action):
        """Verifies if the given action is allowed.

        Raises a subclass of InvalidActionError with details.
        """
        if action.player_idx != self._player_idx:
            raise ActionOutOfTurnError(action.player_idx, self._player_idx)
        try:
            valid_range = self._action_map[action.action_type]
        except KeyError:
            raise ActionNotAllowedError(action.action_type)
        if action.action_type == ActionType.BET or action.action_type == ActionType.RAISE:
            valid_min, valid_max = valid_range
            if action.amount < valid_min or action.amount > valid_max:
                raise ActionAmountError(action.amount, valid_min, valid_max)


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
      pot_winnings: amount won from the pot
    """
    def __init__(self, config, players, button_pos, deck_factory):
        """Creates the hand.

        Args:
          config: Configuration
          players: array of Player
          button_pos: integer button postion
          deck_factory: function which returns a deck.Deck (for injection during
            unittests, normally it's _shuffled_deck_factory)
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
        self.pot_winnings = None

        self.action_on = None
        self.past_action = None

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

    def live_players(self):
        return [p is not None and p.hole_cards is not None
                for p in self.players]

    def _start_betting_round(self):
        if self.config.game_type == GameType.NO_BETTING:
            return
        assert self.config.game_type == GameType.LIMIT
        self.action_on = _next_valid_position(self.button_pos, self.live_players())
        self.past_action = []
        self.current_outlay = [0] * len(self.players)

    def _has_acted(self, player_idx):
        for a in self.past_action:
            if a.action_type == ActionType.BLIND_BET:
                continue
            if a.player_idx == player_idx:
                return True
        return False

    def _equal_outlay(self):
        live_outlay = [x for x, live in zip(self.current_outlay, self.live_players()) if live]
        return max(live_outlay) == min(live_outlay)

    def _current_total_bet(self):
        return max(self.current_outlay)

    def act(self, action):
        """Performs the given action.

        Args:
          action: Action
        """
        if self.action_on != action.player_idx:
            raise ActionOutOfTurnError(action.player_idx, self.action_on)

        # Do stuff with the action here
        if action.action_type == ActionType.CHECK:
            pass
        elif action.action_type == ActionType.BET or action.action_type == ActionType.BLIND_BET:
            self.players[action.player_idx].stack -= action.amount
            self.current_outlay[action.player_idx] += action.amount
        elif action.action_type == ActionType.CALL:
            amount = self._current_total_bet() - self.current_outlay[action.player_idx]
            self.players[action.player_idx].stack -= amount
            self.current_outlay[action.player_idx] += amount
        elif action.action_type == ActionType.RAISE:
            total_amount = self._current_total_bet() - self.current_outlay[action.player_idx] + action.amount
            self.players[action.player_idx].stack -= total_amount
            self.current_outlay[action.player_idx] += total_amount
        elif action.action_type == ActionType.FOLD:
            self.players[action.player_idx].hole_cards = None
        else:
            raise ValueError("Did not understand action {}".format(action))

        self.past_action.append(action)

        self.action_on = _next_valid_position(self.action_on, self.live_players())

        if (sum(self.live_players()) == 1 or
            (self._has_acted(self.action_on) and self._equal_outlay())):
            self.pot += sum(self.current_outlay)
            # We can finish this betting round!
            self.action_on = None
            self.past_action = None
            self.current_outlay = None

    def is_betting_active(self):
        """Returns whether a betting round is in progress.

        Returns:
          boolean
        """
        return self.action_on is not None

    def deal_hole_cards(self):
        for p in self.players:
            if p is None:
                continue
            p.hole_cards = cards.PlayerCards(self.deck.deal(2))

        self._start_betting_round()
        if self.config.blinds:
            for blind in self.config.blinds:
                self.act(Action(player_idx=self.action_on, action_type=ActionType.BLIND_BET, amount=blind))

    def deal_flop(self):
        self.board.cards.extend(self.deck.deal(3))

    def deal_turn(self):
        self.board.cards.extend(self.deck.deal(1))

    def deal_river(self):
        self.board.cards.extend(self.deck.deal(1))

    def showdown(self):
        # Find the winners
        self.ranks = []
        for p in self.players:
            if p is None or p.hole_cards is None:
                self.ranks.append([cards.HandRank.NO_HAND])
                continue
            self.ranks.append(p.hole_cards.combine(self.board).hand_rank())
        best_hand = max(self.ranks)
        self.winners = [i for i, rank in enumerate(self.ranks) if rank == best_hand]

        # Distribute the pot, possibly splitting
        self.pot_winnings = [_none_or_func(lambda _: 0, p) for p in self.players]
        for idx in self.winners:
            amount_won = self.pot // len(self.winners)
            self.pot_winnings[idx] += amount_won
            self.players[idx].stack += amount_won

        # Distribute the extra chips to the first person to act
        extra_chips = self.pot % len(self.winners)
        for offset in range(1, self.config.max_players + 1):
            idx = (self.button_pos + offset) % self.config.max_players
            if idx in self.winners:
                self.pot_winnings[idx] += extra_chips
                self.players[idx].stack += extra_chips
                break




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
        events = []

        if self.state == GameState.WAITING_FOR_START:
            raise WaitingForStartError()

        elif self.state == GameState.PRE_DEAL:
            self.current_hand.deal_hole_cards()
            self.state = GameState.HOLE_CARDS_DEALT
            events.append(Event(
                EventType.HOLE_CARDS_DEALT,
                cards=[_none_or_func(lambda p: p.hole_cards, p)
                       for p in self.current_hand.players]))

        elif self.state == GameState.HOLE_CARDS_DEALT:
            self.current_hand.deal_flop()
            self.state = GameState.FLOP_DEALT
            events.append(Event(
                EventType.FLOP_DEALT,
                cards=self.current_hand.board))

        elif self.state == GameState.FLOP_DEALT:
            self.current_hand.deal_turn()
            self.state = GameState.TURN_DEALT
            events.append(Event(
                EventType.TURN_DEALT,
                card=self.current_hand.board.cards[-1]))

        elif self.state == GameState.TURN_DEALT:
            self.current_hand.deal_river()
            self.state = GameState.RIVER_DEALT
            events.append(Event(
                EventType.RIVER_DEALT,
                card=self.current_hand.board.cards[-1]))

        elif self.state == GameState.RIVER_DEALT:
            self.current_hand.showdown()
            self.state = GameState.SHOWDOWN
            events.append(Event(
                EventType.SHOWDOWN,
                ranks=self.current_hand.ranks,
                winners=self.current_hand.winners))

        elif self.state == GameState.SHOWDOWN:
            self.state = GameState.PAYING_OUT
            events.append(self._handle_payouts())

        elif self.state == GameState.PAYING_OUT:
            self.current_hand = None
            if self.num_players() > 1:
                events.extend(self._create_hand())
                self.state = GameState.PRE_DEAL
            else:
                self.state = GameState.WAITING_FOR_START
                events.append(Event(EventType.WAITING_FOR_START))
        else:
            raise ValueError("Unknown state {}".format(self.state))

        for e in events:
            self._notify(e)


    def _handle_payouts(self):
        net_profit = [_none_or_func(lambda p: p.stack - p.initial_stack, p)
                      for p in self.current_hand.players]
        for p, net in zip(self.players, net_profit):
            if p is None or net is None:
                continue
            p.stack += net
        return Event(
                EventType.PAYING_OUT,
                net_profit=net_profit,
                pot_winnings=self.current_hand.pot_winnings)

    def _advance_button(self):
        if self.button_pos is None:
            if self.num_players() == 0:
                raise NotEnoughPlayersError()
            self.button_pos = random.choice(
                [i for i, p in enumerate(self.players) if p is not None])
        else:
            try:
                self.button_pos = _next_valid_position(
                    self.button_pos, [p is not None for p in self.players])
            except NotEnoughPlayersError:
                self.button_pos = None
                raise

    def _create_hand(self):
        events = []
        if self.current_hand is not None:
            raise ValueError("Can not create hand while one in progress")
        self.current_hand = Hand(
            self.config, self.players, self.button_pos, self._deck_factory)
        events.append(Event(EventType.HAND_STARTED, players=self.current_hand.players))
        players_who_anted = self.current_hand.ante()
        if players_who_anted:
            events.append(Event(EventType.ANTE,
                                amount=self.config.ante,
                                player_indices=players_who_anted))
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
