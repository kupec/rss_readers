from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QListWidget, QMainWindow
from rss_reader.appcontext import AppContext

from rss_reader.feed import FeedWindow


class FeedProvidersWindow(QMainWindow):
    def __init__(self, app_context: AppContext):
        super().__init__()
        self.app_context = app_context

        self.feed_provider_list = QListWidget()
        self.feed_provider_list.addItems([provider.url for provider in app_context.settings.feed_providers])
        self.feed_provider_list.itemSelectionChanged.connect(self.open_provider_feed)

        self.setCentralWidget(self.feed_provider_list)

        self.setWindowTitle('rss reader - providers')
        self.setMinimumWidth(600)
        self.setMinimumHeight(800)

    @pyqtSlot()
    def open_provider_feed(self):
        index = self.feed_provider_list.currentRow() - 1
        provider = self.app_context.settings.feed_providers[index]
        self.feed_window = FeedWindow(self.app_context, provider)
        self.feed_window.show()
        self.close()
