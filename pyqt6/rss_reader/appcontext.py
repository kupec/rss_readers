from dataclasses import dataclass

from PyQt6.QtCore import QThreadPool


@dataclass
class FeedProvider:
    url: str


@dataclass
class Settings:
    feed_providers: list[FeedProvider]


@dataclass
class AppContext:
    thread_pool: QThreadPool
    settings: Settings
