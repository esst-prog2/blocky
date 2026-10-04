import threading
from pathlib import Path

from blocky.files import write_safely
from blocky.language import shown

HOSTS_PATH = Path(r"C:\Windows\System32\drivers\etc\hosts")
BEGIN = "# BEGIN BLOCKY"
END = "# END BLOCKY"
# Normally only the background check writes; the lock keeps any second writer from colliding.
_write_lock = threading.Lock()


def render(text: str, hostnames: list[str]) -> str:
    newline = "\r\n" if "\r\n" in text else "\n"
    kept: list[str] = []
    inside = False
    # Split on line breaks only: splitlines() would also split other programs' lines at characters like U+0085.
    lines = text.replace("\r\n", "\n").split("\n")
    if lines[-1] == "":
        lines.pop()
    for line in lines:
        marker = line.strip()
        if marker == BEGIN:
            if inside:
                raise ValueError(shown("Nested Blocky section in the hosts file"))
            inside = True
        elif marker == END:
            if not inside:
                raise ValueError(shown("Blocky section end without a start in the hosts file"))
            inside = False
        elif not inside:
            kept.append(line)
    if inside:
        raise ValueError(shown("Unterminated Blocky section in the hosts file"))
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
    write_safely(path, updated.encode("utf-8", errors="surrogateescape"))
    return True
