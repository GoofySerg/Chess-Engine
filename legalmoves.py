import copy
from dataclasses import dataclass
import attacks as a
import castling
import piecemoves as p


STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
PROMOTION_PIECES = ("Q", "R", "B", "N")


@dataclass(frozen=True)
class Move:
    from_square: int
    to_square: int
    promotion: str | None = None
    en_passant_capture_square: int | None = None

@dataclass
class Undo:
    from_square: int
    to_square: int
    moved_piece: str | None
    captured_piece: str | None
    promotion: str | None
    castling_snapshot: dict
    en_passant_square: int | None

def _copy_rights(castling_rights):
    
    return {
        key: value.copy() if isinstance(value, dict) else value
        for key, value in castling_rights.items()
    }


def find_king(colour, board):
    return a.findKing(colour, board)


def is_in_check(colour, board):
    return a.isInCheck(colour, board)


def legal_move_objects_for_square(
    squareIndex, colour, board, castling_rights, en_passant_square=None
):
    piece = board[squareIndex - 1]

    if piece is None or piece[0] != colour:
        return []

    legal_moves = []

    for move in pseudo_move_objects_for_square(
        squareIndex, colour, board, castling_rights, en_passant_square
    ):
        test_board = board.copy()
        test_rights = _copy_rights(castling_rights)
        make_move(test_board, test_rights, move)

        if not a.isInCheck(colour, test_board):
            legal_moves.append(move)

    return legal_moves


def pseudo_move_objects_for_square(
    squareIndex, colour, board, castling_rights, en_passant_square=None
):
    piece = board[squareIndex - 1]

    if piece is None:
        return []

    piece_type = piece[1]

    if piece_type == "P":
        return pawn_move_objects(colour, squareIndex, board, en_passant_square)
    if piece_type == "N":
        return target_moves(squareIndex, p.KnightMoves(colour, squareIndex, board))
    if piece_type == "B":
        return target_moves(squareIndex, p.BishopMoves(colour, squareIndex, board))
    if piece_type == "R":
        return target_moves(squareIndex, p.RookMoves(colour, squareIndex, board))
    if piece_type == "Q":
        return target_moves(squareIndex, p.QueenMoves(colour, squareIndex, board))
    if piece_type == "K":
        return target_moves(
            squareIndex,
            p.KingMoves(colour, squareIndex, board)
            + castling.get_castling_moves(colour, board, castling_rights),
        )

    return []


def target_moves(from_square, targets):
    return [Move(from_square, target) for target in targets]


def pawn_move_objects(colour, squareIndex, board, en_passant_square=None):
    moves = []
    direction = -8 if colour == "w" else 8
    start_rank = range(49, 57) if colour == "w" else range(9, 17)
    promotion_rank = range(1, 9) if colour == "w" else range(57, 65)

    one_forward = squareIndex + direction

    if 1 <= one_forward <= 64 and board[one_forward - 1] is None:
        add_pawn_move(moves, squareIndex, one_forward, promotion_rank)

        two_forward = squareIndex + 2 * direction

        if squareIndex in start_rank:
            if 1 <= two_forward <= 64 and board[two_forward - 1] is None:
                moves.append(Move(squareIndex, two_forward))

    current_file = (squareIndex - 1) % 8

    for delta in (direction - 1, direction + 1):
        target = squareIndex + delta

        if not (1 <= target <= 64):
            continue

        target_file = (target - 1) % 8

        if abs(current_file - target_file) != 1:
            continue

        piece = board[target - 1]

        if piece is not None and piece[0] != colour:
            add_pawn_move(moves, squareIndex, target, promotion_rank)
        elif target == en_passant_square:
            captured_square = target + (8 if colour == "w" else -8)
            captured_piece = board[captured_square - 1]

            if captured_piece == (("b" if colour == "w" else "w") + "P"):
                moves.append(Move(squareIndex, target, en_passant_capture_square=captured_square))

    return moves


def add_pawn_move(moves, from_square, to_square, promotion_rank):
    if to_square in promotion_rank:
        for promotion in PROMOTION_PIECES:
            moves.append(Move(from_square, to_square, promotion=promotion))
    else:
        moves.append(Move(from_square, to_square))



def make_move(board, castling_rights, move):
    piece = board[move.from_square - 1]
    captured = board[move.to_square - 1]

    undo = Undo(
        from_square=move.from_square,
        to_square=move.to_square,
        moved_piece=piece,
        captured_piece=captured,
        promotion=move.promotion,
        castling_snapshot=_copy_rights(castling_rights),
        en_passant_square=None
    )

    castling.move_piece(
        board,
        castling_rights,
        move.from_square,
        move.to_square,
        move.promotion,
        move.en_passant_capture_square,
    )

    # en passant square logic
    if piece is not None and piece[1] == "P" and abs(move.to_square - move.from_square) == 16:
        undo.en_passant_square = (move.from_square + move.to_square) // 2
        return undo

    return undo

def all_legal_move_objects(colour, board, castling_rights, en_passant_square=None):
    moves = []

    for square, piece in enumerate(board, start=1):
        if piece is not None and piece[0] == colour:
            moves.extend(
                legal_move_objects_for_square(
                    square, colour, board, castling_rights, en_passant_square
                )
            )

    return moves


def perft(colour, board, castling_rights, depth, en_passant_square=None):
    if depth == 0:
        return 1

    enemy = "b" if colour == "w" else "w"
    nodes = 0

    for move in all_legal_move_objects(colour, board, castling_rights, en_passant_square):
        test_board = board.copy()
        test_rights = copy.deepcopy(castling_rights)
        next_en_passant_square = make_move(test_board, test_rights, move)
        nodes += perft(enemy, test_board, test_rights, depth - 1, next_en_passant_square)

    return nodes


def perft_divide(colour, board, castling_rights, depth, en_passant_square=None):
    enemy = "b" if colour == "w" else "w"
    results = {}

    for move in all_legal_move_objects(colour, board, castling_rights, en_passant_square):
        test_board = board.copy()
        test_rights = copy.deepcopy(castling_rights)
        next_en_passant_square = make_move(test_board, test_rights, move)
        results[move_to_text(move)] = perft(
            enemy, test_board, test_rights, depth - 1, next_en_passant_square
        )

    return results



def move_to_text(move):
    text = square_to_name(move.from_square) + square_to_name(move.to_square)

    if move.promotion is not None:
        text += move.promotion.lower()

    return text


def square_to_name(square):
    file_name = chr(ord("a") + ((square - 1) % 8))
    rank_name = str(8 - ((square - 1) // 8))
    return file_name + rank_name


def square_name_to_index(square_name):
    if square_name == "-":
        return None

    file_index = ord(square_name[0]) - ord("a")
    rank_index = 8 - int(square_name[1])
    return rank_index * 8 + file_index + 1


def board_from_fen(fen):
    parts = fen.split()
    placement = parts[0]
    turn = parts[1] if len(parts) > 1 else "w"
    castling_text = parts[2] if len(parts) > 2 else "-"
    en_passant_square = square_name_to_index(parts[3]) if len(parts) > 3 else None
    board = [None] * 64
    index = 0

    for letter in placement:
        if letter == "/":
            continue
        if letter.isdigit():
            index += int(letter)
            continue

        colour = "w" if letter.isupper() else "b"
        board[index] = colour + letter.upper()
        index += 1

    castling_rights = {
        "w": {"kingside": "K" in castling_text, "queenside": "Q" in castling_text},
        "b": {"kingside": "k" in castling_text, "queenside": "q" in castling_text},
    }

    return board, turn, castling_rights, en_passant_square


def perft_from_fen(fen, depth):
    board, turn, castling_rights, en_passant_square = board_from_fen(fen)
    return perft(turn, board, castling_rights, depth, en_passant_square)


def has_any_legal_moves(colour, board, castling_rights, en_passant_square=None):
    for square, piece in enumerate(board, start=1):
        if piece is not None and piece[0] == colour:
            if legal_move_objects_for_square(
                square, colour, board, castling_rights, en_passant_square
            ):
                return True

    return False


