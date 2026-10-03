from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import customtkinter as ctk

from blocky import hosts
from blocky.controller import Controller
from blocky.domainfield import DomainField, hint
from blocky.timefield import TimeField

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class App(ctk.CTk):
    def __init__(
        self,
        config_path: Path,
        hosts_path: Path = hosts.HOSTS_PATH,
        clock: Callable[[], datetime] = datetime.now,
        warning: Callable[[], str] = lambda: "",
        sync: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self.title("Blocky")
        self.geometry("680x560")
        self.controller = Controller(config_path, hosts_path, clock, sync)
        self.warning = warning
        self._tick_id: str | None = None

        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=12, pady=12)
        for name in ("Status", "Block list", "Schedule", "Shortlist", "History"):
            self.tabs.add(name)

        self._build_status(self.tabs.tab("Status"))
        self._build_block_list(self.tabs.tab("Block list"))
        self._build_schedule(self.tabs.tab("Schedule"))
        self._build_shortlist(self.tabs.tab("Shortlist"))
        self._build_history(self.tabs.tab("History"))

        self._refresh_status()
        self._tick()

    def destroy(self) -> None:
        if self._tick_id is not None:
            self.after_cancel(self._tick_id)
        super().destroy()

    def _attempt(self, action: Callable[[], None], message: ctk.CTkLabel) -> bool:
        try:
            action()
        except (ValueError, OSError) as error:
            message.configure(text=str(error))
            return False
        message.configure(text="")
        return True

    def _tick(self) -> None:
        self._refresh_status()
        self._tick_id = self.after(15000, self._tick)

    def _build_status(self, frame: ctk.CTkFrame) -> None:
        self.status_label = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=16, weight="bold"))
        self.status_label.pack(anchor="w", padx=12, pady=(12, 4))
        self.blocked_label = ctk.CTkLabel(frame, text="", justify="left")
        self.blocked_label.pack(anchor="w", padx=12, pady=4)
        self.released_label = ctk.CTkLabel(frame, text="", justify="left")
        self.released_label.pack(anchor="w", padx=12, pady=4)

        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(24, 4))
        self.override_menu = ctk.CTkOptionMenu(row, values=["No domain blocked"])
        self.override_menu.pack(side="left", padx=(0, 8))
        self.reason_entry = ctk.CTkEntry(row, placeholder_text="Reason", width=260)
        self.reason_entry.pack(side="left", padx=(0, 8))
        ctk.CTkButton(row, text="Override", command=self._override).pack(side="left")

        undo_row = ctk.CTkFrame(frame, fg_color="transparent")
        undo_row.pack(fill="x", padx=12, pady=4)
        self.undo_menu = ctk.CTkOptionMenu(undo_row, values=["No domain unblocked"])
        self.undo_menu.pack(side="left", padx=(0, 8))
        ctk.CTkButton(undo_row, text="Undo override", command=self._undo).pack(side="left")

        self.status_message = ctk.CTkLabel(frame, text="", text_color="red")
        self.status_message.pack(anchor="w", padx=12, pady=4)
        self.warning_label = ctk.CTkLabel(frame, text="", text_color="orange", wraplength=600, justify="left")
        self.warning_label.pack(anchor="w", padx=12, pady=4)

    @staticmethod
    def _remaining(until: datetime, now: datetime) -> str:
        minutes = int((until - now).total_seconds()) // 60
        return f"{minutes // 60}h {minutes % 60:02d}m"

    def _refresh_status(self) -> None:
        now = self.controller.clock()
        view = self.controller.status()
        self.status_label.configure(text=view["text"])
        warning = " ".join(text for text in (self.controller.load_warning, self.warning()) if text)
        self.warning_label.configure(text=warning)
        self.blocked_label.configure(text="Blocked: " + (", ".join(view["blocked"]) or "none"))
        released = view["released"]
        self.released_label.configure(
            text="\n".join(
                f"{domain} unblocked until {until:%H:%M} ({self._remaining(until, now)} left)"
                for domain, until in sorted(released.items())
            )
        )
        self._set_menu(self.override_menu, view["overridable"], "No domain blocked")
        self._set_menu(self.undo_menu, sorted(released), "No domain unblocked")

    @staticmethod
    def _set_menu(menu: ctk.CTkOptionMenu, options: list[str], empty: str) -> None:
        options = options or [empty]
        menu.configure(values=options)
        if menu.get() not in options:
            menu.set(options[0])

    def _override(self) -> None:
        domain = self.override_menu.get()
        if self._attempt(
            lambda: self.controller.override(domain, self.reason_entry.get()),
            self.status_message,
        ):
            self.reason_entry.delete(0, "end")
            self._refresh_status()
            self._render_history()

    def _undo(self) -> None:
        domain = self.undo_menu.get()
        if self._attempt(lambda: self.controller.undo(domain), self.status_message):
            self._refresh_status()
            self._render_history()

    def _build_block_list(self, frame: ctk.CTkFrame) -> None:
        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=12)
        self.new_domain_entry = DomainField(
            row, on_change=self._update_domain_hint, placeholder_text="example.com", width=320
        )
        self.new_domain_entry.pack(side="left", padx=(0, 8))
        self.new_domain_entry.bind("<Return>", lambda _event: self._add_domain())
        self.add_button = ctk.CTkButton(row, text="Add", command=self._add_domain, state="disabled")
        self.add_button.pack(side="left")
        self.domain_hint = ctk.CTkLabel(frame, text="", text_color="gray50")
        self.domain_hint.pack(anchor="w", padx=12)
        self.block_message = ctk.CTkLabel(frame, text="", text_color="red")
        self.block_message.pack(anchor="w", padx=12)
        self.domain_list = ctk.CTkScrollableFrame(frame)
        self.domain_list.pack(fill="both", expand=True, padx=12, pady=8)
        self._render_domains()

    def _render_domains(self) -> None:
        for child in self.domain_list.winfo_children():
            child.destroy()
        for index, domain in enumerate(self.controller.config.domains):
            row = ctk.CTkFrame(self.domain_list, fg_color="transparent")
            row.pack(fill="x", pady=2)
            entry = DomainField(row, width=320)
            entry.insert(0, domain)
            entry.pack(side="left", padx=(0, 8))
            ctk.CTkButton(
                row, text="Save", width=60,
                command=lambda i=index, e=entry: self._edit_domain(i, e.get()),
            ).pack(side="left", padx=(0, 8))
            ctk.CTkButton(
                row, text="Remove", width=70, fg_color="gray40",
                command=lambda i=index: self._remove_domain(i),
            ).pack(side="left")

    def _update_domain_hint(self) -> None:
        addable, text = hint(self.new_domain_entry.get(), self.controller.config.domains)
        self.domain_hint.configure(text=text, text_color="gray50" if addable else "orange")
        self.add_button.configure(state="normal" if addable else "disabled")

    def _add_domain(self) -> None:
        if not hint(self.new_domain_entry.get(), self.controller.config.domains)[0]:
            return
        if self._attempt(lambda: self.controller.add_domain(self.new_domain_entry.get()), self.block_message):
            self.new_domain_entry.delete(0, "end")
            self._update_domain_hint()
            self._after_domain_change()

    def _edit_domain(self, index: int, entry: str) -> None:
        if self._attempt(lambda: self.controller.edit_domain(index, entry), self.block_message):
            self._after_domain_change()

    def _remove_domain(self, index: int) -> None:
        if self._attempt(lambda: self.controller.remove_domain(index), self.block_message):
            self._after_domain_change()

    def _after_domain_change(self) -> None:
        self._render_domains()
        self._refresh_status()

    def _build_schedule(self, frame: ctk.CTkFrame) -> None:
        days_row = ctk.CTkFrame(frame, fg_color="transparent")
        days_row.pack(anchor="w", padx=12, pady=12)
        self.day_boxes: list[ctk.CTkCheckBox] = []
        schedule = self.controller.config.schedule
        for index, name in enumerate(DAYS):
            box = ctk.CTkCheckBox(days_row, text=name, width=60)
            if index in schedule.weekdays:
                box.select()
            box.pack(side="left", padx=2)
            self.day_boxes.append(box)

        times = ctk.CTkFrame(frame, fg_color="transparent")
        times.pack(anchor="w", padx=12, pady=8)
        ctk.CTkLabel(times, text="From").pack(side="left", padx=(0, 6))
        self.start_time = TimeField(times, schedule.start)
        self.start_time.pack(side="left")
        ctk.CTkLabel(times, text="To").pack(side="left", padx=(10, 6))
        self.end_time = TimeField(times, schedule.end)
        self.end_time.pack(side="left")
        ctk.CTkButton(times, text="Save", command=self._save_schedule).pack(side="left", padx=(10, 0))

        self.schedule_message = ctk.CTkLabel(frame, text="", text_color="red")
        self.schedule_message.pack(anchor="w", padx=12)

    def _save_schedule(self) -> None:
        weekdays = [index for index, box in enumerate(self.day_boxes) if box.get()]
        start = self.start_time.get()
        end = self.end_time.get()
        if self._attempt(lambda: self.controller.set_schedule(weekdays, start, end), self.schedule_message):
            self._refresh_status()

    def _build_shortlist(self, frame: ctk.CTkFrame) -> None:
        self.shortlist_box = ctk.CTkTextbox(frame)
        self.shortlist_box.pack(fill="both", expand=True, padx=12, pady=12)
        self.shortlist_box.insert("1.0", "\n".join(self.controller.config.shortlist))
        self.shortlist_message = ctk.CTkLabel(frame, text="", text_color="red")
        self.shortlist_message.pack(anchor="w", padx=12)
        ctk.CTkButton(frame, text="Save shortlist", command=self._save_shortlist).pack(
            anchor="w", padx=12, pady=(0, 12)
        )

    def _save_shortlist(self) -> None:
        lines = self.shortlist_box.get("1.0", "end").splitlines()
        self._attempt(lambda: self.controller.set_shortlist(lines), self.shortlist_message)

    def _build_history(self, frame: ctk.CTkFrame) -> None:
        self.history_box = ctk.CTkTextbox(frame, state="disabled")
        self.history_box.pack(fill="both", expand=True, padx=12, pady=12)
        self._render_history()

    def _render_history(self) -> None:
        lines = self.controller.history_lines()
        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")
        self.history_box.insert("1.0", "\n".join(lines) or "No overrides yet.")
        self.history_box.configure(state="disabled")
