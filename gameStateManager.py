# -------------
#
# Init Settings
#
# -------------

windowをアクティブにする
try:
    import win32gui
    window = win32gui.FindWindow(None, "PuyoPuyoTetris")
    win32gui.SetForegroundWindow(window)
    print("Window activated.", flush=True)
except:
    print("win32gui not installed.")

from lib import *
from params.eval import *

# GetOccupiedPositionsの前計算
InitGetOccupiedPositions()

import boardWatcher
import decisionMaker
import minoMover
import simulator
import evaluator
import openTemplateMaker
import perfectClear


# 探索の深さの設定
INIT_SEARCH_LIMIT = 4
INIT_BEAM_WIDTH = [3,3,3]

# 実行時引数の設定
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("mode", help="Select mode (app/sim)")
parser.add_argument("-q", "--quickSearch", help="Reduce the number of search nodes, and speed up calculation.", action="store_true")
parser.add_argument("-m", "--multiPlay", help="Play with AI in multiplayer-mode.", action="store_true")
args = parser.parse_args()

if args.quickSearch:
    decisionMaker.quickSearch = True

# -------------
#
# Init Settings End
#
# -------------

# simulator上で思考を再現する（無限ループ）
def PytrisSimulator ():
    # 初期化
    decisionMaker.SEARCH_LIMIT = INIT_SEARCH_LIMIT
    decisionMaker.BEAM_WIDTH = INIT_BEAM_WIDTH

    print("\n\nPy-tris Simulator\n\n")

    # 適当に盤面を生成
    board = Board()

    board.followingMinos = [simulator.GenerateMino() for _ in range(FOLLOWING_MINOS_COUNT)]
    board.minoBagContents = ReturnFullBag()
   
    print("\n\n\n")
    PrintBoard(board)

    """# Decide
    while True:
        assert type(board.score) == int
        assert len(board.followingMinos) == FOLLOWING_MINOS_COUNT
        board = simulator.AddFollowingMino(board)

        # 思考ルーチン
        value, mino, path = decisionMaker.Decide(board)

        board, isTspin, isTspinmini = simulator.PutMino(path, board)

        newMainBoard, newTopRowIdx, clearedRowCount = simulator.ClearLinesOfBoard(board)
        scoreAdd, backToBack, ren = evaluator.Score(isTspin, isTspinmini, clearedRowCount, board.backToBack, board.ren)

        board = Board(
            newMainBoard,
            None,
            board.followingMinos,
            board.holdMino,
            True,
            newTopRowIdx,
            board.score + scoreAdd,
            backToBack,
            ren,
            board.minoBagContents
        )
    """

    # Multi-Decide
    # テンプレを狙える時は狙う
    board = simulator.AddFollowingMino(board)
    while True:
        assert type(board.score) == int
        assert len(board.followingMinos) == FOLLOWING_MINOS_COUNT

        # 思考ルーチン
        multipath = perfectClear.PerfectClear(board)
        if not multipath:
            multipath = openTemplateMaker.GetCustomTemplateMove(board)
        if not multipath:
            multipath = decisionMaker.MultiDecide(board)

        for path in multipath:
            board, isTspin, isTspinmini = simulator.PutMino(path, board)

            newMainBoard, newTopRowIdx, clearedRowCount = simulator.ClearLinesOfBoard(board)
            scoreAdd, backToBack, ren = evaluator.Score(isTspin, isTspinmini, clearedRowCount, board.backToBack, board.ren)

            board = Board(
                newMainBoard,
                None,
                board.followingMinos,
                board.holdMino,
                True,
                newTopRowIdx,
                board.score + scoreAdd,
                backToBack,
                ren,
                board.minoBagContents
            )

            board = simulator.AddFollowingMino(board)
        


# 実機上で思考を再現する（無限ループ、シングルスレッド）
# menu画面にいて、Startを押せる状態からはじめないとバグる
def PytrisMover ():
    if args.multiPlay:
        # マルチプレイヤーモード

        boardWatcher.is1P = False
        
        # キャラクターセレクト画面になるまで待機
        while not boardWatcher.IsCharacterSelect():
            time.sleep(0.1)

        # キャラクターセレクトを実行
        time.sleep(0.5)
        print("'Chalacter Select' Recognized.")
        time.sleep(0.5)
        PressEnter()
        time.sleep(0.5)
        if boardWatcher.is1P: # 1Pだったらアルルなのでテトリスにずらす
            Move(MOVE.RIGHT)
            time.sleep(0.5)
        PressEnter()
        time.sleep(0.5)
        PressEnter() # キャラ設定完了
        time.sleep(0.5)
        print("Character selected.")
        
    else:
        # シングルプレイヤーモード
        pass

    while True:
        # 初期化
        decisionMaker.SEARCH_LIMIT = INIT_SEARCH_LIMIT
        decisionMaker.BEAM_WIDTH = INIT_BEAM_WIDTH
        paths = []

        # ゲーム開始待機状態になるまで待機
        while not boardWatcher.IsGameReady():
            time.sleep(0.1)
        
        print("Ready Recognized. Wait for starting a game...")
        
        previousFollowingMinos = [boardWatcher.GetFollowingMinos()[0]]

        # ゲーム開始するまで待機
        while not boardWatcher.HasGameStarted():
            continue
            
        print("Start!")

        # ゲーム開始
        while True:
            # 消去中のラインが消えるまで待つ
            while boardWatcher.IsClearingLines():
                pass

            # followingMinosが変化するまで待つ
            while True:
                if previousFollowingMinos != boardWatcher.GetFollowingMinos():
                    previousFollowingMinos = boardWatcher.GetFollowingMinos()
                    break
            
            # 現在のミノが出てくるまで待つ
            while True:
                if boardWatcher.GetCurrentMino() is not None:
                    break
            
            # 各列において，上から順に見ていって，一番最初にブロックがある部分のrowIdxを格納する
            mainBoard = boardWatcher.GetMainBoard()
            topRowIdx = [BOARD_HEIGHT for _ in range(BOARD_WIDTH)]
            for rowIdx in range(BOARD_HEIGHT-1, -1, -1):
                for colIdx in range(BOARD_WIDTH):
                    if mainBoard[rowIdx] & (0b1000000000 >> colIdx) > 0:
                        topRowIdx[colIdx] = rowIdx
            
            # 盤面の状況を読み取る
            board = Board(
                mainBoard,
                DirectedMino(
                    boardWatcher.GetMinoTypeOfCurrentMino(),
                    FIRST_MINO_DIRECTION,
                    FIRST_MINO_POS
                ),
                boardWatcher.GetFollowingMinos(),
                boardWatcher.GetHoldMino(),
                True,
                topRowIdx,
                0,
                False,
                0
            )

            # 思考ルーチン
            decideTimer = Timer()
            if not paths:
                multiPath = openTemplateMaker.GetCustomTemplateMove(board)
                if not multiPath:
                    multiPath = decisionMaker.MultiDecide(board)
                paths += multiPath

            print("Making Decision in {}s".format(decideTimer.Stop()), flush=True)

            # 移動
            # todo: 連続でおく途中でおきミスしたときや、盤面の状況が変化したときの対処（porinky0424がやります）
            mainBoard = board.mainBoard
            while paths:
                mainBoard.updateMinoBagContents()
                path = paths.pop(0)
                currentMino = boardWatcher.GetMinoTypeOfCurrentMino()

                # 最初に実行するのがHOLDの時は別に実行する
                if path[0] is MOVE.HOLD:
                    if mainBoard.holdMino is MINO.NONE:
                        pcFirstHold = True

                    time.sleep(0.1) # 安定のためにHOLDの前後にsleepを入れる
                    Move(MOVE.HOLD)
                    time.sleep(0.1)

                    # pathからHOLDを取り除く
                    path = path[1:]

                    # 次のミノが出てくるまで待機
                    while True:
                        if boardWatcher.GetCurrentMino() is not None:
                            break
                    
                    currentMino = boardWatcher.GetMinoTypeOfCurrentMino()
                
                # 移動
                directedMino = minoMover.InputMove(
                    path,
                    DirectedMino(
                        currentMino,
                        FIRST_MINO_DIRECTION,
                        FIRST_MINO_POS
                    ),
                    mainBoard
                )

                # おいた後の盤面を生成
                joinedMainBoard = JoinDirectedMinoToBoardWithoutTopRowIdx(directedMino, mainBoard)
                mainBoard, clearedRowCount = ClearLinesWithoutTopRowIdx(joinedMainBoard)
                if pcFirstHold:
                    mainBoard.updateMinoBagContents() # first MOVE.HOLD
                    pcFirstHold = False

                # 試合が終了して、次のゲームが始まっていないか気にしながら次の操作ができるような状態になるまで待機
                isGameReady = False
                if paths:
                    # followingMinosが変化するまで待つ
                    while True:
                        if previousFollowingMinos != boardWatcher.GetFollowingMinos():
                            previousFollowingMinos = boardWatcher.GetFollowingMinos()
                            break

                        # ゲーム開始待機状態に戻ったら、次のゲームに移行する
                        if boardWatcher.IsGameReady():
                            isGameReady = True
                            break

                    # 次のミノが出てくるまで待機
                    while True:
                        if boardWatcher.GetCurrentMino() is not None:
                            break

                        # ゲーム開始待機状態に戻ったら、次のゲームに移行する
                        if boardWatcher.IsGameReady():
                            isGameReady = True
                            break
                    
                    if isGameReady:
                        break

            # ゲーム開始待機状態に戻ったら、次のゲームに移行する
            if isGameReady or boardWatcher.IsGameReady():
                print("Next game started. Reloading...", flush=True)
                break

def main():
    if args.mode == "sim":
        # simulatorモード
        PytrisSimulator()
    elif args.mode == "app":
        # 実機確認モード
        PytrisMover()
    else:
        Error("Invalid mode inputted.")
