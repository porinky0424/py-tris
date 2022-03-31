from lib.classes import *

# 占有しようとしている場所がちゃんと空白になっているかチェックする
def isValidPlace(mainBoard:List[int], occupiedPositions:List[Tuple[int]]) -> bool:
    for pos0, pos1 in occupiedPositions:
        # 盤面の左右の外にはみ出ていないこと
        if not 0 <= pos0 < BOARD_WIDTH:
            return False
        # 盤面の上下の外にはみ出ていないこと
        if not 0 <= pos1 < BOARD_HEIGHT:
            return False
        # posの場所が空白であること
        if mainBoard[pos1] & (0b1000000000 >> pos0) > 0:
            return False
    
    return True

# おこうとしている位置のどこかのブロックの下にちゃんと既存のブロックがあって，おくことができる場所であるかをチェックする
def CanPut(mainBoard:List[int], occupiedPositions:List[Tuple[int]]) -> bool:
    for pos0, pos1 in occupiedPositions:
        if pos1 + 1 < BOARD_HEIGHT and mainBoard[pos1+1] & (0b1000000000 >> pos0) > 0:
            return True
        elif pos1 + 1 == BOARD_HEIGHT:
            return True
    return False

# ボードが空になっているか（全ての行に関して）をチェックする
def isBoardEmpty(mainBoard:List[int]) -> bool:
    for row in mainBoard:
        if row != 0:
            return False
    return True

# ボードの上端がアラインされているかをチェックする
alignedBoardTop = BOARD_HEIGHT # 上端のインデックス。全て空白の場合はボード外を指すことになる
def isBoardTopAligned(mainBoard:List[int]) -> bool:
    global alignedBoardTop
    for i,row in enumerate(mainBoard):
        if row != 0:
            if row == 0b1111111111:
                alignedBoardTop = i
                return True
            else:
                return False
    alignedBoardTop = BOARD_HEIGHT
    return True

