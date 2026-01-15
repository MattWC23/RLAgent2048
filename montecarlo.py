
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
    def __init__(self, board_key, untried : list, visit_count=0, children=None):
        self.visit_count = visit_count
        self.edges = {'UP': EdgeStats(), 'DOWN' : EdgeStats(), 'LEFT' : EdgeStats(), 'RIGHT' : EdgeStats()} #action -> EdgeStats
        self.children = children if children is not None else {} #action -> set(state_key)
        self.key = board_key
        self.untried = untried
    
    def add_child(self, move, board_key):
        self.children.setdefault(move, set()).add(board_key)

    def remove_move(self, move):
        if move in self.untried:
            self.untried.remove(move)

    def pick_untried(self):
        a = random.choice(self.untried)
        self.untried.remove(a)
        return a
    
    def uct_action(self, C=1.2):
        """
        Computes the UCT of its children: value/visits + C * sqrt(log(parent_visits) / child_visits)
        in ordre to pick the best action to take in {UP, DOWN, LEFT, RIGHT}
        Requires that edge statistics are up to date in order to return an accurate computation. Requires no 
        untried actinos
        """
        best_action = None
        best_UCT = float('-inf')
        for action, edge in self.edges.items():
            if edge.visits == 0:
                raise RuntimeError('This should never happen')
            uct = edge.action_value() + C * math.sqrt(math.log(self.visit_count) / edge.visits)
            if  uct > best_UCT:
                best_action = action
                best_UCT = uct
            elif uct == best_UCT:
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
        self.root = StateNode(self.game.key(), untried=self._possible_moves(self.game))
        self.nodes = {self.game.key() : self.root}

    def next_move(self):
        """
        Recommends next move for agent to make of either UP, DOWN, LEFT, RIGHT
        """
        self._compute_mcst()
        optimal_action, optimal_score = '', -1
        for action, edge in self.root.edges.items():
            if edge.visits > optimal_score:
                optimal_score = edge.visits
                optimal_action = action
        return optimal_action


    def _compute_mcst(self):
        """
        Fills out the MCST tree using self.ROLLOUTS simulated game plays. Nodes are selected by UCT followed 
        by random rollout policy.
        """
        for _ in range(self.ROLL_OUTS + len(self.root.untried)): #total simulations plus expanding the tree
            path = [(None, self.game.key(), 0)]
            curr_key = self.root.key
            expanded = False
            while curr_key in self.nodes and not expanded:
                curr_node = self.nodes[curr_key]
                move = None
                if curr_node.untried:
                    move = curr_node.pick_untried()
                    expanded = True
                else:
                    move = curr_node.uct_action()
                move_reward = self.game.move(move)
                new_board_key = self.game.key()
                path.append((move, new_board_key, move_reward))
                curr_key = new_board_key
            
            parent = self.nodes[path[-2][1]]
            parent.add_child(move, new_board_key)
            self.nodes[new_board_key] = StateNode(new_board_key, self._possible_moves(self.game), visit_count=1)
            rollout_reward = self.play_random(self.game, self.SIMS)
            self.back_prop(path, rollout_reward)
            self._reset()

    
    def play_random(self, game : Game, num_iter : int):
        """
        Plays a random policy for `num_iter` moves on the game and returns the reward accumulated.
        """
        for _ in range(num_iter):
            rollout_reward = 0
            playable_moves = [move for move in ['UP', 'DOWN', 'LEFT', 'RIGHT'] if game.can_move(move)]
            idx = random.randint(0, len(playable_moves) - 1)
            move = playable_moves[idx]
            rollout_reward += game.move(move)
            if game.isTerminated():
                break
        
        return rollout_reward
    

    def back_prop(self, path, rollout_reward):
        n = len(path)
        G = rollout_reward
        for i in range(n - 1, 0, -1):
            move, _, reward = path[i]
            G += reward
            parent = path[i - 1][1]
            edge = self.nodes[parent].edges[move]
            edge.total_value += G
            edge.visits += 1
            self.nodes[parent].visit_count += 1

    
    def _reset(self):
        """
        Resets the internal game used to simulate play to be in the state the search tree was initialized with
        """
        self.game = Game(self.root.key)

    
    def _possible_moves(self, game : Game):
        return [move for move in ['UP', 'DOWN', 'LEFT', 'RIGHT'] if game.can_move(move)]
    

    def _expand_tree(self):
        """"
        Expands the Monte Carlo Search Tree by expanding a path from the root for each possible move
        and backpropagates rewards from a random policy to get initial UTC values
        """
        for move in self.root.untried:
            move_reward = self.game.move(move)
            new_board_key = self.game.key()
            self.root.untried.remove(move)
            self.root.add_child(move, new_board_key)
            self.nodes[new_board_key] = StateNode(new_board_key, visit_count=1, untried=self._possible_moves(self.game))
            self.root.edges[move].total_value += move_reward
            self.root.edges[move].visits += 1
            path = self.play_random(self.game, self.SIMS)
            self.back_prop(path)
            self._reset()