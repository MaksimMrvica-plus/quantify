import pyautogui
import time

# 移动到坐标 (470, 840) 并点击
pyautogui.moveTo(470, 840)
pyautogui.click()
pyautogui.click()
time.sleep(3)
# 移动到坐标 (630, 970) 并点击
pyautogui.moveTo(630, 970)
pyautogui.click()

# 延迟3秒
time.sleep(3)
