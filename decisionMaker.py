from lib import *
import evaluator
from functools import total_ordering
import heapq

# 回転するミノを考えるかどうか
quickSearch = False

#時間が立たないともらえない報酬は割引する。
EVAL_TAU = 0.9

# Beam Search用のclass
@total_ordering
class State():
    #　評価値の計算だけ行う
    def __init__(self, board:Board, mino:DirectedMino, path:List[MoveInt], accumPathValue:int, accumScore:int, accumPath:List[List[MoveInt]], tau=EVAL_TAU):
        self.board = board
        self.mino = mino 
        self.path = path
        self.accumPath = accumPath + [path]
        self.tau = tau
        
        # ライン消去
        JoinDirectedMinoToBoardUncopy(mino, board.mainBoard, board.topRowIdx)
        clearedRowCount = ClearLinesCalc(board.mainBoard)
        
        # 評価値の計算
        isTspin = evaluator.IsTSpin(board.mainBoard, mino, path)
        isTspinmini = isTspin and evaluator.IsTSpinMini(board.mainBoard, mino, path)
        self.accumPathValue = accumPathValue + self.tau * evaluator.EvalPath(path, clearedRowCount, board.mainBoard, mino, board.backToBack, board.ren)
        self.eval = self.accumPathValue + self.tau * evaluator.EvalMainBoard(board.mainBoard, clearedRowCount, board.topRowIdx)
        
        # スコアの計算
        self.score, self.backToBack, self.ren = evaluator.Score(isTspin, isTspinmini, clearedRowCount, board.backToBack, board.ren)
        self.score += accumScore

        # Boardを元に戻す
        DeleteDirectedMinoFromBoardUncopy(mino, board.mainBoard, board.topRowIdx)
        
    def __eq__(self, other):
        return self.eval == other.eval

    def __lt__(self, other):
        return self.eval < other.eval
    
    # 実際に遷移する
    def Transit(self):
        # ライン消去
        joinedBoard, joinedTopRowIdx = JoinDirectedMinoToBoard(self.mino, self.board.mainBoard, self.board.topRowIdx)
        newMainBoard, newTopRowIdx, _ = ClearLines(joinedBoard, joinedTopRowIdx)

        # ミノを置いた後の盤面の生成
        if self.path[0] is MOVE.HOLD:
            self.board = BoardAfterHold(self.board)
    
        clearedBoard = Board(
            newMainBoard,
            DirectedMino(
                self.board.followingMinos[0],
                FIRST_MINO_DIRECTION,
                FIRST_MINO_POS
            ),
            self.board.followingMinos[1:] + [MINO.NONE],
            self.board.holdMino,
            True,
            newTopRowIdx,
            self.score,
            self.backToBack,
            self.ren,
            self.board.minoBagContents
        )
        self.board = clearedBoard

    #　ありうる次の盤面をすべて生成する。
    def NextStates(self):
        possibleMoves = GetNextMoves(self.board)
        nextStates = [State(self.board, nextMino, nextPath, self.accumPathValue, self.board.score, self.accumPath, self.tau * EVAL_TAU) for nextMino, nextPath in possibleMoves]
        return nextStates

# minoを今の位置からdirectionを変えずに左右に動かして得られるminoのリストを返す
def GetSideMovedMinos (board:Board, mino:DirectedMino) -> List[Tuple[DirectedMino, List[MoveInt]]]:
    sideMovedMinos = []

    # 左に動かしていく
    # 左右移動を一回もしない場合はこちら側に含める（そのためにxに+1している）
    x,y = mino.pos[0] + 1, mino.pos[1]
    count = -1
    while True:
        x -= 1
        count += 1
        newMino = DirectedMino(
            mino.mino,
            mino.direction,
            (x,y)
        )
        occupiedPositions = GetOccupiedPositions(newMino)
        if isValidPlace(board.mainBoard, occupiedPositions):
            sideMovedMinos.append((newMino, [MOVE.LEFT for _ in range(count)]))
        else:
            break
    
    # 右に動かしていく
    x,y = mino.pos[0], mino.pos[1]
    count = 0
    while True:
        x += 1
        count += 1
        newMino = DirectedMino(
            mino.mino,
            mino.direction,
            (x,y)
        )
        occupiedPositions = GetOccupiedPositions(newMino)
        if isValidPlace(board.mainBoard, occupiedPositions):
            sideMovedMinos.append((newMino, [MOVE.RIGHT for _ in range(count)]))
        else:
            break
    
    return sideMovedMinos

# minoを今の位置で1回だけ回転を試みた場合に得られるminoのリストに，回転を全く試みない場合を足して返す
def GetRotatedMinos (board:Board, mino:DirectedMino) -> List[Tuple[DirectedMino, List[MoveInt]]]:
    rotatedMinos = []

    # 回転なし
    rotatedMinos.append((mino, []))

    # 左回転
    directedMino = Rotate(mino, MOVE.L_ROT, board.mainBoard)
    if directedMino is not None:
        rotatedMinos.append((directedMino, [MOVE.L_ROT]))
    
    # 右回転
    directedMino = Rotate(mino, MOVE.R_ROT, board.mainBoard)
    if directedMino is not None:
        rotatedMinos.append((directedMino, [MOVE.R_ROT]))
    
    return rotatedMinos

def AddToReachableNodes (encodedNode, path:List[MoveInt], reachableNodes:Dict[int, List[MoveInt]]) -> None:
    if encodedNode not in reachableNodes: # まだreachableNodesに登録されていないものは，登録する
        reachableNodes[encodedNode] = path
    else:
        # すでに登録されていた場合，pathが今までのものより短ければ登録する
        oldPath = reachableNodes[encodedNode]
        if len(path) < len(oldPath):
            reachableNodes[encodedNode] = path

# MOVE.DROPを使うことにより，pathの簡易化を行う
def SimplifyPath (path:List[MoveInt]) -> List[MoveInt]:
    # 最後には必ずMOVE.DROPをつける
    # 最後にMOVE.DROPをつけるので，最後の連続するMOVE.DOWNは消去できる
    count = 0
    while count < len(path):
        if path[-(count + 1)] is MOVE.DOWN:
            count += 1
        else:
            break
    simplifiedPath = path[:len(path) - count] + [MOVE.DROP]
    return simplifiedPath

# MOVE.DROPを使うことにより，pathの簡易化を行う
# 引数自体を変更する
def SimplifyPathUncopy (path:List[MoveInt]):
    # 最後には必ずMOVE.DROPをつける
    # 最後にMOVE.DROPをつけるので，最後の連続するMOVE.DOWNは消去できる
    while path:
        if path[-1] is MOVE.DOWN:
            path.pop()
        else:
            break
    path.append(MOVE.DROP)
        
# boardとそこに置きたいminoを入力して，
# (ミノがおける場所，そこにたどり着く方法)
# という形式のタプルの配列を返す
def GetPossibleMoves(
    board:Board,
    directedMino:DirectedMino,
) -> List[Tuple[DirectedMino, List[MoveInt]]]:

    # 到達できるミノをエンコードしたものと，到達するための経路を結ぶ辞書
    reachableNodes = {
        EncodeDirectedMino(directedMino) : []
    }

    # 4方角の全てのミノを最上部で左右に動かす

    undroppedMinos = []

    # そのままの向き
    sideMovedMinos = GetSideMovedMinos(board, directedMino)
    
    for mino, path in sideMovedMinos:
        reachableNodes[EncodeDirectedMino(mino)] = path
    undroppedMinos += sideMovedMinos

    if quickSearch: # quickSearchモードの場合、Tミノ以外は形がおなじものであれば考えない
        if directedMino.mino not in {MINO.O}:
            # 右に1回転したもの
            rightRotatedDirectedMino = Rotate(directedMino, MOVE.R_ROT, board.mainBoard)
            if rightRotatedDirectedMino is not None:
                sideMovedMinos = GetSideMovedMinos(board, rightRotatedDirectedMino)
                for mino, path in sideMovedMinos:
                    path.insert(0, MOVE.R_ROT)
                    reachableNodes[EncodeDirectedMino(mino)] = path
                undroppedMinos += sideMovedMinos
                if directedMino.mino not in {MINO.S, MINO.Z, MINO.I}:
                    # 右に2回転(180回転)したもの
                    upsideDownRotatedDirectedMino = Rotate(rightRotatedDirectedMino, MOVE.R_ROT, board.mainBoard)
                    if upsideDownRotatedDirectedMino is not None:
                        sideMovedMinos = GetSideMovedMinos(board, upsideDownRotatedDirectedMino)
                        for mino, path in sideMovedMinos:
                            path.insert(0, MOVE.R_ROT)
                            path.insert(0, MOVE.R_ROT)
                            reachableNodes[EncodeDirectedMino(mino)] = path
                        undroppedMinos += sideMovedMinos
            if directedMino.mino not in {MINO.S, MINO.Z, MINO.I}:
                # 左に1回転したもの
                leftRotatedDirectedMino = Rotate(directedMino, MOVE.L_ROT, board.mainBoard)
                if leftRotatedDirectedMino is not None:
                    sideMovedMinos = GetSideMovedMinos(board, leftRotatedDirectedMino)
                    for mino, path in sideMovedMinos:
                        path.insert(0, MOVE.L_ROT)
                        reachableNodes[EncodeDirectedMino(mino)] = path
                    undroppedMinos += sideMovedMinos
    else:
        # 右に1回転したもの
        rightRotatedDirectedMino = Rotate(directedMino, MOVE.R_ROT, board.mainBoard)
        if rightRotatedDirectedMino is not None:
            sideMovedMinos = GetSideMovedMinos(board, rightRotatedDirectedMino)
            for mino, path in sideMovedMinos:
                path.insert(0, MOVE.R_ROT)
                reachableNodes[EncodeDirectedMino(mino)] = path
            undroppedMinos += sideMovedMinos
            # 右に2回転(180回転)したもの
            upsideDownRotatedDirectedMino = Rotate(rightRotatedDirectedMino, MOVE.R_ROT, board.mainBoard)
            if upsideDownRotatedDirectedMino is not None:
                sideMovedMinos = GetSideMovedMinos(board, upsideDownRotatedDirectedMino)
                for mino, path in sideMovedMinos:
                    path.insert(0, MOVE.R_ROT)
                    path.insert(0, MOVE.R_ROT)
                    reachableNodes[EncodeDirectedMino(mino)] = path
                undroppedMinos += sideMovedMinos
        # 左に1回転したもの
        leftRotatedDirectedMino = Rotate(directedMino, MOVE.L_ROT, board.mainBoard)
        if leftRotatedDirectedMino is not None:
            sideMovedMinos = GetSideMovedMinos(board, leftRotatedDirectedMino)
            for mino, path in sideMovedMinos:
                path.insert(0, MOVE.L_ROT)
                reachableNodes[EncodeDirectedMino(mino)] = path
            undroppedMinos += sideMovedMinos
    
    # ミノを全て下に落とす

    for mino, path in undroppedMinos:
        dropCount = DropFromTop(board.mainBoard,  board.topRowIdx, mino)
        mino.pos = (mino.pos[0], mino.pos[1] + dropCount)
        path += [MOVE.DOWN for _ in range(dropCount)]
        reachableNodes[EncodeDirectedMino(mino)] = path
    droppedMinos = undroppedMinos # リネーム

    # 回転できるところまで回転する

    if quickSearch:
        if directedMino.mino == MINO.T:
            while droppedMinos:
                mino, path = droppedMinos.pop()
                rightRotatedMino = mino
                leftRotatedMino = mino
                hasRightRotateEnded = False
                hasLeftRotateEnded = False
                rightRotateCount = 1
                leftRotateCount = 1
                while True:
                    # 回転数が少なくなるように、R_ROT, L_ROTを交互に実行する
                    if not hasRightRotateEnded:
                        rightRotatedMino = Rotate(rightRotatedMino, MOVE.R_ROT, board.mainBoard)
                        if rightRotatedMino is not None and EncodeDirectedMino(rightRotatedMino) not in reachableNodes: # 回転可能かつまだ到達してない部分
                            reachableNodes[EncodeDirectedMino(rightRotatedMino)] = path + [MOVE.R_ROT for _ in range(rightRotateCount)]
                            rightRotateCount += 1

                            # 回転中下に1つ落とせるなら落としたものを追加で考える (todo: 1つ以上落とせる場合もなくはなさそう、計算の時間と相談)
                            oneDroppedDirectedMino = DirectedMino(
                                rightRotatedMino.mino,
                                rightRotatedMino.direction,
                                (rightRotatedMino.pos[0], rightRotatedMino.pos[1] + 1)
                            )
                            if isValidPlace(board.mainBoard, GetOccupiedPositions(oneDroppedDirectedMino)):
                                droppedMinos.append((oneDroppedDirectedMino, path + [MOVE.R_ROT for _ in range(rightRotateCount-1)] + [MOVE.DOWN]))
                        else:
                            hasRightRotateEnded = True
                    
                    if not hasLeftRotateEnded:
                        leftRotatedMino = Rotate(leftRotatedMino, MOVE.L_ROT, board.mainBoard)
                        if leftRotatedMino is not None and EncodeDirectedMino(leftRotatedMino) not in reachableNodes: # 回転可能かつまだ到達してない部分
                            reachableNodes[EncodeDirectedMino(leftRotatedMino)] = path + [MOVE.L_ROT for _ in range(leftRotateCount)]
                            leftRotateCount += 1

                            # 回転中下に1つ落とせるなら落としたものを追加で考える (todo: 1つ以上落とせる場合もなくはなさそう、計算の時間と相談)
                            oneDroppedDirectedMino = DirectedMino(
                                leftRotatedMino.mino,
                                leftRotatedMino.direction,
                                (leftRotatedMino.pos[0], leftRotatedMino.pos[1] + 1)
                            )
                            if isValidPlace(board.mainBoard, GetOccupiedPositions(oneDroppedDirectedMino)):
                                droppedMinos.append((oneDroppedDirectedMino, path + [MOVE.L_ROT for _ in range(leftRotateCount-1)] + [MOVE.DOWN]))
                        else:
                            hasLeftRotateEnded = True
                    
                    # どちらの方向にも回転できなくなったら終了
                    if hasRightRotateEnded and hasLeftRotateEnded:
                        break
    else:
        while droppedMinos:
            mino, path = droppedMinos.pop()
            rightRotatedMino = mino
            leftRotatedMino = mino
            hasRightRotateEnded = False
            hasLeftRotateEnded = False
            rightRotateCount = 1
            leftRotateCount = 1
            while True:
                # 回転数が少なくなるように、R_ROT, L_ROTを交互に実行する
                if not hasRightRotateEnded:
                    rightRotatedMino = Rotate(rightRotatedMino, MOVE.R_ROT, board.mainBoard)
                    if rightRotatedMino is not None and EncodeDirectedMino(rightRotatedMino) not in reachableNodes: # 回転可能かつまだ到達してない部分
                        reachableNodes[EncodeDirectedMino(rightRotatedMino)] = path + [MOVE.R_ROT for _ in range(rightRotateCount)]
                        rightRotateCount += 1

                        # 回転中下に1つ落とせるなら落としたものを追加で考える (todo: 1つ以上落とせる場合もなくはなさそう、計算の時間と相談)
                        oneDroppedDirectedMino = DirectedMino(
                            rightRotatedMino.mino,
                            rightRotatedMino.direction,
                            (rightRotatedMino.pos[0], rightRotatedMino.pos[1] + 1)
                        )
                        if isValidPlace(board.mainBoard, GetOccupiedPositions(oneDroppedDirectedMino)):
                            droppedMinos.append((oneDroppedDirectedMino, path + [MOVE.R_ROT for _ in range(rightRotateCount-1)] + [MOVE.DOWN]))
                    else:
                        hasRightRotateEnded = True
                
                if not hasLeftRotateEnded:
                    leftRotatedMino = Rotate(leftRotatedMino, MOVE.L_ROT, board.mainBoard)
                    if leftRotatedMino is not None and EncodeDirectedMino(leftRotatedMino) not in reachableNodes: # 回転可能かつまだ到達してない部分
                        reachableNodes[EncodeDirectedMino(leftRotatedMino)] = path + [MOVE.L_ROT for _ in range(leftRotateCount)]
                        leftRotateCount += 1

                        # 回転中下に1つ落とせるなら落としたものを追加で考える (todo: 1つ以上落とせる場合もなくはなさそう、計算の時間と相談)
                        oneDroppedDirectedMino = DirectedMino(
                            leftRotatedMino.mino,
                            leftRotatedMino.direction,
                            (leftRotatedMino.pos[0], leftRotatedMino.pos[1] + 1)
                        )
                        if isValidPlace(board.mainBoard, GetOccupiedPositions(oneDroppedDirectedMino)):
                            droppedMinos.append((oneDroppedDirectedMino, path + [MOVE.L_ROT for _ in range(leftRotateCount-1)] + [MOVE.DOWN]))
                    else:
                        hasLeftRotateEnded = True
                
                # どちらの方向にも回転できなくなったら終了
                if hasRightRotateEnded and hasLeftRotateEnded:
                    break

    # 結果出力
    possibleMoves = []
    # 方向は異なるが占領する場所は同じになるミノが存在するので，これらを重複して数えないために利用する
    # 例えばzミノはNとSで位置をずらせば同じ場所を占領するようになる
    encodedPlacesList = set()
    for key in reachableNodes:
        path = reachableNodes[key]
        SimplifyPathUncopy(path)
        decodedMino = DecodeDirectedMino(key)
        encodedPlaces = EncodePlacesOccupiedByDirectedMino(decodedMino)
        if encodedPlaces in encodedPlacesList:
            # possibleMovesの中から同じ位置を占領することになるdirectedMinoを探索
            sameMino, samePath = None, None
            for mino, path in possibleMoves:
                if (
                    EncodePlacesOccupiedByDirectedMino(mino) == encodedPlaces
                ):
                    sameMino, samePath = mino, path
                    break
            # 今回考えているpathの方が短かったら入れ替え
            possibleMoves.remove((sameMino, samePath))
            possibleMoves.append((decodedMino, path))
        else:
            if CanPut(board.mainBoard, GetOccupiedPositions(decodedMino)): # 空中に浮いたりしていないことをチェック
                possibleMoves.append((
                    decodedMino,
                    path
                ))
                encodedPlacesList.add(encodedPlaces)
    
    return possibleMoves

# 今のBoardからHoldも含めたミノの操作をすべて見つける。
def GetNextMoves(board:Board) -> List[Tuple[DirectedMino, List[MoveInt]]]:
    boardAfterHold = BoardAfterHold(board)
    
    NextMoves = GetPossibleMoves(board, board.currentMino) + \
                [(mino, [MOVE.HOLD] + path) for mino, path in GetPossibleMoves(boardAfterHold, boardAfterHold.currentMino)]

    return NextMoves


SEARCH_LIMIT = None # initialized in gameStateManager
BEAM_WIDTH = None # initialized in gameStateManager
firstHold = True
def Search (board:Board, mino:DirectedMino, path:List[MOVE], limit:int) -> Tuple[int, List[List[MOVE]]]:
    global BEAM_WIDTH

    state_queue = []
    heapq.heapify(state_queue)
    init_state = State(board, mino, path, 0, board.score, [])
    init_state.Transit()
    heapq.heappush(state_queue, init_state)

    for beamWidth in BEAM_WIDTH:
        next_state_queue = []
        heapq.heapify(next_state_queue)
        while len(state_queue) > 0:

            now_state = heapq.heappop(state_queue)
            for next_state in now_state.NextStates():
                heapq.heappush(next_state_queue, next_state)
            
            while len(next_state_queue) > beamWidth:
                heapq.heappop(next_state_queue)

        state_queue = next_state_queue
        # 実際に遷移
        for state in state_queue:
            state.Transit()
    
    while len(state_queue) > 1:
        heapq.heappop(state_queue)

    final_state = heapq.heappop(state_queue)
    return final_state.eval, final_state.accumPath

# 実際に手を決める関数
def Decide (board:Board) -> Tuple[float, DirectedMino, List[MoveInt]]:
    global SEARCH_LIMIT, BEAM_WIDTH, firstHold

    try:
        possibleMoves = GetNextMoves(board)

        # 評価値計算
        maxValue, maxMino, maxPath = -10000000000, None, None
        for mino, path in possibleMoves:
            # 評価値計算
            value, _ = Search(board, mino, path, SEARCH_LIMIT-1)
            if value >= maxValue:
                maxMino, maxPath = mino, path
                maxValue = value

        if maxMino is None or maxPath is None:
            Warn("Cannot decide path.")
            maxMino, maxPath = possibleMoves[0]
    
    # 実行するなかでassertionが出てしまったら、負けを認める
    except AssertionError:
        print("I Lost...")
        return -100000000000, None, [MOVE.DROP]
    
    # 1回Holdしたら、あとは5手先読みできるようになる。
    if maxPath[0] is MOVE.HOLD and firstHold:
        SEARCH_LIMIT += 1
        BEAM_WIDTH.append(3)
        firstHold = False
    
    return maxValue, maxMino, maxPath

# 複数手を決める関数
def MultiDecide(board:Board) -> List[List[MoveInt]]:
    global SEARCH_LIMIT, BEAM_WIDTH, firstHold

    try:
        possibleMoves = GetNextMoves(board)

        # 評価値計算
        maxValue, maxMino, maxMultiPath = -10000000000, None, None
        for mino, path in possibleMoves:
            # 評価値計算
            value, multipath = Search(board, mino, path, SEARCH_LIMIT-1)
            if value >= maxValue:
                maxMino, maxMultiPath = mino, multipath
                maxValue = value
        
        if maxMino is None or maxMultiPath is None:
            Warn("Cannot decide path.")
            maxMino, maxMultiPath = possibleMoves[0]
        
        # 1回Holdしたら、あとは5手先読みできるようになる。
        if firstHold:
            for path in maxMultiPath:
                if path[0] is MOVE.HOLD:
                    SEARCH_LIMIT += 1
                    BEAM_WIDTH.append(3)
                    firstHold = False
                    break

        maxMultiPath = maxMultiPath[:SEARCH_LIMIT]
    
    # 実行するなかでassertionが出てしまったら、負けを認める
    except AssertionError:
        print("I Lost...")
        return [[MOVE.DROP]]

    return maxMultiPath