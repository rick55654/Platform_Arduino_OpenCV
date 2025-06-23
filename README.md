# Platform_Arduino_OpenCV

本專案為一套整合影像辨識與 Arduino 控制的機器手臂控制系統，
可針對紅色與藍色的「三角形」、「正方形」、「六邊形」目標物進行辨識，並傳送指令給機器手臂執行動作。

---

## 📦 安裝必要模組

請先安裝以下必要模組（建議使用 Python 3.8+）

> 本專案需用到 opencv-python、numpy、pyserial，請務必先安裝！

```bash
pip install opencv-python pyserial numpy
```

---

## 🔧 系統架構

- **OpenCV 模組**：負責即時攝影機影像擷取、HSV 遮罩與輪廓辨識。
- **色彩域值調整工具 (`BRG_Bar.py`)**：可視化設定 HSV 門檻並儲存至 `color_config.json`。
- **主控程式 (`main.py`)**：執行辨識流程、穩定狀態判定、傳送控制訊號。
- **訊號傳送 (`signal_sender.py`)**：將辨識結果透過 Serial 傳送至 Arduino。
- **狀態管理 (`state_manager.py`)**：多幀穩定性判斷模組。

---

## 🎯 目標物偵測邏輯

1. 從攝影機畫面中擷取影像
2. 轉換至 HSV 色彩空間
3. 根據 `color_config.json` 中定義的 HSV 門檻產生遮罩
4. 偵測輪廓並簡化多邊形
5. 直接根據多邊形頂點數與面積、長寬比判斷形狀（三角形、正方形、六邊形）
6. 根據顏色與形狀比對 `action_map` 對應動作
7. 傳送對應代碼給 Arduino

---

## 🎮 使用方法

### 1. 執行 `BRG_Bar.py` 進行 HSV 校正

```bash
python BRG_Bar.py
```

操作方式：

- 使用滑桿調整 HSV 直到遮罩畫面正確標出目標物
- **按下 `r` 鍵：切換為「紅色」模式**
- **按下 `b` 鍵：切換為「藍色」模式**
- **按下 `s` 鍵：儲存目前 HSV 範圍至對應顏色的 JSON 檔案中（將覆蓋該顏色舊資料）**
- 可重複調整與存檔，每個顏色皆會獨立儲存其上下限區間

⚠️ **注意：請務必先按 `r` 或 `b` 選擇目標顏色後再儲存，否則會覆蓋錯誤顏色資料！**

### 2. 執行 `main.py` 啟動主系統

```bash
python main.py
```

功能說明：

- 系統持續進行影像分析與物件辨識
- 當辨識結果穩定達成條件（如紅色+三角形）時：
  - 會在畫面上顯示「Detected: `['A']`」這類代碼
  - 並透過 Serial 傳送對應訊號至 Arduino 進行後續控制

---

## 📁 檔案結構簡述

```bash
Platform_Crawler_Arduino_OpenCV/
├── Arduino2ARM/
│   └── arduino_python.ino     # Arduino 控制端程式碼
├── OpenCV2Arduino/
│   ├── __init__.py
│   ├── color_config.json      # HSV 範圍設定檔，供辨識與調整共用
│   ├── signal_sender.py       # 傳送對應代碼至 Arduino
│   ├── state_manager.py       # 多幀穩定性判斷模組
├── BRG_Bar.py                 # HSV 色彩調整工具（含即時滑桿與儲存功能）
├── main.py                    # 啟動辨識流程的主程式（已整合偵測與 UI 功能）
└── README.md
```

---

## 🧠 特殊功能

- 每種顏色與形狀的組合可對應自訂代碼（如 `Red+Triangle -> 'A'`）
- 加入多幀穩定性判定，避免誤判或閃爍
- 使用 JSON 儲存色彩設定

---

## 👨‍💻 作者

本專案原始作者為 [ray-uncoding](https://github.com/ray-uncoding)，
現有程式碼已根據本次需求進行整合與簡化（如主程式結構、偵測邏輯等），
部分內容與原始版本有所不同，請依本說明文件與程式碼為主
