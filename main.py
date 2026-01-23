from src.game import Game
from src.montecarlo import MCTS

def main():
    board = Game()
    # moves = ["LEFT", "UP", "RIGHT", "DOWN", "LEFT", "UP"]
    print("-------STARTING BOARD-------")
    print(board)
    
    # for move in moves:
    #     board.move(move)
    #     print(f"----------{move}---------")
    #     print(board)
    while not board.isTerminated():
        search_tree = MCTS(board, 50)
        move = search_tree.next_move()
        board.move(move)
        print(f"----------{move}---------")
        print(board)
        print(f'score:{board.score}')

    

if __name__ == "__main__":
    main()