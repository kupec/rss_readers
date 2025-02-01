from dataclasses import dataclass

from PyQt6.QtCore import QSettings, QThreadPool

SETTINGS_FEED_PROVIDERS = 'feed_providers'


@dataclass
class FeedProvider:
    url: str


@dataclass
class Settings:
    feed_providers: list[FeedProvider]

    qsettings: QSettings

    @classmethod
    def load(cls, qsettings: QSettings):
        return Settings(
            feed_providers=qsettings.value(SETTINGS_FEED_PROVIDERS, []),
            qsettings=qsettings,
        )

    def save(self):
        self.qsettings.setValue(SETTINGS_FEED_PROVIDERS, self.feed_providers)


@dataclass
class AppContext:
    thread_pool: QThreadPool
    settings: Settings
