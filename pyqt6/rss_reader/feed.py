import email.utils

from PyQt6.QtCore import (
    QAbstractListModel, QItemSelection, QObject, QRunnable, Qt, pyqtSignal, pyqtSlot
)
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QListView, QMainWindow, QMessageBox, QTextBrowser, QVBoxLayout, QWidget
import requests
from rss_parser import RSSParser
from rss_parser.models import XMLBaseModel

from rss_reader.appcontext import AppContext, FeedProvider


class FeedWindow(QMainWindow):
    def __init__(self, app_context: AppContext, feed_provider: FeedProvider):
        super().__init__()
        self.app_context = app_context

        self.feed_list_model = FeedListModel()
        self.feed_fetcher = FeedFetcher(feed_provider)
        self.feed_fetcher.signals.result.connect(self.update_feed_list)
        self.feed_fetcher.signals.error.connect(self.show_error_message)

        self.feed_list = QListView()
        self.feed_list.setDisabled(True)
        self.feed_list.setModel(self.feed_list_model)
        self.feed_list.selectionModel().selectionChanged.connect(self.select_feed)

        self.feed_content = QWidget()
        content_layout = QVBoxLayout(self.feed_content)

        self.feed_title = QLabel()
        self.feed_title.setStyleSheet('font: 24px')
        self.feed_title.setWordWrap(True)
        content_layout.addWidget(self.feed_title)

        self.feed_date = QLabel()
        self.feed_date.setStyleSheet('font: 18px; color: #444')
        content_layout.addWidget(self.feed_date)

        self.feed_text = QTextBrowser()
        self.feed_text.setStyleSheet('font: 18px')
        self.feed_text.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.feed_text.setOpenExternalLinks(True)
        content_layout.addWidget(self.feed_text, 1)

        self.update_feed_content(None)

        main_widget = QWidget()
        layout = QHBoxLayout(main_widget)
        layout.addWidget(self.feed_list)
        layout.addWidget(self.feed_content, 1)

        self.setCentralWidget(main_widget)

        self.setWindowTitle('rss reader')
        self.setMinimumWidth(1000)
        self.setMinimumHeight(600)

    def show(self):
        self.app_context.thread_pool.start(self.feed_fetcher)

        super().show()

    @pyqtSlot(XMLBaseModel)
    def update_feed_list(self, rss: XMLBaseModel):
        self.feed_list_model.update(rss)
        self.feed_list.setEnabled(True)

    @pyqtSlot(tuple)
    def show_error_message(self, error_tuple: tuple[int, str]):
        code, text = error_tuple
        message_box = QMessageBox()
        message_box.setText(f'Error: [{code}]: {text}')
        message_box.open()

    @pyqtSlot(QItemSelection)
    def select_feed(self, selected: QItemSelection):
        item = None
        if selected.indexes():
            index = selected.indexes()[0].row()
            item = self.feed_list_model.at(index)

        self.update_feed_content(item)

    def update_feed_content(self, item: XMLBaseModel | None):
        if item is None:
            self.feed_title.setText('')
            self.feed_date.setText('')
            self.feed_text.setHtml('Select some news')
        else:
            self.feed_title.setText(item.title.content)
            if item.pub_date:
                date = email.utils.parsedate_to_datetime(item.pub_date.content)
                self.feed_date.setText(date.strftime("%d.%m.%Y %H:%M"))
            else:
                self.feed_date.setText('No date')
            self.feed_text.setHtml(item.description.content)


class FeedListModel(QAbstractListModel):
    def __init__(self, rss: XMLBaseModel | None = None):
        super().__init__()
        self.rss = rss

    def update(self, rss: XMLBaseModel):
        self.beginResetModel()
        self.rss = rss
        self.endResetModel()

    def rowCount(self, _):
        if not self.rss:
            return 1
        return len(self.rss.channel.items)

    def data(self, index, role):
        if role != 0:
            return None
        if not index.isValid():
            return None

        if not self.rss:
            return 'Loading...'

        item = self.at(index.row())
        return item.title.content

    def at(self, i):
        return self.rss.channel.items[i]


class FeedFetcher(QRunnable):
    class Signals(QObject):
        error = pyqtSignal(tuple)
        result = pyqtSignal(object)

    signals = Signals()

    def __init__(self, provider: FeedProvider):
        super().__init__()
        self.url = provider.url

    @pyqtSlot()
    def run(self):
        try:
            response = requests.get(self.url)
            if response.status_code != 200:
                self.signals.error.emit((response.status_code, response.text))
                return

            rss = RSSParser.parse(response.text)
            self.signals.result.emit(rss)
        except Exception as exc:
            self.signals.error.emit((0, str(exc)))
