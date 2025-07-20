import piecemoves as p

def isSquareAttacked(square, byColour, board):
    # Look OUTWARD from `square` instead of scanning every enemy piece. This does
    # a constant handful of move generations from a single square, rather than
    # generating the full move list of every `byColour` piece on the board.
    #
    # Trick for sliders/knights: generate moves from `square` as if it held a
    # piece of the OPPOSITE colour. Those generators stop at the first occupied
    # square in each direction and include it only if it is capturable -- i.e.
    # only if it belongs to `byColour`. So the terminal occupied square in each
    # ray is exactly a candidate attacker.
    enemy = "b" if byColour == "w" else "w"

    # Knights
    for target in p.KnightMoves(enemy, square, board):
        if board[target - 1] == byColour + "N":
            return True

    # Enemy king on an adjacent square
    for target in KingAttacks(square):
        if board[target - 1] == byColour + "K":
            return True

    # Pawns: a `byColour` pawn attacks `square` from one rank "behind" it,
    # diagonally. White pawns attack upward, so a white attacker sits at
    # square+7/square+9; black attackers sit at square-7/square-9.
    pawn_deltas = (7, 9) if byColour == "w" else (-7, -9)
    current_file = (square - 1) % 8
    for delta in pawn_deltas:
        attacker = square + delta
        if not (1 <= attacker <= 64):
            continue
        # Reject diagonals that wrapped across a board edge.
        if abs(((attacker - 1) % 8) - current_file) != 1:
            continue
        if board[attacker - 1] == byColour + "P":
            return True

    # Sliding pieces: the first occupied square along each ray is the only one
    # that can attack `square`.
    for target in p.RookMoves(enemy, square, board):
        piece = board[target - 1]
        if piece is not None and piece[0] == byColour and piece[1] in ("R", "Q"):
            return True

    for target in p.BishopMoves(enemy, square, board):
        piece = board[target - 1]
        if piece is not None and piece[0] == byColour and piece[1] in ("B", "Q"):
            return True

    return False

def KingAttacks(squareIndex):
    attacks = []

    directions = [-9, -8, -7, -1, 1, 7, 8, 9]

    current_file = (squareIndex - 1) % 8

    for direction in directions:
        target = squareIndex + direction

        if not (1 <= target <= 64):
            continue

        target_file = (target - 1) % 8

        if abs(current_file - target_file) > 1:
            continue

        attacks.append(target)

    return attacks

def findKing(colour, board):
    king = colour + "K"

    for i, piece in enumerate(board):
        if piece == king:
            return i + 1

    return None


def isInCheck(colour, board):
    king_square = findKing(colour, board)

    if king_square is None:
        return False

    enemy = "b" if colour == "w" else "w"

    return isSquareAttacked(king_square, enemy, board)