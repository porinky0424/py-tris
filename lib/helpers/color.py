from lib.classes import *
from lib.warning import Warn

# 1マス分の与えられたRGBにしたがって、そのマスがなんのミノで埋められているか判別する
def DetermineColor(r,g,b,pos,warn=False):
    for mino in MINO_COLOR:
        minoR, minoG, minoB = MINO_COLOR[mino]
        if (
            minoR[0] <= r <= minoR[1] and
            minoG[0] <= g <= minoG[1] and
            minoB[0] <= b <= minoB[1]
        ):
            return mino
    # どのミノにも対応していない色だった場合はミノがない場所であると判定する
    if warn:
        Warn("                               No mino matched: r = {}, g = {}, b = {}, place = {}".format(r,g,b,pos))
    return MINO.NONE