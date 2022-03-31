from lib.constants import *
from lib.classes.directedMino import *

class Board():
    def __init__(
        self,
        mainBoard : List[int] = None,
        currentMino : Union[DirectedMino, None] = None,
        followingMinos : List[MinoInt] = None,
        holdMino : MinoInt = None,
        canHold : bool = True,
        topRowIdx : List[int] = None,
        score : int = 0,
        backToBack : bool = False,
        ren : int = 0,
        minoBagContents : Union[List[MinoInt], None] = None
    ) -> None:
        self.mainBoard = mainBoard if mainBoard is not None else [0x0 for _ in range(BOARD_HEIGHT)]
        self.followingMinos = followingMinos if followingMinos is not None else [MINO.NONE for _ in range(FOLLOWING_MINOS_COUNT)]
        self.currentMino = currentMino
        self.holdMino = holdMino if holdMino is not None else MINO.NONE
        self.canHold = canHold
        self.topRowIdx = topRowIdx if topRowIdx is not None else [BOARD_HEIGHT for _ in range(BOARD_WIDTH)]
        self.score = score
        self.backToBack = backToBack
        self.ren = ren
        self.minoBagContents = minoBagContents
    
    # mainBoardの任意の場所にブロックを足す
    def AddBlockToMainBoard (self, pos:Tuple[int]):
        self.mainBoard[pos[1]] |= 0b1000000000 >> pos[0]
        self.topRowIdx[pos[0]] = min(self.topRowIdx[pos[0]], pos[1])
    
    def DeleteBlockInMainBoard (self, pos:Tuple[int]):
        self.mainBoard[pos[1]] &= 0b1111111111 ^ (0b1000000000 >> pos[0])
        if pos[1] == self.topRowIdx[pos[0]]:
            for rowIdx in range(pos[1], BOARD_HEIGHT):
                if (self.mainBoard[rowIdx] & (0b1000000000 >> pos[0])) > 0:
                    self.topRowIdx[pos[0]] = rowIdx
                    break
            else:
                self.topRowIdx[pos[0]] = BOARD_HEIGHT

    def updateMinoBagContents(self):
        # print("                                                                 ", self.currentMino.mino, self.minoBagContents)
        self.minoBagContents.remove(self.currentMino.mino)
        if len(self.minoBagContents) == 0:
            self.minoBagContents = ReturnFullBag()