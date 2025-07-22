import legalmoves as legal


# Material values, keyed by piece type letter. Always positive here; the sign
# (White = +, Black = -) is applied in evaluate().
VALUES = {
    "P": 100,
    "N": 320,
    "B": 330,
    "R": 500,
    "Q": 900,
    "K": 20000,
}

# A mate is worth more than any reachable material swing.
MATE = 1_000_000

# Piece-square tables, written from White's point of view. The board is indexed
# 0..63 with index 0 = a8 and index 63 = h1 (see legalmoves.square_to_name), so
# row 0 of each table below is rank 8 and row 7 is rank 1 -- exactly the visual
# layout. A Black piece on index i is scored with the vertically mirrored square
# (i ^ 56), which swaps rank r with rank 7 - r.
PAWN_PST = [
    0,   0,   0,   0,   0,   0,   0,   0,
    50,  50,  50,  50,  50,  50,  50,  50,
    10,  10,  20,  30,  30,  20,  10,  10,
    5,   5,   10,  25,  25,  10,  5,   5,
    0,   0,   0,   20,  20,  0,   0,   0,
    5,  -5,  -10,  0,   0,  -10, -5,   5,
    5,   10,  10, -20, -20,  10,  10,  5,
    0,   0,   0,   0,   0,   0,   0,   0,
]

KNIGHT_PST = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,  0,   0,   0,   0,  -20, -40,
    -30,  0,   10,  15,  15,  10,  0,  -30,
    -30,  5,   15,  20,  20,  15,  5,  -30,
    -30,  0,   15,  20,  20,  15,  0,  -30,
    -30,  5,   10,  15,  15,  10,  5,  -30,
    -40, -20,  0,   5,   5,   0,  -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50,
]

BISHOP_PST = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,  0,   0,   0,   0,   0,   0,  -10,
    -10,  0,   5,   10,  10,  5,   0,  -10,
    -10,  5,   5,   10,  10,  5,   5,  -10,
    -10,  0,   10,  10,  10,  10,  0,  -10,
    -10,  10,  10,  10,  10,  10,  10, -10,
    -10,  5,   0,   0,   0,   0,   5,  -10,
    -20, -10, -10, -10, -10, -10, -10, -20,
]

ROOK_PST = [
    0,   0,   0,   0,   0,   0,   0,   0,
    5,   10,  10,  10,  10,  10,  10,  5,
    -5,  0,   0,   0,   0,   0,   0,  -5,
    -5,  0,   0,   0,   0,   0,   0,  -5,
    -5,  0,   0,   0,   0,   0,   0,  -5,
    -5,  0,   0,   0,   0,   0,   0,  -5,
    -5,  0,   0,   0,   0,   0,   0,  -5,
    0,   0,   0,   5,   5,   0,   0,   0,
]

QUEEN_PST = [
    -20, -10, -10, -5,  -5,  -10, -10, -20,
    -10,  0,   0,   0,   0,   0,   0,  -10,
    -10,  0,   5,   5,   5,   5,   0,  -10,
    -5,   0,   5,   5,   5,   5,   0,  -5,
    0,    0,   5,   5,   5,   5,   0,  -5,
    -10,  5,   5,   5,   5,   5,   0,  -10,
    -10,  0,   5,   0,   0,   0,   0,  -10,
    -20, -10, -10, -5,  -5,  -10, -10, -20,
]

# Midgame king table: keep the king tucked away near its starting corner.
KING_PST = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20,   20,  0,   0,   0,   0,   20,  20,
    20,   30,  10,  0,   0,   10,  30,  20,
]

PST = {
    "P": PAWN_PST,
    "N": KNIGHT_PST,
    "B": BISHOP_PST,
    "R": ROOK_PST,
    "Q": QUEEN_PST,
    "K": KING_PST,
}


def evaluate(board):
    
    score = 0
    for index in range(64):
        piece = board[index]
        if piece is None:
            continue

        colour = piece[0]
        piece_type = piece[1]

        if colour == "w":
            score += VALUES[piece_type] + PST[piece_type][index]
        else:
            score -= VALUES[piece_type] + PST[piece_type][index ^ 56]

    return score


def terminal_score(colour, board, depth):
    """""
    Checkmate is scaled by remaining depth so the search prefers faster mates
    (and delaying being mated). Stalemate is a draw.
    """
    if legal.is_in_check(colour, board):
        if colour == "w":
            return -(MATE + depth)  # White is mated: terrible for White
        return MATE + depth         # Black is mated: great for White
    return 0  # stalemate


def order_moves(board, moves):
    """Search captures and promotions first to improve alpha-beta cutoffs."""

    def noise(move):
        victim = board[move.to_square - 1]
        gain = VALUES[victim[1]] if victim is not None else 0
        if move.promotion is not None:
            gain += VALUES[move.promotion]
        return gain

    return sorted(moves, key=noise, reverse=True)


def quiescence(board, colour, castling_rights, en_passant_square, alpha, beta):
    """Extend the search over captures/promotions only, until the position is
    quiet. This avoids the horizon effect where the fixed-depth search stops in
    the middle of a trade and miscounts material."""
    enemy = "b" if colour == "w" else "w"
    stand_pat = evaluate(board)

    if colour == "w":  # maximizer
        if stand_pat >= beta:
            return stand_pat
        if stand_pat > alpha:
            alpha = stand_pat
    else:  # minimizer
        if stand_pat <= alpha:
            return stand_pat
        if stand_pat < beta:
            beta = stand_pat

    moves = legal.all_legal_move_objects(colour, board, castling_rights, en_passant_square)
    noisy_moves = [
        move
        for move in moves
        if board[move.to_square - 1] is not None
        or move.en_passant_capture_square is not None
        or move.promotion is not None
    ]

    for move in order_moves(board, noisy_moves):
        new_board = board.copy()
        new_rights = legal._copy_rights(castling_rights)
        undo = legal.make_move(new_board, new_rights, move)

        score = quiescence(
            new_board, enemy, new_rights, undo.en_passant_square, alpha, beta
        )

        if colour == "w":
            if score > alpha:
                alpha = score
            if alpha >= beta:
                return beta
        else:
            if score < beta:
                beta = score
            if alpha >= beta:
                return alpha

    return alpha if colour == "w" else beta


def minmax(depth, board, colour, castling_rights, en_passant_square,
           alpha=float("-inf"), beta=float("inf")):
    
    enemy = "b" if colour == "w" else "w"

    moves = legal.all_legal_move_objects(colour, board, castling_rights, en_passant_square)

    if not moves:
        return terminal_score(colour, board, depth), None

    if depth == 0:
        return quiescence(
            board, colour, castling_rights, en_passant_square, alpha, beta
        ), None

    moves = order_moves(board, moves)
    best_move = None

    if colour == "w":  # maximizer
        best_score = float("-inf")
        for move in moves:
            new_board = board.copy()
            new_rights = legal._copy_rights(castling_rights)
            undo = legal.make_move(new_board, new_rights, move)

            score, _ = minmax(
                depth - 1, new_board, enemy, new_rights,
                undo.en_passant_square, alpha, beta,
            )

            if score > best_score:
                best_score = score
                best_move = move
            if best_score > alpha:
                alpha = best_score
            if alpha >= beta:
                break

        return best_score, best_move

    else:  # minimizer (Black, the AI)
        best_score = float("inf")
        for move in moves:
            new_board = board.copy()
            new_rights = legal._copy_rights(castling_rights)
            undo = legal.make_move(new_board, new_rights, move)

            score, _ = minmax(
                depth - 1, new_board, enemy, new_rights,
                undo.en_passant_square, alpha, beta,
            )

            if score < best_score:
                best_score = score
                best_move = move
            if best_score < beta:
                beta = best_score
            if alpha >= beta:
                break

        return best_score, best_move
