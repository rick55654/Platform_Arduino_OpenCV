# 攝影機畫面擷取、HSV遮罩拉桿＋圖形辨識
import cv2
import numpy as np

# 建立滑桿視窗
cv2.namedWindow("Sliders")
cv2.resizeWindow("Sliders", 500, 350)

def nothing(x):
    # print("[!] 滑桿值變更hahaha")
    # 滑桿回呼函式，不做任何事
    pass

# 建立 HSV 範圍的滑桿（H: 色相, S: 飽和度, V: 明度）
cv2.createTrackbar("H Low", "Sliders", 0, 179, nothing)
cv2.createTrackbar("H High", "Sliders", 179, 179, nothing)
cv2.createTrackbar("S Low", "Sliders", 0, 255, nothing)
cv2.createTrackbar("S High", "Sliders", 255, 255, nothing)
cv2.createTrackbar("V Low", "Sliders", 0, 255, nothing)
cv2.createTrackbar("V High", "Sliders", 255, 255, nothing)
# 建立最小面積的滑桿（用於過濾雜訊與小圖形）
cv2.createTrackbar("Min Area", "Sliders", 0, 10000, nothing)

# 圖形對應動作
action_map = {
    'Triangle': 'A',
    'Square': 'B',
    'Hexagon': 'C',
}

# 開啟攝影機（預設編號為 0）依情況修改
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("[錯誤] 無法開啟攝影機，請檢查攝影機。")
    exit()

print("[整合模組] 調整 HSV 與面積拉桿，按 q 離開")

while True:
    # 讀取攝影機畫面
    ret, frame = cap.read()
    
    if not ret:
        print("[錯誤] 無法讀取攝影機畫面。")
        break
    
    # 將 BGR 影像轉換為 HSV 色彩空間
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 取得拉桿數值
    h_low = cv2.getTrackbarPos("H Low", "Sliders")
    h_high = cv2.getTrackbarPos("H High", "Sliders")
    s_low = cv2.getTrackbarPos("S Low", "Sliders")
    s_high = cv2.getTrackbarPos("S High", "Sliders")
    v_low = cv2.getTrackbarPos("V Low", "Sliders")
    v_high = cv2.getTrackbarPos("V High", "Sliders")
    min_area = cv2.getTrackbarPos("Min Area", "Sliders")

    # 根據 HSV 滑桿數值產生遮罩（只保留指定顏色範圍）
    lower_np = np.array([h_low, s_low, v_low])
    upper_np = np.array([h_high, s_high, v_high])
    mask = cv2.inRange(hsv, lower_np, upper_np)

    # 將遮罩應用到原始影像，得到過濾後的結果
    filtered = cv2.bitwise_and(frame, frame, mask=mask)

    # 複製原始畫面，用於畫出辨識結果
    result_frame = frame.copy()

    # 找出遮罩中的所有輪廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        # 多邊形近似，取得輪廓的頂點數
        approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
        x, y, w, h = cv2.boundingRect(approx) # 外接矩形
        area = cv2.contourArea(cnt)           # 輪廓面積
        num_vertices = len(approx)            # 多邊形頂點數
        aspect_ratio = w / h if h != 0 else 0 # 長寬比

        shape = None
        # 根據頂點數與面積判斷圖形類型
        if num_vertices == 3 and area >= min_area:
            shape = "Triangle"
        elif num_vertices == 4 and 0.8 < aspect_ratio < 1.2 and area >= min_area:
            shape = "Square"
        elif 5 <= num_vertices <= 6 and area >= min_area:
            shape = "Hexagon"

        if shape:
            label = action_map.get(shape)
            if label:
                # 畫出多邊形輪廓
                cv2.drawContours(result_frame, [approx], -1, (0, 0, 255), 2)
                # 在結果畫面上畫出外框與圖形名稱與對應動作
                # cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(result_frame,
                            f"{shape} ({label})",  # 顯示圖形名稱與對應動作
                            (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (255, 255, 255), 2)

    # --- 合併顯示四個畫面 ---
    # 先將所有畫面調整為相同大小
    h_show, w_show = 320, 480
    show_result = cv2.resize(result_frame, (w_show, h_show))   # 左上：圖形辨識結果
    show_filtered = cv2.resize(filtered, (w_show, h_show))     # 右上：過濾後畫面
    show_camera = cv2.resize(frame, (w_show, h_show))          # 左下：原始畫面
    show_mask = cv2.cvtColor(cv2.resize(mask, (w_show, h_show)), cv2.COLOR_GRAY2BGR) # 右下：遮罩

    # 上下合併
    top = np.hstack((show_result, show_filtered))
    bottom = np.hstack((show_camera, show_mask))
    merged = np.vstack((top, bottom))

    # 顯示合併後的畫面
    cv2.imshow("All-in-One View", merged)

    # 按下 q 鍵離開程式
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("[!] 結束程式")
        break

# 釋放攝影機資源並關閉所有視窗
cap.release()
cv2.destroyAllWindows()