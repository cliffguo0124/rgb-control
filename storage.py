"""
storage.py
------------
負責「記住上次的顏色與亮度」：存到一個 JSON 檔，下次讀回來。
GUI 和開機自動套用的程式都會用到這裡的函式。
"""

import json
import os

# 設定檔放在這支程式同一個資料夾，檔名 last_color.json
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_color.json")

# 讀不到檔時的預設值
DEFAULT = {"rgb": [10, 132, 255], "brightness": 100}


def save(rgb, brightness):
    """把目前的顏色 (r,g,b) 和亮度存起來。"""
    data = {"rgb": list(rgb), "brightness": int(brightness)}
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # 存檔失敗不該讓程式當掉


def load():
    """讀回上次存的顏色與亮度，讀不到就用預設值。回傳 (rgb_tuple, brightness)。"""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        rgb = tuple(int(x) for x in data["rgb"])
        brightness = int(data["brightness"])
        return rgb, brightness
    except Exception:
        return tuple(DEFAULT["rgb"]), DEFAULT["brightness"]
