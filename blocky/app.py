from datetime import datetime
from pathlib import Path
from typing import Callable

import customtkinter as ctk

from blocky import config as config_module
from blocky import hosts, rules
from blocky.checker import Checker
from blocky.config import Config
from blocky.domains import validate
from blocky.schedule import Schedule
from blocky import schedule as schedule_module

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class App(ctk.CTk):
    def __init__(
        self,
        config_path: Path,
        hosts_path: Path = hosts.HOSTS_PATH,
        clock: Callable[[], datetime] = datetime.now,
    ) -> None:
        super().__init__()
        self.title("Blocky")
        self.geometry("680x560")
        self.config_path = config_path
        self.clock = clock
        self.config: Config = config_module.load(config_path)
        self.checker = Checker(config_path, hosts_path, clock)

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

    def _save(self) -> None:
        config_module.save(self.config_path, self.config)
        try:
            self.checker.sync()
        except (OSError, ValueError) as error:
            self.status_message.configure(text=f"Could not update the hosts file: {error}")

    def _tick(self) -> None:
        self._refresh_status()
        self.after(15000, self._tick)

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

        self.status_message = ctk.CTkLabel(frame, text="", text_color="red")
        self.status_message.pack(anchor="w", padx=12, pady=4)

    def _refresh_status(self) -> None:
        now = self.clock()
        self.status_label.configure(text=rules.status_text(self.config, now))
        blocked = sorted(set(rules.blocked_domains(self.config, now)))
        self.blocked_label.configure(text="Blocked: " + (", ".join(blocked) or "none"))
        released = rules.released_until(self.config, now)
        lines = [
            f"{domain} unblocked until {until:%H:%M} ({self._remaining(until, now)} left)"
            for domain, until in sorted(released.items())
        ]
        self.released_label.configure(text="\n".join(lines))
        options = rules.overridable_domains(self.config, now) or ["No domain blocked"]
        self.override_menu.configure(values=options)
        if self.override_menu.get() not in options:
            self.override_menu.set(options[0])

    @staticmethod
    def _remaining(until: datetime, now: datetime) -> str:
        minutes = int((until - now).total_seconds()) // 60
        return f"{minutes // 60}h {minutes % 60:02d}m"

    def _override(self) -> None:
        domain = self.override_menu.get()
        try:
            rules.override(self.config, domain, self.reason_entry.get(), self.clock())
        except ValueError as error:
            self.status_message.configure(text=str(error))
            return
        self._save()
        self.reason_entry.delete(0, "end")
        self.status_message.configure(text="")
        self._refresh_status()
        self._render_history()

    def _build_block_list(self, frame: ctk.CTkFrame) -> None:
        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=12)
        self.new_domain_entry = ctk.CTkEntry(row, placeholder_text="example.com", width=320)
        self.new_domain_entry.pack(side="left", padx=(0, 8))
        ctk.CTkButton(row, text="Add", command=self._add_domain).pack(side="left")
        self.block_message = ctk.CTkLabel(frame, text="", text_color="red")
        self.block_message.pack(anchor="w", padx=12)
        self.domain_list = ctk.CTkScrollableFrame(frame)
        self.domain_list.pack(fill="both", expand=True, padx=12, pady=8)
        self._render_domains()

    def _render_domains(self) -> None:
        for child in self.domain_list.winfo_children():
            child.destroy()
        for index, domain in enumerate(self.config.domains):
            row = ctk.CTkFrame(self.domain_list, fg_color="transparent")
            row.pack(fill="x", pady=2)
            entry = ctk.CTkEntry(row, width=320)
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

    def _add_domain(self) -> None:
        try:
            domain = validate(self.new_domain_entry.get())
        except ValueError as error:
            self.block_message.configure(text=str(error))
            return
        if domain in self.config.domains:
            self.block_message.configure(text=f"{domain} is already in the list")
            return
        self.config.domains.append(domain)
        self.new_domain_entry.delete(0, "end")
        self._after_domain_change()

    def _edit_domain(self, index: int, entry: str) -> None:
        try:
            domain = validate(entry)
        except ValueError as error:
            self.block_message.configure(text=str(error))
            return
        self.config.domains[index] = domain
        self._after_domain_change()

    def _remove_domain(self, index: int) -> None:
        del self.config.domains[index]
        self._after_domain_change()

    def _after_domain_change(self) -> None:
        self.block_message.configure(text="")
        self._save()
        self._render_domains()
        self._refresh_status()

    def _build_schedule(self, frame: ctk.CTkFrame) -> None:
        days_row = ctk.CTkFrame(frame, fg_color="transparent")
        days_row.pack(anchor="w", padx=12, pady=12)
        self.day_boxes: list[ctk.CTkCheckBox] = []
        for index, name in enumerate(DAYS):
            box = ctk.CTkCheckBox(days_row, text=name, width=60)
            if index in self.config.schedule.weekdays:
                box.select()
            box.pack(side="left", padx=2)
            self.day_boxes.append(box)

        times = ctk.CTkFrame(frame, fg_color="transparent")
        times.pack(anchor="w", padx=12, pady=8)
        ctk.CTkLabel(times, text="From").pack(side="left", padx=(0, 6))
        self.start_entry = ctk.CTkEntry(times, width=80)
        self.start_entry.insert(0, self.config.schedule.start)
        self.start_entry.pack(side="left", padx=(0, 16))
        ctk.CTkLabel(times, text="To").pack(side="left", padx=(0, 6))
        self.end_entry = ctk.CTkEntry(times, width=80)
        self.end_entry.insert(0, self.config.schedule.end)
        self.end_entry.pack(side="left", padx=(0, 16))
        ctk.CTkButton(times, text="Save schedule", command=self._save_schedule).pack(side="left")

        self.schedule_message = ctk.CTkLabel(frame, text="", text_color="red")
        self.schedule_message.pack(anchor="w", padx=12)

    def _save_schedule(self) -> None:
        schedule = Schedule(
            weekdays=[index for index, box in enumerate(self.day_boxes) if box.get()],
            start=self.start_entry.get().strip(),
            end=self.end_entry.get().strip(),
        )
        try:
            schedule_module.validate(schedule)
        except ValueError as error:
            self.schedule_message.configure(text=str(error))
            return
        self.config.schedule = schedule
        self.schedule_message.configure(text="")
        self._save()
        self._refresh_status()

    def _build_shortlist(self, frame: ctk.CTkFrame) -> None:
        self.shortlist_box = ctk.CTkTextbox(frame)
        self.shortlist_box.pack(fill="both", expand=True, padx=12, pady=12)
        self.shortlist_box.insert("1.0", "\n".join(self.config.shortlist))
        ctk.CTkButton(frame, text="Save shortlist", command=self._save_shortlist).pack(
            anchor="w", padx=12, pady=(0, 12)
        )

    def _save_shortlist(self) -> None:
        text = self.shortlist_box.get("1.0", "end")
        self.config.shortlist = [line.strip() for line in text.splitlines() if line.strip()]
        self._save()

    def _build_history(self, frame: ctk.CTkFrame) -> None:
        self.history_box = ctk.CTkTextbox(frame, state="disabled")
        self.history_box.pack(fill="both", expand=True, padx=12, pady=12)
        self._render_history()

    def _render_history(self) -> None:
        lines = [
            f"{o['timestamp']}  {o['domain']}  — {o['reason']}"
            for o in self.config.overrides
        ]
        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")
        self.history_box.insert("1.0", "\n".join(lines) or "No overrides yet.")
        self.history_box.configure(state="disabled")
