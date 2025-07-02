# Camera capture, HSV mask sliders + shape recognition
import cv2
import numpy as np

cap = cv2.VideoCapture(0) #<<< Modify as needed (0 is usually the built-in camera, 1 is external)

# Create slider window
cv2.namedWindow("Sliders")
cv2.resizeWindow("Sliders", 500, 350)

def nothing(x):
    # Slider callback function, does nothing
    pass

# Create HSV range sliders (H: Hue, S: Saturation, V: Value)
cv2.createTrackbar("H Low", "Sliders", 0, 179, nothing)
cv2.createTrackbar("H High", "Sliders", 179, 179, nothing)
cv2.createTrackbar("S Low", "Sliders", 0, 255, nothing)
cv2.createTrackbar("S High", "Sliders", 255, 255, nothing)
cv2.createTrackbar("V Low", "Sliders", 0, 255, nothing)
cv2.createTrackbar("V High", "Sliders", 255, 255, nothing)
# Create minimum area slider (for filtering noise and small shapes)
cv2.createTrackbar("Min Area", "Sliders", 0, 10000, nothing)

# Shape to action mapping
action_map = {
    'Triangle': 'A',
    'Square': 'B',
    'Hexagon': 'C',
}

if not cap.isOpened():
    print("[Error] Cannot open camera, please check your camera.")
    exit()

print("[Module] Adjust HSV and area sliders, press q to exit.")

while True:
    # Read camera frame
    ret, frame = cap.read()
    
    if not ret:
        print("[Error] Cannot read camera frame.")
        break
    
    # Convert BGR image to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get slider values
    h_low = cv2.getTrackbarPos("H Low", "Sliders")
    h_high = cv2.getTrackbarPos("H High", "Sliders")
    s_low = cv2.getTrackbarPos("S Low", "Sliders")
    s_high = cv2.getTrackbarPos("S High", "Sliders")
    v_low = cv2.getTrackbarPos("V Low", "Sliders")
    v_high = cv2.getTrackbarPos("V High", "Sliders")
    min_area = cv2.getTrackbarPos("Min Area", "Sliders")

    # Generate mask based on HSV slider values (keep only specified color range)
    lower_np = np.array([h_low, s_low, v_low])
    upper_np = np.array([h_high, s_high, v_high])
    mask = cv2.inRange(hsv, lower_np, upper_np)

    # Apply mask to original image to get filtered result
    filtered = cv2.bitwise_and(frame, frame, mask=mask)

    # Copy original frame for drawing recognition results
    result_frame = frame.copy()

    # Find all contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        # Polygon approximation, get number of vertices
        approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
        x, y, w, h = cv2.boundingRect(approx) # Bounding rectangle
        area = cv2.contourArea(cnt)           # Contour area
        num_vertices = len(approx)            # Number of polygon vertices
        aspect_ratio = w / h if h != 0 else 0 # Aspect ratio

        shape = None
        # Determine shape type based on number of vertices and area
        if num_vertices == 3 and area >= min_area:
            shape = "Triangle"
        elif num_vertices == 4 and 0.8 < aspect_ratio < 1.2 and area >= min_area:
            shape = "Square"
        elif 6 <= num_vertices <= 7 and area >= min_area:
            shape = "Hexagon"

        if shape:
            label = action_map.get(shape)
            if label:
                # Draw polygon contour
                cv2.drawContours(result_frame, [approx], -1, (0, 0, 255), 2)
                # Draw bounding box, shape name, action, and area on result frame
                cv2.putText(result_frame,
                            f"{shape} ({label}){int(area)}",  # Show shape, action, area
                            (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (255, 255, 255), 2)

    # --- Merge and display four views ---
    # Resize all frames to the same size
    h_show, w_show = 320, 480
    show_result = cv2.resize(result_frame, (w_show, h_show))   # Top left: shape recognition result
    show_filtered = cv2.resize(filtered, (w_show, h_show))     # Top right: filtered frame
    show_camera = cv2.resize(frame, (w_show, h_show))          # Bottom left: original frame
    show_mask = cv2.cvtColor(cv2.resize(mask, (w_show, h_show)), cv2.COLOR_GRAY2BGR) # Bottom right: mask

    # Merge top and bottom
    top = np.hstack((show_result, show_filtered))
    bottom = np.hstack((show_camera, show_mask))
    merged = np.vstack((top, bottom))

    # Show merged frame
    cv2.imshow("All-in-One View", merged)

    # Press q to exit the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("[!] Program ended")
        break

# Release camera resources and close all windows
cap.release()
cv2.destroyAllWindows()