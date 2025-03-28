from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import QTimer

class BreathingPacer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 300)
        self.breathing_rate = 6.0  # Default breathing rate
        self.phase = "inhale"

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pacer)

        # Line properties
        self.start_x = 150
        self.start_y = 250
        self.end_x = 150
        self.end_y = 250  

         # Breath cycle durations
        self.inhale_time = 0
        self.exhale_time = 0

    def set_breathing_rate(self, rate):
        """Adjusts the pacer speed based on the breathing rate."""
        self.breathing_rate = rate
        cycle_time = 60 / self.breathing_rate

        self.inhale_time = (cycle_time / 2) * 1000  # Convert to milliseconds
        self.exhale_time = (cycle_time / 2) * 1000  # Convert to milliseconds
        
        self.start_pacer()

    def start_pacer(self):
        """Starts the pacer by beginning with inhale phase."""
        self.phase = "inhale"
        self.timer.start(50)  # Refresh every 50ms for smoother animation

    def stop_pacer(self):
        """Stops the pacer animation and resets the line."""
        self.timer.stop()  # Stop the animation
        self.phase = "inhale"  # Reset phase
        self.end_y = 250  # Reset line to start position
        self.update()  # Trigger repaint

    def update_pacer(self):
        """Updates the pacer animation by adjusting the line length."""
        if self.phase == "inhale":
            # Gradually extend the line
            step = (250 / (self.inhale_time / 50))  # Length change per timer tick
            self.end_y -= step
            if self.end_y < 50:
                self.end_y = 50
                self.phase = "exhale"
        else:  # Exhale phase
            # Gradually shorten the line
            step = (250 / (self.exhale_time / 50))
            self.end_y += step
            if self.end_y >= 250:
                self.end_y = 250
                self.phase = "inhale"

        self.update()

    def paintEvent(self, event):
        """Draw the pacer line."""
        painter = QPainter(self)
        
        # Draw static reference lines
        painter.setPen(QPen(QColor(255, 0, 0, 150), 2))  # Red reference lines
        painter.drawLine(130, 250, 170, 250)
        painter.drawLine(130,50, 170, 50)  

        # Draw the breathing pacer line
        painter.setPen(QPen(QColor(0, 150, 255, 180), 3))  # Restore pacer line color

        painter.drawLine(int(self.start_x), int(self.start_y), int(self.end_x), int(self.end_y))
