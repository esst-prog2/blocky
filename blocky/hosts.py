import os
import threading
import time
from pathlib import Path

HOSTS_PATH = Path(r"C:\Windows\System32\drivers\etc\hosts")
BEGIN = "# BEGIN BLOCKY"
END = "# END BLOCKY"
# Antivirus can briefly lock the new file, so the swap is retried before writing in place.
REPLACE_ATTEMPTS = 10
REPLACE_DELAY = 0.1
# The app window and the background check both write the hosts file, one at a time.
_write_lock = threading.Lock()


def render(text: str, hostnames: list[str]) -> str:
    newline = "\r\n" if "\r\n" in text else "\n"
    kept: list[str] = []
    inside = False
    for line in text.splitlines():
        marker = line.strip()
        if marker == BEGIN:
            if inside:
                raise ValueError("Nested Blocky section in the hosts file")
            inside = True
        elif marker == END:
            if not inside:
                raise ValueError("Blocky section end without a start in the hosts file")
            inside = False
        elif not inside:
            kept.append(line)
    if inside:
        raise ValueError("Unterminated Blocky section in the hosts file")
    if hostnames:
        kept.extend([BEGIN, *(f"127.0.0.1 {host}" for host in hostnames), END])
    return "".join(line + newline for line in kept)


def apply(hostnames: list[str], path: Path = HOSTS_PATH) -> bool:
    with _write_lock:
        return _apply(hostnames, path)


def _apply(hostnames: list[str], path: Path) -> bool:
    text = path.read_bytes().decode("utf-8", errors="surrogateescape") if path.exists() else ""
    updated = render(text, hostnames)
    if updated == text:
        return False
    data = updated.encode("utf-8", errors="surrogateescape")
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    for _ in range(REPLACE_ATTEMPTS):
        try:
            os.replace(temporary, path)
            return True
        except PermissionError:
            time.sleep(REPLACE_DELAY)
    path.write_bytes(data)
    temporary.unlink(missing_ok=True)
    return True
