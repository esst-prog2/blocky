import tkinter
from collections.abc import Callable
from dataclasses import replace
from datetime import datetime
from pathlib import Path

import customtkinter as ctk

from blocky import history, hosts
from blocky import settings as settings_module
from blocky import suggestions as suggestions_module
from blocky import theme as t
from blocky.clock import DAY_NAMES, TimeStyle, day_order, format_time
from blocky.controller import Controller
from blocky.domainfield import DomainField, can_save_edit, hint
from blocky.settings import FOLLOW_WINDOWS, Settings
from blocky.timefield import TimeField

TABS = ("Status", "Block list", "Schedule", "Shortlist", "History", "Settings")
ASSETS = Path(__file__).with_name("assets")
WINDOWS_MODE_POLL_MS = 2000
FONT_LIST_WIDTH = 220
FONT_LIST_ROWS = 4
FULL_DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class _Popup(tkinter.Toplevel):
    """A borderless Tk window for a drop-down list.

    Not a customtkinter window: those resize themselves to their size in scaled units when their monitor's DPI
    differs, which made the font list narrower than its button on a second monitor. customtkinter still tracks this
    window for the widgets inside it, and its DPI check calls these two methods on every window it tracks.
    """

    def block_update_dimensions_event(self) -> None:
        pass

    def unblock_update_dimensions_event(self) -> None:
        pass

    def destroy(self) -> None:
        from customtkinter.windows.widgets.scaling.scaling_tracker import ScalingTracker

        # customtkinter forgets its own windows when they close, but not one it only tracks for their widgets.
        ScalingTracker.window_widgets_dict.pop(self, None)
        ScalingTracker.window_dpi_scaling_dict.pop(self, None)
        super().destroy()


class App(ctk.CTk):
    def __init__(
        self,
        config_path: Path,
        hosts_path: Path = hosts.HOSTS_PATH,
        clock: Callable[[], datetime] = datetime.now,
        warning: Callable[[], str] = lambda: "",
        sync: Callable[[], None] | None = None,
        windows_is_light: Callable[[], bool] = settings_module.windows_is_light,
        windows_time: Callable[[], settings_module.WindowsTime] = settings_module.windows_time,
    ) -> None:
        self.controller = Controller(config_path, hosts_path, clock, sync)
        self.windows_is_light = windows_is_light
        self._windows_light = False
        self.windows_time = windows_time
        self._windows_time = settings_module.WindowsTime()
        self.time_style = TimeStyle()
        self._apply_settings()
        super().__init__(fg_color=t.BACKGROUND)
        self.title("Blocky")
        self.geometry("{}x{}".format(*self._fit(t.px(760), t.px(660))))
        self.warning = warning
        self._tick_id: str | None = None
        self._poll_id: str | None = None
        self._redraw_id: str | None = None
        # The settings from before a reset, kept for Undo until the next settings change or until Blocky closes.
        self.settings_before_reset: Settings | None = None

        self._build()
        self._tick()
        self._poll_windows_mode()

    def _apply_settings(self) -> None:
        settings = self.controller.config.settings
        if settings.theme == FOLLOW_WINDOWS:
            self._windows_light = self.windows_is_light()
        t.apply(settings_module.effective_theme(settings, self._windows_light), settings.font, settings.text_size)
        # Read at start and before every redraw; a change in Windows shows at the next settings change or start.
        self._windows_time = self.windows_time()
        self.time_style = settings_module.time_style(settings, self._windows_time)

    def _fit(self, width: int, height: int) -> tuple[int, int]:
        """A window size capped to the screen, which large text could otherwise exceed."""
        # Tk reports the screen in the same DPI-independent units as the window size.
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight() - 120  # room for the taskbar, title bar and window position
        return min(width, screen_width), min(height, screen_height)

    @property
    def icon_path(self) -> Path:
        return ASSETS / f"blocky-{t.THEME}.ico"

    def _build(self, selected: str = TABS[0]) -> None:
        self.configure(fg_color=t.BACKGROUND)
        self.minsize(*self._fit(t.px(640), t.px(560)))
        self.iconbitmap(str(self.icon_path))
        self._build_header()
        self.tabs = ctk.CTkTabview(
            self,
            fg_color=t.BACKGROUND,
            anchor="nw",
            corner_radius=0,
            border_width=0,
            segmented_button_fg_color=t.CARD,
            segmented_button_selected_color=t.DEEP,
            segmented_button_selected_hover_color=t.DEEP,
            segmented_button_unselected_color=t.CARD,
            segmented_button_unselected_hover_color=t.HOVER,
            # One colour for every tab, so it must read on both the selected (deep) and the other tabs.
            text_color=t.ON_DEEP,
        )
        # CTkTabview has no font option; its tab buttons are styled through the inner segmented button.
        self.tabs._segmented_button.configure(font=t.font("button"), height=t.CONTROL_HEIGHT, corner_radius=8)
        self.tabs.pack(fill="both", expand=True, padx=t.MARGIN - 4, pady=(0, t.MARGIN - 6))
        for name in TABS:
            self.tabs.add(name)
        for button in self.tabs._segmented_button._buttons_dict.values():
            button.configure(width=t.px(96))
        # Before anything below lets Tk paint, so a redraw never shows another tab in between. Only when needed:
        # set() hides the other tabs 100 ms later, which would also hide a tab chosen within that time.
        if selected != self.tabs.get():
            self.tabs.set(selected)

        self._build_status(self.tabs.tab("Status"))
        self._build_block_list(self.tabs.tab("Block list"))
        self._build_schedule(self.tabs.tab("Schedule"))
        self._build_shortlist(self.tabs.tab("Shortlist"))
        self._build_history(self.tabs.tab("History"))
        self._build_settings(self.tabs.tab("Settings"))

        self._refresh_status()
        t.paint_window_frame(self)

    def redraw(self) -> None:
        """Build the window again in the current settings, on the same tab."""
        self._redraw_id = None
        selected = self.tabs.get()
        settings_position = self.settings_scroll._parent_canvas.yview()[0]
        for child in self.winfo_children():
            child.destroy()
        self._apply_settings()
        self._build(selected)
        self.update_idletasks()
        self.settings_scroll._parent_canvas.yview_moveto(settings_position)

    def _schedule_redraw(self) -> None:
        # Not right away: the button that was clicked is destroyed by the redraw while its handler still runs.
        if self._redraw_id is None:
            self._redraw_id = self.after_idle(self.redraw)

    def _poll_windows_mode(self) -> None:
        if self.controller.config.settings.theme == FOLLOW_WINDOWS and self.windows_is_light() != self._windows_light:
            self.redraw()
        self._poll_id = self.after(WINDOWS_MODE_POLL_MS, self._poll_windows_mode)

    def destroy(self) -> None:
        for job in (self._tick_id, self._poll_id, self._redraw_id):
            if job is not None:
                self.after_cancel(job)
        super().destroy()

    def _attempt(self, action: Callable[[], object], message: ctk.CTkLabel) -> bool:
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
        t.label(header, "Blocky", "brand", t.ACCENT).pack(side="left")
        t.label(header, "Fewer distractions, on your schedule", "caption", t.MUTED).pack(
            side="left", padx=(t.GAP + 4, 0), pady=(6, 0)
        )
        self.banner = t.card(self, border_width=1, border_color=t.WARNING)
        self.warning_label = t.label(self.banner, "", "body", t.WARNING, wraplength=t.px(660))
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
        self.status_label = t.label(hero, "", "display", t.ON_DEEP, wraplength=t.px(640))
        self.status_label.pack(fill="x", padx=t.PAD + 4, pady=(2, t.GAP))
        self.blocked_chips = ctk.CTkFrame(hero, fg_color="transparent")
        self.blocked_chips.pack(fill="x", padx=t.PAD + 4, pady=(0, t.PAD + 4))

        body = self._section(
            frame, "Override a block", "Unblocks one site until this window ends. Your reason is kept in History."
        )
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x")
        self.override_menu = t.option_menu(row, ["No domain blocked"], width=t.px(170))
        self.override_menu.pack(side="left", padx=(0, t.GAP))
        self.reason_entry = t.entry(row, placeholder_text="Why do you need it?")
        self.reason_entry.pack(side="left", fill="x", expand=True, padx=(0, t.GAP))
        self.reason_entry.bind("<KeyRelease>", lambda _event: self._update_override_state())
        self.reason_entry.bind("<Return>", lambda _event: self._override())
        self.override_button = t.primary_button(row, "Override", self._override, width=t.px(104))
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
            until_text = format_time(until.hour, until.minute, self.time_style)
            text = f"{domain} unblocked until {until_text} ({self._remaining(until, now)} left)"
            t.label(row, text).pack(side="left", fill="x", expand=True)
            t.quiet_button(row, "Undo", lambda d=domain: self._undo(d), width=t.px(72)).pack(side="right")

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
        self.add_button = t.primary_button(row, "Add", self._add_domain, width=t.px(96))
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
        self.domain_list = t.scrollable_frame(box)
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
            save = t.quiet_button(row, "Save", lambda i=index, e=entry: self._edit_domain(i, e.get()), width=t.px(64))
            save.pack(side="left", padx=(0, 2))
            t.set_enabled(save, False)

            def check_edit(e: DomainField = entry, b: ctk.CTkButton = save, original: str = domain) -> None:
                t.set_enabled(b, can_save_edit(e.get(), original, self.controller.config.domains))

            entry.on_change = check_edit
            remove = t.quiet_button(row, "Remove", lambda i=index: self._remove_domain(i), width=t.px(80))
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
        # Weekday number to box, in the order of the user's week; the numbers stored stay 0 (Monday) to 6 (Sunday).
        self.day_boxes: dict[int, ctk.CTkCheckBox] = {}
        for day in day_order(self.time_style):
            box = t.checkbox(days_row, DAY_NAMES[day])
            if day in schedule.weekdays:
                box.select()
            box.pack(side="left")
            self.day_boxes[day] = box

        body = self._section(
            frame, "Time", "Sites are blocked between these times. Type, or use the arrow keys or mouse wheel."
        )
        times = ctk.CTkFrame(body, fg_color="transparent")
        times.pack(fill="x")
        t.label(times, "From", "body", t.MUTED).pack(side="left", padx=(0, t.GAP))
        self.start_time = TimeField(times, schedule.start, self.time_style.twelve_hour)
        self.start_time.pack(side="left")
        t.label(times, "to", "body", t.MUTED).pack(side="left", padx=t.PAD)
        self.end_time = TimeField(times, schedule.end, self.time_style.twelve_hour)
        self.end_time.pack(side="left")

        actions = ctk.CTkFrame(frame, fg_color="transparent")
        actions.pack(fill="x")
        t.primary_button(actions, "Save schedule", self._save_schedule, width=t.px(140)).pack(side="left")
        self.schedule_message = t.Message(actions, t.DANGER)
        self.schedule_message.pack(side="left", padx=t.PAD)

    def _save_schedule(self) -> None:
        weekdays = sorted(day for day, box in self.day_boxes.items() if box.get())
        start = self.start_time.get()
        end = self.end_time.get()
        if self._attempt(lambda: self.controller.set_schedule(weekdays, start, end), self.schedule_message):
            self._refresh_status()
            self._render_history()

    # Shortlist tab

    def _build_shortlist(self, frame: ctk.CTkFrame) -> None:
        ctk.CTkFrame(frame, fg_color="transparent", height=t.GAP).pack()
        body = self._section(frame, "Add a suggestion", "Something better to do, shown on the block page.")
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x")
        self.new_suggestion_entry = self._suggestion_entry(row, placeholder_text="e.g. 10-minute walk")
        self.new_suggestion_entry.pack(side="left", fill="x", expand=True, padx=(0, t.GAP))
        self.new_suggestion_entry.bind("<KeyRelease>", lambda _event: self._update_suggestion_hint(), add="+")
        self.new_suggestion_entry.bind("<Return>", lambda _event: self._add_suggestion())
        self.add_suggestion_button = t.primary_button(row, "Add", self._add_suggestion, width=t.px(96))
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
        self.suggestion_list = t.scrollable_frame(box)
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
            t.label(self.suggestion_list, "No suggestions yet. Add one above.", "body", t.MUTED).pack(fill="x", padx=6)
        for index, suggestion in enumerate(shortlist):
            row = ctk.CTkFrame(self.suggestion_list, fg_color="transparent")
            row.pack(fill="x", pady=(0, t.GAP - 2))
            entry = self._suggestion_entry(row)
            t.list_entry_focus(entry)
            entry.insert(0, suggestion)
            entry.pack(side="left", fill="x", expand=True, padx=(6, t.GAP))
            save = t.quiet_button(
                row, "Save", lambda i=index, e=entry: self._edit_suggestion(i, e.get()), width=t.px(64)
            )
            save.pack(side="left", padx=(0, 2))
            t.set_enabled(save, False)
            entry.on_change = lambda e=entry, b=save, original=suggestion: t.set_enabled(
                b, suggestions_module.can_save_edit(e.get(), original, self.controller.config.shortlist)
            )
            entry.bind("<KeyRelease>", lambda _event, e=entry: e.on_change(), add="+")
            remove = t.quiet_button(row, "Remove", lambda i=index: self._remove_suggestion(i), width=t.px(80))
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
        self.history_list = t.scrollable_frame(body)
        self.history_list.pack(fill="both", expand=True)
        self._render_history()

    def _history_row(
        self, parent: ctk.CTkFrame, cells: list[str], header: bool = False, shaded: bool = False
    ) -> ctk.CTkFrame:
        """One table row. Every cell has a fixed, DPI-scaled width, so the columns line up from row to row."""
        row = ctk.CTkFrame(parent, fg_color=t.HOVER if shaded else "transparent", corner_radius=6)
        for column, ((_, width), text) in enumerate(zip(self.HISTORY_COLUMNS, cells, strict=True)):
            if header:
                role, color = "caption", t.MUTED
                text = text.upper()
            elif column == 1:
                role, color = "button", t.ACCENT if text.startswith("Override") else t.TEXT
            else:
                role, color = "body", t.MUTED if column == 0 else t.TEXT
            last = width == 0
            cell = t.label(row, text, role, color, width=t.px(width or 120), wraplength=t.px(width or 210) - 12)
            cell.pack(side="left", fill="x", expand=last, anchor="n", padx=(12 if column == 0 else 0, 8), pady=7)
        return row

    def _render_history(self) -> None:
        for child in self.history_list.winfo_children():
            child.destroy()
        rows = self.controller.history_rows(self.time_style)[: self.HISTORY_LIMIT]
        if not rows:
            t.label(self.history_list, "No changes yet.", "body", t.MUTED).pack(fill="x", padx=10, pady=6)
        for number, entry in enumerate(rows):
            cells = [history.when(entry.moment, self.time_style), entry.event, entry.item, entry.details]
            self._history_row(self.history_list, cells, shaded=number % 2 == 1).pack(fill="x")

    def history_table(self) -> list[list[str]]:
        rows = [row for row in self.history_list.winfo_children() if isinstance(row, ctk.CTkFrame)]
        return [[cell.cget("text") for cell in row.winfo_children()] for row in rows]

    # Settings tab

    def _build_settings(self, frame: ctk.CTkFrame) -> None:
        self.settings_scroll = t.scrollable_frame(frame)
        self.settings_scroll.pack(fill="both", expand=True)
        scroll = self.settings_scroll
        ctk.CTkFrame(scroll, fg_color="transparent", height=t.GAP).pack()
        current = self.controller.config.settings

        body = self._section(scroll, "Appearance", "Changes show at once and are saved.")
        t.label(body, "Theme", "button").pack(fill="x")
        tiles = ctk.CTkFrame(body, fg_color="transparent")
        tiles.pack(fill="x", pady=(t.GAP, 0))
        self.theme_tiles: dict[str, ctk.CTkFrame] = {}
        for index, name in enumerate((*settings_module.THEMES, FOLLOW_WINDOWS)):
            tile = self._theme_tile(tiles, name, name == current.theme)
            tile.grid(row=index // 3, column=index % 3, sticky="ew", padx=(0, t.GAP), pady=(0, t.GAP))
            self.theme_tiles[name] = tile
        for column in range(3):
            tiles.grid_columnconfigure(column, weight=1, uniform="tile")
        self.follow_choices: dict[str, dict[str, ctk.CTkButton]] = {}
        if current.theme == FOLLOW_WINDOWS:
            for key, title, names in (
                ("dark_theme", "Dark theme when Windows is dark", settings_module.DARK_THEMES),
                ("light_theme", "Light theme when Windows is light", settings_module.LIGHT_THEMES),
            ):
                t.label(body, title, "caption", t.MUTED).pack(fill="x", pady=(t.GAP, 0))
                self.follow_choices[key] = self._choice_row(
                    body, {name: settings_module.label(name) for name in names}, getattr(current, key), key
                )

        # Font and text size side by side: both are about how text looks, and the row saves vertical space.
        pair = ctk.CTkFrame(body, fg_color="transparent")
        pair.pack(fill="x", pady=(t.PAD, 0))
        pair.grid_columnconfigure(1, weight=1)
        font_column = ctk.CTkFrame(pair, fg_color="transparent")
        font_column.grid(row=0, column=0, sticky="nw", padx=(0, t.PAD))
        size_column = ctk.CTkFrame(pair, fg_color="transparent")
        self.font_and_size = (pair, font_column, size_column)
        pair.bind("<Configure>", lambda _event: self._lay_out_font_and_size(), add="+")
        t.label(font_column, "Font", "button").pack(fill="x")
        self.font_menu_button = ctk.CTkButton(
            font_column,
            text=f"{current.font}  ▾",
            command=self._toggle_font_list,
            font=t.font("body", current.font),
            width=t.px(FONT_LIST_WIDTH),
            height=t.CONTROL_HEIGHT,
            corner_radius=8,
            border_width=1,
            border_color=t.BORDER,
            fg_color=t.BACKGROUND,
            hover_color=t.HOVER,
            text_color=t.TEXT,
            anchor="w",
        )
        self.font_menu_button.pack(anchor="w", pady=(t.GAP, 0))
        self.font_list: tkinter.Toplevel | None = None
        self.font_options: dict[str, ctk.CTkButton] = {}

        t.label(size_column, "Text size", "button").pack(fill="x")
        sizes = {name: settings_module.label(name) for name in settings_module.TEXT_SIZES}
        self.size_buttons = self._choice_row(size_column, sizes, current.text_size, "text_size")
        self._lay_out_font_and_size()

        self._build_language_and_time(scroll, current)

        reset = ctk.CTkFrame(scroll, fg_color="transparent")
        reset.pack(fill="x", pady=(0, t.GAP))
        self.reset_button = t.quiet_button(reset, "Reset to default", self._reset_settings)
        self.reset_button.pack(side="left")
        self.reset_notice = ctk.CTkFrame(reset, fg_color="transparent")
        t.label(self.reset_notice, "Settings reset.", "body", t.MUTED).pack(side="left", padx=(t.GAP, 0))
        self.undo_reset_button = t.quiet_button(self.reset_notice, "Undo", self._undo_reset, width=t.px(72))
        self.undo_reset_button.pack(side="left")
        if self.settings_before_reset is not None:
            self.reset_notice.pack(side="left")
        self.settings_message = t.Message(scroll, t.DANGER)
        self.settings_message.pack(fill="x", padx=t.GAP)

    def _theme_tile(self, parent: ctk.CTkFrame, name: str, selected: bool) -> ctk.CTkFrame:
        """A tile in the theme's own colours; Follow Windows shows its dark and light choice side by side."""
        settings = self.controller.config.settings
        if name == FOLLOW_WINDOWS:
            surface, ink, title = t.BACKGROUND, t.TEXT, "Follow Windows"
            dark, light = t.THEMES[settings.dark_theme], t.THEMES[settings.light_theme]
            swatches = [dark["DEEP"], dark["PRIMARY"], light["DEEP"], light["PRIMARY"]]
        else:
            colours = t.THEMES[name]
            surface, ink, title = colours["BACKGROUND"], colours["TEXT"], settings_module.label(name)
            swatches = [colours["CARD"], colours["DEEP"], colours["PRIMARY"]]
        tile = ctk.CTkFrame(
            parent,
            fg_color=surface,
            corner_radius=8,
            border_width=3 if selected else 1,
            border_color=t.ACCENT if selected else t.BORDER,
            cursor="hand2",
        )
        tile.preview = True  # in another theme's colours on purpose
        text = ("✓ " if selected else "") + title
        ctk.CTkLabel(tile, text=text, font=t.font("button"), text_color=ink).pack(
            anchor="w", padx=t.GAP + 4, pady=(t.GAP, 2)
        )
        strip = ctk.CTkFrame(tile, fg_color="transparent")
        strip.pack(anchor="w", padx=t.GAP + 4, pady=(0, t.GAP + 2))
        for colour in swatches:
            swatch = ctk.CTkFrame(strip, fg_color=colour, width=t.px(22), height=t.px(12), corner_radius=3)
            swatch.pack(side="left", padx=(0, 4))
        tile.choose = lambda: self._choose(theme=name)
        for widget in self._descendants(tile):
            widget.bind("<Button-1>", lambda _event: tile.choose(), add="+")
        return tile

    def _build_language_and_time(self, parent: ctk.CTkFrame, current: Settings) -> None:
        body = self._section(parent, "Language and time")
        windows = self._windows_time
        t.label(body, "Time format", "button").pack(fill="x")
        formats = {settings_module.FOLLOW_WINDOWS: "Follow Windows", "24h": "24-hour", "12h": "12-hour"}
        self.time_format_buttons = self._choice_row(body, formats, current.time_format, "time_format")
        windows_format = "12-hour" if windows.twelve_hour else "24-hour"
        t.label(body, f"Windows uses {windows_format} time.", "caption", t.MUTED).pack(fill="x", pady=(t.GAP - 2, 0))

        t.label(body, "First day of the week", "button").pack(fill="x", pady=(t.PAD, 0))
        days = {settings_module.FOLLOW_WINDOWS: "Follow Windows"} | {
            name: name.capitalize() for name in settings_module.FIRST_DAYS
        }
        self.first_day_buttons = self._choice_row(body, days, current.first_day, "first_day")
        windows_day = FULL_DAY_NAMES[windows.first_day]
        t.label(body, f"Windows starts the week on {windows_day}.", "caption", t.MUTED).pack(
            fill="x", pady=(t.GAP - 2, 0)
        )

    def _lay_out_font_and_size(self) -> None:
        """Text size next to the font when both fit in full, otherwise below it, so no button text is cut off."""
        pair, font_column, size_column = self.font_and_size
        needed = font_column.winfo_reqwidth() + pair._apply_widget_scaling(t.PAD) + size_column.winfo_reqwidth()
        side_by_side = pair.winfo_width() >= needed
        self.font_and_size_side_by_side = side_by_side
        if side_by_side:
            size_column.grid(row=0, column=1, columnspan=1, sticky="new", pady=0)
        else:
            size_column.grid(row=1, column=0, columnspan=2, sticky="new", pady=(t.PAD, 0))

    def _toggle_font_list(self) -> None:
        if self.font_list is not None:
            self._close_font_list()
        else:
            self._open_font_list()

    def _open_font_list(self) -> None:
        """A list under the font button that shows each font in itself, FONT_LIST_ROWS at a time.

        A standard menu cannot do this: it shows every entry in one font and never scrolls.
        """
        current = self.controller.config.settings.font
        button = self.font_menu_button
        # Placed under the button before its widgets are made, so customtkinter scales them for that monitor.
        popup = _Popup(self, background=t.BORDER)
        popup.withdraw()
        popup.overrideredirect(True)
        popup.wm_geometry(f"+{button.winfo_rootx()}+{button.winfo_rooty() + button.winfo_height() + 4}")
        popup.deiconify()
        popup.update_idletasks()
        box = ctk.CTkFrame(popup, fg_color=t.CARD, corner_radius=0)
        box.pack(fill="both", expand=True, padx=1, pady=1)
        row_height = t.CONTROL_HEIGHT + 4
        list_height = FONT_LIST_ROWS * row_height - 4
        scroll = t.scrollable_frame(box, width=t.px(FONT_LIST_WIDTH) - 33, height=list_height)
        scroll._scrollbar.configure(height=list_height)  # its default of 200 would make the list taller
        scroll.pack(fill="both", expand=True, padx=4, pady=4)
        self.font_scroll = scroll
        self.font_options = {}
        for name in settings_module.FONTS:
            option = self._toggle(scroll, name, name == current, lambda n=name: self._pick_font(n), name)
            option.configure(anchor="w", border_width=0)
            option.pack(fill="x", pady=(0, 4))
            self.font_options[name] = option
        # Sized and placed in the window's own pixels, not customtkinter's scaled units: as wide as the button and
        # exactly FONT_LIST_ROWS rows tall, whatever padding customtkinter adds around the list.
        popup.update_idletasks()
        first = self.font_options[settings_module.FONTS[0]]
        rows_pixels = FONT_LIST_ROWS * (self.font_options[settings_module.FONTS[1]].winfo_y() - first.winfo_y())
        popup.update()  # actual sizes: the scrollbar's minimum height stretches the list beyond what it asks for
        height = popup.winfo_height() - scroll._parent_canvas.winfo_height() + rows_pixels
        x, y = button.winfo_rootx(), button.winfo_rooty() + button.winfo_height() + 4
        if y + height > popup.winfo_vrooty() + popup.winfo_vrootheight() - 60:  # no room above the taskbar
            y = button.winfo_rooty() - height - 4
        popup.wm_geometry(f"{button.winfo_width()}x{height}+{x}+{y}")
        popup.bind("<Escape>", lambda _event: self._close_font_list())
        popup.bind("<Button-1>", self._click_outside_font_list, add="+")
        self.font_list = popup
        popup.update_idletasks()
        popup.lift()
        popup.focus_force()
        try:
            popup.grab_set()  # clicks elsewhere in Blocky come here, so they can close the list
        except tkinter.TclError:
            pass  # not viewable yet; Escape and picking a font still close it
        # Start on whole rows, with the chosen font second from the top where the list allows it. After the new
        # size has taken effect: Tk limits the scroll position by the list's height at that moment.
        popup.update()
        self._show_font_rows(settings_module.FONTS.index(current) - 1)
        # One wheel notch moves one whole row; "break" keeps customtkinter's own wheel handler from also scrolling.
        popup.bind("<MouseWheel>", self._wheel_font_list)

    def _show_font_rows(self, top: int) -> None:
        """Scroll the font list so that the font at index `top` is the first row."""
        self.font_list_top = min(max(0, top), len(settings_module.FONTS) - FONT_LIST_ROWS)
        first = self.font_options[settings_module.FONTS[0]]
        offset = self.font_options[settings_module.FONTS[self.font_list_top]].winfo_y() - first.winfo_y()
        canvas = self.font_scroll._parent_canvas
        canvas.yview_moveto(offset / float(canvas.cget("scrollregion").split()[3]))

    def _wheel_font_list(self, event: tkinter.Event) -> str:
        self._show_font_rows(self.font_list_top + (-1 if event.delta > 0 else 1))
        return "break"

    def _click_outside_font_list(self, event: tkinter.Event) -> None:
        popup = self.font_list
        if popup is None:
            return
        left, top = popup.winfo_rootx(), popup.winfo_rooty()
        inside = left <= event.x_root < left + popup.winfo_width() and top <= event.y_root < top + popup.winfo_height()
        if not inside:
            self._close_font_list()

    def _close_font_list(self) -> None:
        if self.font_list is not None:
            self.font_list.grab_release()
            self.font_list.destroy()
            self.font_list = None
            self.font_options = {}

    def _pick_font(self, name: str) -> None:
        self._close_font_list()
        self._choose(font=name)

    @staticmethod
    def _descendants(widget) -> list:
        found = [widget]
        for child in widget.winfo_children():
            found.extend(App._descendants(child))
        return found

    def _toggle(
        self,
        parent: ctk.CTkFrame,
        text: str,
        selected: bool,
        command: Callable[..., object],
        font_name: str | None = None,
    ) -> ctk.CTkButton:
        """One choice of several; the chosen one is filled like the selected tab."""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            font=t.font("body", font_name),
            height=t.CONTROL_HEIGHT,
            corner_radius=8,
            border_width=0 if selected else 1,
            border_color=t.BORDER,
            fg_color=t.DEEP if selected else t.BACKGROUND,
            hover_color=t.DEEP if selected else t.HOVER,
            text_color=t.ON_DEEP if selected else t.TEXT,
        )

    def _choice_row(self, parent: ctk.CTkFrame, choices: dict[str, str], chosen: str, key: str) -> dict:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(t.GAP, 0))
        buttons = {}
        for column, (name, text) in enumerate(choices.items()):
            button = self._toggle(row, text, name == chosen, lambda n=name: self._choose(**{key: n}))
            button.configure(
                width=t.px(64)
            )  # a minimum, not customtkinter's 140: the grid stretches them to fill the row
            button.grid(row=0, column=column, sticky="ew", padx=(0, t.GAP))
            row.grid_columnconfigure(column, weight=1, uniform=key)
            buttons[name] = button
        return buttons

    def _choose(self, **changes: str) -> None:
        settings = replace(self.controller.config.settings, **changes)
        if settings == self.controller.config.settings:
            return
        if self._attempt(lambda: self.controller.set_settings(settings), self.settings_message):
            self.settings_before_reset = None
            self._schedule_redraw()

    def _reset_settings(self) -> None:
        before = self.controller.config.settings
        if self._attempt(self.controller.reset_settings, self.settings_message):
            self.settings_before_reset = before
            self._schedule_redraw()

    def _undo_reset(self) -> None:
        before = self.settings_before_reset
        if before is not None and self._attempt(lambda: self.controller.set_settings(before), self.settings_message):
            self.settings_before_reset = None
            self._schedule_redraw()
