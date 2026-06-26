"""
set_color.py
--------------
把你所有的燈一次變成指定顏色。

會自動先把每個燈頭的 LED 數量設成正確值（見下方 ZONE_SIZES），
再上色，所以就算 OpenRGB 重開過也不怕，永遠一鍵全亮。

用法（在 rgb-control 資料夾裡）：
    python set_color.py red        # 紅
    python set_color.py green      # 綠
    python set_color.py blue       # 藍
    python set_color.py purple     # 紫
    python set_color.py white      # 白
    python set_color.py off        # 關燈（變黑）
    python set_color.py 255 128 0  # 也可以直接給 R G B 數字（0~255）
"""

import sys

# 讓終端機能正常顯示中文與 emoji（Windows 預設編碼吃不下）
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from openrgb import OpenRGBClient
from openrgb.utils import RGBColor

# === 我的機器設定：每個燈頭實際的 LED 數量 ===
# 這是我們一顆一顆測出來的，照這個設就會全亮。
# 燈區編號 : LED 數量
ZONE_SIZES = {
    2: 40,    # Aura Addressable 2：風扇 + CPU 水冷頭
    3: 100,   # Aura Addressable 3：冷排
}

# 預先準備好的顏色名稱 → (R, G, B)
COLORS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "purple": (160, 0, 255),
    "pink": (255, 0, 128),
    "orange": (255, 80, 0),
    "white": (255, 255, 255),
    "off": (0, 0, 0),
}


def parse_color(args):
    """把使用者輸入的參數轉成一個 RGBColor。看不懂就回傳 None。"""
    if len(args) == 1 and args[0].lower() in COLORS:
        r, g, b = COLORS[args[0].lower()]
        return RGBColor(r, g, b)
    if len(args) == 3:
        try:
            r, g, b = (max(0, min(255, int(x))) for x in args)
            return RGBColor(r, g, b)
        except ValueError:
            return None
    return None


def ensure_zone_sizes(device):
    """把每個燈頭的 LED 數量調成正確值（只有在跟現在不同時才調，避免閃爍）。"""
    for zone_index, size in ZONE_SIZES.items():
        if zone_index < len(device.zones):
            zone = device.zones[zone_index]
            if len(zone.leds) != size:
                zone.resize(size)


def main():
    args = sys.argv[1:]  # 拿掉程式名稱，留下使用者打的參數
    color = parse_color(args)

    if color is None:
        print("⚠️  用法：")
        print("    python set_color.py <顏色名稱>     例如 red / blue / off")
        print("    python set_color.py <R> <G> <B>    例如 255 128 0")
        print(f"\n可用的顏色名稱：{', '.join(COLORS.keys())}")
        return

    try:
        client = OpenRGBClient()
    except Exception as e:
        print("❌ 連不到 OpenRGB。請先打開 OpenRGB 並啟動 SDK Server。")
        print(f"   （技術錯誤訊息：{e}）")
        return

    devices = client.devices
    if not devices:
        print("⚠️  OpenRGB 沒偵測到任何裝置。可能要用『以系統管理員身分執行』再試一次。")
        return

    # 先把 LED 數量調對，再上色
    for device in devices:
        ensure_zone_sizes(device)
        device.set_color(color)

    print(f"✅ 已把所有燈變成 RGB({color.red}, {color.green}, {color.blue}) 🌈")


if __name__ == "__main__":
    main()
