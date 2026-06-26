"""
resize_zone.py
----------------
調整某個可定址燈頭的 LED 數量，並點亮一個顏色測試。
用來解決「燈條/冷排只亮前面一段」的問題：把數量調到跟實際 LED 一樣多即可。

用法：
    python resize_zone.py <燈區編號> <LED數量> [顏色]

例如：
    python resize_zone.py 3 30 blue   # 把燈區3 調成 30 顆，點藍色
    python resize_zone.py 3 24 blue
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from openrgb import OpenRGBClient
from openrgb.utils import RGBColor

COLORS = {
    "red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255),
    "yellow": (255, 255, 0), "cyan": (0, 255, 255), "purple": (160, 0, 255),
    "pink": (255, 0, 128), "orange": (255, 80, 0), "white": (255, 255, 255),
}


def main():
    if len(sys.argv) < 3:
        print("用法：python resize_zone.py <燈區編號> <LED數量> [顏色]")
        print("例如：python resize_zone.py 3 30 blue")
        return

    zone_index = int(sys.argv[1])
    count = int(sys.argv[2])
    color_name = sys.argv[3].lower() if len(sys.argv) > 3 else "blue"
    r, g, b = COLORS.get(color_name, (0, 0, 255))

    client = OpenRGBClient()
    device = client.devices[0]
    zone = device.zones[zone_index]

    old = len(zone.leds)
    zone.resize(count)
    zone.set_color(RGBColor(r, g, b))
    print(f"✅ {zone.name}：{old} 顆 → {count} 顆，已點亮 {color_name}")
    print("   看一下燈條是不是整條都亮了；還有沒亮的就把數量再調大。")


if __name__ == "__main__":
    main()
