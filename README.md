
# AirMath: Gesture-Based Equation Capture

This project allows users to draw mathematical expressions in the air using hand gestures, convert those motions into InkML files, and view both the LaTeX ground truth and the captured air drawing in an intuitive GUI.

---

## 🧠 Overview

Ideal for building datasets to train models that recognize handwritten math expressions using gesture-based inputs.

---

## 🔧 Components

### 1. `air_draw_inkml_gui.py`

An interactive GUI that:

- Tracks your hand in real-time using a webcam and MediaPipe.
- Allows you to draw expressions with your index finger.
- Uses gestures to pause, clear, and save air-drawn equations.
- Displays ground truth LaTeX equations from `.inkml` files.
- Saves drawn strokes as new `.inkml` files for future training.

### 2. `display_V1.py`

A lightweight viewer that:

- Opens and visualizes `.inkml` files from the `air_data/` directory.
- Displays strokes as plotted paths with proper scale and Y-axis inversion.
- Lets you navigate between saved drawings using a simple interface.

---

## 🧠 How It Works

### ✋ Hand Gesture Controls

| Gesture (Fingers Shown)    | Function                       |
|---------------------------|--------------------------------|
| 1 (Index Finger)           | Start drawing                  |
| 2 (Index + One more)       | Pause/Segment the stroke       |
| 5 (All fingers open)       | Clear canvas (reset drawing)   |

MediaPipe detects landmarks on your hand in real time. Based on the number and orientation of extended fingers, different actions are triggered.

### ✨ Drawing Process

- Launch `air_draw_inkml_gui.py`
- Left panel shows a LaTeX expression from an existing `.inkml` file in the `data/` folder.
- Right panel is the live camera feed with drawing overlay.
- Draw in the air using your index finger.
- Use gestures to segment or clear.
- Click **Save Air Drawing** to:
  - Save your strokes as a new `.inkml` file in `air_data/`
  - Retain the original LaTeX label for future use.

### 🖼️ Viewing Drawings

- Launch `display_V1.py`
- Automatically loads drawings from `air_data/`
- Plots all traces as connected points.
- Provides a **Next** button to view subsequent files.

---

## 📁 Folder Structure

```
.
├── data/                  # Original InkML files with LaTeX ground truth
│   └── example1.inkml
├── air_data/              # Auto-generated air-drawn InkML files
│   └── example1_air_YYYYMMDD_HHMMSS.inkml
├── air_draw_inkml_gui.py  # Main hand tracking + GUI for drawing and saving
├── display_V1.py          # InkML viewer to replay air-drawn expressions
└── README.md              # Project documentation
```

---

## 📦 Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ How to Run

Run Air Drawing GUI:

```bash
python air_draw_inkml_gui.py
```

Run InkML Viewer:

```bash
python display_V1.py
```

---

## 📈 Use Cases & Applications

- Creating datasets for AI models that recognize handwritten math.
- Interactive learning tools for education.
- Future applications in AR/VR math input.
- Research in HCI, gesture recognition, and ink data processing.

---

## 💬 Future Improvements

- Integration with neural networks for symbol prediction.
- Expression parsing and math solver.
- Dynamic GUI labeling with autocomplete LaTeX suggestions.
- Web version using WebRTC + TensorFlow.js.

---

**Feel free to contribute, report issues, or suggest features!**
