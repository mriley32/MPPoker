"""Game manages the poker game and the state of the players."""

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

        
class Manager:
    """Manager is the main class for managing the flow of the game."""

    def __init__(self):
        self.players = [None] * MAX_PLAYERS

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
        return removed
