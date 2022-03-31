from lib.classes import *
from lib.warning import *


class MinoOrder():
    def __init__(self):
        self.SZ = None # S comes earlier than Z
        self.ST = None # S comes earlier than T
        self.ZT = None # Z comes earlier than T
        self.SZ_T = None # T comes later than S,Z

        self.OT = None # O comes earlier than T
        self.LJ = None # L comes earlier than J
        self.OL = None # O comes earlier than L
        self.OJ = None # O comes earlier than J
        self.O_LJ = None # O comes earlier than L,J
        
        self.IT = None # I comes earlier than T
        self.IO = None # I comes earlier than O
        self.IL = None # I comes earlier than L
        self.IJ = None # I comes earlier than J
        self.I_OLJ = None # I comes earlier than O,L,J
        self.OLJ_I = None # I comes later than O,L,J


# MinoOrder を与えられたミノ集合に対して調べる
# コードの効率が悪そうだが，{m:i for i,m in enumerate(minos)} のような辞書を用意して登場順の値で比較する方法では m が辞書中に存在しない時の例外処理が必要なので結局面倒さは大差ない。
def CheckMinoOrder(currentMino:MINO, followingMinos:List[MINO]) -> MinoOrder:
    minoOrder = MinoOrder()

    if currentMino is MINO.S:
        minoOrder.SZ = True
        minoOrder.ST = True
    elif currentMino is MINO.Z:
        minoOrder.SZ = False
        minoOrder.ZT = True
    elif currentMino is MINO.T:
        minoOrder.ST = False
        minoOrder.ZT = False
        minoOrder.OT = False
        minoOrder.IT = False
    elif currentMino is MINO.O:
        minoOrder.OT = True
        minoOrder.OL = True
        minoOrder.OJ = True
        minoOrder.IO = False
    elif currentMino is MINO.L:
        minoOrder.LJ = True
        minoOrder.OL = False
        minoOrder.IL = False        
    elif currentMino is MINO.J:
        minoOrder.LJ = False
        minoOrder.OJ = False
        minoOrder.IJ = False
    elif currentMino is MINO.I:
        minoOrder.IT = True
        minoOrder.IO = True
        minoOrder.IL = True
        minoOrder.IJ = True
    
    for nextMino in followingMinos:

        if minoOrder.SZ is None:
            if nextMino is MINO.S:
                minoOrder.SZ = True
            elif nextMino is MINO.Z:
                minoOrder.SZ = False

        if minoOrder.ST is None:
            if nextMino is MINO.S:
                minoOrder.ST = True
            elif nextMino is MINO.T:
                minoOrder.ST = False

        if minoOrder.ZT is None:
            if nextMino is MINO.Z:
                minoOrder.ZT = True
            elif nextMino is MINO.T:
                minoOrder.ZT = False

        if minoOrder.OT is None:
            if nextMino is MINO.O:
                minoOrder.OT = True
            elif nextMino is MINO.T:
                minoOrder.OT = False

        if minoOrder.LJ is None:
            if nextMino is MINO.L:
                minoOrder.LJ = True
            elif nextMino is MINO.J:
                minoOrder.LJ = False

        if minoOrder.OL is None:
            if nextMino is MINO.O:
                minoOrder.OL = True
            elif nextMino is MINO.L:
                minoOrder.OL = False

        if minoOrder.OJ is None:
            if nextMino is MINO.O:
                minoOrder.OJ = True
            elif nextMino is MINO.J:
                minoOrder.OJ = False

        if minoOrder.IT is None:
            if nextMino is MINO.I:
                minoOrder.IT = True
            elif nextMino is MINO.T:
                minoOrder.IT = False

        if minoOrder.IO is None:
            if nextMino is MINO.I:
                minoOrder.IO = True
            elif nextMino is MINO.O:
                minoOrder.IO = False

        if minoOrder.IL is None:
            if nextMino is MINO.I:
                minoOrder.IL = True
            elif nextMino is MINO.L:
                minoOrder.IL = False

        if minoOrder.IJ is None:
            if nextMino is MINO.I:
                minoOrder.IJ = True
            elif nextMino is MINO.J:
                minoOrder.IJ = False

    minoOrder.SZ_T = minoOrder.ST and minoOrder.ZT
    minoOrder.O_LJ = minoOrder.OL and minoOrder.OJ
    minoOrder.I_OLJ = minoOrder.IO and minoOrder.IL and minoOrder.IJ
    minoOrder.OLJ_I = not (minoOrder.IO or minoOrder.IL or minoOrder.IJ)

    return minoOrder