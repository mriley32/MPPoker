import unittest

import game


class ManagerTestCase(unittest.TestCase):
    def test_add_player(self):
        manager = game.Manager()
        player = game.Player("myname", 1000)
        self.assertEqual(0, manager.add_player(player))
        self.assertEqual("myname", manager.players[0].name)
        self.assertEqual(1000, manager.players[0].stack)
        self.assertEqual(0, manager.players[0].position)

    def test_add_player_too_many(self):
        manager = game.Manager()
        for idx in range(game.MAX_PLAYERS):
            player = game.Player("name{}".format(idx), 1000 * idx)
            self.assertEqual(idx, manager.add_player(player))
        with self.assertRaises(game.GameFullError):
            manager.add_player(game.Player("full", 12345))

    def test_remove_player(self):
        manager = game.Manager()
        manager.add_player(game.Player("name0", 0))
        manager.add_player(game.Player("name1", 1000))
        manager.add_player(game.Player("name2", 2000))
        removed = manager.remove_player(1)
        self.assertEqual("name1", removed.name)
        self.assertEqual(1000, removed.stack)
        self.assertEqual(1, removed.position)

        with self.assertRaises(game.NoSuchPlayerError):
            manager.remove_player(4)

        with self.assertRaises(game.NoSuchPlayerError):
            manager.remove_player(9999)

        

    
if __name__ == '__main__':
    unittest.main()
