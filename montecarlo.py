
from game import Game, game_over
import random
import math


class EdgeStats:
    def __init__(self):
        self.visits = 0
        self.total_value = 0
    
    def action_value(self):
        return self.total_value / self.visits if self.visits > 0 else 0.0
class StateNode:
    def __init__(self, board_key, visit_count=0, children=None):
        self.visit_count = visit_count
        self.edges = {} #action -> EdgeStats
        self.children = children if children else {} #action -> set(state_key)
        self.key = board_key
        self.untried = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    
    def add_child(self, move, board_key):
        self.children[move].add(board_key)
    
    def utc_action(self, C=1.2):
        """
        Computes the UTC of its children: value/visits + C * sqrt(log(parent_visits) / child_visits)
        in ordre to pick the best action to take in {UP, DOWN, LEFT, RIGHT}
        Requires that edge statistics are up to date in order to return an accurate computation
        """
        best_action = None
        best_UTC = float('-inf')
        for action, edge in self.edges.entries():
            if edge.action_value() + C * math.sqrt(math.log(self.visit_count) / edge.visits) > best_UTC:
                best_action = action
            elif edge.action_value() + C * math.sqrt(math.log(self.visit_count) / edge.visits) == best_UTC:
                rand = random.random()
                best_action = action if rand >= 0.5 else best_action
        
        return best_action
        
    
class MCTS():

    def __init__(self, game : Game):
        """"
        Receives a 2048 game in its current state to perform Monte Carlo Tree Search On
        """
        self.game = game.clone()
        self.SIMS = 10000 #allows up to  10,000 moves before ending a simulation
        self.ROLL_OUTS = 500 #the number of simulations performed
        self.root = StateNode(self.game.key())
        self.nodes = {self.game.key() : self.root}

    def next_move(self):
        """
        Recommends next move for agent to make of either UP, DOWN, LEFT, RIGHT
        """
        pass

    # def compute_mcts(self, game : Game):
    #     #First, find valid moves
    #     moves = [move for move in ['UP', 'DOWN', 'LEFT', 'RIGHT'] if game.can_move(move)]
    #     #We need to compute and store the overall reward for starting with a certain move across all simulations
    #     action_values = {}
    #     for move in moves:
    #         new_game = Game(game.board)
    #         reward = new_game.move(move)
    #         reward += self.play_random(new_game, self.SIMS, action_values)
    #         action_values[(self.hashable(new_game.board), move)] = reward
    #     for _ in range(self.ROLL_OUTS - len(moves)):
    #         #Do some kind of UTC calculation to pick inital move
    #         self.play_random() #finish later, simulate the rest randomly
    #     #later return argmax
    #     return None

    def _expand_tree(self):
        """"
        Expands the Monte Carlo Search Tree by expanding a path from the root for each possible move
        and backpropagates rewards from a random policy to get initial UTC values
        """
        playable_moves = [move for move in ['UP', 'DOWN', 'LEFT', 'RIGHT'] if self.game.can_move(move)]
        for move in playable_moves:
            move_reward = self.game.move(move)
            new_board_key = self.game.key()
            self.root.add_child(move, new_board_key)
            self.nodes[new_board_key] = StateNode(new_board_key, visit_count=1)
            self.root.edges[move].total_value += move_reward
            self.root.edges[move].visits += 1
            path = self.play_random()
            self.back_prop(path)



    
    def play_random(self, game : Game, num_iter : int):
        """
        Plays a random policy and returns a list path of board_keys corresponding to nodes in self.nodes
        in the order they were traversed
        """
        path = [game.key()]
        for _ in range(num_iter):
            playable_moves = [move for move in ['UP', 'DOWN', 'LEFT', 'RIGHT'] if self.game.can_move(move)]
            idx = random.randint(0, len(playable_moves) - 1)
            move = playable_moves[idx]
            move_reward = self.game(move)
            new_board_key = self.game.key()
            self.nodes[path[-1]].add_child(move, new_board_key)
            if new_board_key in self.nodes:
                self.nodes[new_board_key].visit_count += 1
            else:
                self.nodes[new_board_key] = StateNode(new_board_key, visit_count=1)
            self.nodes[path[-1]].edges[move] += move_reward
            self.nodes[path[-1]].edges(move) += 1
            path.append(new_board_key)
        
        return path
    

    def back_prop(self, path):
        pass

    
    def _reset(self):
        """
        Resets the internal game used to simulate play to be in the state the search tree was initialized in
        """
        self.game = Game(self.root.board_key)