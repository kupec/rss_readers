from PyQt6.QtCore import QObject, QRunnable, QThreadPool, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QLabel, QMainWindow, QMessageBox

from rss_reader.appcontext import AppContext, FeedProvider, Settings
from rss_reader.feedproviders import FeedProvidersWindow


class LoaderWindow(QMainWindow):
    def __init__(self, thread_pool: QThreadPool):
        super().__init__()
        self.thread_pool = thread_pool

        self.label = QLabel()
        self.label.setStyleSheet('font: 24px')
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setText('Loading...')

        self.setCentralWidget(self.label)

        self.setWindowTitle('rss reader - loader')
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)

    def show(self):
        load_task = SettingsLoadTask()
        load_task.signals.result.connect(self.open_app_window)
        load_task.signals.error.connect(self.show_error_message)
        self.thread_pool.start(load_task)

        super().show()

    @pyqtSlot(Settings)
    def open_app_window(self, settings: Settings):
        app_context = AppContext(
            thread_pool=self.thread_pool,
            settings=settings,
        )
        self.next_window = FeedProvidersWindow(app_context)
        self.next_window.show()
        self.close()

    @pyqtSlot(str)
    def show_error_message(self, error_message: str):
        message_box = QMessageBox()
        message_box.setText(f'Cannot load settings. Error: {error_message}')
        message_box.exec()
        self.close()


class SettingsLoadTask(QRunnable):
    class Signals(QObject):
        error = pyqtSignal(str)
        result = pyqtSignal(object)

    signals = Signals()

    @pyqtSlot()
    def run(self):
        try:
            import time
            time.sleep(0.5)
            settings = Settings(
                feed_providers=[
                    FeedProvider('http://localhost:8001/sample.rss?delay=0.4')
                ]
            )
            self.signals.result.emit(settings)
        except Exception as exc:
            self.signals.error.emit(str(exc))
