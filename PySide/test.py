import sys
from cefpython3 import cefpython as cef
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt


class BrowserWindow(QMainWindow):
    def __init__(self, url):
        super().__init__()
        self.setWindowTitle("Embedded Chrome")
        self.setGeometry(100, 100, 800, 600)

        # Create QWidget to hold the browser frame
        self.browser_frame = QWidget(self)
        self.browser_frame.setGeometry(0, 0, 800, 600)

        # Initialize Chromium (CEF) browser
        cef.Initialize()
        self.browser = cef.CreateBrowserSync(url=url, window_handle=self.browser_frame.winId())
        cef.MessageLoop()

    def closeEvent(self, event):
        cef.Shutdown()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and show the BrowserWindow
    window = BrowserWindow(url="https://www.example.com")
    window.show()

    sys.exit(app.exec())
