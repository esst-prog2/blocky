import os
from pathlib import Path

HOSTS_PATH = Path(r"C:\Windows\System32\drivers\etc\hosts")
BEGIN = "# BEGIN BLOCKY"
END = "# END BLOCKY"


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
    text = path.read_bytes().decode("utf-8", errors="surrogateescape") if path.exists() else ""
    updated = render(text, hostnames)
    if updated == text:
        return False
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(updated.encode("utf-8", errors="surrogateescape"))
    os.replace(temporary, path)
    return True
