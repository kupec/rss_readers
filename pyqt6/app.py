import sys

from PyQt6.QtWidgets import QApplication

from rss_reader.feed import FeedWindow

app = QApplication(sys.argv)

window = FeedWindow()
window.start()

app.exec()
