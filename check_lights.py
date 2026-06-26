"""
check_lights.py
-----------------
這支程式會連到 OpenRGB，把它偵測到的「所有燈光裝置」列出來。
第一次玩，先跑這支，確認 OpenRGB 有抓到你的硬體。

用法（在 rgb-control 資料夾裡）：
    python check_lights.py
"""

import sys

# 讓終端機能正常顯示中文與 emoji（Windows 預設編碼吃不下）
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from openrgb import OpenRGBClient


def main():
    # 連到本機正在執行的 OpenRGB（預設位址 127.0.0.1，連接埠 6742）
    try:
        client = OpenRGBClient()
    except Exception as e:
        print("❌ 連不到 OpenRGB。請先確認：")
        print("   1. OpenRGB 已經打開（建議用『以系統管理員身分執行』）")
        print("   2. OpenRGB 裡的 SDK Server 已啟動")
        print(f"   （技術錯誤訊息：{e}）")
        return

    devices = client.devices
    print(f"✅ 連線成功！OpenRGB 偵測到 {len(devices)} 個燈光裝置：\n")

    for i, device in enumerate(devices):
        print(f"[{i}] {device.name}")
        print(f"     類型：{device.type.name}")
        print(f"     LED 數量：{len(device.leds)}")
        print()


if __name__ == "__main__":
    main()
