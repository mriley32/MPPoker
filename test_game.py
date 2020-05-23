import unittest

import cards
import deck
import game


def in_order_deck_factory():
    return deck.Deck()

def deck_factory_from_cards(player_cards, board):
    return lambda: deck.Deck.from_initial_cards_str(
        " ".join(player_cards) + " " + board)

def check_call_all(manager):
    while manager.current_hand.is_betting_active():
        allowed = manager.current_hand.allowed_action()
        for act in [game.ActionType.CHECK, game.ActionType.CALL]:
            if allowed.is_action_type_allowed(act):
                #print("{} acting with {}".format(allowed.player_idx, act))
                manager.act(game.Action(player_idx=allowed.player_idx, action_type=act))
                break



class AddRemoveTestCase(unittest.TestCase):
    def setUp(self):
        self.manager = game.Manager(game.Configuration())
        self.recorder = game.RecordingListener()
        self.manager.add_listener(self.recorder)

    def test_add_player(self):
        player = game.Player("myname", 1000)
        self.assertEqual(0, self.manager.add_player(player))
        self.assertEqual("myname", self.manager.players[0].name)
        self.assertEqual(1000, self.manager.players[0].stack)
        self.assertEqual(0, self.manager.players[0].position)

        self.assertEqual(1, len(self.recorder.events))
        self.assertEqual(
            "Event(EventType.PLAYER_ADDED, player=Player(myname, 1000, 0))",
            str(self.recorder.events[0]))

    def test_add_player_too_many(self):
        for idx in range(self.manager.config.max_players):
            player = game.Player("name{}".format(idx), 1000 * idx)
            self.assertEqual(idx, self.manager.add_player(player))
        with self.assertRaises(game.GameFullError):
            self.manager.add_player(game.Player("full", 12345))

    def test_remove_player(self):
        self.manager.add_player(game.Player("name0", 0))
        self.manager.add_player(game.Player("name1", 1000))
        self.manager.add_player(game.Player("name2", 2000))

        # We clear the recorder here because we don't care what
        # happened before the thing we wanted to test.
        self.recorder.clear()

        removed = self.manager.remove_player(1)
        self.assertEqual("name1", removed.name)
        self.assertEqual(1000, removed.stack)
        self.assertEqual(1, removed.position)

        self.assertEqual(1, len(self.recorder.events))
        self.assertEqual(
            "Event(EventType.PLAYER_REMOVED, player=Player(name1, 1000, 1))",
            str(self.recorder.events[0]))

        with self.assertRaises(game.NoSuchPlayerError):
            self.manager.remove_player(4)

        with self.assertRaises(game.NoSuchPlayerError):
            self.manager.remove_player(9999)


class AdvanceButtonTestCase(unittest.TestCase):
    def setUp(self):
        self.manager = game.Manager(game.Configuration())
        # We'll create players in postiions 0, 2, 3, and 7
        for idx in range(self.manager.config.max_players):
            self.manager.add_player(game.Player("name{}".format(idx), 0))
        for idx in [1, 4, 5, 6, 8, 9]:
            self.manager.remove_player(idx)

    def test_from_none(self):
        for repeat in range(20):
            self.manager.button_pos = None
            self.manager._advance_button()
            self.assertIn(self.manager.button_pos, [0, 2, 3, 7])

    def test_cycle(self):
        self.manager.button_pos = 9
        self.manager._advance_button()
        self.assertEqual(0, self.manager.button_pos)
        self.manager._advance_button()
        self.assertEqual(2, self.manager.button_pos)
        self.manager._advance_button()
        self.assertEqual(3, self.manager.button_pos)
        self.manager._advance_button()
        self.assertEqual(7, self.manager.button_pos)
        self.manager._advance_button()
        self.assertEqual(0, self.manager.button_pos)

    def test_single_player(self):
        for idx in [0, 3, 7]:
            self.manager.remove_player(idx)
        self.manager.button_pos = 0
        self.manager._advance_button()
        self.assertEqual(2, self.manager.button_pos)
        self.manager._advance_button()
        self.assertEqual(2, self.manager.button_pos)

    def test_no_player(self):
        self.manager._advance_button()
        for idx in [0, 2, 3, 7]:
            self.manager.remove_player(idx)
        self.assertIsNotNone(self.manager.button_pos)
        self.assertEqual(0, self.manager.num_players())
        with self.assertRaises(game.NotEnoughPlayersError):
            self.manager._advance_button()
        self.assertIsNone(self.manager.button_pos)
        with self.assertRaises(game.NotEnoughPlayersError):
            self.manager._advance_button()
        self.assertIsNone(self.manager.button_pos)


class MainStatesTestCase(unittest.TestCase):
    def setUp(self):
        self.manager = game.Manager(game.Configuration())
        self.manager._deck_factory = in_order_deck_factory
        # We'll create players in postiions 0, 2, 4
        for idx in range(5):
            self.manager.add_player(game.Player("name{}".format(idx), 0))
        for idx in [1, 3]:
            self.manager.remove_player(idx)
        # Add the recorder last because we don't care about the add/remove events.
        self.recorder = game.RecordingListener()
        self.manager.add_listener(self.recorder)
        # we do long string diffs
        self.maxDiff = None

    def test_start_game(self):
        self.manager.start_game()
        self.assertEqual(game.GameState.PRE_DEAL, self.manager.state)
        self.assertIsNotNone(self.manager.button_pos)
        with self.assertRaises(game.WrongStateError):
            self.manager.start_game()

    def test_multiple_proceed(self):
        self.manager.start_game()
        self.assertEqual(game.GameState.PRE_DEAL, self.manager.state)
        self.assertEqual(1, len(self.recorder.events))
        self.assertEqual(game.EventType.HAND_STARTED,
                         self.recorder.events[0].event_type)
        self.assertEqual(
            "HandPlayer(name0, 0, 0, False), " +
            "None, " +
            "HandPlayer(name2, 0, 0, False), " +
            "None, " +
            "HandPlayer(name4, 0, 0, False), " +
            "None, " +
            "None, " +
            "None, " +
            "None, " +
            "None",
            ', '.join(str(p) for p in self.recorder.events[0].players))

        self.recorder.clear()
        self.manager.proceed()
        self.assertEqual(game.GameState.HOLE_CARDS_DEALT, self.manager.state)
        for idx in [0, 2, 4]:
            self.assertEqual(2, len(self.manager.current_hand.players[idx].hole_cards.cards))
        self.assertEqual(1, len(self.recorder.events))
        self.assertEqual(game.EventType.HOLE_CARDS_DEALT,
                         self.recorder.events[0].event_type)
        self.assertEqual(
            "2c 3c, " +
            "None, " +
            "4c 5c, " +
            "None, " +
            "6c 7c, " +
            "None, " +
            "None, " +
            "None, " +
            "None, " +
            "None",
            ', '.join(str(p) for p in self.recorder.events[0].cards))

        self.recorder.clear()
        self.manager.proceed()
        self.assertEqual(game.GameState.FLOP_DEALT, self.manager.state)
        self.assertEqual(3, len(self.manager.current_hand.board.cards))
        self.assertEqual(1, len(self.recorder.events))
        self.assertEqual(
            "Event(EventType.FLOP_DEALT, cards=8c 9c Tc)",
            str(self.recorder.events[0]))

        self.recorder.clear()
        self.manager.proceed()
        self.assertEqual(game.GameState.TURN_DEALT, self.manager.state)
        self.assertEqual(4, len(self.manager.current_hand.board.cards))
        self.assertEqual(1, len(self.recorder.events))
        self.assertEqual(
            "Event(EventType.TURN_DEALT, card=Jc)",
            str(self.recorder.events[0]))

        self.recorder.clear()
        self.manager.proceed()
        self.assertEqual(game.GameState.RIVER_DEALT, self.manager.state)
        self.assertEqual(5, len(self.manager.current_hand.board.cards))
        self.assertEqual(1, len(self.recorder.events))
        self.assertEqual(
            "Event(EventType.RIVER_DEALT, card=Qc)",
            str(self.recorder.events[0]))

        self.recorder.clear()
        self.manager.proceed()
        self.assertEqual(game.GameState.SHOWDOWN, self.manager.state)
        self.assertGreater(len(self.manager.current_hand.winners), 0)
        self.assertEqual(1, len(self.recorder.events))
        self.assertEqual(
            "Event(EventType.SHOWDOWN" +
            ", ranks=["
            "[<HandRank.STRAIGHT_FLUSH: 8>, 12], "
            "[<HandRank.NO_HAND: -1>], "
            "[<HandRank.STRAIGHT_FLUSH: 8>, 12], "
            "[<HandRank.NO_HAND: -1>], "
            "[<HandRank.STRAIGHT_FLUSH: 8>, 12], "
            "[<HandRank.NO_HAND: -1>], "
            "[<HandRank.NO_HAND: -1>], "
            "[<HandRank.NO_HAND: -1>], "
            "[<HandRank.NO_HAND: -1>], "
            "[<HandRank.NO_HAND: -1>]]" +
            ", winners=[0, 2, 4]" +
            ")",
            str(self.recorder.events[0]))

        self.recorder.clear()
        self.manager.proceed()
        self.assertEqual(game.GameState.PAYING_OUT, self.manager.state)
        self.assertEqual(1, len(self.recorder.events))
        self.assertEqual(
            "Event(EventType.PAYING_OUT" +
            ", net_profit=[0, None, 0, None, 0, None, None, None, None, None]"
            ", pot_winnings=[0, None, 0, None, 0, None, None, None, None, None]"
            ")",
            str(self.recorder.events[0]))

        self.recorder.clear()
        self.manager.proceed()
        self.assertEqual(game.GameState.PRE_DEAL, self.manager.state)
        self.assertEqual(1, len(self.recorder.events))
        self.assertEqual(game.EventType.HAND_STARTED,
                         self.recorder.events[0].event_type)
        self.assertEqual(
            "HandPlayer(name0, 0, 0, False), " +
            "None, " +
            "HandPlayer(name2, 0, 0, False), " +
            "None, " +
            "HandPlayer(name4, 0, 0, False), " +
            "None, " +
            "None, " +
            "None, " +
            "None, " +
            "None",
            ', '.join(str(p) for p in self.recorder.events[0].players))

    def test_paying_out_to_waiting(self):
        self.manager.start_game()
        while self.manager.state != game.GameState.PAYING_OUT:
            self.manager.proceed()
        for idx in [2, 4]:
            self.manager.remove_player(idx)
        self.recorder.clear()
        self.manager.proceed()
        self.assertEqual(game.GameState.WAITING_FOR_START, self.manager.state)
        self.assertEqual(1, len(self.recorder.events))
        self.assertEqual(
            "Event(EventType.WAITING_FOR_START, )",
            str(self.recorder.events[0]))

    def test_proceed_from_waiting(self):
        with self.assertRaises(game.WaitingForStartError):
            self.manager.proceed()


class MainStatesWithBettingTestCase(unittest.TestCase):
    def setUp(self):
        self.manager = game.Manager(game.Configuration(game_type=game.GameType.LIMIT,
                                                       limits=[10,20],
                                                       blinds=[5, 10]))
        self.manager._deck_factory = in_order_deck_factory
        # We'll create players in postiions 0, 1, 2
        for idx in range(3):
            self.manager.add_player(game.Player("name{}".format(idx), 1000))

        # Button will be advanced to 0
        self.manager.button_pos = 5
        self.recorder = game.RecordingListener()
        self.manager.add_listener(self.recorder)
        # we do long string diffs
        self.maxDiff = None

    def test_check_call_all(self):
        # We are only checking the betting related events here.
        with self.assertRaisesRegex(game.ActionInWrongStateError, "GameState.WAITING_FOR_START"):
            self.manager.act(game.Action(0, game.ActionType.CALL))

        self.manager.start_game()
        self.assertEqual(game.GameState.PRE_DEAL, self.manager.state)

        # Pre flop
        self.recorder.clear()
        self.manager.proceed()
        self.assertEqual(game.GameState.HOLE_CARDS_DEALT, self.manager.state)
        self.assertEqual(2, len(self.recorder.events))
        e = self.recorder.events[0]
        self.assertEqual(game.EventType.HOLE_CARDS_DEALT, e.event_type)
        e = self.recorder.events[1]
        self.assertEqual(game.EventType.ACTION_ON, e.event_type)
        self.assertEqual(0, e.hand_player.base_player.position)
        self.assertIsInstance(e.allowed, game.AllowedAction)

        with self.assertRaises(game.BettingActiveError):
            self.manager.proceed()

        self.recorder.clear()
        check_call_all(self.manager)
        self.assertEqual(5, len(self.recorder.events))
        e = self.recorder.events[0]
        self.assertEqual(game.EventType.ACTION, e.event_type)
        self.assertEqual(0, e.action.player_idx)
        self.assertEqual(game.ActionType.CALL, e.action.action_type)
        e = self.recorder.events[1]
        self.assertEqual(game.EventType.ACTION_ON, e.event_type)
        self.assertEqual(1, e.hand_player.base_player.position)
        self.assertIsInstance(e.allowed, game.AllowedAction)
        e = self.recorder.events[2]
        self.assertEqual(game.EventType.ACTION, e.event_type)
        self.assertEqual(1, e.action.player_idx)
        self.assertEqual(game.ActionType.CALL, e.action.action_type)
        e = self.recorder.events[3]
        self.assertEqual(game.EventType.ACTION_ON, e.event_type)
        self.assertEqual(2, e.hand_player.base_player.position)
        self.assertIsInstance(e.allowed, game.AllowedAction)
        e = self.recorder.events[4]
        self.assertEqual(game.EventType.ACTION, e.event_type)
        self.assertEqual(2, e.action.player_idx)
        self.assertEqual(game.ActionType.CHECK, e.action.action_type)

        with self.assertRaisesRegex(game.ActionOutOfTurnError, "(0, None)"):
            self.manager.act(game.Action(0, game.ActionType.CALL))

        for expected_state, expected_event_type in [
                [game.GameState.FLOP_DEALT, game.EventType.FLOP_DEALT],
                [game.GameState.TURN_DEALT, game.EventType.TURN_DEALT],
                [game.GameState.RIVER_DEALT, game.EventType.RIVER_DEALT]]:
            self.recorder.clear()
            self.manager.proceed()
            self.assertEqual(expected_state, self.manager.state)
            self.assertEqual(2, len(self.recorder.events))
            e = self.recorder.events[0]
            self.assertEqual(expected_event_type, e.event_type)
            e = self.recorder.events[1]
            self.assertEqual(game.EventType.ACTION_ON, e.event_type)
            self.assertEqual(1, e.hand_player.base_player.position)
            self.assertIsInstance(e.allowed, game.AllowedAction)

            with self.assertRaises(game.BettingActiveError):
                self.manager.proceed()

            self.recorder.clear()
            check_call_all(self.manager)
            self.assertEqual(5, len(self.recorder.events))
            e = self.recorder.events[0]
            self.assertEqual(game.EventType.ACTION, e.event_type)
            self.assertEqual(1, e.action.player_idx)
            self.assertEqual(game.ActionType.CHECK, e.action.action_type)
            e = self.recorder.events[1]
            self.assertEqual(game.EventType.ACTION_ON, e.event_type)
            self.assertEqual(2, e.hand_player.base_player.position)
            self.assertIsInstance(e.allowed, game.AllowedAction)
            e = self.recorder.events[2]
            self.assertEqual(game.EventType.ACTION, e.event_type)
            self.assertEqual(2, e.action.player_idx)
            self.assertEqual(game.ActionType.CHECK, e.action.action_type)
            e = self.recorder.events[3]
            self.assertEqual(game.EventType.ACTION_ON, e.event_type)
            self.assertEqual(0, e.hand_player.base_player.position)
            self.assertIsInstance(e.allowed, game.AllowedAction)
            e = self.recorder.events[4]
            self.assertEqual(game.EventType.ACTION, e.event_type)
            self.assertEqual(0, e.action.player_idx)
            self.assertEqual(game.ActionType.CHECK, e.action.action_type)

            with self.assertRaisesRegex(game.ActionOutOfTurnError, "(0, None)"):
                self.manager.act(game.Action(0, game.ActionType.CALL))


class AnteTestCase(unittest.TestCase):
    def setUp(self):
        self.manager = game.Manager(game.Configuration(ante=100))
        # We'll create players in postiions 0, 1
        for idx in range(2):
            self.manager.add_player(game.Player("name{}".format(idx), 500))
        # Add the recorder last because we don't care about the add events.
        self.recorder = game.RecordingListener()
        self.manager.add_listener(self.recorder)

    def test_ante_events(self):
        self.manager.start_game()
        self.assertEqual(game.GameState.PRE_DEAL, self.manager.state)
        self.assertEqual(2, len(self.recorder.events))
        self.assertEqual(game.EventType.HAND_STARTED,
                         self.recorder.events[0].event_type)
        self.assertEqual(game.EventType.ANTE,
                         self.recorder.events[1].event_type)
        self.assertEqual(100, self.recorder.events[1].amount)
        self.assertEqual([0, 1], self.recorder.events[1].player_indices)


class ShowdownTestCase(unittest.TestCase):
    def setUp(self):
        self.manager = game.Manager(game.Configuration(ante=100))
        # We'll create players in postiions 0, 2, 4
        for idx in range(5):
            self.manager.add_player(game.Player("name{}".format(idx), 1000))
        for idx in [1, 3]:
            self.manager.remove_player(idx)
        self.recorder = game.RecordingListener()
        self.manager.add_listener(self.recorder)


    def advance_to_showdown(self, player_cards, board):
        self.manager._deck_factory = deck_factory_from_cards(player_cards, board)

        self.manager.start_game()
        while self.manager.state != game.GameState.SHOWDOWN:
            self.manager.proceed()

    def test_single_winner(self):
        self.advance_to_showdown(["Ks 2c", "As 3c", "Js 4c"],
                                 "Ac Kd Qh Jd 5c")
        self.assertEqual([2], self.manager.current_hand.winners)
        self.assertEqual(900, self.manager.current_hand.players[0].stack)
        self.assertEqual(1200, self.manager.current_hand.players[2].stack)
        self.assertEqual(900, self.manager.current_hand.players[4].stack)
        self.recorder.clear()
        self.manager.proceed()
        self.assertEqual(game.GameState.PAYING_OUT, self.manager.state)
        self.assertEqual(1, len(self.recorder.events))
        self.assertEqual(game.EventType.PAYING_OUT,
                         self.recorder.events[0].event_type)
        self.assertEqual([-100, None, 200, None, -100, None, None, None, None, None],
                         self.recorder.events[0].net_profit)
        self.assertEqual([0, None, 300, None, 0, None, None, None, None, None],
                         self.recorder.events[0].pot_winnings)
        self.assertEqual(900, self.manager.players[0].stack)
        self.assertEqual(1200, self.manager.players[2].stack)
        self.assertEqual(900, self.manager.players[4].stack)

    def test_two_winner(self):
        self.advance_to_showdown(["As Ks", "Ad Kd", "Jd Td"],
                                 "Ac Kc 2h 3h 4h")
        self.assertEqual([0, 2], self.manager.current_hand.winners)
        self.assertEqual(1050, self.manager.current_hand.players[0].stack)
        self.assertEqual(1050, self.manager.current_hand.players[2].stack)
        self.assertEqual(900, self.manager.current_hand.players[4].stack)
        self.recorder.clear()
        self.manager.proceed()
        self.assertEqual(game.GameState.PAYING_OUT, self.manager.state)
        self.assertEqual(1, len(self.recorder.events))
        self.assertEqual(game.EventType.PAYING_OUT,
                         self.recorder.events[0].event_type)
        self.assertEqual([50, None, 50, None, -100, None, None, None, None, None],
                         self.recorder.events[0].net_profit)
        self.assertEqual([150, None, 150, None, 0, None, None, None, None, None],
                         self.recorder.events[0].pot_winnings)
        self.assertEqual(1050, self.manager.players[0].stack)
        self.assertEqual(1050, self.manager.players[2].stack)
        self.assertEqual(900, self.manager.players[4].stack)

    def test_two_winner_unequal_pot(self):
        # Kind of a hack -- we adjust the configuration after the manager is created.
        # This will make a pot of 21, split two ways
        self.manager.config.ante = 7
        self.manager.button_pos = 9  # we want it to advance to position 0
        self.advance_to_showdown(["As Ks", "Ad Kd", "Jd Td"],
                                 "Ac Kc 2h 3h 4h")
        self.assertEqual(0, self.manager.current_hand.button_pos)
        self.assertEqual([0, 2], self.manager.current_hand.winners)
        self.assertEqual(1003, self.manager.current_hand.players[0].stack)
        self.assertEqual(1004, self.manager.current_hand.players[2].stack)
        self.assertEqual(993, self.manager.current_hand.players[4].stack)

    def test_play_the_board_missing_player(self):
        # This test is a little weird because it's testing something
        # that can't actually happen right now because we have no
        # opporunity for anyone to fold.
        self.manager._deck_factory = deck_factory_from_cards(
            ["Ks 2c", "8d 9d", "Js 4c"],
            "Ac Kd Qh Jd Tc")

        self.manager.start_game()
        while self.manager.state != game.GameState.RIVER_DEALT:
            self.manager.proceed()
        self.manager.current_hand.players[2].hole_cards = None
        self.manager.proceed()
        self.assertEqual(game.GameState.SHOWDOWN, self.manager.state)
        self.assertEqual([0, 4], self.manager.current_hand.winners)
        self.assertEqual(1050, self.manager.current_hand.players[0].stack)
        self.assertEqual(900, self.manager.current_hand.players[2].stack)
        self.assertEqual(1050, self.manager.current_hand.players[4].stack)


class LimitBettingRoundTestCase(unittest.TestCase):
    def initialize(self, config):
        self.manager = game.Manager(config)
        # We'll create players in postiions 0, 1, 3, 4
        for idx in range(5):
            self.manager.add_player(game.Player("name{}".format(idx), 1000))
        self.manager.remove_player(2)

        self.manager.button_pos = 2
        self.manager.start_game()
        self.assertEqual(3, self.manager.button_pos)
        self.manager.proceed()
        self.assertEqual(game.GameState.HOLE_CARDS_DEALT, self.manager.state)

    def get_stacks(self):
        return [game._none_or_func(lambda p: p.stack, p) for p in self.manager.current_hand.players]

    def perform_actions(self, actions):
        for a in actions:
            self.assertTrue(self.manager.current_hand.is_betting_active())
            self.manager.act(a)

    def test_no_blinds_check_around(self):
        self.initialize(game.Configuration(
            max_players=5, game_type=game.GameType.LIMIT, limits=(100, 200)))
        self.perform_actions([
            game.Action(4, game.ActionType.CHECK),
            game.Action(0, game.ActionType.CHECK),
            game.Action(1, game.ActionType.CHECK),
            game.Action(3, game.ActionType.CHECK),
            ])

        self.assertFalse(self.manager.current_hand.is_betting_active())
        self.assertEqual(0, self.manager.current_hand.pot)
        self.assertEqual([1000, 1000, None, 1000, 1000], self.get_stacks())
        self.assertEqual([True, True, False, True, True], self.manager.current_hand.live_players())

    def test_no_blinds_bet_call(self):
        self.initialize(game.Configuration(
            max_players=5, game_type=game.GameType.LIMIT, limits=(100, 200)))
        self.perform_actions([
            game.Action(4, game.ActionType.CHECK),
            game.Action(0, game.ActionType.BET, amount=100),
            game.Action(1, game.ActionType.CALL),
            game.Action(3, game.ActionType.CALL),
            game.Action(4, game.ActionType.CALL),
            ])

        self.assertFalse(self.manager.current_hand.is_betting_active())
        self.assertEqual(400, self.manager.current_hand.pot)
        self.assertEqual([900, 900, None, 900, 900], self.get_stacks())
        self.assertEqual([True, True, False, True, True], self.manager.current_hand.live_players())

    def test_no_blinds_bet_all_fold(self):
        self.initialize(game.Configuration(
            max_players=5, game_type=game.GameType.LIMIT, limits=(100, 200)))
        self.perform_actions([
            game.Action(4, game.ActionType.CHECK),
            game.Action(0, game.ActionType.BET, amount=100),
            game.Action(1, game.ActionType.FOLD),
            game.Action(3, game.ActionType.FOLD),
            game.Action(4, game.ActionType.FOLD),
            ])

        self.assertFalse(self.manager.current_hand.is_betting_active())
        self.assertEqual(100, self.manager.current_hand.pot)
        self.assertEqual([900, 1000, None, 1000, 1000], self.get_stacks())
        self.assertEqual([True, False, False, False, False], self.manager.current_hand.live_players())

    def test_no_blinds_bet_raise_fold_call(self):
        self.initialize(game.Configuration(
            max_players=5, game_type=game.GameType.LIMIT, limits=(100, 200)))
        self.perform_actions([
            game.Action(4, game.ActionType.BET, amount=100),
            game.Action(0, game.ActionType.CALL),
            game.Action(1, game.ActionType.RAISE, amount=100),
            game.Action(3, game.ActionType.FOLD),
            game.Action(4, game.ActionType.CALL),
            game.Action(0, game.ActionType.FOLD),
            ])

        self.assertFalse(self.manager.current_hand.is_betting_active())
        self.assertEqual(500, self.manager.current_hand.pot)
        self.assertEqual([900, 800, None, 1000, 800], self.get_stacks())
        self.assertEqual([False, True, False, False, True], self.manager.current_hand.live_players())

    def test_no_blinds_reraise(self):
        self.initialize(game.Configuration(
            max_players=5, game_type=game.GameType.LIMIT, limits=(100, 200)))
        self.perform_actions([
            game.Action(4, game.ActionType.BET, amount=100),
            game.Action(0, game.ActionType.CALL),
            game.Action(1, game.ActionType.RAISE, amount=100),
            game.Action(3, game.ActionType.FOLD),
            game.Action(4, game.ActionType.RAISE, amount=100),
            game.Action(0, game.ActionType.FOLD),
            game.Action(1, game.ActionType.CALL),
            ])

        self.assertFalse(self.manager.current_hand.is_betting_active())
        self.assertEqual(700, self.manager.current_hand.pot)
        self.assertEqual([900, 700, None, 1000, 700], self.get_stacks())
        self.assertEqual([False, True, False, False, True], self.manager.current_hand.live_players())

    def test_blinds_all_call(self):
        self.initialize(game.Configuration(
            max_players=5, game_type=game.GameType.LIMIT, limits=(100, 200), blinds=(50, 100)))
        self.perform_actions([
            game.Action(1, game.ActionType.CALL),
            game.Action(3, game.ActionType.CALL),
            game.Action(4, game.ActionType.CALL),
            game.Action(0, game.ActionType.CHECK),
            ])

        self.assertFalse(self.manager.current_hand.is_betting_active())
        self.assertEqual(400, self.manager.current_hand.pot)
        self.assertEqual([900, 900, None, 900, 900], self.get_stacks())
        self.assertEqual([True, True, False, True, True], self.manager.current_hand.live_players())

    def test_blinds_raise_all_fold(self):
        self.initialize(game.Configuration(
            max_players=5, game_type=game.GameType.LIMIT, limits=(100, 200), blinds=(50, 100)))
        self.perform_actions([
            game.Action(1, game.ActionType.RAISE, amount=100),
            game.Action(3, game.ActionType.FOLD),
            game.Action(4, game.ActionType.FOLD),
            game.Action(0, game.ActionType.FOLD),
            ])

        self.assertFalse(self.manager.current_hand.is_betting_active())
        self.assertEqual(350, self.manager.current_hand.pot)
        self.assertEqual([900, 800, None, 1000, 950], self.get_stacks())
        self.assertEqual([False, True, False, False, False], self.manager.current_hand.live_players())

    def test_blinds_fold_to_big_blind(self):
        self.initialize(game.Configuration(
            max_players=5, game_type=game.GameType.LIMIT, limits=(100, 200), blinds=(50, 100)))
        self.perform_actions([
            game.Action(1, game.ActionType.FOLD),
            game.Action(3, game.ActionType.FOLD),
            game.Action(4, game.ActionType.FOLD),
            ])

        self.assertFalse(self.manager.current_hand.is_betting_active())
        self.assertEqual(150, self.manager.current_hand.pot)
        self.assertEqual([900, 1000, None, 1000, 950], self.get_stacks())
        self.assertEqual([True, False, False, False, False], self.manager.current_hand.live_players())

    def test_blinds_small_blind_raise(self):
        self.initialize(game.Configuration(
            max_players=5, game_type=game.GameType.LIMIT, limits=(100, 200), blinds=(50, 100)))
        self.perform_actions([
            game.Action(1, game.ActionType.CALL),
            game.Action(3, game.ActionType.CALL),
            game.Action(4, game.ActionType.RAISE, amount=100),
            game.Action(0, game.ActionType.FOLD),
            game.Action(1, game.ActionType.CALL),
            game.Action(3, game.ActionType.CALL),
            ])

        self.assertFalse(self.manager.current_hand.is_betting_active())
        self.assertEqual(700, self.manager.current_hand.pot)
        self.assertEqual([900, 800, None, 800, 800], self.get_stacks())
        self.assertEqual([False, True, False, True, True], self.manager.current_hand.live_players())

    def test_blinds_big_blind_raise(self):
        self.initialize(game.Configuration(
            max_players=5, game_type=game.GameType.LIMIT, limits=(100, 200), blinds=(50, 100)))
        self.perform_actions([
            game.Action(1, game.ActionType.CALL),
            game.Action(3, game.ActionType.CALL),
            game.Action(4, game.ActionType.CALL),
            game.Action(0, game.ActionType.RAISE, amount=100),
            game.Action(1, game.ActionType.CALL),
            game.Action(3, game.ActionType.CALL),
            game.Action(4, game.ActionType.FOLD),
            ])

        self.assertFalse(self.manager.current_hand.is_betting_active())
        self.assertEqual(700, self.manager.current_hand.pot)
        self.assertEqual([800, 800, None, 800, 900], self.get_stacks())
        self.assertEqual([True, True, False, True, False], self.manager.current_hand.live_players())


    def test_actions_verified(self):
        # This is just testing one case of actions being checked. Detailed look at all the weird cases for
        # allowed actions are in the AllowedActionTestCase.
        self.initialize(game.Configuration(
            max_players=5, game_type=game.GameType.LIMIT, limits=(100, 200), blinds=(50, 100)))
        with self.assertRaises(game.ActionAmountError):
            self.manager.act(game.Action(1, game.ActionType.RAISE, amount=999))


class AllowedActionTestCase(unittest.TestCase):
    def initialize(self, config):
        self.manager = game.Manager(config)
        # We'll create players in postiions 0, 1, 2
        for idx in range(3):
            self.manager.add_player(game.Player("name{}".format(idx), 1000))

        self.manager.button_pos = 2
        self.manager.start_game()
        self.assertEqual(0, self.manager.button_pos)
        self.manager.proceed()
        self.assertEqual(game.GameState.HOLE_CARDS_DEALT, self.manager.state)

    def assert_allowed_actions(self, allowed, player_idx, action_map):
        self.assertEqual(player_idx, allowed.player_idx)
        for act in [game.ActionType.CHECK,
                    game.ActionType.BET,
                    game.ActionType.CALL,
                    game.ActionType.RAISE,
                    game.ActionType.FOLD,
                    game.ActionType.BLIND_BET]:
            self.assertEqual(act in action_map, allowed.is_action_type_allowed(act), act)
        for act in [game.ActionType.BET,
                    game.ActionType.CALL,
                    game.ActionType.RAISE]:
            if act in action_map:
                self.assertEqual(action_map[act],
                                 allowed.range_for_action(act),
                                 act)

    def test_allowed_action_api(self):
        # This test covers the external API of AllowedAction. Other test cases will verify the code
        # that generates AllowedAction for different game states.
        allowed = game.AllowedAction()
        allowed._player_idx = 3
        allowed._action_map[game.ActionType.CHECK] = None
        allowed._action_map[game.ActionType.BET] = (10, 20)
        allowed._action_map[game.ActionType.CALL] = (5, 5)
        self.assertTrue(allowed.is_action_type_allowed(game.ActionType.CHECK))
        self.assertTrue(allowed.is_action_type_allowed(game.ActionType.BET))
        self.assertFalse(allowed.is_action_type_allowed(game.ActionType.RAISE))
        self.assertTrue(allowed.is_action_type_allowed(game.ActionType.CALL))

        with self.assertRaises(ValueError):
            allowed.range_for_action(game.ActionType.CHECK)
        with self.assertRaises(game.ActionNotAllowedError):
            allowed.range_for_action(game.ActionType.RAISE)
        self.assertEqual((10, 20), allowed.range_for_action(game.ActionType.BET))
        self.assertEqual((5, 5), allowed.range_for_action(game.ActionType.CALL))

        with self.assertRaises(game.ActionOutOfTurnError):
            allowed.check_action(game.Action(0, game.ActionType.CHECK))
        with self.assertRaises(game.ActionAmountError):
            allowed.check_action(game.Action(3, game.ActionType.BET, 9))
        with self.assertRaises(game.ActionAmountError):
            allowed.check_action(game.Action(3, game.ActionType.BET, 21))
        allowed.check_action(game.Action(3, game.ActionType.BET, 10))
        allowed.check_action(game.Action(3, game.ActionType.BET, 20))
        allowed.check_action(game.Action(3, game.ActionType.CALL))

        allowed._action_map[game.ActionType.RAISE] = (100, 200)
        with self.assertRaises(game.ActionAmountError):
            allowed.check_action(game.Action(3, game.ActionType.RAISE, 9999))
        allowed.check_action(game.Action(3, game.ActionType.RAISE, 200))

    def test_simple_limit(self):
        self.initialize(game.Configuration(
            max_players=3, game_type=game.GameType.LIMIT, limits=(100, 200), blinds=(50, 100)))

        # pre flop
        allowed = self.manager.current_hand.allowed_action()
        self.assert_allowed_actions(allowed, 0, {game.ActionType.CALL: (100, 100),
                                                 game.ActionType.RAISE: (100, 100),
                                                 game.ActionType.FOLD: None,})

        self.manager.act(game.Action(0, game.ActionType.CALL))
        allowed = self.manager.current_hand.allowed_action()
        self.assert_allowed_actions(allowed, 1, {game.ActionType.CALL: (50, 50),
                                                 game.ActionType.RAISE: (100, 100),
                                                 game.ActionType.FOLD: None,})

        self.manager.act(game.Action(1, game.ActionType.CALL))
        allowed = self.manager.current_hand.allowed_action()
        self.assert_allowed_actions(allowed, 2, {game.ActionType.CHECK: None,
                                                 game.ActionType.RAISE: (100, 100),
                                                 game.ActionType.FOLD: None,})

        self.manager.act(game.Action(2, game.ActionType.CHECK))

        for expected_state, expected_bet in [[game.GameState.FLOP_DEALT, 100],
                                             [game.GameState.TURN_DEALT, 200],
                                             [game.GameState.RIVER_DEALT, 200]]:
            self.manager.proceed()
            self.assertEqual(expected_state, self.manager.state)
            for player_idx in [1, 2, 0]:
                allowed = self.manager.current_hand.allowed_action()
                self.assert_allowed_actions(allowed, player_idx,
                                            {game.ActionType.CHECK: None,
                                             game.ActionType.BET: (expected_bet, expected_bet),
                                             game.ActionType.FOLD: None})
                self.manager.act(game.Action(player_idx, game.ActionType.CHECK))



    # Lots of testing to be added
    # Error cases
    # * betting when should only call or raise
    # Other
    # * Manager dealing with everyone folding correctly


if __name__ == '__main__':
    unittest.main()
