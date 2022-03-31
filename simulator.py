from lib import *
import minoMover
import evaluator
import time # debug

DISPLAY_DELTA_TIME = 0.02

# 1つのnowDirectedMinoを置く動きを再現して出力
# 返り値としておいた後のboardを返す
def PutMino (moveList:List[MoveInt], board:Board) -> Tuple[Board, bool, bool]:

    global pcFirstHold

    board.updateMinoBagContents()
    if moveList[0] is MOVE.HOLD:
        if board.holdMino is MINO.NONE:
            pcFirstHold = True
        PrintBoardWithDirectedMino(board, board.currentMino, True)
        moveList = moveList[1:]
        board = BoardAfterHold(board)
        if pcFirstHold:
            board.updateMinoBagContents() # first MOVE.HOLD
            pcFirstHold = False

    # moveListに従って1つずつ動かしていく
    nextDirectedMino = board.currentMino
    for move in moveList:
        PrintBoardWithDirectedMino(board, nextDirectedMino, True)
        nextDirectedMino = minoMover.MoveOneStep(move, nextDirectedMino, board)
        time.sleep(DISPLAY_DELTA_TIME)
    
    # 最終状態の出力
    PrintBoardWithDirectedMino(board, nextDirectedMino, True)

    isTspin = evaluator.IsTSpin(board.mainBoard, nextDirectedMino, moveList)
    isTspinmini = isTspin and evaluator.IsTSpinMini(board.mainBoard, nextDirectedMino, moveList)

    joinedMainBoard, joinedTopRowIdx = JoinDirectedMinoToBoard(nextDirectedMino, board.mainBoard, board.topRowIdx)
    return Board(
        joinedMainBoard,
        board.currentMino,
        board.followingMinos,
        board.holdMino,
        board.canHold,
        joinedTopRowIdx,
        board.score,
        board.backToBack,
        board.ren,
        board.minoBagContents
    ), isTspin, isTspinmini

# ラインをクリアする
def ClearLinesOfBoard(board:Board) -> Tuple[List[MinoInt], List[MinoInt], int]:
    newMainBoard, newTopRowIdx, clearedRowCount = ClearLines(board.mainBoard, board.topRowIdx)
    time.sleep(DISPLAY_DELTA_TIME)
    PrintBoard(Board(
        newMainBoard,
        board.currentMino,
        board.followingMinos,
        board.holdMino,
        board.canHold,
        newTopRowIdx,
        board.score,
        board.backToBack,
        board.ren,
        board.minoBagContents
    ), True, None, False, True)
    time.sleep(DISPLAY_DELTA_TIME)
    return newMainBoard, newTopRowIdx, clearedRowCount

# 次のミノを付け足し，押し出してネクストのミノをcurrentMinoにする
# Holdができるようになったのでミノを2個付け足す場合がある。
def AddFollowingMino (board:Board) -> Board:
   
    if board.followingMinos[-1] is MINO.NONE:
        board.followingMinos[-1] = GenerateMino()

    return Board(
        board.mainBoard,
        DirectedMino(
            board.followingMinos[0],
            FIRST_MINO_DIRECTION,
            FIRST_MINO_POS
        ),
        board.followingMinos[1:] + [GenerateMino()],
        board.holdMino,
        True,
        board.topRowIdx,
        board.score,
        board.backToBack,
        board.ren,
        board.minoBagContents
    )

# 7種1巡の法則に従ってランダムでミノを生成する
bags = []
def GenerateMino () -> MinoInt:
    global bags

    # bagsが空であれば，7種類のミノをランダムに生成してbagsに入れる
    if not bags:
        bags = random.sample([
            MINO.I,
            MINO.J,
            MINO.L,
            MINO.O,
            MINO.S,
            MINO.T,
            MINO.Z
        ], 7)
        # perfect clear test (the order matters)
        # bags = [
        #     MINO.Z,
        #     MINO.L,
        #     MINO.I,
        #     MINO.O,
        #     MINO.T,
        #     MINO.S,
        #     MINO.J,
        # ]
    return bags.pop(0)
