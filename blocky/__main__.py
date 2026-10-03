import ctypes
import os
import sys
import threading
from datetime import datetime
from pathlib import Path

from blocky import config as config_module
from blocky import rules
from blocky.app import App
from blocky.checker import Checker, log_error
from blocky.controller import warning_text
from blocky.server import Server

ADMIN_NEEDED = "Blocky needs administrator rights to edit the hosts file. Start it again and choose Yes."


def is_admin() -> bool:
    return bool(ctypes.windll.shell32.IsUserAnAdmin())


def relaunch_as_admin() -> bool:
    arguments = " ".join(f'"{argument}"' for argument in sys.argv[1:])
    result = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f"-m blocky {arguments}".strip(), os.getcwd(), 1
    )
    return result > 32


def show_admin_needed() -> None:
    ctypes.windll.user32.MessageBoxW(None, ADMIN_NEEDED, "Blocky", 0x30)


def stop_blocking(stop: threading.Event, worker: threading.Thread, checker: Checker, error_log: Path) -> None:
    stop.set()
    checker.request_sync()
    worker.join()
    try:
        checker.clear()
    except Exception as error:
        log_error(error_log, f"Could not remove Blocky's hosts entries: {error!r}")


def start_block_page(load_state) -> tuple[Server | None, str | None]:
    try:
        server = Server(load_state)
    except OSError as error:
        return None, f"The block page could not start, so blocked sites show the browser's error page: {error}"
    server.start()
    return server, None


def main() -> None:
    if os.name == "nt" and not is_admin():
        if not relaunch_as_admin():
            show_admin_needed()
        return

    config_path = config_module.default_path()
    error_log = config_path.parent / "errors.log"
    stop = threading.Event()
    checker = Checker(config_path, error_log=error_log)
    worker = threading.Thread(target=checker.run, args=(stop,), daemon=True)
    worker.start()

    server, server_warning = start_block_page(
        lambda: rules.snapshot(config_module.load(config_path), datetime.now())
    )

    try:
        App(
            config_path,
            warning=lambda: warning_text(checker.last_error, server_warning),
            sync=checker.request_sync,
        ).mainloop()
    finally:
        stop_blocking(stop, worker, checker, error_log)
        if server is not None:
            server.stop()


if __name__ == "__main__":
    main()
