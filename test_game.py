import unittest

import cards
import deck
import game


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


def in_order_deck_factory():
    return deck.Deck()
        
        
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
            "HandPlayer(name0, 0, False), " +
            "None, " +
            "HandPlayer(name2, 0, False), " +
            "None, " +
            "HandPlayer(name4, 0, False), " +
            "None, " +
            "None, " +
            "None, " +
            "None, " +
            "None",
            ', '.join(str(p) for p in self.recorder.events[0].args["players"]))

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
            ', '.join(str(p) for p in self.recorder.events[0].args["cards"]))

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
            ", net_profit=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]"
            ", pot_winnings=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]"
            ")",
            str(self.recorder.events[0]))

        self.recorder.clear()
        self.manager.proceed()
        self.assertEqual(game.GameState.PRE_DEAL, self.manager.state)
        self.assertEqual(1, len(self.recorder.events))
        self.assertEqual(game.EventType.HAND_STARTED,
                         self.recorder.events[0].event_type)
        self.assertEqual(
            "HandPlayer(name0, 0, False), " +
            "None, " +
            "HandPlayer(name2, 0, False), " +
            "None, " +
            "HandPlayer(name4, 0, False), " +
            "None, " +
            "None, " +
            "None, " +
            "None, " +
            "None",
            ', '.join(str(p) for p in self.recorder.events[0].args["players"]))

    def test_paying_out_to_waiting(self):
        self.manager.start_game()
        # Kind of a dumb test because it's relying on 6 stages to get
        # to paying out, but we'll deal with it later.
        for _ in range(6):
            self.manager.proceed()
        self.assertEqual(game.GameState.PAYING_OUT, self.manager.state)
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

            
class AnteTestCase(unittest.TestCase):
    def setUp(self):
        self.manager = game.Manager(game.Configuration(ante=100))
        self.manager._deck_factory = in_order_deck_factory
        # We'll create players in postiions 0, 1, 4
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
        self.assertEqual([0, 1], self.recorder.events[1].args["player_indices"])


class ShowdownTestCase(unittest.TestCase):
    def setUp(self):
        self.manager = game.Manager(game.Configuration())
        # We'll create players in postiions 0, 2, 4
        for idx in range(5):
            self.manager.add_player(game.Player("name{}".format(idx), 0))
        for idx in [1, 3]:
            self.manager.remove_player(idx)
        # Advance the game to just before showdown. The test cases
        # will mess with the cards tehmselves.
        self.manager.start_game()
        # Kind of a dumb test because it's relying on the number of
        # stages to get to RIVER_DEALT, but we'll deal with it later.
        for _ in range(4):
            self.manager.proceed()
        self.assertEqual(game.GameState.RIVER_DEALT, self.manager.state)

    def test_single_winner(self):
        self.manager.current_hand.board = (
            cards.PlayerCards.from_str("Ac Kd Qh Jd 5c"))
        self.manager.current_hand.players[0].hole_cards = (
            cards.PlayerCards.from_str("Ks 2c"))
        self.manager.current_hand.players[2].hole_cards = (
            cards.PlayerCards.from_str("As 3c"))
        self.manager.current_hand.players[4].hole_cards = (
            cards.PlayerCards.from_str("Js 4c"))
        self.assertIsNone(self.manager.current_hand.winners)
        self.manager.proceed()
        self.assertEqual(game.GameState.SHOWDOWN, self.manager.state)
        self.assertEqual([2], self.manager.current_hand.winners)
        
    def test_two_winner(self):
        self.manager.current_hand.board = (
            cards.PlayerCards.from_str("Ac Kc 2h 3h 4h"))
        self.manager.current_hand.players[0].hole_cards = (
            cards.PlayerCards.from_str("As Ks"))
        self.manager.current_hand.players[2].hole_cards = (
            cards.PlayerCards.from_str("Ad Kd"))
        self.manager.current_hand.players[4].hole_cards = (
            cards.PlayerCards.from_str("Jd Td"))
        self.assertIsNone(self.manager.current_hand.winners)
        self.manager.proceed()
        self.assertEqual(game.GameState.SHOWDOWN, self.manager.state)
        self.assertEqual([0, 2], self.manager.current_hand.winners)

    def test_play_the_board_missing_player(self):
        self.manager.current_hand.board = (
            cards.PlayerCards.from_str("Ac Kd Qh Jd Tc"))
        self.manager.current_hand.players[0].hole_cards = (
            cards.PlayerCards.from_str("Ks 2c"))
        self.manager.current_hand.players[2].hole_cards = None
        self.manager.current_hand.players[4].hole_cards = (
            cards.PlayerCards.from_str("Js 4c"))
        self.assertIsNone(self.manager.current_hand.winners)
        self.manager.proceed()
        self.assertEqual(game.GameState.SHOWDOWN, self.manager.state)
        self.assertEqual([0, 4], self.manager.current_hand.winners)
        

    
if __name__ == '__main__':
    unittest.main()
