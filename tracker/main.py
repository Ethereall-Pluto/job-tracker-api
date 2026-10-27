from pathlib import Path

from tracker.api import create_app

app = create_app(Path("tracker.db"))
