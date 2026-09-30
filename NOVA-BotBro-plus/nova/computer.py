import math
import subprocess
import time
from datetime import datetime

try:
    import pyautogui
except Exception:  # Allows unit tests to run on non-GUI CI hosts.
    pyautogui = None

from .config import ACTION_DELAY, SCREENSHOT_DIR

# Deliberately excludes command shells and arbitrary interpreters.
ALLOWED_APPS = {
    'mspaint.exe',
    'notepad.exe',
    'calc.exe',
    'explorer.exe',
    'chrome.exe',
    'code.exe',
}

class Computer:
    def __init__(self):
        if pyautogui is None:
            raise RuntimeError('PyAutoGUI requires a graphical desktop session.')
        self.screenshots: list[str] = []

    def screen_size(self):
        return pyautogui.size()

    def launch_app(self, app):
        app = app.lower().strip()
        if app not in ALLOWED_APPS:
            raise ValueError(f'Application is not allowlisted: {app}')
        subprocess.Popen([app], shell=False)
        time.sleep(1)

    def click(self, x, y):
        self._check(x, y); pyautogui.click(x, y); time.sleep(ACTION_DELAY)

    def double_click(self, x, y):
        self._check(x, y); pyautogui.doubleClick(x, y, interval=.12); time.sleep(ACTION_DELAY)

    def move(self, x, y):
        self._check(x, y); pyautogui.moveTo(x, y)

    def drag(self, x1, y1, x2, y2):
        self._check(x1, y1); self._check(x2, y2)
        pyautogui.moveTo(x1, y1); pyautogui.dragTo(x2, y2, duration=.5)

    def type(self, text):
        pyautogui.write(str(text), interval=.008); time.sleep(ACTION_DELAY)

    def press(self, key):
        pyautogui.press(key); time.sleep(ACTION_DELAY)

    def hotkey(self, keys):
        if not isinstance(keys, list) or not keys:
            raise ValueError('hotkey requires a non-empty list')
        pyautogui.hotkey(*keys); time.sleep(ACTION_DELAY)

    def scroll(self, amount):
        pyautogui.scroll(int(amount)); time.sleep(ACTION_DELAY)

    def screenshot(self, label='screen'):
        p = SCREENSHOT_DIR / f'{datetime.now():%Y%m%d_%H%M%S_%f}_{label}.png'
        pyautogui.screenshot(str(p))
        self.screenshots.append(str(p))
        return p

    def draw_lion(self):
        w, h = self.screen_size(); cx, cy = w // 2, h // 2 + 20

        def stroke(points):
            pyautogui.moveTo(*points[0]); pyautogui.mouseDown()
            for p in points[1:]: pyautogui.moveTo(*p, duration=.025)
            pyautogui.mouseUp()

        stroke([(cx + 150 * math.cos(2 * math.pi * i / 80), cy + 150 * math.sin(2 * math.pi * i / 80)) for i in range(81)])
        for i in range(16):
            a = 2 * math.pi * i / 16
            stroke([(cx + 155 * math.cos(a), cy + 155 * math.sin(a)),
                    (cx + 190 * math.cos(a), cy + 190 * math.sin(a))])
        for pts in [
            [(cx-110,cy-105),(cx-155,cy-160),(cx-75,cy-135),(cx-110,cy-105)],
            [(cx+110,cy-105),(cx+155,cy-160),(cx+75,cy-135),(cx+110,cy-105)],
            [(cx-70,cy-25),(cx-35,cy-30)], [(cx+35,cy-30),(cx+70,cy-25)],
            [(cx-20,cy+30),(cx,cy+45),(cx+20,cy+30),(cx,cy+20),(cx-20,cy+30)],
            [(cx,cy+45),(cx,cy+85),(cx-35,cy+100)], [(cx,cy+85),(cx+35,cy+100)]
        ]: stroke(pts)
        time.sleep(.5)

    def _check(self, x, y):
        w, h = self.screen_size()
        if not (0 <= int(x) < w and 0 <= int(y) < h):
            raise ValueError(f'Coordinate outside screen: {x},{y}')
