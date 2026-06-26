"""
identify_zones.py
-------------------
把主機板上 3 個可定址 (Addressable) 燈頭各設成不同顏色，
方便你用肉眼判斷「冷排 / 燈條」實際接在哪一個燈頭上。

    Addressable 1 -> 紅
    Addressable 2 -> 綠
    Addressable 3 -> 藍
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from openrgb import OpenRGBClient
from openrgb.utils import RGBColor

MARKERS = [
    ("紅", RGBColor(255, 0, 0)),
    ("綠", RGBColor(0, 255, 0)),
    ("藍", RGBColor(0, 0, 255)),
]


def main():
    client = OpenRGBClient()
    device = client.devices[0]  # 主機板

    addressable = [z for z in device.zones if "Addressable" in z.name]
    for zone, (name, color) in zip(addressable, MARKERS):
        zone.set_color(color)
        print(f"  {zone.name} → {name}（{len(zone.leds)} 顆 LED）")

    print("\n看一下你的冷排現在是什麼顏色，告訴我，就知道它接在哪個燈頭了。")


if __name__ == "__main__":
    main()
