import os
from pathlib import Path

from tracker.api import create_app

app = create_app(Path(os.environ.get("TRACKER_DB", "tracker.db")))
