import argparse
import sys
import time
from dataclasses import dataclass

import legalmoves


@dataclass(frozen=True)
class PerftPosition:
    key: str
    name: str
    fen: str
    expected: dict[int, int]


# Reference node counts from https://www.chessprogramming.org/Perft_Results
POSITIONS = {
    position.key: position
    for position in (
        PerftPosition(
            "start",
            "Starting position",
            legalmoves.STARTING_FEN,
            {
                1: 20,
                2: 400,
                3: 8902,
                4: 197281,
                5: 4865609,
                6: 119060324,
            },
        ),
        PerftPosition(
            "kiwipete",
            "Position 2 / Kiwipete",
            "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
            {
                1: 48,
                2: 2039,
                3: 97862,
                4: 4085603,
                5: 193690690,
                6: 8031647685,
            },
        ),
        PerftPosition(
            "endgame",
            "Position 3 / en passant stress",
            "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
            {
                1: 14,
                2: 191,
                3: 2812,
                4: 43238,
                5: 674624,
                6: 11030083,
            },
        ),
        PerftPosition(
            "promotion",
            "Position 4 / promotion and castling stress",
            "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1",
            {
                1: 6,
                2: 264,
                3: 9467,
                4: 422333,
                5: 15833292,
                6: 706045033,
            },
        ),
        PerftPosition(
            "position5",
            "Position 5",
            "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",
            {
                1: 44,
                2: 1486,
                3: 62379,
                4: 2103487,
                5: 89941194,
            },
        ),
        PerftPosition(
            "position6",
            "Position 6",
            "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10",
            {
                1: 46,
                2: 2079,
                3: 89890,
                4: 3894594,
                5: 164075551,
                6: 6923051137,
            },
        ),
    )
}


def main():
    args = parse_args()

    if args.list:
        list_positions()
        return 0

    if args.fen:
        if args.all:
            print("--all can only be used with the built-in reference positions.")
            return 2
        return run_custom_fen(args)

    if args.all:
        return run_all_positions(args)

    position = POSITIONS[args.position]
    depths = selected_depths(position, args.depth)
    return run_position(position, depths, args.divide)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Run perft move-generation checks. Perft counts all legal move "
            "paths from a position to a given depth."
        )
    )
    parser.add_argument(
        "-p",
        "--position",
        choices=POSITIONS.keys(),
        default="start",
        help="built-in reference position to test",
    )
    parser.add_argument(
        "-f",
        "--fen",
        help="custom FEN to test instead of a built-in position",
    )
    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        help="depth to test. Built-in positions default to all stored depths up to 4",
    )
    parser.add_argument(
        "-e",
        "--expected",
        type=int,
        help="expected node count for a custom FEN/depth",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="test every built-in reference position",
    )
    parser.add_argument(
        "--divide",
        action="store_true",
        help="print each root move and its node count for the selected depth",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="show built-in reference positions",
    )
    return parser.parse_args()


def list_positions():
    for key, position in POSITIONS.items():
        depths = ", ".join(str(depth) for depth in sorted(position.expected))
        print(f"{key}: {position.name} (depths {depths})")
        print(f"  {position.fen}")


def selected_depths(position, depth):
    if depth is not None:
        return [depth]

    return [
        stored_depth
        for stored_depth in sorted(position.expected)
        if stored_depth <= 4
    ]


def run_all_positions(args):
    failures = 0

    for position in POSITIONS.values():
        failures += run_position(position, selected_depths(position, args.depth), args.divide)

    return 1 if failures else 0


def run_position(position, depths, show_divide):
    failures = 0

    print(f"\n{position.name}")
    print(position.fen)

    for depth in depths:
        expected = position.expected.get(depth)
        passed = run_single_check(position.fen, depth, expected)

        if not passed:
            failures += 1

    if show_divide:
        print_divide(position.fen, depths[-1])

    return failures


def run_custom_fen(args):
    if args.depth is None:
        print("Custom FEN checks need --depth.")
        return 2

    passed = run_single_check(args.fen, args.depth, args.expected)

    if args.divide:
        print_divide(args.fen, args.depth)

    return 0 if passed else 1


def run_single_check(fen, depth, expected=None):
    start = time.perf_counter()
    actual = legalmoves.perft_from_fen(fen, depth)
    elapsed = time.perf_counter() - start

    if expected is None:
        print(f"depth {depth}: {actual:,} nodes ({elapsed:.3f}s)")
        return True

    if actual == expected:
        print(f"PASS depth {depth}: {actual:,} nodes ({elapsed:.3f}s)")
        return True

    delta = actual - expected
    print(
        f"FAIL depth {depth}: got {actual:,}, expected {expected:,}, "
        f"delta {delta:+,} ({elapsed:.3f}s)"
    )
    return False


def print_divide(fen, depth):
    board, turn, castling_rights, en_passant_square = legalmoves.board_from_fen(fen)
    divide = legalmoves.perft_divide(
        turn,
        board,
        castling_rights,
        depth,
        en_passant_square,
    )

    print(f"\nDivide depth {depth}")

    total = 0
    for move, count in sorted(divide.items()):
        total += count
        print(f"{move}: {count}")

    print(f"Total: {total}")


if __name__ == "__main__":
    sys.exit(main())
