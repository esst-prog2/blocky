import os
import time
from pathlib import Path

# Antivirus can briefly lock a freshly written file, so the swap is retried before writing in place.
REPLACE_ATTEMPTS = 10
REPLACE_DELAY = 0.1


def write_safely(path: Path, data: bytes) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    for _ in range(REPLACE_ATTEMPTS):
        try:
            os.replace(temporary, path)
            return
        except PermissionError:
            time.sleep(REPLACE_DELAY)
    path.write_bytes(data)
    temporary.unlink(missing_ok=True)
