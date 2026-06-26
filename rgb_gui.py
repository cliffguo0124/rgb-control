"""
rgb_gui.py
------------
一個現代深色質感的視窗，點顏色就能控制你電腦的 RGB 燈。
用 CustomTkinter 做的（pip install customtkinter）。

特色：
  - 圓角彩色按鈕
  - 上方即時顏色預覽
  - 亮度滑桿（調整整體亮度）
  - 自訂顏色調色盤、關燈

啟動方式：
    python rgb_gui.py

（記得 OpenRGB 要開著、SDK Server 有啟動）
"""

import os

import customtkinter as ctk
from tkinter import colorchooser

from openrgb import OpenRGBClient
from openrgb.utils import RGBColor

import storage

ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rgb_icon.ico")

# === 我的機器設定：每個燈頭實際的 LED 數量 ===
ZONE_SIZES = {
    2: 40,    # Aura Addressable 2：風扇 + CPU 水冷頭
    3: 100,   # Aura Addressable 3：冷排
}

# 精選色盤：顯示名稱 + 十六進位色碼
PALETTE = [
    ("紅", "#FF3B30"),
    ("橘", "#FF9500"),
    ("黃", "#FFD60A"),
    ("綠", "#34C759"),
    ("青", "#00C7BE"),
    ("藍", "#0A84FF"),
    ("靛", "#5E5CE6"),
    ("紫", "#BF5AF2"),
    ("粉", "#FF2D55"),
    ("白", "#FFFFFF"),
]

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


class RGBApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.client = None
        # 讀回上次存的顏色、亮度、關燈前的顏色（第一次跑就用預設值）
        self.base_rgb, self.brightness, self.last_on = storage.load()
        self.is_off = (self.base_rgb == (0, 0, 0))  # 目前是不是關燈狀態

        self.title("RGB 燈控")
        self.geometry("420x620")
        self.resizable(False, False)
        self.configure(fg_color="#0d0d0f")
        try:
            self.iconbitmap(ICON_PATH)
        except Exception:
            pass

        # ---- 標題 ----
        ctk.CTkLabel(
            self, text="🌈  RGB 燈控",
            font=ctk.CTkFont("Microsoft JhengHei", 24, "bold"),
        ).pack(pady=(22, 4))
        ctk.CTkLabel(
            self, text="點一個顏色，整台機器一起變",
            font=ctk.CTkFont("Microsoft JhengHei", 12),
            text_color="#8a8a90",
        ).pack(pady=(0, 14))

        # ---- 即時顏色預覽 ----
        self.preview = ctk.CTkFrame(
            self, height=90, corner_radius=18,
            fg_color=rgb_to_hex(*self.base_rgb),
        )
        self.preview.pack(fill="x", padx=24, pady=(0, 6))
        self.preview.pack_propagate(False)
        self.preview_label = ctk.CTkLabel(
            self.preview, text="", font=ctk.CTkFont("Consolas", 13, "bold"),
        )
        self.preview_label.pack(expand=True)

        # ---- 顏色按鈕（5 欄）----
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(padx=20, pady=(10, 4))
        for i, (name, hex_color) in enumerate(PALETTE):
            text_color = "#000000" if name == "白" else "#ffffff"
            btn = ctk.CTkButton(
                grid, text=name, width=62, height=58, corner_radius=16,
                fg_color=hex_color, hover_color=hex_color, text_color=text_color,
                font=ctk.CTkFont("Microsoft JhengHei", 15, "bold"),
                command=lambda h=hex_color: self.choose(hex_to_rgb(h)),
            )
            btn.grid(row=i // 5, column=i % 5, padx=6, pady=6)

        # ---- 亮度滑桿 ----
        bright_row = ctk.CTkFrame(self, fg_color="transparent")
        bright_row.pack(fill="x", padx=24, pady=(14, 4))
        ctk.CTkLabel(
            bright_row, text="💡 亮度",
            font=ctk.CTkFont("Microsoft JhengHei", 13),
        ).pack(side="left")
        self.bright_value = ctk.CTkLabel(
            bright_row, text=f"{self.brightness}%",
            font=ctk.CTkFont("Consolas", 13),
            text_color="#8a8a90",
        )
        self.bright_value.pack(side="right")
        self.slider = ctk.CTkSlider(
            self, from_=0, to=100, number_of_steps=100,
            command=self.on_brightness,
        )
        self.slider.set(self.brightness)
        self.slider.pack(fill="x", padx=24, pady=(0, 14))

        # ---- 自訂顏色 / 關燈 ----
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=24, pady=(0, 10))
        ctk.CTkButton(
            actions, text="🎨  自訂顏色", height=44, corner_radius=14,
            fg_color="#2b2b30", hover_color="#3a3a42",
            font=ctk.CTkFont("Microsoft JhengHei", 14),
            command=self.pick_color,
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))
        self.power_btn = ctk.CTkButton(
            actions, text="⏻  關燈", width=110, height=44, corner_radius=14,
            fg_color="#2b2b30", hover_color="#5a2b2b",
            font=ctk.CTkFont("Microsoft JhengHei", 14),
            command=self.toggle_power,
        )
        self.power_btn.pack(side="right")
        self.update_power_button()  # 依照目前狀態顯示「關燈」或「開燈」

        # ---- 狀態列 ----
        self.status = ctk.CTkLabel(
            self, text="連線中…",
            font=ctk.CTkFont("Microsoft JhengHei", 11),
            text_color="#8a8a90",
        )
        self.status.pack(pady=(4, 12))

        self.connect()
        self.refresh_preview()
        self.apply()  # 開啟時自動套用上次存的顏色
        self.health_check()  # 啟動背景自動重連檢查

    # ---------- OpenRGB ----------
    def connect(self):
        try:
            self.client = OpenRGBClient()
            n = len(self.client.devices)
            self.set_status(f"● 已連線　偵測到 {n} 個裝置", "#34C759")
        except Exception:
            self.client = None
            self.set_status("● 等待 OpenRGB…（上線後會自動連線）", "#FFD60A")

    def health_check(self):
        """每 2 秒檢查一次：沒連上就嘗試重連，連上後自動套用上次顏色。"""
        if self.client is None:
            try:
                self.client = OpenRGBClient()
                n = len(self.client.devices)
                self.set_status(f"● 已連線　偵測到 {n} 個裝置", "#34C759")
                self.apply()  # 一連上就把上次的顏色套回去
            except Exception:
                self.client = None  # 還沒好，下次再試
        self.after(2000, self.health_check)  # 2 秒後再檢查一次

    def ensure_zone_sizes(self, device):
        for zone_index, size in ZONE_SIZES.items():
            if zone_index < len(device.zones):
                zone = device.zones[zone_index]
                if len(zone.leds) != size:
                    zone.resize(size)

    def apply(self):
        """把（目前顏色 × 亮度）送到燈上。"""
        r, g, b = self.current_rgb()
        if self.client is None:
            self.connect()
            if self.client is None:
                return
        try:
            color = RGBColor(r, g, b)
            for device in self.client.devices:
                self.ensure_zone_sizes(device)
                device.set_color(color)
            self.set_status(f"● 已套用　RGB({r}, {g}, {b})", "#34C759")
        except Exception:
            self.set_status("● 送出失敗，重新連線中…", "#FFD60A")
            self.connect()

    # ---------- 互動 ----------
    def current_rgb(self):
        factor = self.brightness / 100
        r, g, b = self.base_rgb
        return (int(r * factor), int(g * factor), int(b * factor))

    def choose(self, rgb):
        self.base_rgb = rgb
        if rgb != (0, 0, 0):
            self.last_on = rgb        # 記住這個「亮著」的顏色
            self.is_off = False
        self.update_power_button()
        self.refresh_preview()
        self.apply()
        storage.save(self.base_rgb, self.brightness, self.last_on)

    def on_brightness(self, value):
        self.brightness = int(value)
        self.bright_value.configure(text=f"{self.brightness}%")
        self.refresh_preview()
        self.apply()
        storage.save(self.base_rgb, self.brightness, self.last_on)

    def toggle_power(self):
        """開關切換：關燈會先記住顏色，再按一次就恢復。"""
        if self.is_off:
            # 開燈：回到關燈前的顏色
            self.base_rgb = self.last_on
            self.is_off = False
        else:
            # 關燈：先記住現在的顏色，再變黑
            if self.base_rgb != (0, 0, 0):
                self.last_on = self.base_rgb
            self.base_rgb = (0, 0, 0)
            self.is_off = True
        self.update_power_button()
        self.refresh_preview()
        self.apply()
        storage.save(self.base_rgb, self.brightness, self.last_on)

    def update_power_button(self):
        """依照目前是開是關，切換按鈕文字。"""
        self.power_btn.configure(text="💡  開燈" if self.is_off else "⏻  關燈")

    def pick_color(self):
        result = colorchooser.askcolor(title="選一個顏色")
        if result and result[0]:
            self.choose(tuple(int(x) for x in result[0]))

    def refresh_preview(self):
        r, g, b = self.current_rgb()
        self.preview.configure(fg_color=rgb_to_hex(r, g, b))
        # 顏色太亮用黑字，太暗用白字
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        self.preview_label.configure(
            text=rgb_to_hex(r, g, b).upper(),
            text_color="#000000" if luminance > 140 else "#ffffff",
        )

    def set_status(self, text, color="#8a8a90"):
        self.status.configure(text=text, text_color=color)


if __name__ == "__main__":
    RGBApp().mainloop()
