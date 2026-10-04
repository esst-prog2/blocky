import re

from blocky.language import _

_LABEL = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")


def host_of(entry: str) -> str:
    text = entry.strip().lower()
    if "://" in text:
        text = text.split("://", 1)[1]
    text = re.split(r"[/?#]", text, maxsplit=1)[0]
    return text.split(":", 1)[0]


def validate(entry: str) -> str:
    domain = host_of(entry)
    labels = domain.split(".")
    if len(labels) < 2 or not all(_LABEL.match(label) for label in labels):
        raise ValueError(_("'{entry}' is not a valid domain", entry=entry.strip()))
    if not labels[-1].isalpha() or len(labels[-1]) < 2:
        raise ValueError(_("'{entry}' is not a valid domain", entry=entry.strip()))
    return domain


def covered_hostnames(domain: str) -> list[str]:
    if domain.startswith("www."):
        return [domain]
    return [domain, f"www.{domain}"]
