import ctypes
import os
import sys
import threading
from datetime import datetime
from pathlib import Path

from blocky import config as config_module
from blocky import dpi, language, rules
from blocky import settings as settings_module
from blocky.app import App
from blocky.checker import Checker, log_error
from blocky.controller import warning_text
from blocky.server import Server

ADMIN_NEEDED = language.marked(
    "Blocky needs administrator rights to edit the hosts file. Start it again and choose Yes."
)


def is_admin() -> bool:
    return bool(ctypes.windll.shell32.IsUserAnAdmin())


def relaunch_as_admin() -> bool:
    arguments = " ".join(f'"{argument}"' for argument in sys.argv[1:])
    result = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f"-m blocky {arguments}".strip(), os.getcwd(), 1
    )
    return result > 32


def start_language(config_path: Path) -> str:
    """The language for what Blocky shows before its window opens: the stored choice, or Windows' under Follow Windows."""
    try:
        settings = config_module.load(config_path).settings
    except (ValueError, OSError):
        settings = settings_module.Settings()  # a damaged config is recovered later; until then, follow Windows
    return settings_module.effective_language(settings, language.windows_language())


def recover_config(config_path: Path, error_log: Path) -> str | None:
    """Recover a damaged config; the warning is returned for the window and logged in English."""
    _, warning = config_module.load_or_recover(config_path, datetime.now())
    if warning:
        log_error(error_log, str(language.english(warning)))  # errors.log stays English
    return warning


def show_admin_needed() -> None:
    ctypes.windll.user32.MessageBoxW(None, language._(ADMIN_NEEDED), "Blocky", 0x30)


def stop_blocking(stop: threading.Event, worker: threading.Thread, checker: Checker, error_log: Path) -> None:
    """Stop the background check and remove Blocky's hosts entries; safe to call again."""
    stop.set()
    checker.request_sync()
    worker.join()
    try:
        checker.clear()
    except Exception as error:
        log_error(error_log, f"Could not remove Blocky's hosts entries: {error!r}")


def page_state(config_path: Path) -> dict:
    """What the block page shows, in the theme, font, text size, time format and language the window uses."""
    config = config_module.load(config_path)
    settings = config.settings
    windows_light = settings.theme == settings_module.FOLLOW_WINDOWS and settings_module.windows_is_light()
    appearance = {
        "theme": settings_module.effective_theme(settings, windows_light),
        "font": settings.font,
        "text_size": settings.text_size,
    }
    style = settings_module.time_style(settings, settings_module.windows_time())
    time_style = {"twelveHour": style.twelve_hour, "firstDay": style.first_day}
    code = settings_module.effective_language(settings, language.windows_language())
    # windowEnd stays "HH:MM": the extension reads it; the page shows it in the user's format.
    snapshot = rules.snapshot(config, datetime.now())
    return {**snapshot, "appearance": appearance, "timeStyle": time_style, "language": code}


def start_block_page(load_state) -> tuple[Server | None, str | None]:
    try:
        server = Server(load_state)
    except OSError as error:
        return None, language._(
            "The block page could not start, so blocked sites show the browser's error page: {error}", error=error
        )
    server.start()
    return server, None


def main() -> None:
    # Before any window, the administrator message included: Windows lets a process choose its DPI mode only once.
    dpi.follow_each_monitor()
    config_path = config_module.default_path()
    # Also before the administrator message, so that message and the start-up warnings use the user's language.
    language.apply(start_language(config_path))
    if os.name == "nt" and not is_admin():
        if not relaunch_as_admin():
            show_admin_needed()
        return

    # Lets Windows show Blocky's own icon in the taskbar instead of Python's.
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Blocky")
    error_log = config_path.parent / "errors.log"
    # Recover a damaged config before the background check reads it.
    config_warning = recover_config(config_path, error_log)
    stop = threading.Event()
    checker = Checker(config_path, error_log=error_log)
    worker = threading.Thread(target=checker.run, args=(stop,), daemon=True)
    worker.start()

    server, server_warning = start_block_page(lambda: page_state(config_path))

    try:
        App(
            config_path,
            warning=lambda: warning_text(checker.last_error, server_warning, config_warning),
            sync=checker.request_sync,
            # When Windows shuts down with Blocky open it ends the process before the cleanup below would run.
            session_ending=lambda: stop_blocking(stop, worker, checker, error_log),
        ).mainloop()
    finally:
        stop_blocking(stop, worker, checker, error_log)
        if server is not None:
            server.stop()


if __name__ == "__main__":
    main()
