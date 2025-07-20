import attacks as a


STARTING_SQUARES = {
    "w": {
        "king": 61,
        "kingside_rook": 64,
        "queenside_rook": 57,
        "kingside_empty": [62, 63],
        "queenside_empty": [58, 59, 60],
        "kingside_safe": [61, 62, 63],
        "queenside_safe": [61, 60, 59],
        "kingside_target": 63,
        "queenside_target": 59,
    },
    "b": {
        "king": 5,
        "kingside_rook": 8,
        "queenside_rook": 1,
        "kingside_empty": [6, 7],
        "queenside_empty": [2, 3, 4],
        "kingside_safe": [5, 6, 7],
        "queenside_safe": [5, 4, 3],
        "kingside_target": 7,
        "queenside_target": 3,
    },
}


def starting_rights():
    return {
        "w": {"kingside": True, "queenside": True},
        "b": {"kingside": True, "queenside": True},
    }


def get_castling_moves(colour, board, castling_rights):
    moves = []
    enemy = "b" if colour == "w" else "w"
    squares = STARTING_SQUARES[colour]

    if board[squares["king"] - 1] != f"{colour}K":
        return moves

    if _can_castle(colour, "kingside", board, castling_rights, enemy):
        moves.append(squares["kingside_target"])

    if _can_castle(colour, "queenside", board, castling_rights, enemy):
        moves.append(squares["queenside_target"])

    return moves


def move_piece(board, castling_rights, from_square, to_square, promotion=None, en_passant_capture_square=None,):
    piece = board[from_square - 1]

    if piece is None:
        return

    capture_square = en_passant_capture_square or to_square
    captured_piece = board[capture_square - 1]
    updateCastlingRights(piece, from_square, castling_rights)
    _update_rights_for_capture(captured_piece, to_square, castling_rights)

    board[to_square - 1] = piece[0] + promotion if promotion is not None else piece
    board[from_square - 1] = None

    if en_passant_capture_square is not None:
        board[en_passant_capture_square - 1] = None

    if piece[1] == "K" and abs(to_square - from_square) == 2:
        _move_castling_rook(board, piece[0], to_square)


def _can_castle(colour, side, board, castling_rights, enemy):
    squares = STARTING_SQUARES[colour]

    if not _has_castling_right(castling_rights, colour, side):
        return False

    if board[squares[f"{side}_rook"] - 1] != f"{colour}R":
        return False

    if any(board[square - 1] is not None for square in squares[f"{side}_empty"]):
        return False

    return all(
        not a.isSquareAttacked(square, enemy, board)
        for square in squares[f"{side}_safe"]
    )


def _move_castling_rook(board, colour, king_target_square):
    if colour == "w" and king_target_square == 63:
        board[62 - 1] = "wR"
        board[64 - 1] = None
    elif colour == "w" and king_target_square == 59:
        board[60 - 1] = "wR"
        board[57 - 1] = None
    elif colour == "b" and king_target_square == 7:
        board[6 - 1] = "bR"
        board[8 - 1] = None
    elif colour == "b" and king_target_square == 3:
        board[4 - 1] = "bR"
        board[1 - 1] = None


def updateCastlingRights(piece, from_square, castling_rights):
    if piece is None:
        return

    colour = piece[0]
    squares = STARTING_SQUARES[colour]

    if piece[1] == "K":
        _set_castling_right(castling_rights, colour, "kingside", False)
        _set_castling_right(castling_rights, colour, "queenside", False)
    elif piece[1] == "R":
        if from_square == squares["kingside_rook"]:
            _set_castling_right(castling_rights, colour, "kingside", False)
        elif from_square == squares["queenside_rook"]:
            _set_castling_right(castling_rights, colour, "queenside", False)


def _update_rights_for_capture(captured_piece, to_square, castling_rights):
    if captured_piece is None or captured_piece[1] != "R":
        return

    colour = captured_piece[0]
    squares = STARTING_SQUARES[colour]

    if to_square == squares["kingside_rook"]:
        _set_castling_right(castling_rights, colour, "kingside", False)
    elif to_square == squares["queenside_rook"]:
        _set_castling_right(castling_rights, colour, "queenside", False)


def _has_castling_right(castling_rights, colour, side):
    return castling_rights[colour][side]


def _set_castling_right(castling_rights, colour, side, can_castle):
    castling_rights[colour][side] = can_castle
