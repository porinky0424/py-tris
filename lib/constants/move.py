from typing import List

# MOVEはクラス定数
# 型の検査がなくなるため高速化
class MOVE():
    LEFT = 0
    RIGHT = 1
    DOWN = 2
    DROP = 3
    HOLD = 4
    R_ROT = 5
    L_ROT = 6

# intのエイリアスとしてMoveIntを定義
MoveInt = int

# 盤面中心で左右に線対称なミノ移動を返す
def ReflectMove(move:MOVE) -> MOVE:
    if move is MOVE.LEFT:
        return MOVE.RIGHT
    elif move is MOVE.RIGHT:
        return MOVE.LEFT
    elif move is MOVE.R_ROT:
        return MOVE.L_ROT
    elif move is MOVE.L_ROT:
        return MOVE.R_ROT
    else:
        return move

def ReflectMoves(moves:List[MOVE]) -> List[MOVE]:
    return [ReflectMove(move) for move in moves]
