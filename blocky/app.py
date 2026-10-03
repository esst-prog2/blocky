from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import customtkinter as ctk

from blocky import history, hosts
from blocky import suggestions as suggestions_module
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
        self.iconbitmap(str(Path(__file__).with_name("assets") / "blocky.ico"))
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
        t.paint_window_frame(self)

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
        self._render_history()

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
            self._render_history()

    # Shortlist tab

    def _build_shortlist(self, frame: ctk.CTkFrame) -> None:
        ctk.CTkFrame(frame, fg_color="transparent", height=t.GAP).pack()
        body = self._section(
            frame, "Add a suggestion", "Something better to do, shown on the block page and in new tabs."
        )
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x")
        self.new_suggestion_entry = self._suggestion_entry(row, placeholder_text="e.g. 10-minute walk")
        self.new_suggestion_entry.pack(side="left", fill="x", expand=True, padx=(0, t.GAP))
        self.new_suggestion_entry.bind("<KeyRelease>", lambda _event: self._update_suggestion_hint(), add="+")
        self.new_suggestion_entry.bind("<Return>", lambda _event: self._add_suggestion())
        self.add_suggestion_button = t.primary_button(row, "Add", self._add_suggestion, width=96)
        self.add_suggestion_button.pack(side="left")
        t.set_enabled(self.add_suggestion_button, False)
        self.suggestion_hint = t.Message(body, t.WARNING)
        self.suggestion_hint.pack(fill="x", pady=(t.GAP, 0))
        self.shortlist_message = t.Message(body, t.DANGER)
        self.shortlist_message.pack(fill="x", pady=(t.GAP, 0))

        box = t.card(frame)
        box.pack(fill="both", expand=True, pady=(0, t.GAP + 4))
        self.shortlist_title = t.label(box, "", "title")
        self.shortlist_title.pack(fill="x", padx=t.PAD, pady=(t.PAD - 2, t.GAP))
        self.suggestion_list = ctk.CTkScrollableFrame(
            box, fg_color="transparent", scrollbar_button_color=t.DISABLED,
            scrollbar_button_hover_color=t.BORDER,
        )
        self.suggestion_list.pack(fill="both", expand=True, padx=t.PAD - 6, pady=(0, t.PAD - 6))
        self._render_suggestions()

    def _suggestion_entry(self, parent: ctk.CTkFrame, **kwargs) -> ctk.CTkEntry:
        entry = t.entry(parent, **kwargs)
        too_long = self.register(lambda text: len(text) <= suggestions_module.MAX_LENGTH)
        entry.configure(validate="key", validatecommand=(too_long, "%P"))
        return entry

    def _render_suggestions(self) -> None:
        for child in self.suggestion_list.winfo_children():
            child.destroy()
        shortlist = self.controller.config.shortlist
        self.shortlist_title.configure(text=f"Suggestions ({len(shortlist)})")
        if not shortlist:
            t.label(self.suggestion_list, "No suggestions yet. Add one above.", "body", t.MUTED).pack(
                fill="x", padx=6
            )
        for index, suggestion in enumerate(shortlist):
            row = ctk.CTkFrame(self.suggestion_list, fg_color="transparent")
            row.pack(fill="x", pady=(0, t.GAP - 2))
            entry = self._suggestion_entry(row)
            t.list_entry_focus(entry)
            entry.insert(0, suggestion)
            entry.pack(side="left", fill="x", expand=True, padx=(6, t.GAP))
            save = t.quiet_button(row, "Save", lambda i=index, e=entry: self._edit_suggestion(i, e.get()), width=64)
            save.pack(side="left", padx=(0, 2))
            t.set_enabled(save, False)
            entry.on_change = lambda e=entry, b=save, original=suggestion: t.set_enabled(
                b, suggestions_module.can_save_edit(e.get(), original, self.controller.config.shortlist)
            )
            entry.bind("<KeyRelease>", lambda _event, e=entry: e.on_change(), add="+")
            remove = t.quiet_button(row, "Remove", lambda i=index: self._remove_suggestion(i), width=80)
            t.danger_on_hover(remove)
            remove.pack(side="left")

    def _update_suggestion_hint(self) -> None:
        addable, text = suggestions_module.hint(self.new_suggestion_entry.get(), self.controller.config.shortlist)
        self.suggestion_hint.configure(text=text)
        t.set_enabled(self.add_suggestion_button, addable)

    def _add_suggestion(self) -> None:
        if not suggestions_module.hint(self.new_suggestion_entry.get(), self.controller.config.shortlist)[0]:
            return
        if self._attempt(
            lambda: self.controller.add_suggestion(self.new_suggestion_entry.get()), self.shortlist_message
        ):
            self.new_suggestion_entry.delete(0, "end")
            self._update_suggestion_hint()
            self._after_suggestion_change()

    def _edit_suggestion(self, index: int, text: str) -> None:
        original = self.controller.config.shortlist[index]
        if not suggestions_module.can_save_edit(text, original, self.controller.config.shortlist):
            return
        if self._attempt(lambda: self.controller.edit_suggestion(index, text), self.shortlist_message):
            self._after_suggestion_change()

    def _remove_suggestion(self, index: int) -> None:
        if self._attempt(lambda: self.controller.remove_suggestion(index), self.shortlist_message):
            self._after_suggestion_change()

    def _after_suggestion_change(self) -> None:
        self._render_suggestions()
        self._render_history()

    # History tab

    HISTORY_COLUMNS = (("When", 160), ("Event", 148), ("Item", 150), ("Details", 0))
    HISTORY_LIMIT = 300

    def _build_history(self, frame: ctk.CTkFrame) -> None:
        ctk.CTkFrame(frame, fg_color="transparent", height=t.GAP).pack()
        body = self._section(frame, "History", "Every change you make in Blocky, newest first.", expand=True)
        header = self._history_row(body, [name for name, _ in self.HISTORY_COLUMNS], header=True)
        header.pack(fill="x", padx=(6, 22))
        self.history_list = ctk.CTkScrollableFrame(
            body, fg_color="transparent", scrollbar_button_color=t.DISABLED,
            scrollbar_button_hover_color=t.BORDER,
        )
        self.history_list.pack(fill="both", expand=True)
        self._render_history()

    def _history_row(self, parent: ctk.CTkFrame, cells: list[str], header: bool = False,
                     shaded: bool = False) -> ctk.CTkFrame:
        """One table row. Every cell has a fixed, DPI-scaled width, so the columns line up from row to row."""
        row = ctk.CTkFrame(parent, fg_color=t.HOVER if shaded else "transparent", corner_radius=6)
        for column, ((_, width), text) in enumerate(zip(self.HISTORY_COLUMNS, cells, strict=True)):
            if header:
                role, color = "caption", t.MUTED
                text = text.upper()
            elif column == 1:
                role, color = "button", t.SAGE if text.startswith("Override") else t.TEXT
            else:
                role, color = "body", t.MUTED if column == 0 else t.TEXT
            last = width == 0
            cell = t.label(row, text, role, color, width=width or 120, wraplength=(width or 210) - 12)
            cell.pack(side="left", fill="x", expand=last, anchor="n", padx=(12 if column == 0 else 0, 8), pady=7)
        return row

    def _render_history(self) -> None:
        for child in self.history_list.winfo_children():
            child.destroy()
        rows = self.controller.history_rows()[: self.HISTORY_LIMIT]
        if not rows:
            t.label(self.history_list, "No changes yet.", "body", t.MUTED).pack(fill="x", padx=10, pady=6)
        for number, entry in enumerate(rows):
            cells = [history.when(entry.moment), entry.event, entry.item, entry.details]
            self._history_row(self.history_list, cells, shaded=number % 2 == 1).pack(fill="x")

    def history_table(self) -> list[list[str]]:
        rows = [row for row in self.history_list.winfo_children() if isinstance(row, ctk.CTkFrame)]
        return [[cell.cget("text") for cell in row.winfo_children()] for row in rows]
