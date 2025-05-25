import sys
import subprocess
import time
import urllib.request
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QMessageBox
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, QRect, QUrl, QTimer
from PySide6.QtWebEngineCore import QWebEngineSettings

def is_url_reachable(url, timeout=3):
    try:
        urllib.request.urlopen(url, timeout=timeout)
        return True
    except:
        return False


def show_auto_confirm_box(main_url, local_url, timeout_ms=3000):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setWindowTitle("Connection Failed")
    msg_box.setText(f"Cannot load:\n{main_url}\nUse local server instead?")
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

    timer = QTimer()
    timer.setInterval(timeout_ms)
    timer.setSingleShot(True)
    timer.timeout.connect(lambda: msg_box.done(QMessageBox.Yes))
    timer.start()

    return msg_box.exec() == QMessageBox.Yes


class BrowserWindow(QMainWindow):
    def __init__(self, url: str, geometry: QRect, title="Web Viewer"):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(geometry)


        # Create the WebView widget
        web_view = QWebEngineView()

        # Enable necessary settings for autoplay
        web_view.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        web_view.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        web_view.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        web_view.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        web_view.settings().setAttribute(QWebEngineSettings.AutoLoadIconsForPage, True)
        web_view.settings().setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)

        # Load URL
        web_view.load(QUrl(url))

        # Connect signal when page finishes loading to run JS for autoplay
        web_view.loadFinished.connect(self.on_load_finished)

        # web_view.load(QUrl(url))


        web_view.load(QUrl(url))

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(web_view)



        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


    def on_load_finished(self, ok):
        if ok:
            js = """
            const videos = document.querySelectorAll("video");
            videos.forEach(video => {
                video.muted = true;  // Mute video to enable autoplay
                video.play().catch(err => console.log('Autoplay failed:', err));
            });
            """
            self.findChild(QWebEngineView).page().runJavaScript(js)



def try_run_local_server(command="python manage.py runserver", wait_time=8):
    # Launch the local Django server
    subprocess.Popen(command, shell=True)
    print("Started Django server. Waiting to boot...")

    time.sleep(wait_time)  # give time for Django to start


if __name__ == "__main__":


    app = QApplication(sys.argv)

    screens = app.screens()
    single_screen = len(screens) < 2
    screen_geom = screens[0].geometry()
    half_width = screen_geom.width() // 2
    height = screen_geom.height()



    import json

    with open(r"PySide\config.json", "r") as f:
        config_data = json.load(f)
    

    configs = [
        {
            "main_url": config_data['windows'][0]['main_url'],
            "local_url": config_data['windows'][0]['local_url'],
            "geometry": screens[0].geometry() if not single_screen else QRect(screen_geom.left(), screen_geom.top(), half_width, height),
            "title": "Window 1"
        },
        {
            "main_url": config_data['windows'][1]['main_url'],
            "local_url": config_data['windows'][1]['local_url'],
            "geometry": screens[1].geometry() if not single_screen else QRect(screen_geom.left() + half_width, screen_geom.top(), half_width, height),
            "title": "Window 2"
        }
    ]

    windows = []

    fail  = 0

    for config in configs:
        url_to_load = config["main_url"]
        if not is_url_reachable(url_to_load):
            user_agreed = show_auto_confirm_box(config["main_url"], config["local_url"])
            if user_agreed:
                try_run_local_server(command=config_data['server_command'])  # runs `python manage.py runserver`
                if is_url_reachable(config["local_url"], timeout=6):
                    url_to_load = config["local_url"]
                else:
                    QMessageBox.critical(
                        None,
                        "Local Server Error",
                        f"Local URL failed to load:\n{config['local_url']}"
                    )
                    fail+=1
                    continue
            else:
                continue  # user declined using local server

        window = BrowserWindow(url_to_load, config["geometry"], config["title"])
        windows.append(window)

    for w in windows:
        w.show()

    if fail>=2:
        sys.exit()
    else:
        sys.exit(app.exec())
