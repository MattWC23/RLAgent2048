from game import Game
from montecarlo import MCTS

def main():
    board = Game()
    # moves = ["LEFT", "UP", "RIGHT", "DOWN", "LEFT", "UP"]
    print("-------STARTING BOARD-------")
    print(board)
    
    # for move in moves:
    #     board.move(move)
    #     print(f"----------{move}---------")
    #     print(board)
    for _ in range(100):
        search_tree = MCTS(board)
        move = search_tree.next_move()
        board.move(move)
        print(f"----------{move}---------")
        print(board)


if __name__ == "__main__":
    main()