from constants.position import WINDOW_X, WINDOW_Y
import pyautogui
import time

def Init():
    # pyautoguiの遅延を0にする
    pyautogui.PAUSE = 0

    # windowをアクティブにする
    pyautogui.click(WINDOW_X + 1, WINDOW_Y + 1)
    time.sleep(0.5)
