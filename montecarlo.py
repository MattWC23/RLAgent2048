
from game import Game
import random
class MCTS():

    def __init__(self, game : Game):
        """"
        Receives a 2048 game in its current state to perform Monte Carlo Tree Search On
        """
        self.game = game
        self.SIMS = 10
        self.ROLL_OUTS = 500

    def next_move(self):
        """
        Recommends next move for agent to make of either UP, DOWN, LEFT, RIGHT
        """
        pass

    def compute_mcts(self, game : Game):
        #First, find valid moves
        moves = [move for move in ['UP', 'DOWN', 'LEFT', 'RIGHT'] if game.can_move(move)]

        for move in moves:
            pass

    
    def play_random(self, game, num_iter):
        pass

