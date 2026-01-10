"""
A instance of a 2048 game
"""
import random
class Game():
    PROB_SPAWN_TWO = 0.8
    def __init__(self, board=None):
        self.game_state = "ACTIVE"
        if board:
            if len(board) != 4 or len(board[0]) != 4:
                raise RuntimeError("Board must always be 4x4 grid")
            
            self.board = [[tile for tile in row] for row in board]
            if self._game_over():
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
        if direction not in ["UP", "DOWN", "LEFT", "RIGHT"]:
            raise RuntimeError("Invalid direction")

        if self.game_state == "TERMINATED":
            return
        board_original = [[tile for tile in row] for row in self.board]
        if direction == "UP":
            for j in range(4):
                temp_row = [self.board[0][j], self.board[1][j], self.board[2][j], self.board[3][j]]
                self._merge_row(temp_row)

                for i in range(4):
                    self.board[i][j] = temp_row[i]

        if direction == "DOWN":
            for j in range(4):
                temp_row = [self.board[3][j], self.board[2][j], self.board[1][j], self.board[0][j]]
                self._merge_row(temp_row)
                for i in range(4):
                    self.board[3 - i][j] = temp_row[i]
        if direction == "LEFT":
            for i in range(4):
                self._merge_row(self.board[i])
        
        if direction == "RIGHT":
            for i in range(4):
                temp_row = self.board[i][::-1]
                self._merge_row(temp_row)
                self.board[i] = temp_row[::-1]
        if board_original != self.board:
            self._spawntile()
        if self._game_over():
            self.game_state = "TERMINATED"
    
    def _merge_row(self, row):
        """
        Merges a row vector as if hitting LEFT in the game
        Requires: row length 4
        """
        self._move_zeros(row)
        for i in range(3):
            if row[i] == row[i + 1]:
                row[i] *= 2
                row[i + 1] = 0
        
        self._move_zeros(row)
    

    def _move_zeros(self, row):
            lastnonzero = 0
            for curr in range(len(row)):
                if row[curr] != 0:
                    temp = row[lastnonzero]
                    row[lastnonzero] = row[curr]
                    row[curr] = temp
                    lastnonzero += 1

    def _game_over(self):
        return False

    def __str__(self):
        return str(self.board[0]) + '\n' + str(self.board[1]) + '\n' + str(self.board[2]) + '\n' + str(self.board[3])
        
        
            
        