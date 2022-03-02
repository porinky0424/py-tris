import initSettings
import boardWatcher
import decisionMaker
import minoMover
import simulator
from lib import *

# ゲーム画面を認識して標準出力に出力する関数（無限ループ）
def PytrisBoardWatcher ():
    print("\n\nPy-tris Board Watcher\n\n")

    # ゲームの再開
    PressEnter()

    # 盤面を出力する分の行数を確保する
    for _ in range(DISPLAYED_BOARD_HEIGHT):
        print("", flush=True)
    
    # boardオブジェクトの生成
    board = Board()

    # メインループ
    while True:
        with mss.mss() as sct:
            a = Timer()
            # キャプチャする範囲は1P側の半分で十分
            region = {'top': WINDOW_Y, 'left': WINDOW_X, 'width': WINDOW_WIDTH / 2, 'height': WINDOW_HEIGHT}
            img = sct.grab(region)
            img = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
            board.mainBoard = boardWatcher.GetMainBoard(img)
            board.followingMinos = boardWatcher.GetFollowingMinos(img)
            board.holdMino = boardWatcher.GetHoldMino(img)
            PrintBoard(board, True, a.Stop())

# simulator上で思考を再現する（無限ループ）
def PytrisSimulator ():
    print("\n\nPy-tris Simulator\n\n")

    # 適当に盤面を生成
    board = Board()

    # board.AddBlockToMainBoard((5 ,38))
    # board.AddBlockToMainBoard((5 ,37))
    # board.AddBlockToMainBoard((4 ,37))
    # board.AddBlockToMainBoard((1 ,37))
    # board.AddBlockToMainBoard((1 ,38))
    # for i in range(10):
    #     board.AddBlockToMainBoard((i ,39))

    board.followingMinos = [simulator.GenerateMino() for _ in range(FOLLOWING_MINOS_COUNT)]
    print("\n\n\n")
    PrintBoard(board)

    while True:
        addedMino = simulator.GenerateMino()
        board = simulator.AddFollowingMino(board, addedMino)

        # 思考ルーチン
        value, mino, path = decisionMaker.Decide(board)

        board = simulator.PutMino(path, board.currentMino, board)

        newMainBoard, clearedRowCount = simulator.ClearLinesOfBoard(board)
        board = Board(
            newMainBoard,
            None,
            board.followingMinos,
            board.holdMino,
            True
        )

# 実機上で思考を再現する（無限ループ、シングルスレッド）
# Start Overを押せる状態からはじめないとバグる
def PytrisMover ():
    # ゲームの再開
    PressEnter()
    time.sleep(3.7)

    # 現在の盤面の状況を読み取る
    with mss.mss() as sct:
        region = {'top': WINDOW_Y, 'left': WINDOW_X, 'width': WINDOW_WIDTH / 2, 'height': WINDOW_HEIGHT}
        img = sct.grab(region)
    img = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
    board = Board(
        None,
        DirectedMino(boardWatcher.GetCurrentMino(), DIRECTION.N, FIRST_MINO_POS),
        boardWatcher.GetFollowingMinos(img),
        boardWatcher.GetHoldMino(img),
        True
    )

    while True:
        # 思考ルーチン
        value, mino, path = decisionMaker.Decide(board)
        print("debug path:", path)

        # 移動
        directedMino = minoMover.InputMove(path, board.currentMino, board.mainBoard)

        # ライン消去
        joinedMainBoard = JoinDirectedMinoToBoard(directedMino, board.mainBoard)
        newMainBoard, clearedRowCount = ClearLines(joinedMainBoard)
        board = Board(
            newMainBoard,
            None,
            board.followingMinos,
            board.holdMino,
            True
        )
        PrintBoard(board, False)

        # 次の状態の盤面を用意
        while True: # 次のfollowingMinosを認識
            with mss.mss() as sct:
                region = {'top': WINDOW_Y, 'left': WINDOW_X, 'width': WINDOW_WIDTH / 2, 'height': WINDOW_HEIGHT}
                img = sct.grab(region)
            img = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
            followingMinos = boardWatcher.GetFollowingMinos(img)
            if followingMinos != board.followingMinos: # followingMinosが変わったら次へ
                break
        board = simulator.AddFollowingMino(board, followingMinos[-1])



def main():
    # ゲームの初期設定
    initSettings.Init()
    
    # # 盤面監視モード
    # PytrisBoardWatcher()

    # # simulatorモード
    # PytrisSimulator()

    # 実機確認モード
    PytrisMover()
