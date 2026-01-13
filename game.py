"""
A instance of a 2048 game
"""
import random


def game_over(board):
        """
        Returns if it is possible to make a legal move on the game board
        """
        dirs = [(1, 0), (0,1), (-1, 0), (0, -1)]
        for i in range(4):
            for j in range(4):
                if board[i][j] == 0:
                    return False
                for dx,dy in dirs:
                    if 0 <= i + dx < 4 and 0 <= j + dy < 4:
                        if board[i][j] == board[i + dx][j + dy]:
                            return False
        
        return True
class Game():
    PROB_SPAWN_TWO = 0.9
    def __init__(self, board=None):
        self.game_state = "ACTIVE"
        if board:
            if len(board) != 4 or len(board[0]) != 4:
                raise RuntimeError("Board must always be 4x4 grid")
            
            self.board = [[tile for tile in row] for row in board]
            if game_over(self.board):
                self.game_state = "TERMINATED"
        else:
            self.board = [[0] * 4 for _ in range(4)]
            self._spawntile()
            self._spawntile()
        
        return
            

    def _spawntile(self):
        availables = []
        for i in range(16):
            if self.board[i // 4][i % 4] == 0:
                availables.append(i)
        if not availables:
            self.game_state = "TERMINATED"
            return

        idx = random.randint(0, len(availables) -1 )
        board_idx = availables[idx]
        self.board[board_idx // 4][board_idx % 4 ] = 2 if random.random() <= self.PROB_SPAWN_TWO else 4

        return
    
    def move(self, direction):
        """
        Moves the game board in desired direction, updates if game is active or terminated, and spawns
        in a new tile if possible. Returns the merged score gained by performing the move
        """
        if self.game_state == "TERMINATED":
            return 0
        has_changed, total_reward = self._move_board(self.board, direction)
        if has_changed:
            self._spawntile()
        if game_over(self.board):
            self.game_state = "TERMINATED"
        
        return total_reward
    

    def _move_board(self, board, direction):
        """"
        Moves a board in direction
        Returns (hasChanged, totalReward)
        """
        if direction not in ["UP", "DOWN", "LEFT", "RIGHT"]:
            raise RuntimeError("Invalid direction")
        
        total_gains = 0
        board_original = [[tile for tile in row] for row in board]
        if direction == "UP":
            for j in range(4):
                temp_row = [board[0][j], board[1][j], board[2][j], board[3][j]]
                total_gains += self._merge_row(temp_row)

                for i in range(4):
                    board[i][j] = temp_row[i]

        elif direction == "DOWN":
            for j in range(4):
                temp_row = [board[3][j], board[2][j], board[1][j], board[0][j]]
                total_gains += self._merge_row(temp_row)
                for i in range(4):
                    board[3 - i][j] = temp_row[i]

        elif direction == "LEFT":
            for i in range(4):
                total_gains += self._merge_row(board[i])
        
        else:
            for i in range(4):
                temp_row = board[i][::-1]
                total_gains += self._merge_row(temp_row)
                board[i] = temp_row[::-1]
        
        return (board_original != board, total_gains)
    
    def _merge_row(self, row):
        """
        Merges a row vector as if hitting LEFT in the game
        Requires: row length 4
        Returns the value of tiles merged
        """
        value = 0
        self._move_zeros(row)
        for i in range(3):
            if row[i] == row[i + 1]:
                row[i] *= 2
                value += row[i]
                row[i + 1] = 0
        
        self._move_zeros(row)
        return value
    

    def _move_zeros(self, row):
            lastnonzero = 0
            for curr in range(len(row)):
                if row[curr] != 0:
                    temp = row[lastnonzero]
                    row[lastnonzero] = row[curr]
                    row[curr] = temp
                    lastnonzero += 1

    
    
    def isTerminated(self):
        """
        Returns if the state of the game is terminated
        """
        return self.game_state == "TERMINATED"

    def __str__(self):
        return str(self.board[0]) + '\n' + str(self.board[1]) + '\n' + str(self.board[2]) + '\n' + str(self.board[3])
        
    def can_move(self, direction):
        if direction not in ["UP", "DOWN", "RIGHT", "LEFT"]:
            raise RuntimeError("Invalid Direction") 

        board_copy = [[tile for tile in row] for row in self.board]
        has_changed = self._move_board(board_copy, direction)
        return has_changed
    
    def key(self):
        return tuple(tuple(row) for row in self.board)

    def clone(self):
        return Game(self.board)
