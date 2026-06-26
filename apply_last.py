"""
apply_last.py
---------------
不開視窗，直接把「上次存的顏色」套用到燈上。
這支是給「開機自動執行」用的。

因為開機時 OpenRGB 可能還沒完全啟動，這裡會重試最多約 60 秒，
等 OpenRGB 的 SDK Server 上線後再套用。

用法：
    python apply_last.py
"""

import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from openrgb import OpenRGBClient
from openrgb.utils import RGBColor

import storage

ZONE_SIZES = {
    2: 40,    # Aura Addressable 2：風扇 + CPU 水冷頭
    3: 100,   # Aura Addressable 3：冷排
}

RETRY_SECONDS = 60   # 最多等多久（開機時 OpenRGB 可能還沒起來）
RETRY_INTERVAL = 3   # 每隔幾秒重試一次


def connect_with_retry():
    """重試連線，直到 OpenRGB 上線或超時。"""
    deadline = time.time() + RETRY_SECONDS
    while time.time() < deadline:
        try:
            return OpenRGBClient()
        except Exception:
            time.sleep(RETRY_INTERVAL)
    return None


def main():
    rgb, brightness = storage.load()
    factor = brightness / 100
    r, g, b = (int(c * factor) for c in rgb)

    client = connect_with_retry()
    if client is None:
        print("❌ 等不到 OpenRGB，放棄套用。")
        return

    color = RGBColor(r, g, b)
    for device in client.devices:
        for zone_index, size in ZONE_SIZES.items():
            if zone_index < len(device.zones) and len(device.zones[zone_index].leds) != size:
                device.zones[zone_index].resize(size)
        device.set_color(color)

    print(f"✅ 已套用上次的顏色 RGB({r}, {g}, {b})")


if __name__ == "__main__":
    main()
