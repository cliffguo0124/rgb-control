"""
inspect_zones.py
------------------
把每個裝置底下的「燈區 (zone)」細節列出來，
特別是可定址 (ARGB) 燈區目前設定幾顆 LED、最多能設幾顆。
用來診斷「燈條/冷排只亮一部分」的問題。

用法：
    python inspect_zones.py
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from openrgb import OpenRGBClient


def main():
    client = OpenRGBClient()
    for d_idx, device in enumerate(client.devices):
        print(f"[{d_idx}] {device.name}（共 {len(device.leds)} 顆 LED）")
        for z_idx, zone in enumerate(device.zones):
            print(f"    燈區[{z_idx}] {zone.name}：目前 {len(zone.leds)} 顆 LED")
            # 把這個 zone 物件實際擁有的欄位全部印出來，方便診斷
            for key, val in vars(zone).items():
                if key in ("leds", "colors", "device_id"):
                    continue
                print(f"        - {key} = {val}")
        print()


if __name__ == "__main__":
    main()
