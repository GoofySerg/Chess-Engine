import pygame
import castling
import legalmoves
import ai_opponent as opp

pygame.init()

screen = pygame.display.set_mode((800, 800))

run = True
turn = 'w'
castling_rights = castling.starting_rights()
en_passant_square = None

#Size of squares
size = 100

board = [None] * 64
pieces = {}

for piece in ['bB', 'bK', 'bN', 'bP', 'bQ', 'bR', 'wB', 'wK', 'wN', 'wP', 'wQ', 'wR']:
    img = pygame.image.load(f'pieces/{piece}.png')
    scaled = pygame.transform.scale(img, (size, size))
    pieces[piece] = scaled.convert_alpha()



startingPos = legalmoves.STARTING_FEN

def fenToBoard(position):
    global board, turn, castling_rights, en_passant_square

    board, turn, castling_rights, en_passant_square = legalmoves.board_from_fen(position)

def drawPieces():
    xOffset = 0
    yOffset = 0
    
    for p in board:
        if p is not None:
            screen.blit(pieces[p], (xOffset, yOffset))
            xOffset += size
        else:
            xOffset += size
        if xOffset == 800:
            xOffset = 0
            yOffset += 100

            
black = (118, 150, 86)
white = (255, 255, 255)

#board length, must be even
boardLength = 8


def drawBoard():
    cnt = 0

    for i in range(1,boardLength+1):
        
        for z in range(1,boardLength+1):

            if cnt % 2 == 0:
                pygame.draw.rect(screen, white,[size*(z-1),size*(i-1),size,size])

            else:
                pygame.draw.rect(screen, black, [size*(z-1),size*(i-1),size,size])

            cnt +=1
            
        cnt-=1



pygame.display.update()
fenToBoard(startingPos)
    
for piec in board:
    print(piec)


def getClickedSquare(mousePos):
    x, y = mousePos
    if x < 0 or x >= boardLength * size or y < 0 or y >= boardLength * size:
        return None

    col = x // size
    row = y // size
    return row * 8 + col + 1  # 1-indexed

def isPieceColour(square, colour):  # square is 1-indexed
    if square is None or square < 1 or square > len(board):
        return False

    return board[square - 1] is not None and board[square - 1][0] == colour

def movePiece(move):  # move uses 1-indexed squares
    global en_passant_square

    en_passant_square = legalmoves.make_move(board, castling_rights, move)

def getValidMoves(square, colour):  # square is 1-indexed
    return legalmoves.legal_move_objects_for_square(
        square, colour, board, castling_rights, en_passant_square
    )

def drawCheckHighlight(colour):
    if not legalmoves.is_in_check(colour, board):
        return

    king_square = legalmoves.find_king(colour, board)

    if king_square is None:
        return

    row = (king_square - 1) // 8
    col = (king_square - 1) % 8
    pygame.draw.rect(screen, (255, 80, 80), (col * size, row * size, size, size))

selectedSquare = None
validMoves = []
validMoveObjects = []
enemyPossibleMoves = []


while run:
    screen.fill(white)
    drawBoard()
    drawCheckHighlight(turn)

    if selectedSquare is not None:
        for move in validMoves:
            row = (move - 1) // 8
            col = (move - 1) % 8
            pygame.draw.rect(screen, (240, 0, 0), (col * size, row * size, size, size))

    drawPieces()

    

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and turn == 'w':
                mouse_pos = pygame.mouse.get_pos()
                clickedSquare = getClickedSquare(mouse_pos)  
                print(clickedSquare)
                
                if selectedSquare is None and isPieceColour(clickedSquare, turn):
                    selectedSquare = clickedSquare
                    validMoveObjects = getValidMoves(clickedSquare, turn)
                    validMoves = sorted({move.to_square for move in validMoveObjects})
                    print(validMoveObjects)
                    print(validMoves)

                elif selectedSquare is not None:
                    if clickedSquare in validMoves:
                        chosenMove = next(
                            move for move in validMoveObjects if move.to_square == clickedSquare
                        )
                        movePiece(chosenMove)
                        turn = 'b'
                        
                        if not legalmoves.has_any_legal_moves(
                            turn, board, castling_rights, en_passant_square
                        ):
                            if legalmoves.is_in_check(turn, board):
                                print(f"Checkmate: {'white' if turn == 'b' else 'black'} wins")
                            else:
                                print("Stalemate")


                    selectedSquare = None
                    validMoves = []
                    validMoveObjects = []
        

        if event.type == pygame.QUIT:
            run = False
    if turn == 'b':
        score, chosenMove = opp.minmax(2, board, 'b', castling_rights, en_passant_square)
        if chosenMove is not None:
            movePiece(chosenMove)

        turn = 'w'
    
    pygame.display.flip()

pygame.quit()




