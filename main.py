import sys
import asyncio
from PyQt6.QtWidgets import QApplication
from ui_main import HeartRateMonitorApp
from qasync import QEventLoop, asyncSlot

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create and set the event loop properly
    loop = QEventLoop()
    asyncio.set_event_loop(loop)

    window = HeartRateMonitorApp()
    window.show()

    # Run the event loop with qasync
    with loop:
        loop.run_forever()
