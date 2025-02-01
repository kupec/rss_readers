from PyQt6.QtCore import QAbstractListModel, pyqtSlot
from PyQt6.QtWidgets import (
    QHBoxLayout, QInputDialog, QListView, QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget
)
from rss_reader.appcontext import AppContext, FeedProvider, Settings

from rss_reader.feed import FeedWindow


class FeedProvidersWindow(QMainWindow):
    def __init__(self, app_context: AppContext):
        super().__init__()
        self.app_context = app_context

        self.feed_provider_list_model = FeedProviderListModel(self.app_context.settings)
        self.feed_provider_list = QListView()
        self.feed_provider_list.setModel(self.feed_provider_list_model)
        self.feed_provider_list.doubleClicked.connect(self.open_provider_feed)

        self.add_button = QPushButton()
        self.add_button.setText('Add')
        self.add_button.clicked.connect(self.on_add_provider)

        self.remove_button = QPushButton()
        self.remove_button.setText('Remove')
        self.remove_button.clicked.connect(self.on_remove_provider)

        buttons = QWidget()
        buttons_layout = QHBoxLayout(buttons)
        buttons_layout.addWidget(self.add_button, 1)
        buttons_layout.addWidget(self.remove_button, 1)

        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.addWidget(self.feed_provider_list, 1)
        layout.addWidget(buttons)

        self.setCentralWidget(main_widget)

        self.setWindowTitle('rss reader - providers')
        self.setMinimumWidth(600)
        self.setMinimumHeight(800)

    @pyqtSlot()
    def on_add_provider(self):
        dialog = QInputDialog()
        dialog.setLabelText('Specify URL of RSS feed')
        dialog.setOkButtonText('Add')
        dialog.setCancelButtonText('Cancel')
        dialog.open()

        @pyqtSlot()
        def on_accept():
            self.feed_provider_list_model.add(dialog.textValue())

        dialog.accepted.connect(on_accept)

    @pyqtSlot()
    def on_remove_provider(self):
        dialog = QMessageBox()
        dialog.setText('Are you sure?')
        dialog.setInformativeText('The operation cannot be reverted')
        remove_button = dialog.addButton("Delete", QMessageBox.ButtonRole.DestructiveRole)
        dialog.addButton(QMessageBox.StandardButton.Cancel)
        dialog.open()

        @pyqtSlot()
        def on_remove():
            if dialog.clickedButton() is remove_button:
                self.feed_provider_list_model.remove(self.feed_provider_list.currentIndex().row())

        dialog.buttonClicked.connect(on_remove)

    @pyqtSlot()
    def open_provider_feed(self):
        index = self.feed_provider_list.currentIndex().row() - 1
        provider = self.feed_provider_list_model.at(index)
        self.feed_window = FeedWindow(self.app_context, provider)
        self.feed_window.show()
        self.close()


class FeedProviderListModel(QAbstractListModel):
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings

    def add(self, url: str):
        count = len(self.settings.feed_providers)
        self.beginInsertRows(self.index(0), count+1, count+1)

        self.settings.feed_providers.append(FeedProvider(url=url))
        self.settings.save()

        self.endInsertRows()

    def remove(self, rowIndex: int):
        self.beginRemoveRows(self.index(0), rowIndex, rowIndex)

        self.settings.feed_providers.remove(self.settings.feed_providers[rowIndex])
        self.settings.save()

        self.endRemoveRows()

    def rowCount(self, _):
        return len(self.settings.feed_providers)

    def data(self, index, role):
        if role != 0:
            return None
        if not index.isValid():
            return None

        return self.at(index.row()).url

    def at(self, i):
        return self.settings.feed_providers[i]
