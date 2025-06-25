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
- **主控程式 (`main.py`)**：執行辨識流程、穩定狀態判定、傳送控制訊號。
- **訊號傳送 (`signal_sender.py`)**：將辨識結果透過 Serial 傳送至 Arduino。
- **狀態管理 (`state_manager.py`)**：多幀穩定性判斷模組。

---

## 🎯 目標物偵測邏輯

1. **攝影機畫面擷取**：主程式持續從攝影機取得即時影像。
2. **HSV 色彩空間轉換**：將 BGR 影像轉換為 HSV，方便進行顏色遮罩。
3. **遮罩與輪廓偵測**：根據 HSV 範圍產生遮罩，並尋找所有輪廓。
4. **多邊形近似與形狀判斷**：對每個輪廓進行多邊形近似，根據頂點數、面積、長寬比判斷形狀（三角形、正方形、六邊形）。
5. **比對動作對應表**：根據顏色與形狀組合查詢 `action_map`，取得對應 Arduino 指令。
6. **多幀穩定性判斷**：利用 `StateManager`，只有當辨識結果穩定出現多幀才會觸發指令傳送，避免閃爍誤判。
7. **畫面即時標註**：於畫面上即時標註偵測到的形狀、面積與對應代碼，並顯示遮罩畫面。
8. **指令傳送**：穩定辨識後，將對應代碼透過 Serial 傳送至 Arduino 執行動作。

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
Platform_Arduino_OpenCV/
├── Arduino2ARM/
│   ├── arduino/                    # Arduino 端程式碼資料夾
│   │   └── arduino.ino             # Arduino 控制端程式碼
│   └── python/                     # Python 端測試程式資料夾
│       ├── serial_basic.py         # Python 端：基本序列埠傳送程式
│       └── camera_HSV.py           # Python 端：基本形狀辨識程式
├── OpenCV2Arduino/
│   ├── __init__.py
│   ├── app_ui.py                   # UI 類別（主程式用）
│   ├── color_config.json           # HSV 範圍設定檔，供辨識與調整共用
│   ├── signal_sender.py            # 傳送對應代碼至 Arduino
│   ├── state_manager.py            # 多幀穩定性判斷模組
├── BRG_Bar.py                      # HSV 參數儲存工具
├── main.py                         # 啟動辨識流程的主程式
└── README.md
```
- **Arduino2ARM/arduino/**：Arduino 端程式碼。
- **Arduino2ARM/python/**：Python 端測試與通訊程式碼。
- **main.py**：主辨識流程，包含影像處理、形狀判斷、指令傳送與 UI。
- **OpenCV2Arduino/**：模組化各功能（UI、Serial 傳送、狀態管理、HSV 設定）。

---

## 👨‍💻 作者

本專案原始作者為 [ray-uncoding](https://github.com/ray-uncoding)，
現有程式碼已根據本次需求進行整合與簡化（如主程式結構、偵測邏輯等），
部分內容與原始版本有所不同，請依本說明文件與程式碼為主
