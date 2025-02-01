import sys

from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QApplication
from rss_reader.apploader import LoaderWindow


app = QApplication(sys.argv)

thread_pool = QThreadPool()
window = LoaderWindow(thread_pool)
window.show()

app.exec()
