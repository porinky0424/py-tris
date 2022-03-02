from lib.classes import *

# mainBoard内で横一列が揃っている場合にそれを除去して，何ライン除去したかという情報と共に返す
def ClearLines(mainBoard:List[int]) -> Tuple[List[int], int]:
    # クリアされたrowのインデックスを保存していく
    clearedRowIdx = set()
    for i in range(BOARD_HEIGHT):
        # 横一列が揃っているかチェック
        if mainBoard[i] == 0b1111111111:
            clearedRowIdx.add(i)

    # clearedRowIdxに入っている行を実際に削除する
    newMainBoard = [0b0 for _ in range(BOARD_HEIGHT)]
    for i in range(BOARD_HEIGHT):
        if i not in clearedRowIdx:
            newMainBoard.append(mainBoard[i])
    
    return newMainBoard[(-BOARD_HEIGHT):], len(clearedRowIdx)
