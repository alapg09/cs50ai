"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # variables to hold the numbers of moves
    num_X = 0
    num_O = 0
    num_EMPTY = 0

    # looping through the grid
    for i in range(3):
        for j in range(3):
            match board[i][j]:
                case "X":
                    num_X += 1
                case "O":
                    num_O += 1
                case _:
                    num_EMPTY += 1

    # terminal grid
    if num_EMPTY == 0:
        return None
    
    # move calculation logic
    if num_X == num_O:
        return X
    else: 
        return O
    


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # list to hold the possible actions
    empty_cells = []

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                empty_cells.append((i,j))

    # terminal grid
    if len(empty_cells) == 0:
        return None

    return set(empty_cells)


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    # new_board
    new_board = [[EMPTY, EMPTY, EMPTY],
                [EMPTY, EMPTY, EMPTY],
                [EMPTY, EMPTY, EMPTY]]

    # cloning
    for i in range(3):
        for j in range(3):
            new_board[i][j] = board[i][j]
    # unpacking the action
    i, j = action

    # checking if the action is out of bounds
    if not (0 <= i < 3 and 0 <= j < 3):
        raise Exception("move out of bounds")

    # checking if the cell is empty
    if board[i][j] != EMPTY:
        raise Exception("invalid move")
    else:
        # current player will make his move
        current_move = player(board)
        new_board[i][j] = current_move

    return new_board

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # seperating rows, columns and diagonals as they are the only possibility for winning
    rows = board
    columns = [list(col) for col in zip(*board)]

    diagonal1 = [board[i][i] for i in range(3)]         # Top-left to bottom-right
    diagonal2 = [board[i][2 - i] for i in range(3)]     # Top-right to bottom-left

    # all the possible winning lines
    winning_lines = rows + columns + [diagonal1, diagonal2]

    # if all the entries of a line same
    for line in winning_lines:
        if line[0] == line[1] == line[2] != EMPTY:
            return line[0]  # 'X' or 'O'

    


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    if winner(board) is not None:
        return True
    
    for i in range(3):
        for j in range(3):
            # if any cell is empty --> not terminal
            if board[i][j] == EMPTY:
                return False
    

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # using the winner function
    w = winner(board)
    if w == X:
        return 1
    elif w == O:
        return -1
    else:
        return 0


def minimax(board):
    if terminal(board):
        return None

    current = player(board)
    best_move = None

    if current == X:
        best_score = float('-inf')
        for action in actions(board):
            score = min_value(result(board, action), alpha=float('-inf'), beta=float('inf'))
            if score > best_score:
                best_score = score
                best_move = action
    else:
        best_score = float('inf')
        for action in actions(board):
            score = max_value(result(board, action), alpha=float('-inf'), beta=float('inf'))
            if score < best_score:
                best_score = score
                best_move = action

    return best_move


def max_value(board, alpha, beta):
    if terminal(board):
        return utility(board)

    v = float('-inf')
    for action in actions(board):
        v = max(v, min_value(result(board, action), alpha, beta))
        alpha = max(alpha, v)
        if alpha >= beta:
            break  # β cutoff
    return v


def min_value(board, alpha, beta):
    if terminal(board):
        return utility(board)

    v = float('inf')
    for action in actions(board):
        v = min(v, max_value(result(board, action), alpha, beta))
        beta = min(beta, v)
        if beta <= alpha:
            break  # α cutoff
    return v