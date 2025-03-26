from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget
from PyQt6.QtCore import QTimer, Qt
import asyncio
from bleak import BleakScanner, BleakClient
import sys
from compute_lf_hf import compute_lf_hf

class HeartRateMonitorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Heart Rate Monitor")
        self.setGeometry(100, 100, 400, 300)
        
        self.layout = QVBoxLayout()
        
        # Welcome Label
        self.label = QLabel("HEART RATE MONITOR", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)
        
        # Buttons
        self.btn_connect = QPushButton("Connect to a device", self)
        self.btn_connect.clicked.connect(self.scan_devices)
        self.layout.addWidget(self.btn_connect)
        
        self.btn_start = QPushButton("Start Recording", self)
        self.btn_start.setEnabled(False)
        self.btn_start.clicked.connect(self.toggle_recording)
        self.layout.addWidget(self.btn_start)
        
        # Device List
        self.device_list = QListWidget(self)
        self.device_list.itemClicked.connect(self.connect_to_device)
        self.layout.addWidget(self.device_list)
        self.device_list.hide()
        
        # Heart Rate Label
        self.hr_label = QLabel("Heart Rate: -- BPM", self)
        self.hr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.hr_label)
        
        self.setLayout(self.layout)
        
        #RR intervals 
        self.rr_data = [] 
        self.rr_label = QLabel("RR Intervals: --", self)
        self.rr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.rr_label)

        #LF/HF 
        self.lf_hf_label = QLabel("LF/HF: --", self)
        self.lf_hf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.lf_hf_label)


        # Bluetooth Variables
        self.selected_device = None
        self.client = None
        self.heart_rate_data = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.save_data)
        self.recording = False
    
    def scan_devices(self):
        """Scans for Bluetooth devices and displays them in the list."""
        self.device_list.clear()
        self.device_list.show()
        asyncio.create_task(self.async_scan())
    
    async def async_scan(self):
        devices = await BleakScanner.discover()
        for device in devices:
            self.device_list.addItem(f"{device.name} ({device.address})")
    
    def connect_to_device(self, item):
        """Connects to the selected Bluetooth device."""
        device_info = item.text().split(" (")
        self.selected_device = device_info[1][:-1]  # Extract MAC address
        self.device_list.hide()
        self.btn_start.setEnabled(True)
        self.label.setText(f"Connected to {device_info[0]}")
    
    def toggle_recording(self):
        """Starts or stops heart rate recording."""
        if self.recording:
            self.recording = False
            self.btn_start.setText("Start Recording")
            self.timer.stop()
            asyncio.create_task(self.stop_heart_rate())
        else:
            self.recording = True
            self.btn_start.setText("Stop Recording")
            self.start_recording()

    def start_recording(self):
        """Starts heart rate recording."""
        if self.selected_device:
            asyncio.create_task(self.read_heart_rate())
            self.timer.start(5000)  # Save data every 5 seconds

    async def stop_heart_rate(self):
        """Stops heart rate notifications."""
        if self.client:
            await self.client.stop_notify("00002a37-0000-1000-8000-00805f9b34fb")
    
    async def read_heart_rate(self):
        """Reads heart rate and RR interval data from the device."""
        HR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"  # Standard HR UUID
        while self.recording:  # Keep trying as long as recording is on
            try:
                async with BleakClient(self.selected_device) as self.client:
                    print("Connected to device, starting notifications...")
                    await self.client.start_notify(HR_UUID, self.heart_rate_callback)
                    while True:
                        print("Listening for HR updates...")
                        await asyncio.sleep(1)
            except Exception as e:
                print("Connection lost, retrying in 5 seconds...", e)
                await asyncio.sleep(5)  
    
    
    def heart_rate_callback(self, sender, data):
        """Callback function to update UI with heart rate, RR interval data, and LF/HF metrics"""

        heart_rate = data[1]  # Heart Rate in BPM
        rr_intervals = []

        # Extract RR intervals (each interval is 2 bytes)
        for i in range(2, len(data), 2):
            rr_interval = int.from_bytes(data[i:i+2], byteorder='little') / 1024.0  # Convert to seconds
            rr_intervals.append(rr_interval)

        # Store RR intervals
        self.rr_data.extend(rr_intervals)  # Maintain a continuous list of RR intervals
        self.heart_rate_data.append((heart_rate, rr_intervals))
        # Keep only the last 60 seconds of RR intervals
        max_time_window = 60  # seconds
        while sum(self.rr_data) > max_time_window:
            self.rr_data.pop(0)

        # Compute LF/HF every update if we have enough data
        lf_power, hf_power, lf_hf_ratio = compute_lf_hf(self.rr_data) if len(self.rr_data) >= 30 else (None, None, None)

        # Update UI
        rr_text = ", ".join(f"{rr*1000:.1f} ms" for rr in rr_intervals) if rr_intervals else "N/A"
        lf_text = f"LF: {lf_power:.2f}" if lf_power else "LF: --"
        hf_text = f"HF: {hf_power:.2f}" if hf_power else "HF: --"
        lf_hf_text = f"LF/HF: {lf_hf_ratio:.2f}" if lf_hf_ratio else "LF/HF: --"

        self.hr_label.setText(f"HR: {heart_rate} BPM")
        self.rr_label.setText(f"RR Intervals: {rr_text}")
        self.lf_hf_label.setText(f"{lf_text} | {hf_text} | {lf_hf_text}")

        print(f"HR: {heart_rate} BPM | RR: {rr_intervals} | {lf_text} | {hf_text} | {lf_hf_text}")
    
    def save_data(self):
        """Saves recorded heart rate and RR interval data to a file."""
        with open("heart_rate_data.txt", "w") as file:
            for hr, rr_list in self.heart_rate_data:
                rr_str = ", ".join(f"{rr*1000:.1f} ms" for rr in rr_list) if rr_list else "N/A"
                file.write(f"HR: {hr} BPM | RR: {rr_str}\n")
        print("Data saved!")
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HeartRateMonitorApp()
    window.show()
    sys.exit(app.exec())
