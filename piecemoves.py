def sameColour(colour, piece):
    if piece == 0 or piece is None:
        return False
    return piece[0] == colour

top_boundary    = {1, 2, 3, 4, 5, 6, 7, 8}
right_boundary  = {8, 16, 24, 32, 40, 48, 56, 64}
bottom_boundary = {57, 58, 59, 60, 61, 62, 63, 64}
left_boundary   = {1, 9, 17, 25, 33, 41, 49, 57}  

# Maps each delta to the boundary set(s) that block movement in that direction 
_BOUNDARY_CHECKS = {
    +1: (right_boundary,),
    -1: (left_boundary,),
    -8: (top_boundary,),
    +8: (bottom_boundary,),
    -7: (right_boundary, top_boundary),
    -9: (left_boundary,  top_boundary),
    +9: (right_boundary, bottom_boundary),
    +7: (left_boundary,  bottom_boundary),
}

ROOK_BOUNDARY_CHECKS = {
    +1: (right_boundary,),
    -1: (left_boundary,),
    -8: (top_boundary,),
    +8: (bottom_boundary,),
}

PAWN_BOUNDARY_CHECKS = {
    -8: (top_boundary,),
}

BISHOP_BOUNDARY_CHECKS = {
    -7: (right_boundary, top_boundary),
    -9: (left_boundary,  top_boundary),
    +9: (right_boundary, bottom_boundary),
    +7: (left_boundary,  bottom_boundary),
}

def QueenMoves(colour, squareIndex, board):
    moves = []

    for delta, boundaries in _BOUNDARY_CHECKS.items():
        current = squareIndex
        while True:
            # If the current square sits on a wrapping edge, stop before stepping
            if any(current in b for b in boundaries):
                break

            nxt = current + delta
            if not (1 <= nxt <= 64):
                break

            piece = board[nxt - 1]
            if piece is not None:
                if not sameColour(colour, piece):
                    moves.append(nxt)
                break

            moves.append(nxt)
            current = nxt
    return moves

def RookMoves(colour, squareIndex, board):
    moves = []

    for delta, boundaries in ROOK_BOUNDARY_CHECKS.items():
        current = squareIndex
        while True:
            # If the current square sits on a wrapping edge, stop before stepping
            if any(current in b for b in boundaries):
                break

            nxt = current + delta
            if not (1 <= nxt <= 64):
                break

            piece = board[nxt - 1]
            if piece is not None:
                if not sameColour(colour, piece):
                    moves.append(nxt)
                break

            moves.append(nxt)
            current = nxt
    
    return moves

def BishopMoves(colour, squareIndex, board):
    moves = []

    for delta, boundaries in BISHOP_BOUNDARY_CHECKS.items():
        current = squareIndex
        while True:
            # If the current square sits on a wrapping edge, stop before stepping
            if any(current in b for b in boundaries):
                break

            nxt = current + delta
            if not (1 <= nxt <= 64):
                break

            piece = board[nxt - 1]
            if piece is not None:
                if not sameColour(colour, piece):
                    moves.append(nxt)
                break

            moves.append(nxt)
            current = nxt
    return moves


def KingMoves(colour, squareIndex, board):
    moves = []

    directions = [-9, -8, -7, -1, 1, 7, 8, 9]

    current_file = (squareIndex - 1) % 8

    for direction in directions:
        move = squareIndex + direction

        if not (1 <= move <= 64):
            continue

        target_file = (move - 1) % 8

        if abs(current_file - target_file) > 1:
            continue

        piece = board[move - 1]

        if piece is None or not sameColour(colour, piece):
            moves.append(move)

    return moves

def KnightMoves(colour, squareIndex, board):
    moves = []

    knight_offsets = [
        (-2, -1), (-2, 1),
        (-1, -2), (-1, 2),
        (1, -2),  (1, 2),
        (2, -1),  (2, 1)
    ]

    file = (squareIndex - 1) % 8
    rank = (squareIndex - 1) // 8

    for file_change, rank_change in knight_offsets:
        new_file = file + file_change
        new_rank = rank + rank_change

        if 0 <= new_file < 8 and 0 <= new_rank < 8:
            move = new_rank * 8 + new_file + 1
            piece = board[move - 1]

            if piece is None or not sameColour(colour, piece):
                moves.append(move)

    return moves
