from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import customtkinter as ctk

from blocky import hosts
from blocky import theme as t
from blocky.controller import Controller
from blocky.domainfield import DomainField, can_save_edit, hint
from blocky.timefield import TimeField

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
TABS = ("Status", "Block list", "Schedule", "Shortlist", "History")


class App(ctk.CTk):
    def __init__(
        self,
        config_path: Path,
        hosts_path: Path = hosts.HOSTS_PATH,
        clock: Callable[[], datetime] = datetime.now,
        warning: Callable[[], str] = lambda: "",
        sync: Callable[[], None] | None = None,
    ) -> None:
        ctk.set_appearance_mode("dark")
        super().__init__(fg_color=t.BACKGROUND)
        self.title("Blocky")
        self.geometry("760x660")
        self.minsize(640, 560)
        self.controller = Controller(config_path, hosts_path, clock, sync)
        self.warning = warning
        self._tick_id: str | None = None

        self._build_header()
        self.tabs = ctk.CTkTabview(
            self, fg_color=t.BACKGROUND, anchor="nw", corner_radius=0, border_width=0,
            segmented_button_fg_color=t.CARD, segmented_button_selected_color=t.DEEP,
            segmented_button_selected_hover_color=t.DEEP, segmented_button_unselected_color=t.CARD,
            segmented_button_unselected_hover_color=t.HOVER, text_color=t.TEXT,
        )
        # CTkTabview has no font option; its tab buttons are styled through the inner segmented button.
        self.tabs._segmented_button.configure(font=t.font("button"), height=36, corner_radius=8)
        self.tabs.pack(fill="both", expand=True, padx=t.MARGIN - 4, pady=(0, t.MARGIN - 6))
        for name in TABS:
            self.tabs.add(name)
        for button in self.tabs._segmented_button._buttons_dict.values():
            button.configure(width=104)

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

    # Layout helpers

    @staticmethod
    def _section(parent: ctk.CTkFrame, title: str, caption: str = "", expand: bool = False) -> ctk.CTkFrame:
        """A card with a title and an optional caption; returns the frame to put its content in."""
        box = t.card(parent)
        box.pack(fill="both" if expand else "x", expand=expand, pady=(0, t.GAP + 4))
        t.label(box, title, "title").pack(fill="x", padx=t.PAD, pady=(t.PAD - 2, 0))
        if caption:
            t.label(box, caption, "caption", t.MUTED).pack(fill="x", padx=t.PAD, pady=(2, 0))
        body = ctk.CTkFrame(box, fg_color="transparent")
        body.pack(fill="both", expand=expand, padx=t.PAD, pady=(t.GAP + 2, t.PAD))
        return body

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=t.MARGIN - 4, pady=(t.MARGIN - 4, t.GAP))
        t.label(header, "Blocky", "brand", t.SAGE).pack(side="left")
        t.label(header, "Fewer distractions, on your schedule", "caption", t.MUTED).pack(
            side="left", padx=(t.GAP + 4, 0), pady=(6, 0)
        )
        self.banner = t.card(self, border_width=1, border_color=t.WARNING)
        self.warning_label = t.label(self.banner, "", "body", t.WARNING, wraplength=660)
        self.warning_label.pack(fill="x", padx=t.PAD - 2, pady=t.GAP + 2)

    def _show_warning(self, text: str) -> None:
        self.warning_label.configure(text=f"⚠  {text.removeprefix('Warning: ')}" if text else "")
        if text and not self.banner.winfo_ismapped():
            self.banner.pack(fill="x", padx=t.MARGIN - 4, pady=(0, t.GAP), before=self.tabs)
        elif not text and self.banner.winfo_ismapped():
            self.banner.pack_forget()

    # Status tab

    def _build_status(self, frame: ctk.CTkFrame) -> None:
        hero = t.card(frame, color=t.DEEP)
        hero.pack(fill="x", pady=(t.GAP, t.GAP + 4))
        t.label(hero, "RIGHT NOW", "caption", t.SOFT_ON_DEEP).pack(fill="x", padx=t.PAD + 4, pady=(t.PAD + 2, 0))
        self.status_label = t.label(hero, "", "display", t.TEXT, wraplength=640)
        self.status_label.pack(fill="x", padx=t.PAD + 4, pady=(2, t.GAP))
        self.blocked_chips = ctk.CTkFrame(hero, fg_color="transparent")
        self.blocked_chips.pack(fill="x", padx=t.PAD + 4, pady=(0, t.PAD + 4))

        body = self._section(
            frame, "Override a block", "Unblocks one site until this window ends. Your reason is kept in History."
        )
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x")
        self.override_menu = t.option_menu(row, ["No domain blocked"], width=170)
        self.override_menu.pack(side="left", padx=(0, t.GAP))
        self.reason_entry = t.entry(row, placeholder_text="Why do you need it?")
        self.reason_entry.pack(side="left", fill="x", expand=True, padx=(0, t.GAP))
        self.reason_entry.bind("<KeyRelease>", lambda _event: self._update_override_state())
        self.reason_entry.bind("<Return>", lambda _event: self._override())
        self.override_button = t.primary_button(row, "Override", self._override, width=104)
        self.override_button.pack(side="left")
        self.override_hint = t.Message(body)
        self.override_hint.pack(fill="x", pady=(t.GAP, 0))
        self.status_message = t.Message(body, t.DANGER)
        self.status_message.pack(fill="x", pady=(t.GAP, 0))

        self.released_list = self._section(frame, "Unblocked right now")

    @staticmethod
    def _remaining(until: datetime, now: datetime) -> str:
        minutes = int((until - now).total_seconds()) // 60
        return f"{minutes // 60}h {minutes % 60:02d}m"

    def _refresh_status(self) -> None:
        now = self.controller.clock()
        view = self.controller.status()
        self.status_label.configure(text=view["text"])
        self._show_warning(" ".join(text for text in (self.controller.load_warning, self.warning()) if text))
        self._render_chips(view["overridable"])
        self._render_released(view["released"], now)
        self._set_menu(self.override_menu, view["overridable"], "No domain blocked")
        self._overridable = view["overridable"]
        self._update_override_state()

    def _render_released(self, released: dict[str, datetime], now: datetime) -> None:
        for child in self.released_list.winfo_children():
            child.destroy()
        if not released:
            t.label(self.released_list, "Nothing is unblocked.", "body", t.MUTED).pack(fill="x")
            return
        for domain, until in sorted(released.items()):
            row = ctk.CTkFrame(self.released_list, fg_color="transparent")
            row.pack(fill="x")
            text = f"{domain} unblocked until {until:%H:%M} ({self._remaining(until, now)} left)"
            t.label(row, text).pack(side="left", fill="x", expand=True)
            t.quiet_button(row, "Undo", lambda d=domain: self._undo(d), width=72).pack(side="right")

    def released_texts(self) -> list[str]:
        rows = [row for row in self.released_list.winfo_children() if isinstance(row, ctk.CTkFrame)]
        return [row.winfo_children()[0].cget("text") for row in rows]

    def _render_chips(self, domains: list[str]) -> None:
        for child in self.blocked_chips.winfo_children():
            child.destroy()
        if not domains:
            t.label(self.blocked_chips, "No sites are blocked.", "body", t.SOFT_ON_DEEP).pack(side="left")
            return
        for domain in domains:
            t.chip(self.blocked_chips, domain).pack(side="left", padx=(0, t.GAP - 2))

    def blocked_chip_texts(self) -> list[str]:
        return [chip.cget("text") for chip in self.blocked_chips.winfo_children()]

    def _can_override(self) -> bool:
        return self.override_menu.get() in self._overridable and bool(self.reason_entry.get().strip())

    def _update_override_state(self) -> None:
        domain_available = self.override_menu.get() in self._overridable
        t.set_enabled(self.override_button, self._can_override())
        missing_reason = domain_available and not self.reason_entry.get().strip()
        self.override_hint.configure(text="Type a reason to override" if missing_reason else "")

    @staticmethod
    def _set_menu(menu: ctk.CTkOptionMenu, options: list[str], empty: str) -> None:
        options = options or [empty]
        menu.configure(values=options)
        if menu.get() not in options:
            menu.set(options[0])

    def _override(self) -> None:
        if not self._can_override():
            return
        domain = self.override_menu.get()
        if self._attempt(
            lambda: self.controller.override(domain, self.reason_entry.get()),
            self.status_message,
        ):
            self.reason_entry.delete(0, "end")
            self._refresh_status()
            self._render_history()

    def _undo(self, domain: str) -> None:
        if self._attempt(lambda: self.controller.undo(domain), self.status_message):
            self._refresh_status()
            self._render_history()

    # Block list tab

    def _build_block_list(self, frame: ctk.CTkFrame) -> None:
        ctk.CTkFrame(frame, fg_color="transparent", height=t.GAP).pack()
        body = self._section(frame, "Add a site", "Its www. version is blocked too. You can paste a full web address.")
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x")
        self.new_domain_entry = DomainField(
            row, on_change=self._update_domain_hint, placeholder_text="example.com", **t.entry_style()
        )
        self.new_domain_entry.pack(side="left", fill="x", expand=True, padx=(0, t.GAP))
        self.new_domain_entry.bind("<Return>", lambda _event: self._add_domain())
        self.add_button = t.primary_button(row, "Add", self._add_domain, width=96)
        self.add_button.pack(side="left")
        t.set_enabled(self.add_button, False)
        self.domain_hint = t.Message(body)
        self.domain_hint.pack(fill="x", pady=(t.GAP, 0))
        self.block_message = t.Message(body, t.DANGER)
        self.block_message.pack(fill="x", pady=(t.GAP, 0))

        box = t.card(frame)
        box.pack(fill="both", expand=True, pady=(0, t.GAP + 4))
        self.list_title = t.label(box, "", "title")
        self.list_title.pack(fill="x", padx=t.PAD, pady=(t.PAD - 2, t.GAP))
        self.domain_list = ctk.CTkScrollableFrame(
            box, fg_color="transparent", scrollbar_button_color=t.DISABLED,
            scrollbar_button_hover_color=t.BORDER,
        )
        self.domain_list.pack(fill="both", expand=True, padx=t.PAD - 6, pady=(0, t.PAD - 6))
        self._render_domains()

    def _render_domains(self) -> None:
        for child in self.domain_list.winfo_children():
            child.destroy()
        domains = self.controller.config.domains
        self.list_title.configure(text=f"Blocked sites ({len(domains)})")
        if not domains:
            t.label(self.domain_list, "No sites yet. Add one above.", "body", t.MUTED).pack(fill="x", padx=6)
        for index, domain in enumerate(domains):
            row = ctk.CTkFrame(self.domain_list, fg_color="transparent")
            row.pack(fill="x", pady=(0, t.GAP - 2))
            entry = DomainField(row, **t.entry_style())
            t.list_entry_focus(entry)
            entry.insert(0, domain)
            entry.pack(side="left", fill="x", expand=True, padx=(6, t.GAP))
            save = t.quiet_button(
                row, "Save", lambda i=index, e=entry: self._edit_domain(i, e.get()), width=64
            )
            save.pack(side="left", padx=(0, 2))
            t.set_enabled(save, False)
            entry.on_change = lambda e=entry, b=save, original=domain: t.set_enabled(
                b, can_save_edit(e.get(), original, self.controller.config.domains)
            )
            remove = t.quiet_button(row, "Remove", lambda i=index: self._remove_domain(i), width=80)
            t.danger_on_hover(remove)
            remove.pack(side="left")

    def _update_domain_hint(self) -> None:
        addable, text = hint(self.new_domain_entry.get(), self.controller.config.domains)
        self.domain_hint.configure(text=text, text_color=t.MUTED if addable else t.WARNING)
        t.set_enabled(self.add_button, addable)

    def _add_domain(self) -> None:
        if not hint(self.new_domain_entry.get(), self.controller.config.domains)[0]:
            return
        if self._attempt(lambda: self.controller.add_domain(self.new_domain_entry.get()), self.block_message):
            self.new_domain_entry.delete(0, "end")
            self._update_domain_hint()
            self._after_domain_change()

    def _edit_domain(self, index: int, entry: str) -> None:
        original = self.controller.config.domains[index]
        if not can_save_edit(entry, original, self.controller.config.domains):
            return
        if self._attempt(lambda: self.controller.edit_domain(index, entry), self.block_message):
            self._after_domain_change()

    def _remove_domain(self, index: int) -> None:
        if self._attempt(lambda: self.controller.remove_domain(index), self.block_message):
            self._after_domain_change()

    def _after_domain_change(self) -> None:
        self._render_domains()
        self._refresh_status()

    # Schedule tab

    def _build_schedule(self, frame: ctk.CTkFrame) -> None:
        ctk.CTkFrame(frame, fg_color="transparent", height=t.GAP).pack()
        schedule = self.controller.config.schedule
        body = self._section(frame, "Days", "Blocking only happens on the days you tick.")
        days_row = ctk.CTkFrame(body, fg_color="transparent")
        days_row.pack(fill="x")
        self.day_boxes: list[ctk.CTkCheckBox] = []
        for index, name in enumerate(DAYS):
            box = t.checkbox(days_row, name)
            if index in schedule.weekdays:
                box.select()
            box.pack(side="left")
            self.day_boxes.append(box)

        body = self._section(
            frame, "Time", "Sites are blocked between these times. Type, or use the arrow keys or mouse wheel."
        )
        times = ctk.CTkFrame(body, fg_color="transparent")
        times.pack(fill="x")
        t.label(times, "From", "body", t.MUTED).pack(side="left", padx=(0, t.GAP))
        self.start_time = TimeField(times, schedule.start)
        self.start_time.pack(side="left")
        t.label(times, "to", "body", t.MUTED).pack(side="left", padx=t.PAD)
        self.end_time = TimeField(times, schedule.end)
        self.end_time.pack(side="left")

        actions = ctk.CTkFrame(frame, fg_color="transparent")
        actions.pack(fill="x")
        t.primary_button(actions, "Save schedule", self._save_schedule, width=140).pack(side="left")
        self.schedule_message = t.Message(actions, t.DANGER)
        self.schedule_message.pack(side="left", padx=t.PAD)

    def _save_schedule(self) -> None:
        weekdays = [index for index, box in enumerate(self.day_boxes) if box.get()]
        start = self.start_time.get()
        end = self.end_time.get()
        if self._attempt(lambda: self.controller.set_schedule(weekdays, start, end), self.schedule_message):
            self._refresh_status()

    # Shortlist and History tabs

    def _build_shortlist(self, frame: ctk.CTkFrame) -> None:
        ctk.CTkFrame(frame, fg_color="transparent", height=t.GAP).pack()
        body = self._section(
            frame, "Suggestions", "Shown on the block page and in new tabs. One suggestion per line.", expand=True
        )
        self.shortlist_box = t.textbox(body)
        self.shortlist_box.pack(fill="both", expand=True)
        self.shortlist_box.insert("1.0", "\n".join(self.controller.config.shortlist))
        actions = ctk.CTkFrame(frame, fg_color="transparent")
        actions.pack(fill="x")
        t.primary_button(actions, "Save suggestions", self._save_shortlist, width=150).pack(side="left")
        self.shortlist_message = t.Message(actions, t.DANGER)
        self.shortlist_message.pack(side="left", padx=t.PAD)

    def _save_shortlist(self) -> None:
        lines = self.shortlist_box.get("1.0", "end").splitlines()
        self._attempt(lambda: self.controller.set_shortlist(lines), self.shortlist_message)

    def _build_history(self, frame: ctk.CTkFrame) -> None:
        ctk.CTkFrame(frame, fg_color="transparent", height=t.GAP).pack()
        body = self._section(frame, "Override history", "Every override and undo, oldest first.", expand=True)
        self.history_box = t.textbox(body, state="disabled", wrap="word")
        self.history_box.pack(fill="both", expand=True)
        self._render_history()

    def _render_history(self) -> None:
        lines = self.controller.history_lines()
        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")
        self.history_box.insert("1.0", "\n".join(lines) or "No overrides yet.")
        self.history_box.configure(state="disabled")
