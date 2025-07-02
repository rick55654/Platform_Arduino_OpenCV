# Platform_Arduino_OpenCV

This project is an integrated machine arm control system combining image recognition and Arduino control.
It can recognize red and blue "triangle", "square", and "hexagon" targets, and send commands to the robotic arm for action.

---

## 📦 Required Module Installation

Please install the following required modules (Python 3.8+ recommended):

> This project requires opencv-python, numpy, and pyserial. Please install them first!

```bash
pip install opencv-python pyserial numpy
```

---

## 🔧 System Architecture

- **OpenCV Module**: Responsible for real-time camera image capture, HSV masking, and contour recognition.
- **Main Program (`main.py`)**: Executes the recognition process, stable state judgment, and sends control signals.
- **Signal Sender (`signal_sender.py`)**: Sends recognition results to Arduino via Serial.
- **State Manager (`state_manager.py`)**: Multi-frame stability judgment module.

---

## 🎯 Target Detection Logic

1. **Camera Frame Capture**: The main program continuously captures real-time images from the camera.
2. **HSV Color Space Conversion**: Converts BGR images to HSV for easier color masking.
3. **Masking and Contour Detection**: Generates masks based on HSV ranges and finds all contours.
4. **Polygon Approximation and Shape Judgment**: Approximates each contour as a polygon and determines the shape (triangle, square, hexagon) based on the number of vertices, area, and aspect ratio.
5. **Action Mapping**: Looks up the `action_map` for the corresponding Arduino command based on color and shape.
6. **Multi-frame Stability Judgment**: Uses `StateManager` to trigger command sending only when the recognition result is stable for multiple frames, avoiding flicker misjudgment.
7. **Real-time Annotation**: Annotates detected shapes, area, and corresponding code on the screen in real time, and displays the mask view.
8. **Command Sending**: After stable recognition, sends the corresponding code to Arduino via Serial for action.

### 2. Run `main.py` to Start the Main System

```bash
python main.py
```

Function Description:

- The system continuously performs image analysis and object recognition.
- When the recognition result is stable and meets the condition (e.g., red + triangle):
  - The code such as "Detected: `['A']`" will be displayed on the screen.
  - The corresponding signal will be sent to Arduino via Serial for further control.

---

## 📁 File Structure Overview

```bash
Platform_Arduino_OpenCV/
├── Arduino2ARM/
│   ├── arduino/                    # Arduino code folder
│   │   └── arduino.ino             # Arduino control code
│   └── python/                     # Python test code folder
│       ├── serial_basic.py         # Python: basic serial communication script
│       └── camera_HSV.py           # Python: basic shape recognition script
├── OpenCV2Arduino/
│   ├── __init__.py
│   ├── app_ui.py                   # UI class (for main program)
│   ├── color_config.json           # HSV range config file for recognition and adjustment
│   ├── signal_sender.py            # Sends corresponding code to Arduino
│   ├── state_manager.py            # Multi-frame stability judgment module
├── main.py                         # Main program for recognition process
└── README.md
```
- **Arduino2ARM/arduino/**: Arduino side code.
- **Arduino2ARM/python/**: Python test and communication scripts.
- **main.py**: Main recognition process, including image processing, shape judgment, command sending, and UI.
- **OpenCV2Arduino/**: Modularized functions (UI, Serial sending, state management).

---

## 👨‍💻 Author

The original author of this project is [ray-uncoding](https://github.com/ray-uncoding).
The current code has been adjusted and simplified for the NTUST Cup event (such as main program structure, detection logic, etc.).
Most of the content is different from the original version. Please refer to this documentation and code.
