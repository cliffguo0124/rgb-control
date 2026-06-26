# 🌈 rgb-control

我自己寫的電腦 RGB 燈控程式，用 Python + OpenRGB。
有現代深色 GUI、亮度調整、記憶上次顏色、開機自動套用。

## 功能
- 🎨 圖形介面一鍵變色（紅橘黃綠青藍靛紫粉白）＋ 自訂任意顏色
- 💡 亮度滑桿
- 💾 記住上次的顏色，下次打開自動套用
- 🔌 自動偵測 OpenRGB，斷線會自己重連
- ⚡ 開機自動套用上次的顏色
- 🖼️ 專屬 icon ＋ 桌面捷徑

## 檔案說明
| 檔案 | 作用 |
|------|------|
| `rgb_gui.py` | 主程式：圖形介面 |
| `apply_last.py` | 開機時自動套用上次顏色（不開視窗） |
| `storage.py` | 負責記住 / 讀回上次的顏色 |
| `set_color.py` | 指令版一鍵變色 |
| `check_lights.py` | 列出 OpenRGB 偵測到的裝置 |
| `inspect_zones.py` | 檢視各燈區的 LED 數量 |
| `identify_zones.py` | 各燈頭點不同色，辨識燈條接在哪 |
| `resize_zone.py` | 調整燈頭的 LED 數量 |
| `make_icon.py` | 產生 App 圖示 |

## 需要先準備
1. 安裝 [OpenRGB](https://openrgb.org/) 並啟動它的 SDK Server
2. 安裝 Python 套件：`pip install -r requirements.txt`

## 怎麼用
```bash
# 圖形介面（推薦）
python rgb_gui.py

# 或用指令
python check_lights.py        # 先看抓到哪些燈
python set_color.py red       # 變紅
python set_color.py off       # 關燈
python set_color.py 255 128 0 # 自訂 R G B
```

## 我的機器設定
這個專案是為我的 ASUS TUF GAMING B760M-PLUS 主機板調過的：
- Addressable 2（風扇 + CPU 水冷頭）：40 顆 LED
- Addressable 3（冷排）：100 顆 LED

換別台電腦的話，用 `inspect_zones.py` / `resize_zone.py` 重新測一次數量即可。

## 注意
- 同一時間只能有一個軟體控制 RGB，使用前請關掉 SignalRGB / Razer Synapse 等燈控軟體。
