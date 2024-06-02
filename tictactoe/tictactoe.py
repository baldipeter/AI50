"""
Tic Tac Toe Player
"""

import math
import copy

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
    count = 0
    for i in board:
        for j in i:
            if j == EMPTY:
                count += 1
    if (count % 2) == 1:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible_actions.add((i, j))
    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    (i, j) = action
    if i not in range(3) or j not in range(3) or (board[i][j] != EMPTY):
        raise Exception("invalid move")
    move = copy.deepcopy(board)
    move[i][j] = player(board)
    return move


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check rows
    for i in board:
        if len(set(i)) == 1 and i[0] != None:
            return i[0]

    # Check columns
    for j in range(3):
        if board[0][j] == board[1][j] and board[0][j] == board[2][j] and board[0][j] != None:
            return board[0][j]

    # Check diagonal
    if board[1][1] == board[0][0] and board[1][1] == board[2][2] and board[1][1] != None:
        return board[1][1]
    elif board[1][1] == board[0][2] and board[1][1] == board[2][0] and board[1][1] != None:
        return board[1][1]

    # If noone has win
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None or is_full(board):
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def is_full(board):
    """
    Check if there are any EMPTY slots left
    """
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                return False
    return True


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    # Save every action in a dict
    best_action = {}
    turn = player(board)
    for action in actions(board):
        if turn == X:
            # As X has made a move the Min_Value function is called (as it is O's turn)
            v = Min_Value(result(board, action))
        elif turn == O:
            v = Max_Value(result(board, action))
        best_action[action] = v

    # Sort the actions based on v
    best_action = sorted(best_action.items(), key=lambda item: item[1])

    # Decide which action to take, among equals the choice is up to the dict
    if turn == X:
        return best_action[-1][0]
    return best_action[0][0]


def Max_Value(board):
    """
    Minimax algorithm's max value finder function
    """
    if terminal(board):
        return utility(board)
    v = -math.inf
    for action in actions(board):
        v = max(v, Min_Value(result(board, action)))
    return v


def Min_Value(board):
    """
    Minimax algorithm's min value finder function
    """
    if terminal(board):
        return utility(board)
    v = math.inf
    for action in actions(board):
        v = min(v, Max_Value(result(board, action)))
    return v
