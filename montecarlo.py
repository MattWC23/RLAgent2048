
from game import Game, game_over
from typing import Dict, Set
import random
import math


class EdgeStats:
    def __init__(self):
        self.visits: int = 0
        self.total_value: float = 0
    
    def action_value(self) -> float:
        return self.total_value / self.visits if self.visits > 0 else 0.0
class StateNode:
    visit_count : int
    edges : Dict[str, EdgeStats]
    children : Dict[str, Set[tuple]]
    key : tuple
    def __init__(self, board_key, visit_count=0, children=None):
        self.visit_count = visit_count
        self.edges = {'UP': set(), 'DOWN' : set(), 'LEFT' : set(), 'RIGHT' : set()} #action -> EdgeStats
        self.children = children if children is not None else {} #action -> set(state_key)
        self.key = board_key
        self.untried = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    
    def add_child(self, move, board_key):
        self.children[move].setdefault(move, set()).add(board_key)
    
    def utc_action(self, C=1.2):
        """
        Computes the UTC of its children: value/visits + C * sqrt(log(parent_visits) / child_visits)
        in ordre to pick the best action to take in {UP, DOWN, LEFT, RIGHT}
        Requires that edge statistics are up to date in order to return an accurate computation
        """
        best_action = None
        best_UTC = float('-inf')
        for action, edge in self.edges.items():
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

    def compute_mcts(self):
        self._expand_tree()


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
            path = self.play_random(self.game, self.SIMS)
            self.back_prop(path)
            self._reset()



    
    def play_random(self, game : Game, num_iter : int):
        """
        Plays a random policy and returns a list path of board_keys corresponding to nodes in self.nodes
        in the order they were traversed. The first node in the path is the initial state given before
        any random moves are played. Eeach item in the path is (direction of indegree edge, node state, value of moving).
        An example path is [(None, s1, 0), ('RIGHT', s2, 3.2), ...., ('UP', sn, 34)]
        """
        path = [(None, game.key(), 0)]
        for _ in range(num_iter):
            playable_moves = [move for move in ['UP', 'DOWN', 'LEFT', 'RIGHT'] if game.can_move(move)]
            idx = random.randint(0, len(playable_moves) - 1)
            move = playable_moves[idx]
            move_reward = game.move(move)
            new_board_key = game.key()
            self.nodes[path[-1]].add_child(move, new_board_key)
            if new_board_key in self.nodes:
                self.nodes[new_board_key].visit_count += 1
            else:
                self.nodes[new_board_key] = StateNode(new_board_key, visit_count=1)
            self.nodes[path[-1][1]].edges[move].total_value += move_reward
            self.nodes[path[-1][1]].edges[move].visits += 1
            path.append((move,new_board_key, move_reward))
            if game.isTerminated():
                break
        
        return path
    

    def back_prop(self, path):
        n = len(path)
        for i in range(n - 1, 0, -1):
            move, _, reward = path[i]
            parent = path[i - 1][1]
            edge = self.nodes[parent].edges[move]
            edge.total_value += reward
            edge.visits += 1
            self.nodes[parent] += 1

    
    def _reset(self):
        """
        Resets the internal game used to simulate play to be in the state the search tree was initialized with
        """
        self.game = Game(self.root.key)