#################################################
# Hw6 - Tetris
# Your andrewID: akong
# Your section: F
#################################################

from tkinter import *
import random
import copy
import numpy as np
import time


##### My Functions
def gameDimensions():
    #(rows, cols, cellSize, side margin, top bottom margin)
    return (20, 10, 30, 225, 40)

#Starts the game
def playTetris():
    rows, cols, cellSize, sideMargin, topMargin = gameDimensions()
    width = sideMargin*2+cellSize*cols
    height = topMargin*2+cellSize*rows
    run(width, height)

#Draws the board with drawCell at the corrent spots
def drawBoard(canvas, data):
    for rowIndex in range(data.rows):
        for colIndex in range(data.cols):
            drawCell(canvas, data, rowIndex, colIndex, \
            data.board[rowIndex][colIndex],data.cellSize,data.margin,\
                     data.topMargin)

def drawHold(canvas, data):
    top = data.topMargin*3
    left = data.topMargin
    right = data.margin - left
    bot = top + right
    canvas.create_rectangle(left-4,top-4,right+4,bot+4, fill = "black")
    canvas.create_rectangle(left,top,right,bot, fill = data.emptyColor)
    canvas.create_text((left+right)//2,top-4,text="Hold", fill="white",\
                       font = ("Arial " + str(data.cellSize)) + " bold", anchor = "s")

    if data.heldPiece != None:
        hold = data.tetrisPieces[data.heldPieceNum]
        color = data.tetrisPieceColors[data.heldPieceNum]
        height = len(hold)
        width = len(hold[0])
        startX = (left+right)/2-width*data.cellSize/2
        startY = (top+bot)/2-height*data.cellSize/2
        for row in range(height):
            for col in range(width):
                if hold[row][col]:
                    drawCell(canvas, data, row,col,color,data.cellSize,startX,startY)

def drawQueue(canvas,data):
    top = data.topMargin
    left = data.width - data.margin+data.topMargin
    right = data.width - top
    bot = top + (right-left)*4
    height = right-left
    canvas.create_text((left + right) // 2, top - 4, text="Up Next",\
                       fill="white", \
                       font=("Arial " + str(data.cellSize)) + " bold",\
                       anchor="s")
    for i in range(len(data.queue)):
        canvas.create_rectangle(left-4,top+i*height-4,right+4,top+height+i*height+4, fill = "black")
        canvas.create_rectangle(left,top+i*height,right,top+(i+1)*height, fill = data.emptyColor)
        pieceNum = data.queue[i]
        piece = data.tetrisPieces[pieceNum]
        color = data.tetrisPieceColors[pieceNum]
        tall = len(piece)
        wide = len(piece[0])
        startX = (left+right)/2-wide*data.cellSize/2
        startY = (top+(i+0.5)*height)-tall*data.cellSize/2
        for row in range(tall):
            for col in range(wide):
                if piece[row][col]:
                    drawCell(canvas,data, row, col, color, data.cellSize,startX, startY)
    # canvas.create_rectangle(left, top, right, bot, fill="white")

def lighten(color):
    change = 1.7
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    newColor = ""
    for piece in (r,g,b):
        if piece*change > 255:
            piece = 255
        else:
            piece *= change
        piece = int(piece)
        piece = str(hex(piece))[2:]
        if len(piece) == 1:
            piece += piece
        newColor += piece
    return "#" + newColor

#Draws each block on the playing field
def drawCell(canvas, data, row, col, color,cellSize,margin, topMargin):
    startX = margin + cellSize*col
    startY = topMargin + cellSize*row
    canvas.create_rectangle(startX,startY,startX+cellSize,startY+cellSize,\
    width = '4', fill = color)
    detail = cellSize//8
    detailColor = lighten(color)
    canvas.create_polygon((startX+2,startY+2,\
                          startX+detail+2,startY+detail+2,\
                          startX+8*detail, startY+detail+2,\
                          startX+8*detail, startY+8*detail,\
                          startX-2+cellSize,startY-2+cellSize,\
                          startX+cellSize-2,startY+2), fill=detailColor\
                          )
    canvas.create_line(startX+detail+2,startY+detail*6,\
                       startX+detail+2,startY+8*detail,\
                       startX+4*detail+2,startY+8*detail,fill=lighten(detailColor))

#Spawns a new piece and resets all the piece data
def newFallingPiece(data,piece):
    data.fallingPiece = data.tetrisPieces[piece]
    data.fallingPieceColor = data.tetrisPieceColors[piece]
    data.numFallingPieceCols = len(data.fallingPiece[0])
    try:
        data.lastHeight = data.fallingPieceRow+len(data.fallingPiece)
    except:
        pass
    data.fallingPieceRow = 0
    if piece == 0:
        data.fallingPieceRow = 2
    data.pieceNum = piece
    data.pieceRotPos = 0
    data.fallingPieceCol = data.cols//2-data.numFallingPieceCols//2

#Draws the piece based on starting position and data.piece
def drawFallingPiece(canvas, data):
    piece = data.fallingPiece
    pieceColor = data.fallingPieceColor
    row = data.fallingPieceRow
    col = data.fallingPieceCol
    for rowIndex in range(len(piece)):
        for colIndex in range(len(piece[0])):
            if piece[rowIndex][colIndex]:
                drawCell(canvas, data, rowIndex+row, colIndex+col, pieceColor,\
                         data.cellSize, data.margin, data.topMargin)
    #Game over screen display
    if data.isGameOver:
        canvas.create_rectangle(data.margin,data.margin+data.cellSize,\
        data.width-data.margin,data.margin+3*data.cellSize, fill="white")
        canvas.create_text(data.width//2, data.margin+data.cellSize*2, \
        text = "GAME HAS ENDED\npress r to restart!")

#Moves, checks if move is legal, if not it undoes it
def moveFallingPieces(data, drow, dcol):
    data.fallingPieceRow += drow
    data.fallingPieceCol += dcol
    if fallingPieceIsLegal(data):
        return True
    else:
        data.fallingPieceRow -= drow
        data.fallingPieceCol -= dcol
        return False


def fallingPieceIsLegal(data):
    #Making code more readable
    piece = data.fallingPiece
    pieceRow = data.fallingPieceRow
    pieceCol = data.fallingPieceCol
    pHeight = len(piece)
    pWidth = len(piece[0])
    
    #Check if each cell of each piece is legal i.e. doesn't overlap colored bloc
    for i in range(pHeight):
        for j in range(pWidth):
            if piece[i][j]:
                if pieceCol < 0 or pieceCol+pWidth > data.cols or\
                 pHeight+pieceRow-1 >= data.rows or \
                 data.board[i+pieceRow]\
                 [j+pieceCol] != data.emptyColor:
                    return False
    return True

def rotateFallingPiece(data):
    #Store old info
    oldPiece = copy.deepcopy(data.fallingPiece)
    oldRowPos = data.fallingPieceRow
    oldColPos =  data.fallingPieceCol
    oldRows = len(oldPiece)
    oldCols = len(oldPiece[0])
    
    #Calculate new location, dimensions, and piece
    newRows = oldCols
    newCols = oldRows
    newRowPos = oldRowPos + oldRows//2 - newRows//2
    newColPos = oldColPos + oldCols//2 - newCols//2
    #initialize newPiece and assign values from oldPiece
    newPiece = []
    for i in range(oldCols):
        newPiece.append([])
        for j in range(oldRows):
            newPiece[i].append(None)
    for i in range(oldRows):
        for j in range(oldCols):
            newPiece[newRows-1-j][i] = oldPiece[i][j]
            
    #Assigning new variables
    data.fallingPieceRow = newRowPos
    data.fallingPieceCol = newColPos
    data.fallingPiece = newPiece

    if data.pieceNum == 5:
        data.fallingPieceCol += 0

    #Legality check! get ur lawyer!
    if fallingPieceIsLegal(data):
        data.pieceRotPos -= 1
        data.pieceRotPos %= 4
        return True
    elif moveFallingPieces(data,0,-1):
        if fallingPieceIsLegal(data):
            data.pieceRotPos -= 1
            data.pieceRotPos %= 4
            return True
    else:
        data.fallingPieceRow = oldRowPos
        data.fallingPieceCol = oldColPos
        data.fallingPiece = oldPiece
        return False

#Integrates a fallen piece into the data.board
def placeFallingPiece(data):
    piece = data.fallingPiece
    pWidth = len(piece[0])
    pHeight = len(piece)
    startRow = data.fallingPieceRow
    startCol = data.fallingPieceCol
    
    #iterates over the piece, placing each piece at the right board spot 
    for i in range(pHeight):
        for j in range(pWidth):
            if piece[i][j]:
                data.board[startRow+i][startCol+j] = data.fallingPieceColor
    removeFullRows(data)
    newFallingPiece(data,data.queue.pop(0))
    data.queue.append(random.randint(0,len(data.tetrisPieces)-1))
    data.canSwitch = True
    
#Removes full rows (sorry for the useless comment)
def removeFullRows(data):
    oldBoard = data.board
    newBoard = []
    #makes a new board that doesn't have any full rows on it
    for rowIndex in range(len(oldBoard)-1,-1,-1):
        if oldBoard[rowIndex].count(data.emptyColor) != 0:
            #Inserts new rows at the top because we're iterating from the bottom
            newBoard.insert(0, oldBoard[rowIndex])
    fullRows = len(oldBoard)-len(newBoard)
    #However many rows were taken out, add new blank rows and add to score
    for i in range(fullRows):
        newBoard.insert(0,[data.emptyColor]*data.cols)
    data.board = newBoard
    data.score += fullRows**2

def holdPiece(data):
    if data.heldPieceNum == None:
        data.heldPieceNum = data.pieceNum
        data.heldPiece = data.fallingPiece
        newFallingPiece(data,data.queue.pop(0))
        data.queue.append(random.randint(0,len(data.tetrisPieces)-1))
    elif data.canSwitch:
        temp = data.heldPieceNum
        data.heldPieceNum = data.pieceNum
        data.heldPiece = data.fallingPiece
        newFallingPiece(data,temp)
        data.canSwitch = False

def drawScore(canvas, data):
    canvas.create_text(data.width//2, data.topMargin//2, text="Score: " +\
    str(data.score), font="bold")

def hardDrop(data):
    while moveFallingPieces(data, +1, 0):
        pass
    placeFallingPiece(data)

################################################## Bot commands

# def moveRight():




####################################
# customize these functions
####################################

def init(data):
    data.rows, data.cols, data.cellSize, data.margin,data.topMargin\
        = gameDimensions()
    data.emptyColor = "#2d2d2d"
    data.board = []
    for i in range(data.rows):
        data.board.append([])
        for j in range(data.cols):
            data.board[i].append(data.emptyColor)
    
    iPiece = [[  True,  True,  True,  True ]]
    jPiece = [[  True, False, False ],[  True,  True,  True ]]
    lPiece = [[ False, False,  True ],[  True,  True,  True ]]
    oPiece = [[  True,  True ],[  True,  True ]]
    sPiece = [[ False,  True,  True ],[  True,  True, False ]]
    tPiece = [[ False,  True, False ],[  True,  True,  True ]]
    zPiece = [[  True,  True, False ],[ False,  True,  True ]]

    cyan = "#00bbbb"
    blue = "#3159d1"
    orange = "#ffa500"
    yellow = "#ffcc55"
    green = "#23ac00"
    purple = "#663399"
    red = "#a51404"

    data.tetrisPieces = [iPiece, jPiece, lPiece, oPiece, sPiece, tPiece, zPiece]
    data.tetrisPieceColors = [cyan,blue,orange,yellow,green,purple,red]
    data.score = 0
    data.isGameOver = False
    data.heldPieceNum = None
    data.heldPiece = None
    data.canSwitch = True
    data.pieceNum = random.randint(0,len(data.tetrisPieces)-1)
    data.lastHeight = len(data.tetrisPieces[data.pieceNum])
    data.pieceRotPos = 0
    data.queue = [random.randint(0,len(data.tetrisPieces)-1) for _ in range(4)]
    newFallingPiece(data,data.pieceNum)


def mousePressed(event, data):
    pass
    # use event.x and event.y

def keyPressed(event, data):


    #Controls restart
    if event.keysym == 'r':
        init(data)
    
    #Controls arrow movements
    if not (data.isGameOver):
        if event.keysym == "Left":
            moveFallingPieces(data, 0, -1)
        
        if event.keysym == "Right":
            moveFallingPieces(data, 0, 1)
        
        if event.keysym == "Down":
            moveFallingPieces(data, 1, 0)
        
        if event.keysym == "Up":
            rotateFallingPiece(data)
            rotateFallingPiece(data)
            rotateFallingPiece(data)

        if event.keysym == "??":
            holdPiece(data)

        if event.keysym == "space":
            hardDrop(data)

        if event.keysym == "t":
            time.sleep(60)
    # firstScore = rateBoard(data)
    # thing = copy.deepcopy(data)
    # hardDrop(thing)
    # print((data.pieceRotPos, data.fallingPieceCol))
    # print(rateBoard(thing) - firstScore)
    print(data.pieceRotPos)


#Moves pieces, if it can't then it places it
def timerFired(data):
    if not (data.isGameOver):
        if not moveFallingPieces(data,+1,0):
            placeFallingPiece(data)
        if not fallingPieceIsLegal(data):
            data.isGameOver = True
        

def redrawAll(canvas, data):
    canvas.create_rectangle(0,0,data.width, data.height, fill="orange")
    drawBoard(canvas, data)
    drawFallingPiece(canvas, data)
    drawScore(canvas, data)
    drawHold(canvas,data)
    drawQueue(canvas,data)

####################################
# use the run function as-is
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        AI(canvas,data,redrawAllWrapper)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 1000 # milliseconds
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window
    init(data)
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    
    print("bye!")


# 1. Make a set of methods that simulates moves and drops
# like move left and drop, or move right and drop, or rotate
# #bestSpot = (rotation state, position state)
# bestSpot = (0,0)
# for i in range(4):
    # tempPiece = rotate(piece, i)
    # for j in range (0,10):
#         tempPoints = Testdrop(board, tempPiece, j)
#                 if tempPoints > curMaxPts:
#                     curMaxPts = tempPoints
#                     bestSpot = (i,j)
#     moveTo(i,j)
# 2.

def rateBoard(data):
    lines = 0
    holes = 0
    score = 0
    for row in data.board:
        if row.count(data.emptyColor) == 0:
            lines += 1
    score += lines**2

    colBoard = np.transpose(copy.deepcopy(data.board))
    for col in colBoard:
        col = np.ndarray.tolist(col)
        while len(col) > 0 and col[0] == data.emptyColor:
            col.pop(0)
        new = col.count(data.emptyColor)
        holes += new
    score -= holes/5

    biggestHeight = 0

    for i in range(len(data.board)):
        if data.board[i].count(data.emptyColor) != data.cols:
            biggestHeight = data.rows-i
            break
    # print("lastHeight:",data.lastHeight)
    # print("biggestHeight",biggestHeight)
    score += (data.lastHeight-biggestHeight)/10

    return score



def AI(canvas,data,redraw):
    origScore = rateBoard(data)
    delay = 0
    alreadyChecked = []
    bestScore = -float("inf")
    bestMove = []
    progression = []

    data.fallingPieceCol = 0
    for i in range(4):
        # if data.fallingPiece not in
        #For each rotation, move to the left and rotate piece once if you
        # pass an index not on the right wall
        while moveFallingPieces(data,0,-1):
            pass
        rotateFallingPiece(data)
        if data.fallingPiece not in alreadyChecked:
            for j in range(10):
                if moveFallingPieces(data,0,1):
                    if j == 0:
                        moveFallingPieces(data,0,-1)
                    thing = copy.deepcopy(data)
                    hardDrop(thing)
                    rating = rateBoard(thing)-origScore
                    if rating > bestScore:
                        bestScore = rating
                        bestMove = [(data.pieceRotPos,j)]
                    elif rating == bestScore:
                        bestMove.append((data.pieceRotPos,j))
            alreadyChecked.append(data.fallingPiece)
        print(alreadyChecked)
    bestMove = random.choice(bestMove)


    redraw(canvas,data)
    moveFallingPieces(data,0,-1)
    while data.pieceRotPos != bestMove[0]:
        # print(data.pieceRotPos)
        rotateFallingPiece(data)
        redraw(canvas,data)
    data.fallingPieceCol = bestMove[1]
    redraw(canvas,data)
    print("BEST: ", bestMove)
    hardDrop(data)




    # print(fart.fallingPiece)



playTetris()


