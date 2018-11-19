# It is wednesday, November 14th 2018, 7:42:08 pm in Daniel Cohen's room
import tetris

def moveRight():
    tetris.playTetris()
    tetris.moveFallingPieces(tetris.data, 1, 0)
    print(tetris.data.fallingPiece)
    print("works")

moveRight()