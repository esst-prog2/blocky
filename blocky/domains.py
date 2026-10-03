import re

_LABEL = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")


def validate(entry: str) -> str:
    domain = entry.strip().lower()
    labels = domain.split(".")
    if len(labels) < 2 or not all(_LABEL.match(label) for label in labels):
        raise ValueError(f"'{entry.strip()}' is not a valid domain")
    if not labels[-1].isalpha() or len(labels[-1]) < 2:
        raise ValueError(f"'{entry.strip()}' is not a valid domain")
    return domain


def covered_hostnames(domain: str) -> list[str]:
    if domain.startswith("www."):
        return [domain]
    return [domain, f"www.{domain}"]
