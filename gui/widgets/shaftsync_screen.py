# gui/widgets/shaftsync_screen.py
import os
import serial
import csv
import numpy as np
from scipy.interpolate import interp1d # pyright: ignore[reportMissingImports]
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
import pyqtgraph as pg # pyright: ignore[reportMissingImports]
from collections import deque
from datetime import datetime


class ShaftSyncScreen(QWidget):
    def __init__(self, go_home_callback):
        super().__init__()
        self.go_home_callback = go_home_callback
        self.paused = False
        self.interpolate = False   # <-- NEW toggle state
        self.csv_file = None
        self.csv_writer = None

        # --- Serial setup ---
        self.serial_port_name = "COM4"
        self.baudrate = 115200
        self.serial_port = None

        # --- Main Layout ---
        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)

        # Title
        self.title = QLabel("📡 ShaftSync – Real-Time Encoder Monitor")
        self.title.setAlignment(Qt.AlignHCenter)
        self.title.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.layout.addWidget(self.title)

        # --- Top-right layout: RPM boxes + buttons ---
        top_layout = QHBoxLayout()
        top_layout.addStretch()  # push widgets to the right

        # Input RPM box
        self.input_box = QLabel("Input Shaft:\n-- rpm")
        self.input_box.setAlignment(Qt.AlignCenter)
        self.input_box.setStyleSheet("""
            background-color: #FFCCCC;
            font-size: 14px; font-weight: bold;
            border: 2px solid #990000;
            padding: 6px;
        """)
        self.input_box.setFixedSize(120, 60)
        top_layout.addWidget(self.input_box)

        # Output RPM box
        self.output_box = QLabel("Output Shaft:\n-- rpm")
        self.output_box.setAlignment(Qt.AlignCenter)
        self.output_box.setStyleSheet("""
            background-color: #CCCCFF;
            font-size: 14px; font-weight: bold;
            border: 2px solid #000099;
            padding: 6px;
        """)
        self.output_box.setFixedSize(120, 60)
        top_layout.addWidget(self.output_box)

        # Difference box
        self.diff_box = QLabel("Difference:\n-- %")
        self.diff_box.setAlignment(Qt.AlignCenter)
        self.diff_box.setStyleSheet("""
            background-color: #CCFFCC;
            font-size: 14px; font-weight: bold;
            border: 2px solid #04A604FF;
            padding: 6px;
        """)
        self.diff_box.setFixedSize(120, 60)
        top_layout.addWidget(self.diff_box)

        # Interpolate button (left of Pause)
        self.btn_interpolate = QPushButton("🔀 Interp OFF")
        self.btn_interpolate.setMinimumSize(100, 60)
        self.btn_interpolate.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.btn_interpolate.clicked.connect(self.toggle_interpolate)
        top_layout.addWidget(self.btn_interpolate)

        # Pause button
        self.btn_pause = QPushButton("⏸ Pause")
        self.btn_pause.setMinimumSize(100, 60)
        self.btn_pause.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.btn_pause.clicked.connect(self.toggle_pause)
        top_layout.addWidget(self.btn_pause)

        self.layout.addLayout(top_layout)

        # --- Plot ---
        self.plot_widget = pg.PlotWidget(title="RPM vs Time")
        self.plot_widget.setBackground('w')
        self.plot_widget.addLegend()
        self.plot_widget.showGrid(x=True, y=True)
        self.layout.addWidget(self.plot_widget)

        self.time_window = 100
        self.x_data = deque(maxlen=self.time_window)
        self.in_data = deque(maxlen=self.time_window)
        self.out_data = deque(maxlen=self.time_window)
        self.counter = 0

        self.in_curve = self.plot_widget.plot(pen='r', name="Input RPM")
        self.out_curve = self.plot_widget.plot(pen='b', name="Output RPM")

        # --- Bottom buttons layout: Save CSV left, Back right ---
        bottom_layout = QHBoxLayout()

        self.btn_save = QPushButton("💾 Save CSV")
        self.btn_save.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_save.clicked.connect(self.save_csv)

        self.btn_back = QPushButton("⬅️ Back to Home")
        self.btn_back.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_back.clicked.connect(self.go_home_callback)

        bottom_layout.addWidget(self.btn_save, stretch=5)
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.btn_back, stretch=5)

        self.layout.addLayout(bottom_layout)
        self.setLayout(self.layout)

        # --- Timer ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial)
        self.timer.start(50)  # 20 Hz

        self.init_serial()

    # --- Serial init ---
    def init_serial(self):
        try:
            self.serial_port = serial.Serial(self.serial_port_name, self.baudrate, timeout=1)
            print(f"[ShaftSync] Connected to {self.serial_port_name}")
        except Exception as e:
            print(f"[ShaftSync] Could not open {self.serial_port_name}: {e}")
            self.serial_port = None

    # --- Read Serial ---
    def read_serial(self):
        if self.paused:
            return

        if self.serial_port and self.serial_port.in_waiting > 0:
            try:
                latest_line = None
                while self.serial_port.in_waiting > 0:
                    latest_line = self.serial_port.readline().decode(errors='ignore').strip()

                if latest_line and latest_line.startswith("IN:") and ",OUT:" in latest_line:
                    parts = latest_line.replace("IN:", "").split(",OUT:")
                    if len(parts) == 2:
                        input_val = float(parts[0])
                        output_val = float(parts[1])
                        diff = ((input_val - output_val) / input_val * 100) if input_val != 0 else 0

                        # Update colored boxes
                        self.input_box.setText(f"Input Shaft:\n{input_val:.2f} rpm")
                        self.output_box.setText(f"Output Shaft:\n{output_val:.2f} rpm")
                        self.diff_box.setText(f"Difference:\n{diff:.2f} %")

                        # Update plot
                        self.counter += 1
                        self.x_data.append(self.counter)
                        self.in_data.append(input_val)
                        self.out_data.append(output_val)

                        if self.interpolate and len(self.x_data) > 3:
                            x = np.array(self.x_data)
                            xin = np.linspace(x.min(), x.max(), 300)
                            f_in = interp1d(x, np.array(self.in_data), kind='cubic')
                            f_out = interp1d(x, np.array(self.out_data), kind='cubic')
                            self.in_curve.setData(xin, f_in(xin))
                            self.out_curve.setData(xin, f_out(xin))
                        else:
                            self.in_curve.setData(list(self.x_data), list(self.in_data))
                            self.out_curve.setData(list(self.x_data), list(self.out_data))

                        # Save CSV
                        if self.csv_writer:
                            self.csv_writer.writerow([datetime.now().strftime("%H:%M:%S.%f"), input_val, output_val, diff])
            except Exception as e:
                print(f"[ShaftSync] Serial read error: {e}")

    # --- Pause / Resume ---
    def toggle_pause(self):
        self.paused = not self.paused
        self.btn_pause.setText("▶️ Resume" if self.paused else "⏸ Pause")

    # --- Interpolate toggle ---
    def toggle_interpolate(self):
        self.interpolate = not self.interpolate
        self.btn_interpolate.setText("🔀 Interp ON" if self.interpolate else "🔀 Interp OFF")

    # --- CSV Logging ---
    def save_csv(self):
        # Ensure the folder exists
        folder_path = os.path.join("data", "shaftsync")  # adjust folder name if needed
        os.makedirs(folder_path, exist_ok=True)

        if not self.csv_writer:
            filename = f"shaftsync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            full_path = os.path.join(folder_path, filename)
            self.csv_file = open(full_path, mode='w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(["Timestamp", "Input_RPM", "Output_RPM", "Difference_%"])
            self.btn_save.setText("✅ Saving CSV")
        else:
            self.csv_file.close()
            self.csv_writer = None
            self.csv_file = None
            self.btn_save.setText("💾 Save CSV")

    # --- Cleanup ---
    def closeEvent(self, event):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        if self.csv_file:
            self.csv_file.close()
        event.accept()
