from game import Game

def main():
    board = Game()
    moves = ["LEFT", "UP", "RIGHT", "DOWN", "LEFT", "UP"]
    print("-------STARTING BOARD-------")
    print(board)
    
    for move in moves:
        board.move(move)
        print(f"----------{move}---------")
        print(board)

if __name__ == "__main__":
    main()