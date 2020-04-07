import unittest

import game


class ManagerTestCase(unittest.TestCase):
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

        

    
if __name__ == '__main__':
    unittest.main()
