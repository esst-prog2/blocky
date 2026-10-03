import ctypes
import os
import sys
import threading
from datetime import datetime

from blocky import config as config_module
from blocky import rules
from blocky.app import App
from blocky.checker import Checker
from blocky.server import Server


def is_admin() -> bool:
    return bool(ctypes.windll.shell32.IsUserAnAdmin())


def relaunch_as_admin() -> None:
    arguments = " ".join(f'"{argument}"' for argument in sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f"-m blocky {arguments}".strip(), os.getcwd(), 1
    )


def main() -> None:
    if os.name == "nt" and not is_admin():
        relaunch_as_admin()
        return

    config_path = config_module.default_path()
    stop = threading.Event()
    checker = Checker(config_path)
    threading.Thread(target=checker.run, args=(stop,), daemon=True).start()

    server = Server(lambda: rules.snapshot(config_module.load(config_path), datetime.now()))
    server.start()

    try:
        App(config_path).mainloop()
    finally:
        stop.set()
        server.stop()


if __name__ == "__main__":
    main()
