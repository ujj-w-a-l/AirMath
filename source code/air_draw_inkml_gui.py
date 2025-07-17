import tkinter as tk
from tkinter import ttk
import cv2
import mediapipe as mp
import numpy as np
import time
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import os

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Global variables for drawing
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
canvas = None
traces = [[]]
prev_x, prev_y = None, None
is_drawing = True
last_clear_time = 0
clear_cooldown = 1

class InkMLApp:
    def __init__(self, root):
        self.root = root
        self.root.title("InkML Equation Viewer and Air Drawing")

        self.data_folder = "data"
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        self.inkml_files = [f for f in os.listdir(self.data_folder) if f.endswith(".inkml")]
        print(f"Found InkML files: {self.inkml_files}")
        if not self.inkml_files:
            raise ValueError("No InkML files found in 'data' folder!")
        self.current_index = 0
        self.current_inkml_path = os.path.join(self.data_folder, self.inkml_files[self.current_index])
        print(f"Starting with: {self.current_inkml_path}")

        self.left_frame = ttk.Frame(root, width=640, height=480)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10)
        self.right_frame = ttk.Frame(root, width=640, height=480)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10)

        self.button_frame = ttk.Frame(root)
        self.button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        self.prev_button = ttk.Button(self.button_frame, text="Previous", command=self.prev_inkml)
        self.prev_button.grid(row=0, column=0, padx=5)
        self.save_button = ttk.Button(self.button_frame, text="Save Air Drawing", command=self.save_air_inkml)
        self.save_button.grid(row=0, column=1, padx=5)
        self.next_button = ttk.Button(self.button_frame, text="Next", command=self.next_inkml)
        self.next_button.grid(row=0, column=2, padx=5)

        self.left_label = ttk.Label(self.left_frame)
        self.left_label.pack()
        self.load_inkml()

        self.right_label = ttk.Label(self.right_frame)
        self.right_label.pack()
        self.update_air_drawing()

    def load_inkml(self):
        try:
            print(f"Loading: {self.current_inkml_path}")
            tree = ET.parse(self.current_inkml_path)
            root = tree.getroot()

            latex = root.find(".//{http://www.w3.org/2003/InkML}annotation[@type='truth']").text.strip()
            print(f"LaTeX: {latex}")

            plt.figure(figsize=(8, 2))
            plt.text(0.5, 0.5, f"${latex}$", fontsize=20, ha='center', va='center')
            plt.axis('off')
            plt.rc('text', usetex=False)
            plt.rc('font', family='serif')

            canvas = FigureCanvasAgg(plt.gcf())
            canvas.draw()
            buf = canvas.buffer_rgba()
            img_array = np.asarray(buf)
            img_array = img_array[:, :, :3]
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

            h, w = img_array.shape[:2]
            scale = min(640 / w, 480 / h)
            new_w, new_h = int(w * scale), int(h * scale)
            img_resized = cv2.resize(img_array, (new_w, new_h), interpolation=cv2.INTER_AREA)
            inkml_canvas = np.zeros((480, 640, 3), dtype=np.uint8)
            y_offset = (480 - new_h) // 2
            x_offset = (640 - new_w) // 2
            inkml_canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = img_resized

            img = cv2.cvtColor(inkml_canvas, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            photo = ImageTk.PhotoImage(image=img)
            self.left_label.configure(image=photo)
            self.left_label.image = photo

            plt.close()
            print(f"Loaded successfully: {self.current_inkml_path}")
        except Exception as e:
            print(f"Error loading InkML: {e}")

    def update_air_drawing(self):
        global canvas, traces, prev_x, prev_y, is_drawing, last_clear_time

        ret, frame = cap.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        if canvas is None:
            canvas = np.zeros_like(frame)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                finger_count = 0
                finger_tips = [4, 8, 12, 16, 20]
                finger_pip = [2, 6, 10, 14, 18]
                wrist = hand_landmarks.landmark[0]

                for tip_id, pip_id in zip(finger_tips, finger_pip):
                    tip = hand_landmarks.landmark[tip_id]
                    pip = hand_landmarks.landmark[pip_id]
                    if tip_id == 4:
                        if abs(tip.x - wrist.x) > 0.15 and tip.y < pip.y:
                            finger_count += 1
                    else:
                        if tip.y < pip.y - 0.05:
                            finger_count += 1

                status = "Drawing" if is_drawing else "Paused"
                cv2.putText(frame, f"Fingers: {finger_count} | {status}", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                current_time = time.time()
                if finger_count == 2:
                    is_drawing = False
                    if traces[-1]:
                        traces.append([])
                elif finger_count == 5 and (current_time - last_clear_time) > clear_cooldown:
                    canvas = np.zeros_like(frame)
                    traces = [[]]
                    is_drawing = True
                    last_clear_time = current_time
                else:
                    is_drawing = True

                x, y = int(hand_landmarks.landmark[8].x * 640), int(hand_landmarks.landmark[8].y * 480)
                cv2.circle(frame, (x, y), 8, (0, 255, 0), -1)

                if is_drawing and prev_x is not None and prev_y is not None:
                    cv2.line(canvas, (prev_x, prev_y), (x, y), (255, 255, 255), 5)
                    x_scaled = 0.8 + (x / 640) * (1.8 - 0.8)
                    y_scaled = 6.4 + (y / 480) * (6.8 - 6.4)
                    traces[-1].append((x_scaled, y_scaled))

                prev_x, prev_y = x, y
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        else:
            prev_x, prev_y = None, None
            if traces[-1]:
                traces.append([])

        frame = cv2.bitwise_or(frame, canvas)
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        photo = ImageTk.PhotoImage(image=img)
        self.right_label.configure(image=photo)
        self.right_label.image = photo

        self.root.after(10, self.update_air_drawing)

    def save_air_inkml(self):
        """Save the air-drawn traces to the 'air_data' folder with a unique name, excluding copyright and writer annotations."""
        global traces

        tree = ET.parse(self.current_inkml_path)
        original_root = tree.getroot()

        ink = ET.Element("ink", xmlns="http://www.w3.org/2003/InkML")
        trace_format = ET.SubElement(ink, "traceFormat")
        ET.SubElement(trace_format, "channel", name="X", type="decimal")
        ET.SubElement(trace_format, "channel", name="Y", type="decimal")

        for annot in original_root.findall(".//{http://www.w3.org/2003/InkML}annotation"):
            annot_type = annot.get("type").lower()
            if annot_type not in ["copyright", "writer"]:
                ink.append(annot)

        for annot_xml in original_root.findall(".//{http://www.w3.org/2003/InkML}annotationXML"):
            ink.append(annot_xml)

        for i, trace in enumerate(traces):
            if trace:
                trace_elem = ET.SubElement(ink, "trace", id=str(i))
                trace_elem.text = ", ".join(f"{x:.6f} {y:.6f}" for x, y in trace)

        trace_group = original_root.find(".//{http://www.w3.org/2003/InkML}traceGroup")
        if trace_group is not None:
            ink.append(trace_group)

        air_data_folder = "air_data"
        if not os.path.exists(air_data_folder):
            print(f"Creating folder: {air_data_folder}")
            os.makedirs(air_data_folder)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        base_name = os.path.basename(self.current_inkml_path).replace(".inkml", "")
        new_filename = os.path.join(air_data_folder, f"{base_name}_air_{timestamp}.inkml")
        print(f"Attempting to save to: {new_filename}")

        try:
            ET.indent(ET.ElementTree(ink), space="  ")
            ET.ElementTree(ink).write(new_filename, encoding="utf-8", xml_declaration=True)
            print(f"Air drawing saved as {new_filename}")
        except Exception as e:
            print(f"Error saving file: {e}")

    def next_inkml(self):
        print(f"Next clicked. Current index: {self.current_index}, Total files: {len(self.inkml_files)}")
        if self.current_index < len(self.inkml_files) - 1:
            self.current_index += 1
            self.current_inkml_path = os.path.join(self.data_folder, self.inkml_files[self.current_index])
            print(f"Switching to: {self.current_inkml_path}")
            self.load_inkml()
        else:
            print("At the last file, no next file available.")

    def prev_inkml(self):
        print(f"Prev clicked. Current index: {self.current_index}")
        if self.current_index > 0:
            self.current_index -= 1
            self.current_inkml_path = os.path.join(self.data_folder, self.inkml_files[self.current_index])
            print(f"Switching to: {self.current_inkml_path}")
            self.load_inkml()
        else:
            print("At the first file, no previous file available.")

if __name__ == "__main__":
    root = tk.Tk()
    app = InkMLApp(root)
    root.mainloop()

    cap.release()
    cv2.destroyAllWindows()
