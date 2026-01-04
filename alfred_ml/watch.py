import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .config import AlfredConfig
from .ingest import ingest_all

class _Handler(FileSystemEventHandler):
    def __init__(self, cfg: AlfredConfig):
        self.cfg = cfg
        self._last = 0.0

    def on_any_event(self, event):
        now = time.time()
        if now - self._last < 1.0:
            return
        self._last = now
        ingest_all(self.cfg)

def watch(cfg: AlfredConfig) -> None:
    cfg.docs_dir.mkdir(parents=True, exist_ok=True)
    handler = _Handler(cfg)
    observer = Observer()
    observer.schedule(handler, str(cfg.docs_dir), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(0.5)
    finally:
        observer.stop()
        observer.join()
