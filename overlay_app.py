#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import requests
import keyboard
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QShortcut, QDesktopWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QUrl
from PyQt5.QtGui import QPainter, QColor, QFont, QPixmap, QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView

class TelemetryOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setupTimer()

    def initUI(self):
        self.setWindowTitle('StarbaseSim Telemetry Overlay')
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowTransparentForInput
        )

        self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.8)

        desktop = QDesktopWidget()
        screen_geometry = desktop.screenGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        overlay_height = 225

        self.resize(screen_width, overlay_height)
        self.move(0, screen_height - overlay_height)

        self.web_view = QWebEngineView(self)
        self.web_view.setStyleSheet("background: transparent;")

        self.web_view.resize(screen_width, screen_height)

        offset_y = -(screen_height - overlay_height)
        self.web_view.move(0, offset_y)

        self.web_view.load(QUrl("http://localhost:5000/"))

        self.setupGlobalHotkeys()

    def setupGlobalHotkeys(self):
        keyboard.add_hotkey('`', self.toggle_visibility_safe)

    def toggle_visibility_safe(self):
        QTimer.singleShot(0, self.toggle_visibility)

    def setupTimer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_server)
        self.timer.start(5000)

    def check_server(self):
        try:
            response = requests.get("http://localhost:5000/api/telemetry", timeout=1)
            if response.status_code == 200:
                pass
        except:
            pass

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        event.ignore()

def main():
    app = QApplication(sys.argv)

    try:
        response = requests.get("http://localhost:5000/api/telemetry", timeout=2)
    except:
        print("Cannot connect to telemetry server")
        return

    overlay = TelemetryOverlay()
    overlay.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()