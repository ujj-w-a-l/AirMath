import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

class InkMLReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("InkML Reader")

        # Set a smaller, fixed window size
        self.root.geometry("800x600")  # Width x Height in pixels

        # Get list of InkML files from 'data' folder
        self.data_folder = "air_data"
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        self.inkml_files = [f for f in os.listdir(self.data_folder) if f.endswith(".inkml")]
        print(f"Found InkML files: {self.inkml_files}")
        if not self.inkml_files:
            raise ValueError("No InkML files found in 'data' folder!")
        self.current_index = 0
        self.current_inkml_path = os.path.join(self.data_folder, self.inkml_files[self.current_index])
        print(f"Starting with: {self.current_inkml_path}")

        # UI setup
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(padx=10, pady=10, fill='both', expand=True)

        # Canvas for Matplotlib plot, smaller figure size
        self.fig = plt.Figure(figsize=(6, 5))  # Reduced from 10x10 to 6x5
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=10)
        
        # Next button
        self.next_button = ttk.Button(self.button_frame, text="Next", command=self.next_inkml)
        self.next_button.grid(row=0, column=0, padx=5)

        # Load and display the initial file
        self.load_inkml()

    def load_inkml(self):
        """Load and plot the current InkML file."""
        try:
            print(f"Loading: {self.current_inkml_path}")
            tree = ET.parse(self.current_inkml_path)
            root = tree.getroot()

            namespace = {'inkml': 'http://www.w3.org/2003/InkML'}

            print("InkML File Content:")
            strokes = []
            for trace in root.findall('.//inkml:trace', namespace):
                trace_id = trace.attrib.get('id', 'Unknown')
                trace_data = trace.text.strip() if trace.text else ""
                print(f"Trace ID: {trace_id}")
                print(f"Data: {trace_data}\n")

                if not trace_data:
                    print(f"Trace {trace_id} is empty!")
                    continue

                try:
                    points = [list(map(float, point.split())) for point in trace_data.split(',')]
                    strokes.append(points)
                except ValueError as e:
                    print(f"Error parsing trace {trace_id}: {e}")
                    continue

            if not strokes:
                print("No valid strokes to plot!")
                self.ax.clear()
                self.ax.text(0.5, 0.5, "No strokes found!", ha='center', va='center', fontsize=12)
            else:
                self.ax.clear()
                for stroke in strokes:
                    x, y = zip(*stroke)
                    self.ax.plot(x, y, marker='o', linewidth=2)
                self.ax.invert_yaxis()
                self.ax.set_title(f"Drawn Equation from {os.path.basename(self.current_inkml_path)}", fontsize=12)
                self.ax.grid(True)

            self.canvas.draw()
            print(f"Loaded successfully: {self.current_inkml_path}")

        except Exception as e:
            print(f"Error reading InkML file: {e}")
            self.ax.clear()
            self.ax.text(0.5, 0.5, f"Error: {e}", ha='center', va='center', fontsize=12)
            self.canvas.draw()

    def next_inkml(self):
        """Load the next InkML file in the list."""
        print(f"Next clicked. Current index: {self.current_index}, Total files: {len(self.inkml_files)}")
        if self.current_index < len(self.inkml_files) - 1:
            self.current_index += 1
            self.current_inkml_path = os.path.join(self.data_folder, self.inkml_files[self.current_index])
            print(f"Switching to: {self.current_inkml_path}")
            self.load_inkml()
        else:
            print("At the last file, no next file available.")
            self.ax.text(0.5, 0.5, "No more files!", ha='center', va='center', fontsize=12)
            self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = InkMLReaderApp(root)
    root.mainloop()
