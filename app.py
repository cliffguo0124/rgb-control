"""
app.py — LUMEN RGB 燈控（pywebview 版）
-----------------------------------------
用這個取代原本的 rgb_gui.py：
  - 介面（玻璃毛玻璃、呼吸光暈、動畫）由 index.html 負責
  - 控燈邏輯（OpenRGB）由本檔的 Api 類別負責
  - JS 透過 window.pywebview.api.xxx() 呼叫下面的方法

啟動：
  pip install -r requirements.txt
  python app.py
（記得先開好 OpenRGB，並啟用其 SDK Server）
"""

import os
import time
import json
import threading

import webview
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor

import storage

HERE = os.path.dirname(os.path.abspath(__file__))

# === 我的機器設定：每個燈頭實際的 LED 數量 ===
# 換別台電腦的話，用原專案的 inspect_zones.py / resize_zone.py 重新量一次
ZONE_SIZES = {
    2: 40,   # Aura Addressable 2：風扇 + CPU 水冷頭
    3: 100,  # Aura Addressable 3：冷排
}


class Api:
    """所有 self.xxx() 方法都會自動暴露給 JS：window.pywebview.api.xxx()"""

    def __init__(self):
        self.client = None
        self._window = None
        self._maximized = False
        # 讀回上次的顏色、亮度、關燈前的顏色
        self.base, self.brightness, self.last_on = storage.load()
        self.is_off = (self.base == (0, 0, 0))
        self._connect()

    def set_window(self, window):
        self._window = window

    # ---------- OpenRGB ----------
    def _connect(self):
        try:
            self.client = OpenRGBClient()
            return True
        except Exception:
            self.client = None
            return False

    def _current_rgb(self):
        if self.is_off:
            return (0, 0, 0)
        f = self.brightness / 100
        r, g, b = self.base
        return (int(r * f), int(g * f), int(b * f))

    def _ensure_zone_sizes(self, device):
        for zone_index, size in ZONE_SIZES.items():
            if zone_index < len(device.zones):
                zone = device.zones[zone_index]
                if len(zone.leds) != size:
                    zone.resize(size)

    def _apply(self):
        """把（目前顏色 × 亮度）送到燈上。"""
        if self.client is None and not self._connect():
            return False
        try:
            r, g, b = self._current_rgb()
            color = RGBColor(r, g, b)
            for device in self.client.devices:
                self._ensure_zone_sizes(device)
                device.set_color(color)
            return True
        except Exception:
            self.client = None
            return False

    # ---------- 給 JS 呼叫 ----------
    def get_state(self):
        return {
            "r": self.base[0], "g": self.base[1], "b": self.base[2],
            "brightness": self.brightness,
            "is_off": self.is_off,
            "connected": self.client is not None,
            "device_count": len(self.client.devices) if self.client else 0,
        }

    def set_color(self, r, g, b):
        self.base = (int(r), int(g), int(b))
        if self.base != (0, 0, 0):
            self.last_on = self.base
        self.is_off = False
        ok = self._apply()
        storage.save(self.base, self.brightness, self.last_on)
        return ok

    def set_brightness(self, value):
        self.brightness = max(0, min(100, int(value)))
        self.is_off = False
        ok = self._apply()
        storage.save(self.base, self.brightness, self.last_on)
        return ok

    def set_power(self, on):
        """on=True 開燈（回到上次顏色），on=False 關燈。"""
        if on:
            if self.is_off:
                self.base = self.last_on
            self.is_off = False
        else:
            if self.base != (0, 0, 0):
                self.last_on = self.base
            self.is_off = True
        ok = self._apply()
        storage.save(self.base, self.brightness, self.last_on)
        return ok

    # ---------- 視窗控制（無邊框視窗用）----------
    def minimize(self):
        try:
            self._window.minimize()
        except Exception:
            pass

    def toggle_max(self):
        try:
            if self._maximized:
                self._window.restore()
            else:
                self._window.maximize()
            self._maximized = not self._maximized
        except Exception:
            pass

    def close(self):
        try:
            self._window.destroy()
        except Exception:
            pass

    def resize_edge(self, corner, dx, dy):
        """給四個角落的縮放把手呼叫。corner 是 nw/ne/sw/se，dx/dy 是這次滑鼠位移。"""
        try:
            import ctypes
            from ctypes import wintypes
            hwnd = ctypes.windll.user32.FindWindowW(None, "LUMEN · RGB 燈控")
            if not hwnd:
                return
            rect = wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
            left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
            dx, dy = int(dx), int(dy)
            MIN_W, MIN_H = 860, 640
            if "e" in corner:
                right += dx
            if "w" in corner:
                left += dx
            if "s" in corner:
                bottom += dy
            if "n" in corner:
                top += dy
            # 限制最小尺寸
            if right - left < MIN_W:
                if "w" in corner:
                    left = right - MIN_W
                else:
                    right = left + MIN_W
            if bottom - top < MIN_H:
                if "n" in corner:
                    top = bottom - MIN_H
                else:
                    bottom = top + MIN_H
            ctypes.windll.user32.MoveWindow(
                hwnd, left, top, right - left, bottom - top, True
            )
        except Exception:
            pass


def health_loop(api):
    """每 2 秒：沒連上就重連，連上就把上次顏色套回去；並把連線狀態推給介面。"""
    while True:
        time.sleep(2)
        if api.client is None:
            if api._connect():
                api._apply()
        try:
            st = json.dumps(api.get_state())
            if api._window:
                api._window.evaluate_js(
                    f"window.lumenSetStatus && window.lumenSetStatus({st})"
                )
        except Exception:
            pass


def main():
    api = Api()
    window = webview.create_window(
        "LUMEN · RGB 燈控",
        os.path.join(HERE, "index.html"),
        js_api=api,
        width=964,
        height=720,
        min_size=(860, 640),       # 最小尺寸，避免縮太小擠壞版面
        resizable=True,            # 允許調整視窗大小
        frameless=True,            # 無邊框 → 用 HTML 內的 Windows 視窗鈕
        easy_drag=False,           # 拖曳只限 .pywebview-drag-region
        background_color="#040406",
    )
    api.set_window(window)

    threading.Thread(target=health_loop, args=(api,), daemon=True).start()

    # 開窗時把上次的顏色先套上去
    def on_loaded():
        api._apply()
    window.events.loaded += on_loaded

    webview.start()


if __name__ == "__main__":
    main()
