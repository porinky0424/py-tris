from lib import *
import decisionMaker



class PCState():
    Wait = 0
    FirstSZTLeft = 1
    FirstSZTRight = 2
    Second = 3



pcState = PCState.Wait
pcReturnValueQueue = [] # 返り値キュー



def AssignPCMinoMoves(
        minos:List[MINO], 
        tMove:List[MOVE],
        oMove:List[MOVE],
        zMove:List[MOVE],
        iMove:List[MOVE],
        lMove:List[MOVE],
        sMove:List[MOVE],
        jMove:List[MOVE]
    ) -> List[Tuple[DirectedMino, List[MOVE]]]:
    minoBag = ReturnFullBag()
    pcReturnValueQueue = []
    for i,nextMino in enumerate(minos):
        minoBag.remove(nextMino)
        pcReturnValueQueue.append( ReturnCorrespondingMinoMove(nextMino, tMove, oMove, zMove, iMove, lMove, sMove, jMove) )
    pcReturnValueQueue.append( ReturnCorrespondingMinoMove(minoBag[0], tMove, oMove, zMove, iMove, lMove, sMove, jMove) )
    return pcReturnValueQueue

def ReturnCorrespondingMinoMove(
        mino:MINO,
        tMove:List[MOVE],
        oMove:List[MOVE],
        zMove:List[MOVE],
        iMove:List[MOVE],
        lMove:List[MOVE],
        sMove:List[MOVE],
        jMove:List[MOVE]
    ) -> List[MOVE]:
    if mino is MINO.T:
        return tMove
    elif mino is MINO.O:
        return oMove
    elif mino is MINO.Z:
        return zMove
    elif mino is MINO.I:
        return iMove
    elif mino is MINO.L:
        return lMove
    elif mino is MINO.S:
        return sMove
    elif mino is MINO.J:
        return jMove



# 各ミノの直近の動き
# 未定義だとエラーになりうるので一応定義しておく
tMove = []
oMove = []
zMove = []
iMove = []
lMove = []
sMove = []
jMove = []

pcFirstHold = False # used differently from firstHold

# CAUTION: ミノの左右移動を埋め込みにしている部分あり
def PerfectClear(board:Board) -> List[List[MoveInt]]:

    global pcState
    global pcReturnValueQueue
    global tMove
    global oMove
    global zMove
    global iMove
    global lMove
    global sMove
    global jMove

    if pcReturnValueQueue: # pcState is not PCState.Wait
        # 返り値キューが空でなければ思考済みなので前から取って返すだけ
        return [pcReturnValueQueue.pop(0)]

    elif pcState is PCState.Wait:
        minoOrder = CheckMinoOrder(board.currentMino.mino, board.followingMinos)

        if (len(board.minoBagContents) == 7) and isBoardTopAligned(board.mainBoard):
            # 一巡目のパフェ積みが可能

            #----- hold 可否を判断 -----#
            if board.holdMino is MINO.NONE:
                canHoldInPC = True
            else:
                canHoldInPC = False
            # tHold = minoOrder.SZ_T
            # oHold = minoOrder.O_LJ and not (minoOrder.SZ_T and minoOrder.OT)
            # iHold = (not tHold and not oHold) or () or () # そもそも他に hold が必要ないか，他の hold 解消後だったら，hold してよい FIXME
            iHold = canHoldInPC
            # SZT/ZST では，T が来たら Z/S の hold 解消
            # OLJ なら，L が来たら O の hold 解消
            # OLJ なら，J が来たら O の hold 解消

            #----- 積み方の左右を決定 -----#
            if minoOrder.SZ:
                # SZT が左側にくるタイプで進める
                pcState = PCState.FirstSZTLeft
            else:
                # SZT が右側にくるタイプで進める
                pcState = PCState.FirstSZTRight

            #----- でこぼこ側 (SZT) -----#
            if minoOrder.SZ: # SZT or STZ or TSZ
                zMove = [MOVE.LEFT, MOVE.LEFT, MOVE.LEFT, MOVE.DROP]
                tMove = [MOVE.R_ROT, MOVE.LEFT, MOVE.LEFT, MOVE.LEFT, MOVE.LEFT, MOVE.DROP]
                if not minoOrder.ST: # TSZ
                    # S をハードドロップできない
                    sMove = [MOVE.LEFT] + [MOVE.DOWN for _ in range(alignedBoardTop - FIRST_MINO_POS[1] - 1)] + [MOVE.LEFT]
                else: # SZT or STZ
                    # S をハードドロップ可能
                    sMove = [MOVE.LEFT, MOVE.LEFT, MOVE.DROP]
                    if minoOrder.ZT: # SZT
                        # Z をホールドする必要がある
                        pcState = PCState.Wait
                        pcReturnValueQueue = []
                        return [] # TODO: hold
            else: # ZST or ZTS or TZS
                sMove = [MOVE.RIGHT, MOVE.RIGHT, MOVE.RIGHT, MOVE.RIGHT, MOVE.DROP]
                tMove = [MOVE.L_ROT, MOVE.RIGHT, MOVE.RIGHT, MOVE.RIGHT, MOVE.RIGHT, MOVE.RIGHT, MOVE.DROP]
                if not minoOrder.ZT: # TZS
                    # Z をハードドロップできない
                    zMove = [MOVE.RIGHT, MOVE.RIGHT] + [MOVE.DOWN for _ in range(alignedBoardTop - FIRST_MINO_POS[1] - 1)] + [MOVE.RIGHT]
                else: # ZST or ZTS
                    # Z をハードドロップ可能
                    zMove = [MOVE.RIGHT, MOVE.RIGHT, MOVE.RIGHT, MOVE.DROP]
                    if minoOrder.ST: # ZST
                        # S をホールドする必要がある
                        pcState = PCState.Wait
                        pcReturnValueQueue = []
                        return [] # TODO: hold

            #----- 長方形側 (OLJ,I) -----#
            #TODO: I がOLJよりも最後かどうか判定して hold するなりなんなり

            if minoOrder.O_LJ: # OLJ or OJL
                # TODO: hold
                pcState = PCState.Wait
                pcReturnValueQueue = []
                return [] # TODO
            else:
                # O の動き
                if not minoOrder.OL and not minoOrder.OJ: # LJO or JLO
                    # O をハードドロップできない
                    oMove = [MOVE.DOWN for _ in range(alignedBoardTop - FIRST_MINO_POS[1] - 1 - 1)] + [MOVE.RIGHT, MOVE.RIGHT]
                    # oMove = [MOVE.DOWN for _ in range(alignedBoardTop - FIRST_MINO_POS[1] - 1 - 1)] + [MOVE.RIGHT, MOVE.RIGHT, MOVE.RIGHT]
                else: # JOL or LOJ
                    # O をハードドロップ可能
                    oMove = [MOVE.RIGHT, MOVE.RIGHT, MOVE.DROP]
                    # oMove = [MOVE.RIGHT, MOVE.RIGHT, MOVE.RIGHT, MOVE.DROP]
                # SZT が右側の場合は O の動きを鏡映にする
                if not minoOrder.SZ:
                    oMove = ReflectMoves(oMove)

                # L,J の動き
                if minoOrder.LJ: # LJO or LOJ
                    if minoOrder.SZ:
                        lMove = [MOVE.RIGHT, MOVE.RIGHT, MOVE.RIGHT, MOVE.DROP]
                        jMove = [MOVE.R_ROT, MOVE.R_ROT, MOVE.RIGHT, MOVE.RIGHT, MOVE.RIGHT, MOVE.DROP]
                    else:
                        if minoOrder.OJ: # LOJ
                            lMove = [MOVE.LEFT, MOVE.LEFT, MOVE.DROP]
                            jMove = [MOVE.R_ROT, MOVE.R_ROT, MOVE.LEFT, MOVE.LEFT, MOVE.DROP]
                            oMove = [MOVE.LEFT, MOVE.LEFT, MOVE.LEFT, MOVE.DROP] # 変な向きになるので O の動きも変えておく
                        else:
                            pcState = PCState.Wait
                            pcReturnValueQueue = []
                            return [] # TODO
                else: # JLO or JOL
                    if not minoOrder.SZ:
                        lMove = [MOVE.R_ROT, MOVE.R_ROT, MOVE.LEFT, MOVE.LEFT, MOVE.DROP]
                        jMove = [MOVE.LEFT, MOVE.LEFT, MOVE.DROP]
                    else:
                        if minoOrder.OL: # JOL
                            lMove = [MOVE.R_ROT, MOVE.R_ROT, MOVE.RIGHT, MOVE.RIGHT, MOVE.RIGHT, MOVE.DROP]
                            jMove = [MOVE.RIGHT, MOVE.RIGHT, MOVE.RIGHT, MOVE.DROP]
                            oMove = [MOVE.RIGHT, MOVE.RIGHT, MOVE.RIGHT, MOVE.DROP] # 変な向きになるので O の動きも変えておく
                        else:
                            pcState = PCState.Wait
                            pcReturnValueQueue = []
                            return [] # TODO

                # I の動き
                iMove = [MOVE.L_ROT, MOVE.RIGHT, MOVE.RIGHT, MOVE.RIGHT, MOVE.RIGHT, MOVE.RIGHT, MOVE.DROP]
                if not minoOrder.SZ:
                    iMove = ReflectMoves(iMove)

            pcReturnValueQueue = AssignPCMinoMoves(
                [board.currentMino.mino] + board.followingMinos,
                tMove, oMove, zMove, iMove, lMove, sMove, jMove
            )
            return [pcReturnValueQueue.pop(0)]

    elif pcState in [PCState.FirstSZTRight, PCState.FirstSZTLeft]:
        pcState = PCState.Wait
        pcReturnValueQueue = SearchPCSecondMove(board, 3)
        if not pcReturnValueQueue:
            return []
        else:
            return [pcReturnValueQueue.pop(0)]

    else:
        # あきらめて帰る
        pcState = PCState.Wait
        pcReturnValueQueue = []
        return []


# 一巡目のパフェ積みが終わった状態で使う。
# minoNum 個のミノを，パフェから溢れないようにしながら積んでいけるかを全探索により調べる。
# 高々3,4個であるうえに，パフェからあふれる場合は枝刈りをするので，実用上充分高速に動く。
def SearchPCSecondMove(board:Board, minoNum:int) -> List[List[MoveInt]]:

    # boardsは(盤面、それに至るミノの動き)のリスト
    boards = [(board, [])]
    for _ in range(minoNum):
        nextBoards = []
        for board, accumPath in boards:
            moves = decisionMaker.GetNextMoves(board)

            for mino, path in moves:

                # ラインの消去
                joindBoard, joinedTopRowIdx = JoinDirectedMinoToBoard(mino, board.mainBoard, board.topRowIdx)
                newMainBoard, newTopRowIdx, _ = ClearLines(joindBoard, joinedTopRowIdx)

                # boardAfterHoldは
                # もしHoldをしていたらその操作だけ行った後の盤面
                # そうではないときは元の盤面
                boardAfterHold = board
                if path[0] is MOVE.HOLD:
                    boardAfterHold = BoardAfterHold(board)

                nextBoard = Board(
                    newMainBoard,
                    DirectedMino(
                        boardAfterHold.followingMinos[0],
                        FIRST_MINO_DIRECTION,
                        FIRST_MINO_POS
                    ),
                    boardAfterHold.followingMinos[1:] + [MINO.NONE],
                    boardAfterHold.holdMino,
                    True,
                    newTopRowIdx,
                    boardAfterHold.score,
                    boardAfterHold.backToBack,
                    boardAfterHold.ren,
                    boardAfterHold.minoBagContents
                )

                if BOARD_HEIGHT - min(nextBoard.topRowIdx) <= 4:
                    nextBoards.append((nextBoard, accumPath + [path]))
        
       
            boards = nextBoards

    if boards:
        for board, path in boards:
            if BOARD_HEIGHT - min(board.topRowIdx) == 0:
                return path
        return []              
    else:
        return [] 



# https://harddrop.com/wiki/Perfect_Clear_Opener
# https://tannsokumegane.com/tetris-perfectclear/
# https://tetrisopener.wicurio.com/index.php?%E9%96%8B%E5%B9%95%E3%83%91%E3%83%95%E3%82%A7%E7%A9%8D%E3%81%BF

