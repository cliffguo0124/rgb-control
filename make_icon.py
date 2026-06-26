"""
make_icon.py
--------------
產生 App 圖示 rgb_icon.ico：
深色圓角底 + 紅綠藍三圓疊加（加色混合，中間融合成白光），很有 RGB 的感覺。

執行：
    python make_icon.py
會在同資料夾產生 rgb_icon.ico 和 rgb_icon.png（預覽用）。
"""

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from PIL import Image, ImageDraw, ImageChops

S = 1024  # 先用大尺寸畫，最後縮小，邊緣才平滑


def circle_layer(center, radius, color):
    layer = Image.new("RGB", (S, S), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, y = center
    d.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)
    return layer


def main():
    cx = cy = S // 2
    r = int(S * 0.25)         # 每個圓的半徑
    offset = int(S * 0.135)   # 三個圓彼此錯開的距離

    # 三個圓排成正三角形
    centers = [
        (cx, cy - offset),                                   # 上
        (cx - int(offset * 0.87), cy + int(offset * 0.5)),   # 左下
        (cx + int(offset * 0.87), cy + int(offset * 0.5)),   # 右下
    ]
    colors = [(255, 25, 35), (20, 230, 60), (30, 90, 255)]

    # 加色混合：重疊處會越加越亮，三色交集變白
    circles = Image.new("RGB", (S, S), (0, 0, 0))
    for c, col in zip(centers, colors):
        circles = ImageChops.add(circles, circle_layer(c, r, col))

    # 深色圓角底
    bg = Image.new("RGB", (S, S), (22, 22, 28))

    # lighter：每個像素取「底色」與「圓」較亮的那個，
    # 圓的部分保持鮮豔，圓外則露出深色底
    result = ImageChops.lighter(bg, circles)

    # 整體裁成圓角方形
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=255
    )
    final = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    final.paste(result, (0, 0), mask)

    # 縮到 256 再輸出多尺寸 .ico
    preview = final.resize((256, 256), Image.LANCZOS)
    preview.save("rgb_icon.png")
    preview.save(
        "rgb_icon.ico",
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)],
    )
    print("✅ 已產生 rgb_icon.ico 和 rgb_icon.png")


if __name__ == "__main__":
    main()
