
from src.game import Game, game_over
from typing import Dict, Set
import random
import math

def sum_board(board):
        output = 0
        for row in board:
            output += sum(row)
        
        return output

def _possible_moves(game : Game):
        return [move for move in ['UP', 'DOWN', 'LEFT', 'RIGHT'] if game.can_move(move)]
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
        legal = _possible_moves(Game(board_key))
        self.edges = {a: EdgeStats() for a in legal} #action -> EdgeStats
        self.untried = legal[:]
        self.children = children if children is not None else {} #action -> set(state_key)
        self.key = board_key
    
    def add_child(self, move, board_key):
        self.children.setdefault(move, set()).add(board_key)

    def remove_move(self, move):
        if move in self.untried:
            self.untried.remove(move)

    def pick_untried(self):
        a = random.choice(self.untried)
        self.untried.remove(a)
        return a
    
    def uct_action(self, C=50):
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

    def __init__(self, game : Game, C=50):
        """"
        Receives a 2048 game in its current state to perform Monte Carlo Tree Search On
        """
        self.game = game.clone()
        self.SIMS = 80 #allows up to  10,000 moves before ending a simulation
        self.ROLL_OUTS = 500 #the number of simulations performed
        self.root = StateNode(self.game.key())
        self.nodes = {self.game.key() : self.root}
        self.C = C
        self.max_depth = 1

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
        # optimal_action, optimal_score = '', -1
        # for action, edge in self.root.edges.items():
        #     if edge.action_value() > optimal_score:
        #         optimal_score = edge.action_value()
        #         optimal_action = action
        # return optimal_action


    def _compute_mcst(self):
        """
        Fills out the MCST tree using self.ROLLOUTS simulated game plays. Nodes are selected by UCT followed 
        by random rollout policy.
        """
        for _ in range(self.ROLL_OUTS + len(self.root.untried)): #total simulations plus expanding the tree
            #print(f'count:{_ + 1}')
            path = [(None, self.game.key(), 0)]
            curr_key = self.root.key
            expanded = False
            seen = set()
            while curr_key in self.nodes and not expanded:
                #print(f'stuck in while loop')
                curr_node = self.nodes[curr_key]
                move = None
                if curr_node.untried:
                    #print('untried nodes')
                    move = curr_node.pick_untried()
                    expanded = True
                else:
                    #print('spam uct')
                    move = curr_node.uct_action(C=self.C)
                move_reward = self.game.move(move)
                # self.game.move(move)
                # move_reward = self.game.reward(sum_board)
                new_board_key = self.game.key()
                if new_board_key in seen:
                    #cycle reached
                    break
                path.append((move, new_board_key, move_reward))
                seen.add(new_board_key)
                curr_key = new_board_key
                #print(curr_key in self.nodes)
                #print('matching key?')
                #if curr_key in self.nodes:
                    #print(self.nodes[curr_key].key)
            
            parent = self.nodes[path[-2][1]]
            if curr_key not in self.nodes:
                parent.add_child(move, curr_key)
                self.nodes[new_board_key] = StateNode(curr_key, visit_count=1)
            rollout_reward = self.play_random(self.game, self.SIMS)
            self.back_prop(path, rollout_reward)
            self.max_depth = max(self.max_depth, len(path))
            self._reset()
            #print(f'max depth in tree:{self.max_depth}')
            #print(f'depth selected: {len(path) - 1}')

    
    def play_random(self, game : Game, num_iter : int):
        """
        Plays a random policy for `num_iter` moves on the game and returns the reward accumulated.
        """
        rollout_reward = 0
        for _ in range(num_iter):
            #print(f'rollout count:{_ + 1}')
            if game.isTerminated():
                break
            playable_moves = [move for move in ['UP', 'DOWN', 'LEFT', 'RIGHT'] if game.can_move(move)]
            idx = random.randint(0, len(playable_moves) - 1)
            move = playable_moves[idx]
            # game.move(move)
            rollout_reward += game.move(move)
            #rollout_reward += self.game.reward(sum_board)
            
        
        return self.rollout_value(self.game, rollout_reward)
    

    def back_prop(self, path, rollout_reward):
        #print(f'path: {path}')
        #print('\n\n')
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
            self.nodes[new_board_key] = StateNode(new_board_key, visit_count=1)
            self.root.edges[move].total_value += move_reward
            self.root.edges[move].visits += 1
            path = self.play_random(self.game, self.SIMS)
            self.back_prop(path)
            self._reset()

    def __str__(self):
        """
        Pretty-print the MCTS from the root up to depth `d`.
        Set `self.print_depth` before calling str(mcts), or it defaults to self.max_depth.
        """
        #d = getattr(self, "print_depth", None)
        # if d is None:
        #     d = getattr(self, "max_depth", 1)

        d = 20

        lines = []
        visited = set()

        def edge_summary(node, action):
            e = node.edges[action]
            if getattr(e, "visits", 0) == 0:
                return "v=0, Q=NA"
            q = e.action_value()  # assumes EdgeStats.action_value() exists
            return f"v={e.visits}, Q={q:.3f}, tot={e.total_value:.1f}"

        def dfs(node_key, depth, prefix=""):
            node = self.nodes.get(node_key)
            if node is None:
                lines.append(prefix + f"[missing node] {node_key}")
                return
            if node_key in visited:
                lines.append(prefix + f"[cycle/seen] visits={node.visit_count} key={node_key}")
                return
            visited.add(node_key)

            lines.append(prefix + f"Node visits={node.visit_count} untried={list(node.untried)} key={node.key}")

            if depth >= d:
                return

            # deterministic action order
            for action in ["UP", "DOWN", "LEFT", "RIGHT"]:
                child_keys = sorted(list(node.children.get(action, set())))
                lines.append(prefix + f"  ├─ {action}: {edge_summary(node, action)}  children={len(child_keys)}")
                for ck in child_keys:
                    dfs(ck, depth + 1, prefix + "  │   ")

        dfs(self.root.key, depth=0, prefix="")
        return "\n".join(lines)
    

    def evaluate_board(self, board) -> float:
        """
        V(s) = w_e*empties + w_m*monotone - w_s*smooth + w_c*corner + w_p*merge_count
        Uses log2(tile) features to stabilize scale across game stages.
        """
        # Default weights (reasonable starting point; tune later)
        w_e = 2.0
        w_m = 1.0
        w_s = 1.0
        w_c = 0.5
        w_p = 0.5

        empties = self._count_empties(board) / 16.0                     # in [0,1]
        mono = self._monotonicity(board)                                 # >= 0 (log-space)
        smooth = self._smoothness(board)                                 # >= 0 (log-space penalty)
        corner = 1.0 if self._max_in_corner(board) else 0.0              # 0 or 1
        merges = self._merge_count(board) / 24.0                         # roughly [0,1] (24 neighbor pairs)

        # (Optional) lightly normalize mono/smooth to reduce scale sensitivity.
        # These constants aren't "the truth"—they're just practical scaling.
        mono_norm = mono / 10.0
        smooth_norm = smooth / 20.0

        return (w_e * empties
                + w_m * mono_norm
                - w_s * smooth_norm
                + w_c * corner
                + w_p * merges)

    def rollout_value(self, game, rollout_score_delta: float) -> float:
        """
        Combine your merge-score deltas with the heuristic.
        If you want purely heuristic leaf evaluation, set lambda_score=0.0.
        """
        lambda_score = 0.1  # start small so score doesn't drown structure
        return lambda_score * rollout_score_delta + self.evaluate_board(game.board)

    # -------- Feature helpers --------

    def _log_tile(self, x: int) -> int:
        return 0 if x == 0 else int(math.log2(x))

    def _count_empties(self, board) -> int:
        return sum(1 for i in range(4) for j in range(4) if board[i][j] == 0)

    def _max_in_corner(self, board) -> bool:
        mx = max(max(row) for row in board)
        corners = (board[0][0], board[0][3], board[3][0], board[3][3])
        return mx in corners

    def _merge_count(self, board) -> int:
        # Count adjacent equal nonzero tiles (potential merges)
        c = 0
        for i in range(4):
            for j in range(4):
                v = board[i][j]
                if v == 0:
                    continue
                if i + 1 < 4 and board[i+1][j] == v:
                    c += 1
                if j + 1 < 4 and board[i][j+1] == v:
                    c += 1
        return c

    def _smoothness(self, board) -> float:
        """
        Penalize large differences between adjacent tiles (in log space).
        Lower is better; we return a nonnegative penalty.
        """
        penalty = 0.0
        for i in range(4):
            for j in range(4):
                v = board[i][j]
                if v == 0:
                    continue
                lv = self._log_tile(v)
                # right neighbor
                if j + 1 < 4 and board[i][j+1] != 0:
                    penalty += abs(lv - self._log_tile(board[i][j+1]))
                # down neighbor
                if i + 1 < 4 and board[i+1][j] != 0:
                    penalty += abs(lv - self._log_tile(board[i+1][j]))
        return penalty

    def _monotonicity(self, board) -> float:
        """
        Reward boards that are monotone along rows/cols in log space.
        """
        def line_mono(vals):
            # vals: list of 4 tile values (ints)
            logs = [self._log_tile(x) for x in vals]
            inc = 0.0
            dec = 0.0
            for k in range(3):
                a, b = logs[k], logs[k+1]
                if a < b:
                    inc += (b - a)
                elif a > b:
                    dec += (a - b)
            return max(inc, dec)

        score = 0.0
        for i in range(4):
            score += line_mono(board[i])
        for j in range(4):
            score += line_mono([board[i][j] for i in range(4)])
        return score
