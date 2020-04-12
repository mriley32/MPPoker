import unittest

import game


class AddRemoveTestCase(unittest.TestCase):
    def setUp(self):
        self.manager = game.Manager()
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
        for idx in range(game.MAX_PLAYERS):
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
        self.manager = game.Manager()
        # We'll create players in postiions 0, 2, 3, and 7
        for idx in range(game.MAX_PLAYERS):
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
        self.manager = game.Manager()
        # We'll create players in postiions 0, 2, 4
        for idx in range(5):
            self.manager.add_player(game.Player("name{}".format(idx), 0))
        for idx in [1, 3]:
            self.manager.remove_player(idx)

    def test_start_game(self):
        self.manager.start_game()
        self.assertEqual(game.GameState.PRE_DEAL, self.manager.state)
        self.assertIsNotNone(self.manager.button_pos)
        with self.assertRaises(game.WrongStateError):
            self.manager.start_game()
        

    
if __name__ == '__main__':
    unittest.main()
