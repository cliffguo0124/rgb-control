"""
storage.py
------------
負責「記住上次的顏色與亮度」：存到一個 JSON 檔，下次讀回來。
GUI 和開機自動套用的程式都會用到這裡的函式。

也會記住「關燈前的顏色」(last_on)，這樣按開燈時才能恢復。
"""

import json
import os

# 設定檔放在這支程式同一個資料夾，檔名 last_color.json
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_color.json")

# 讀不到檔時的預設值
DEFAULT = {"rgb": [10, 132, 255], "brightness": 100, "last_on": [10, 132, 255]}


def save(rgb, brightness, last_on=None):
    """把目前的顏色 (r,g,b)、亮度、以及關燈前的顏色存起來。"""
    data = {"rgb": list(rgb), "brightness": int(brightness)}
    if last_on is not None:
        data["last_on"] = list(last_on)
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # 存檔失敗不該讓程式當掉


def load():
    """讀回上次存的設定，讀不到就用預設值。
    回傳 (rgb, brightness, last_on)。"""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        rgb = tuple(int(x) for x in data["rgb"])
        brightness = int(data["brightness"])
        last_on = data.get("last_on")
        if last_on:
            last_on = tuple(int(x) for x in last_on)
        else:
            # 舊檔案沒存 last_on：若目前不是黑色就用它，否則用預設
            last_on = rgb if rgb != (0, 0, 0) else tuple(DEFAULT["last_on"])
        return rgb, brightness, last_on
    except Exception:
        return tuple(DEFAULT["rgb"]), DEFAULT["brightness"], tuple(DEFAULT["last_on"])
