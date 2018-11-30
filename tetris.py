#################################################
# Hw6 - Tetris
# Your andrewID: akong
# Your section: F
#################################################

from tkinter import *
import random
import copy
import time
import os


##### My Functions
def drawSlider(canvas,data):
    left = data.margin*4/10
    top = data.topMargin*10
    right = data.margin*6/10
    bot = data.topMargin*15
    gridSize = data.topMargin-10

    canvas.create_text(data.margin/2,data.topMargin*9,text="Speed")
    canvas.create_rectangle(left-3,top,right+3,bot,fill = "black")
    for i in range(data.speed):
        canvas.create_rectangle(left,bot-data.topMargin*i-2,right,bot-data.topMargin*(i+1),fill="blue",width=5)



def gameDimensions():
    #(rows, cols, cellSize, side margin, top bottom margin)
    return (20, 10, 30, 225, 40)

#Starts the game
def playTetris(maxPieces = -1,gameMode=1):
    rows, cols, cellSize, sideMargin, topMargin = gameDimensions()
    width = sideMargin*2+cellSize*cols
    height = topMargin*2+cellSize*rows
    no = run(width, height,maxPieces,gameMode)
    return no

def genReadout(data):
    totTime = time.time() - data.beginRun
    print("TOTAL TIME: ", totTime)
    print("TOTAL SCORE: ", data.score)
    print("Score/Pieces ", data.score / data.numPlaced)
    print("Score breakdown: ")
    print("singles: ", data.scoring[0])
    print("doubles: ", data.scoring[1])
    print("trips: ", data.scoring[2])
    print("tetrodes: ", data.scoring[3])
    data.isGameOver = True


#Draws the board with drawCell at the corrent spots
def drawBoard(canvas, data):
    for rowIndex in range(data.rows):
        for colIndex in range(data.cols):
            drawCell(canvas, data, rowIndex, colIndex, \
            data.board[rowIndex][colIndex],data.cellSize,data.margin+data.offset,\
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
    for i in range(4):
        canvas.create_rectangle(left-4,top+i*height-4,right+4,top+height+i*height+4, fill = "black")
        canvas.create_rectangle(left,top+i*height,right,top+(i+1)*height, fill = data.emptyColor)
        pieceNum = (data.currentQueue + data.nextQueue)[i]
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
        data.lastHeight = data.rows-(data.fallingPieceRow+len(data.fallingPiece))
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
        return data

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
    data.lastClear = 0
    data.numPlaced += 1
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

    if len(data.currentQueue) == 0:
        data.currentQueue = copy.copy(data.nextQueue)
        random.shuffle(data.nextQueue)
    newFallingPiece(data,data.currentQueue.pop(0))
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
    if fullRows != 0:
        data.scoring[fullRows-1] += 1
    data.lastClear = fullRows
    data.score += fullRows**2

def holdPiece(data):
    if data.heldPieceNum == None:
        data.heldPieceNum = data.pieceNum
        data.heldPiece = data.fallingPiece
        newFallingPiece(data,(data.currentQueue+data.nextQueue).pop(0))
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

def init(data,offset=0):
    data.beginRun = time.time()
    data.rows, data.cols, data.cellSize, data.margin,data.topMargin\
        = gameDimensions()
    data.offset = offset
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
    data.timedOut = False
    data.isGameOver = False
    data.heldPieceNum = None
    data.heldPiece = None
    data.canSwitch = True
    data.pieceNum = random.randint(0,len(data.tetrisPieces)-1)
    data.lastHeight = 0
    data.pieceRotPos = 0

    data.lastClear = 0
    data.qPos = 0
    data.currentQueue = list(range(7))
    data.nextQueue = list(range(7))
    random.shuffle(data.currentQueue)
    random.shuffle(data.nextQueue)

    data.scoring = [0,0,0,0]
    data.numPlaced = 0
    data.timeCounter = 0
    data.speed = 4


    newFallingPiece(data,data.pieceNum)
    # holdPiece(data)


def mousePressed(event, data):
    print(event.y)
    print(data.margin*4/10)
    print(data.margin*6/10)
    if data.margin*4/10 < event.x < data.margin*6/10:
        if data.topMargin*10 < event.y < data.topMargin*15:
            data.speed = 5-int((event.y-data.topMargin*10)/data.topMargin)
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

    if event.keysym == "q":
        genReadout(data)



    # firstScore = rateBoard(data)
    # thing = copy.deepcopy(data)
    # hardDrop(thing)
    # print((data.pieceRotPos, data.fallingPieceCol))
    # print(rateBoard(thing) - firstScore)
    # print(data.fallingPiece)


#Moves pieces, if it can't then it places it
def timerFired(data):
    if not (data.isGameOver):
        data.timeCounter += 1
        if not moveFallingPieces(data,+1,0):
            placeFallingPiece(data)
        if not fallingPieceIsLegal(data):
            data.isGameOver = True

    if not data.timedOut and data.maxPieces != -1 and data.numPlaced == data.maxPieces:
        data.isGameOver = True
        data.timedOut = True
        genReadout(data)




def redrawAll(canvas, data):
    canvas.create_rectangle(data.offset,0,data.width+data.offset, data.height, fill="orange")
    drawBoard(canvas, data)
    drawFallingPiece(canvas, data)
    drawScore(canvas, data)
    drawHold(canvas,data)
    drawQueue(canvas,data)
    drawSlider(canvas,data)


####################################
# Run function from 15-112 course notes
####################################

def run(width=300, height=300, maxPieces = -1,gameMode = 1):

    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        if gameMode != 1:
            canvas.create_rectangle(data.offset, 0, data.width+data.offset, data.height,
                                    fill='white', width=0)
        redrawAll(canvas, data)
        redrawAll(canvas, secData)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)
        redrawAll(canvas, secData)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)
        redrawAll(canvas, secData)

    def timerFiredWrapper(canvas, data):

        timerFired(data)
        redrawAllWrapper(canvas, data)
        redrawAll(canvas, secData)

        AI(canvas, data, redrawAllWrapper,data.speed)

        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)

        if data.isGameOver:
            root.destroy()
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    newWidth = width
    data.height = height
    data.timerDelay = 10 # milliseconds
    data.maxPieces = maxPieces
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window
    init(data)

    if gameMode != 1:
        secData = Struct()
        secData.width = width*2
        secData.height = height
        secData.maxPieces = maxPieces
        init(secData,offset=width)

        newWidth = data.width*2
        print("yea")



    # create the root and the canvas
    canvas = Canvas(root, width=newWidth, height=data.height)
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
    genReadout(data)
    print("bye!")
    return data



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

def cReader(file):
    f = open(file,"r")
    coeffs = f.read()
    f.close()
    coeffs.replace("\n","")
    coeffs = coeffs.split(" ")
    new = [float(x) for x in coeffs]
    return new

def cWriter(file, coeffs):
    f = open(file,"w")
    newFile = ""
    for num in coeffs:
        newFile += str(num) + " "
    newFile = newFile[:-1]
    f.write(newFile)


def rateBoard(data):
    #original coeffs:
    # line: 1
    # hole: 0.5
    # comp: 0.1

    # noLineC = 0
    # oneLineC = 0
    # twoLineC = 0
    # threeLineC = 0
    # fourLineC = 0
    lineCoeff,holeCoeff,compCoeff = cReader("coeffs.txt")
    heightCoeff = .1

    # lineCoeff = 1
    # holeCoeff = .5
    # compCoeff = 0.1

    score = 0


    # temp = [noLineC,oneLineC,twoLineC, threeLineC,fourLineC]
    # score += data.lastClear*temp[data.lastClear]

    if data.lastClear == 1:
        score -= .25
    elif data.lastClear == 2:
        score -= 0.1
    else:
        score += data.lastClear**4*lineCoeff

    # score += data.lastClear**2*lineCoeff



    holes = 0
    for i in range(data.cols):
        top=0
        newHoles = 0
        while top<data.rows and data.board[top][i] == data.emptyColor:
            top += 1
        while top < data.rows:
            if data.board[top][i] == data.emptyColor:
                newHoles += 1
            top += 1
        holes += newHoles
    score -= holes*holeCoeff

    # score -= data.lastHeight*heightCoeff #minimize height you place stuff at





    colHeight = []
    for j in range(data.cols):
        for i in range(data.rows):
            if i == data.rows:
                break
            if data.board[i][j] != data.emptyColor:
                break
        colHeight.append(i)
    compareHeight = 0
    for i in range(data.cols-1):
        compareHeight += abs(colHeight[i]-colHeight[i+1])
    score -= compareHeight*compCoeff

    return score


def findBestMove(data,bestScore = -float("inf")):
    origScore = rateBoard(data)
    alreadyChecked = []
    bestMove = []

    for i in range(4):
        data.fallingPieceCol = 5
        rotateFallingPiece(data)
        # if data.fallingPiece not in
        # For each rotation, move to the left and rotate piece once if you
        # pass an index not on the right wall
        data.fallingPieceCol = 0

        # oneRot = time.time()
        if data.fallingPiece not in alreadyChecked:
            for j in range(10):
                if moveFallingPieces(data, 0, 1):
                    if j == 0:
                        moveFallingPieces(data, 0, -1)
                    thing = copy.deepcopy(data)
                    hardDrop(thing)
                    rating = rateBoard(thing) - origScore
                    # print(rating)
                    if rating > bestScore:
                        bestScore = rating
                        bestMove = [(data.pieceRotPos, j,0)]
                    elif rating == bestScore:
                        bestMove.append((data.pieceRotPos, j,0))
                    # allMove.append((data.pieceRotPos,j,0))
            alreadyChecked.append(copy.copy(data.fallingPiece))
    if data.canSwitch:
        holding = copy.deepcopy(data)
        holdPiece(holding)
        newMoves, newScore = findBestMove(holding,bestScore)
        if newScore > bestScore and len(newMoves) > 0:
            bestScore = newScore
            bestMove = newMoves
            for i in range(len(bestMove)):
                bestMove[i] = (bestMove[i][0], bestMove[i][1], 1)
    return bestMove,bestScore




def makeMove(data,bestMove):
    # time.sleep(.1)
    if bestMove[2] == 1:
        holdPiece(data)
    moveFallingPieces(data, 0, -1)
    while data.pieceRotPos != bestMove[0]:
        rotateFallingPiece(data)
    data.fallingPieceCol = bestMove[1]



def AI(canvas,data,redraw,speed=5):
    if not fallingPieceIsLegal(data):
        data.isGameOver = True
    if data.isGameOver:
        return

    start = time.time()

    # try:
    #     bestMove = data.nextMove
    #     bestScore = -float("inf")
    # except:
    bestMove,bestScore = findBestMove(data)

    if len(bestMove) > 1:
        newBestMoves = []
        topNextScore = -float('inf')
        for move in bestMove:
            testHold = copy.deepcopy(data)
            makeMove(testHold,move)
            hardDrop(testHold)
            newMoves,newScore = findBestMove(testHold,bestScore)
            if newScore > topNextScore and len(newMoves) > 0:
                topNextScore = newScore
                newBestMoves = [move]
        if newBestMoves != []:
            bestMove = newBestMoves

    try:
        bestMove = random.choice(bestMove)
        makeMove(data, bestMove)
    except:
        pass
    # time.sleep((5-speed)/10)
    redraw(canvas, data) #this function takes hella long
    # time.sleep((5-speed)/10)
    hardDrop(data)

    # print("BEST: ", bestMove, bestScore, "Time: ", time.time()-start)


def testCoeffs(reps,maxPieces):
    listRats = []
    timedOut = True
    for i in range(reps):
        output = playTetris(maxPieces)
        listRats.append(output.score/output.numPlaced)
        if not timedOut:
            timedOut = False
            break
    return sum(listRats)/reps, timedOut


def gradDescent():
    alpha = .05
    maxPieces = 500
    reps = 1
    cFile = "coeffs.txt"
    coeffs = cReader(cFile)
    # bestRatio = []
    bestRatio = 0
    bestCoeffs = []
    for line in range(25,125,25):
        for hole in range(25,125,25):
            for side in range(1,6,1):
                coeffs = [line/100,hole/100,side/10]
                print(coeffs)
                cWriter(cFile,coeffs)

                rat, timedOut = testCoeffs(reps,maxPieces)
                if not timedOut:
                    continue
                else:
                    if rat-bestRatio > 0.1:
                        bestCoeffs = coeffs
                print(bestCoeffs)
                print(bestRatio)

# gradDescent()
    #
    #
    #
    #
    # # Iterating through each feature
    # for i in range(len(coeffs)):
    #     #Run the game, then run it again with a slightly changed coeff
    #     lastRat,timedOut1 = testCoeffs(reps,maxPieces)
    #
    #     coeffs[i] += alpha
    #     cWriter(cFile,coeffs)
    #
    #     newRat,timedOut2 = testCoeffs(reps, maxPieces)
    #     print(lastRat)
    #     print(newRat)
    #     #if the ratio goes up, change coeffs again
    #     while newRat-lastRat > 0.01:
    #         #if game just straight up lost after change, change coeffs immediately
    #         if not timedOut2:
    #             coeffs[i] += alpha
    #             cWriter(cFile, coeffs)
    #             lastRat = testCoeffs(reps, maxPieces)
    #         else:
    #             lastRat = newRat
    #
    #         # either way, test again
    #
    #         coeffs[i] += alpha
    #         cWriter(cFile, coeffs)
    #
    #         newRat = testCoeffs(reps, maxPieces)



# gradDescent()
playTetris(gameMode=2)


def tester():
    maxPieces = 50
    reps = 100
    lst = []
    for i in range(reps):
        output = playTetris(maxPieces)
        lst.append(output.score/output.numPlaced)
    print(lst)

# tester()

# yah = playTetris(200)
# print(yah.numPlaced)



# AI should
# - take in board state,
# - find the best move and score for the current piece, returning them
# - do each best move (in a new data) and find bestmove and bestscore for next piece in each new data
# - only keep moves that return the highest future return ???
# - make new data where it does each bestmove and finds the next best score


# TODO: You commented out two redraws (692,458), and the BEST:
# fix lookahead
# have it auto-optimize variables
# New tetris pieces test

