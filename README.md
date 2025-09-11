# Chess Engine

A simple chess game with a playable GUI and an AI opponent, written in Python
with [pygame](https://www.pygame.org/). You play White by clicking pieces; the
computer plays Black using an alpha-beta search.

## Features

- Graphical 8x8 board with piece images and legal-move highlighting
- Full move legality: checks, pins, castling, en passant, and promotion
- Check, checkmate, and stalemate detection
- AI opponent using minimax with alpha-beta pruning, quiescence search,
  material values, and piece-square tables
- `perft` move-generation checker for validating the move generator

## Requirements

- Python 3
- pygame (see `requirements.txt`)

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

Click one of your (White) pieces to select it; legal destination squares are
highlighted. Click a highlighted square to move. Black replies automatically.

## Project layout

| File | Purpose |
| --- | --- |
| `main.py` | Entry point: pygame window, board rendering, input, and game loop |
| `legalmoves.py` | Legal move generation, FEN parsing, make-move, check/mate detection |
| `piecemoves.py` | Pseudo-legal move rules per piece type |
| `attacks.py` | Square-attack detection used for check and legality |
| `castling.py` | Castling rights tracking and castling logic |
| `ai_opponent.py` | Alpha-beta search, evaluation, and piece-square tables |
| `perft_check.py` | Perft counts for testing move-generation correctness |
| `pieces/` | Piece image assets (PNG) |
