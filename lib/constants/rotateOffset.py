# 回転入れの際のオフセットの優先順位を定める

from lib.constants.direction import DIRECTION
from lib.constants.move import MOVE

OFFSETS_I = {
    DIRECTION.N : {
        MOVE.L_ROT : [
            (0,0),
            (-1,0),
            (2,0),
            (-1,-2),
            (2,1),
        ],
        MOVE.R_ROT : [
            (0,0),
            (-2,0),
            (1,0),
            (-2,1),
            (1,-2),
        ]
    },

    DIRECTION.E : {
        MOVE.L_ROT : [
            (0,0),
            (2,0),
            (-1,0),
            (2,-1),
            (-1,2),
        ],
        MOVE.R_ROT : [
            (0,0),
            (-1,0),
            (2,0),
            (-1,-2),
            (2,1),
        ]
    },

    DIRECTION.S : {
        MOVE.L_ROT : [
            (0,0),
            (1,0),
            (-2,0),
            (1,2),
            (-2,-1),
        ],
        MOVE.R_ROT : [
            (0,0),
            (2,0),
            (-1,0),
            (2,-1),
            (-1,2),
        ]
    },

    DIRECTION.W : {
        MOVE.L_ROT : [
            (0,0),
            (1,0),
            (-2,0),
            (-2,1),
            (1,-2),
        ],
        MOVE.R_ROT : [
            (0,0),
            (-2,0),
            (1,0),
            (1,2),
            (-2,-1),
        ]
    },   
}

OFFSETS_EXCEPT_I = {
    DIRECTION.N : {
        MOVE.L_ROT : [
            (0,0),
            (1,0),
            (1,-1),
            (0,2),
            (1,2),
        ],
        MOVE.R_ROT : [
            (0,0),
            (-1,0),
            (-1,-1),
            (0,2),
            (-1,2),
        ]
    },

    DIRECTION.E : {
        MOVE.L_ROT : [
            (0,0),
            (1,0),
            (1,1),
            (0,-2),
            (1,-2),
        ],
        MOVE.R_ROT : [
            (0,0),
            (1,0),
            (1,1),
            (0,-2),
            (1,-2),
        ]
    },

    DIRECTION.S : {
        MOVE.L_ROT : [
            (0,0),
            (-1,0),
            (-1,-1),
            (0,2),
            (-1,2),
        ],
        MOVE.R_ROT : [
            (0,0),
            (1,0),
            (1,-1),
            (0,2),
            (1,2),
        ]
    },

    DIRECTION.W : {
        MOVE.L_ROT : [
            (0,0),
            (-1,0),
            (-1,1),
            (0,-2),
            (-1,-2),
        ],
        MOVE.R_ROT : [
            (0,0),
            (-1,0),
            (-1,1),
            (0,-2),
            (-1,-2),
        ]
    },    
}