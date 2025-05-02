from gi.repository import Adw, Gtk, GObject
from enum import Enum


class DiagnosticStatus(Enum):
    Required = 0 # unused for the moment
    Unoptimized = 1
    Optimized = 2


class DiagnosticRow(Adw.ExpanderRow):
    __gtype_name__ = 'DiagnosticRow'

    updated = GObject.Signal('updated')

    def __init__(self, root_window: Adw.ApplicationWindow, cqs, check_name: str, wiki_anchor: str|None=None, autofix_dialog: Adw.Dialog|None=None, **kwargs):
        super().__init__(**kwargs)

        self.root_window = root_window
        self.rtcqs = cqs
        self.check_name = check_name
        self.wiki_anchor = wiki_anchor

        if autofix_dialog is not None:
            autofix_dialog.fixing.connect(self.on_fixing)
            autofix_dialog.fixed.connect(self.on_fixed)

        status = self.status()
        fix_exists = autofix_dialog is not None

        self.add_css_class("toolbar")

        self.set_title(self.title())
        # self.set_subtitle("Use performance governor to limit xruns")

        self.status_icon = StatusIcon(status)
        self.add_prefix(self.status_icon)

        self.spacer = Gtk.Separator()
        self.spacer.add_css_class("spacer")
        self.add_suffix(self.spacer)

        self.wiki_button = WikiButton(self.wiki_link())
        self.add_suffix(self.wiki_button)

        self.fix_button = FixButton(fix_exists, status)
        self.add_suffix(self.fix_button)

        if fix_exists:
            self.fix_button.connect("clicked", autofix_dialog.present)

        self.diagnostic_view = DiagnosticView(self.diagnostic())
        self.add_row(self.diagnostic_view)
        self.diagnostic_view.get_parent().set_activatable(False) # prevent row from reacting to hover

    def status(self) -> DiagnosticStatus:
        if self.rtcqs.status[self.check_name]:
            return DiagnosticStatus.Optimized
        return DiagnosticStatus.Unoptimized

    def title(self) -> str:
        return self.rtcqs.headline[self.check_name]

    def diagnostic(self) -> str:
        return self.rtcqs.output[self.check_name]

    def wiki_link(self) -> str|None:
        if self.wiki_anchor is None:
            return None
        return f"{self.rtcqs.wiki_url}{self.wiki_anchor}"

    def refresh(self) -> None:
        """ refresh widgets when rtcqs is updated
        """
        status = self.status()
        self.status_icon.set_status(status)
        self.fix_button.set_status(status)
        self.diagnostic_view.set_text(self.diagnostic())

    def on_fixing(self, _) -> None:
        pass

    def on_fixed(self, _) -> None:
        self.updated.emit()


class StatusIcon(Gtk.Image):
    ok_icon = "selection-mode-symbolic"
    warning_icon = "dialog-warning-symbolic"
    important_icon = "emblem-important-symbolic"

    def __init__(self, status: DiagnosticStatus, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_status(status)

    def set_status(self, status: DiagnosticStatus) -> None:
        [self.remove_css_class(s) for s in ["warning", "success"]]
        match status:
            case DiagnosticStatus.Required:
                raise NotImplementedError
            case DiagnosticStatus.Unoptimized:
                self.set_from_icon_name(self.warning_icon)
                self.add_css_class("warning")
                self.set_tooltip_text("Unoptimized")
            case DiagnosticStatus.Optimized:
                self.set_from_icon_name(self.ok_icon)
                self.add_css_class("success")
                self.set_tooltip_text("Optimized")


class WikiButton(Gtk.LinkButton):
    def __init__(self, wiki_link: str|None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_css_class("dimmed")
        self.add_css_class("circular")
        self.remove_css_class("link") # make the button white
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.set_icon_name("dialog-question-symbolic")

        if wiki_link is not None:
            self.set_uri(wiki_link)
            self.set_tooltip_text("Open Wiki")
        else:
            self.set_tooltip_text("No related Wiki")

        self.set_sensitive(wiki_link is not None)


class FixButton(Gtk.Button):
    def __init__(self, fix_exists:bool, status:DiagnosticStatus, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_css_class("circular")
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.set_icon_name("applications-engineering-symbolic")
        self.fix_exists = fix_exists
        self.set_status(status)

    def set_status(self, status:DiagnosticStatus):
        [self.remove_css_class(s) for s in ["accent", "dimmed"]]
        self.set_visible(self.fix_exists)
        match status:
            case DiagnosticStatus.Required:
                raise NotImplementedError
            case DiagnosticStatus.Optimized:
                self.set_tooltip_text("nothing to do")
                self.set_sensitive(False)
                self.add_css_class("dimmed")
            case DiagnosticStatus.Unoptimized:
                if self.fix_exists:
                    self.set_tooltip_text("run fix")
                    self.set_sensitive(True)
                    self.add_css_class("accent")
                else:
                    self.set_tooltip_text("fix not implemented")
                    self.set_sensitive(False)
                    self.add_css_class("dimmed")


class DiagnosticView(Gtk.TextView):
    margin = 10

    def __init__(self, text:str='', **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_editable(False)
        self.set_cursor_visible(False)
        self.set_left_margin(self.margin)
        self.set_right_margin(self.margin)
        self.set_bottom_margin(self.margin)
        self.set_top_margin(self.margin)
        self.add_css_class("dimmed")
        self.remove_css_class("view")
        self.set_justification(Gtk.Justification.LEFT)
        self.set_pixels_inside_wrap(5)
        self.set_wrap_mode(Gtk.WrapMode.WORD)

        self.text_buffer = Gtk.TextBuffer()
        self.set_buffer(self.text_buffer)
        self.set_text(text)

    def set_text(self, text):
        self.text_buffer.set_text(text)


