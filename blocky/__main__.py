import ctypes
import os
import sys
import threading
from datetime import datetime

from blocky import config as config_module
from blocky import rules
from blocky.app import App
from blocky.checker import Checker
from blocky.controller import warning_text
from blocky.server import Server


def is_admin() -> bool:
    return bool(ctypes.windll.shell32.IsUserAnAdmin())


def relaunch_as_admin() -> None:
    arguments = " ".join(f'"{argument}"' for argument in sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f"-m blocky {arguments}".strip(), os.getcwd(), 1
    )


def start_block_page(load_state) -> tuple[Server | None, str | None]:
    try:
        server = Server(load_state)
    except OSError as error:
        return None, f"The block page could not start, so blocked sites show the browser's error page: {error}"
    server.start()
    return server, None


def main() -> None:
    if os.name == "nt" and not is_admin():
        relaunch_as_admin()
        return

    config_path = config_module.default_path()
    stop = threading.Event()
    checker = Checker(config_path)
    threading.Thread(target=checker.run, args=(stop,), daemon=True).start()

    server, server_warning = start_block_page(
        lambda: rules.snapshot(config_module.load(config_path), datetime.now())
    )

    try:
        App(config_path, warning=lambda: warning_text(checker.last_error, server_warning)).mainloop()
    finally:
        stop.set()
        if server is not None:
            server.stop()


if __name__ == "__main__":
    main()
