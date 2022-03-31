from lib.classes import *

def Warn(msg):
    warnings.warn(msg)

def Error(msg):
    print(msg)
    raise Exception