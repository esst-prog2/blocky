"""Mutation testing with cosmic-ray: makes small changes to Blocky's code and reports changes no test notices.

Usage: .venv\\Scripts\\python tools\\mutation_test.py [module ...] [--report]

Each module is tested against its own test files only, to keep runs short. Results go to .mutation/ (ignored by
git); a stopped run resumes where it left off. cosmic-ray edits the source files in place while it runs, so the
script refuses to start with uncommitted changes in blocky/ and restores blocky/ when it stops.
UI and startup code (app.py, theme.py, __main__.py) are left out.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / ".mutation"
SCRIPTS = ROOT / ".venv" / "Scripts"
TESTS = {
    "hosts": "test_hosts test_properties",
    "domains": "test_domains test_domainfield test_properties",
    "schedule": "test_schedule test_properties",
    "rules": "test_rules test_robustness test_properties",
    "config": "test_config test_p1_config test_properties",
    "timefield": "test_timefield test_properties",
    "domainfield": "test_domainfield test_properties",
    "history": "test_history test_controller",
    "suggestions": "test_suggestions test_controller",
    "checker": "test_checker test_robustness test_p1",
    "files": "test_hosts test_p1_config test_robustness",
    "server": "test_server test_extension_files",
    "controller": "test_controller",
}


def cosmic_ray(*arguments: str) -> subprocess.CompletedProcess:
    # UTF-8 output: cosmic-ray cannot read test output in the Windows code page (the status text has an em dash).
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [str(SCRIPTS / "cosmic-ray.exe"), *arguments], cwd=ROOT, env=env, capture_output=True, text=True
    )


def write_config(module: str) -> Path:
    # Forward slashes: cosmic-ray splits the command Unix-style, which would drop backslashes.
    python = (SCRIPTS / "python.exe").as_posix()
    test_files = " ".join(f"tests/{name}.py" for name in TESTS[module].split())
    config = OUT / f"{module}.toml"
    config.write_text(
        "[cosmic-ray]\n"
        f'module-path = "blocky/{module}.py"\n'
        "timeout = 120.0\n"
        "excluded-modules = []\n"
        f"test-command = '{python} -m pytest -x -q -p no:cacheprovider {test_files}'\n\n"
        '[cosmic-ray.distributor]\nname = "local"\n',
        encoding="utf-8",
    )
    return config


def report(module: str) -> None:
    session = OUT / f"{module}.sqlite"
    if not session.exists():
        print(f"{module}: not run yet")
        return
    counts: dict[str, int] = {}
    survivors = []
    for line in cosmic_ray("dump", str(session)).stdout.splitlines():
        job, result = json.loads(line)
        outcome = result["test_outcome"] if result else "pending"
        counts[outcome] = counts.get(outcome, 0) + 1
        if outcome == "survived":
            changed = [
                row[1:].strip()
                for row in result["diff"].splitlines()
                if row[:1] in "+-" and row[:3] not in ("---", "+++")
            ]
            survivors.append(f"    line {job['mutations'][0]['start_pos'][0]}: " + "  =>  ".join(changed))
    print(f"{module}: " + ", ".join(f"{count} {outcome}" for outcome, count in sorted(counts.items())))
    print("\n".join(survivors))


def run(module: str) -> None:
    config = write_config(module)
    session = OUT / f"{module}.sqlite"
    if not session.exists():
        cosmic_ray("init", str(config), str(session)).check_returncode()
    print(f"{module}: running...", flush=True)
    cosmic_ray("exec", str(config), str(session))


def main() -> None:
    names = [name for name in sys.argv[1:] if not name.startswith("--")] or list(TESTS)
    unknown = set(names) - set(TESTS)
    if unknown:
        sys.exit(f"Unknown module(s): {', '.join(sorted(unknown))}")
    OUT.mkdir(exist_ok=True)
    if "--report" not in sys.argv:
        if subprocess.run(["git", "diff", "--quiet", "--", "blocky"], cwd=ROOT).returncode != 0:
            sys.exit("blocky/ has uncommitted changes; commit or stash them first, the run edits these files.")
        try:
            for name in names:
                run(name)
        finally:
            subprocess.run(["git", "checkout", "--", "blocky"], cwd=ROOT)
    for name in names:
        report(name)


if __name__ == "__main__":
    main()
