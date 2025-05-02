from gi.repository import Adw
from gi.repository import Gtk

class DiagnosticRow(Adw.ExpanderRow):
    __gtype_name__ = 'DiagnosticRow'

    ok_icon = "selection-mode-symbolic"
    warning_icon = "dialog-warning-symbolic"
    important_icon = "emblem-important-symbolic"

    def __init__(self, cqs, check_name, wiki_anchor=None, **kwargs):
        super().__init__(**kwargs)

        self.rtcqs = cqs
        self.check_name = check_name
        self.wiki_anchor = wiki_anchor

        self.add_css_class("toolbar")

        self.set_title(self.title())
        # self.set_subtitle("Use performance governor to limit xruns")

        self.check_icon = Gtk.Image()
        self.update_check()
        self.add_prefix(self.check_icon)

        self.spacer = Gtk.Separator()
        self.spacer.add_css_class("spacer")
        self.add_suffix(self.spacer)

        self.info_button = Gtk.LinkButton()
        self.info_button.add_css_class("dimmed")
        self.info_button.add_css_class("circular")
        self.info_button.remove_css_class("link") # make the button white
        self.info_button.set_margin_top(8)
        self.info_button.set_margin_bottom(8)
        self.info_button.set_uri(self.wiki_link())
        self.info_button.set_tooltip_text("Open Wiki" if self.wiki_anchor is not None else "No related Wiki")
        self.info_button.set_icon_name("dialog-question-symbolic")
        self.info_button.set_sensitive(self.wiki_anchor is not None)
        self.add_suffix(self.info_button)

        self.fix_button = Gtk.Button()
        self.fix_button.add_css_class("dimmed")
        self.fix_button.add_css_class("circular")
        self.fix_button.set_margin_top(8)
        self.fix_button.set_margin_bottom(8)
        self.fix_button.set_tooltip_text("fix not implemented")
        self.fix_button.set_icon_name("applications-engineering-symbolic")
        self.fix_button.set_sensitive(False) # no autofix implemented yet
        self.add_suffix(self.fix_button)

        margin = 10
        self.diagnostic = Gtk.TextView()
        self.diagnostic.set_editable(False)
        self.diagnostic.set_cursor_visible(False)
        self.diagnostic.set_left_margin(margin)
        self.diagnostic.set_right_margin(margin)
        self.diagnostic.set_bottom_margin(margin)
        self.diagnostic.set_top_margin(margin)
        self.diagnostic.add_css_class("dimmed")
        self.diagnostic.remove_css_class("view")
        self.diagnostic.set_justification(Gtk.Justification.LEFT)
        self.diagnostic.set_pixels_inside_wrap(5)

        self.text_buffer = Gtk.TextBuffer()
        self.text_buffer.set_text(self.rtcqs.output[self.check_name])
        self.diagnostic.set_buffer(self.text_buffer)
        self.diagnostic.set_wrap_mode(Gtk.WrapMode.WORD)

        self.add_row(self.diagnostic)
        self.diagnostic.get_parent().set_activatable(False) # prevent row from reacting to hover

    def status(self):
        return self.rtcqs.status[self.check_name]

    def title(self):
        return self.rtcqs.headline[self.check_name]

    def wiki_link(self):
        return f"{self.rtcqs.wiki_url}{self.wiki_anchor}"

    def update_check(self):
        self.check_icon.set_from_icon_name(self.ok_icon if self.status() else self.warning_icon)
        self.check_icon.add_css_class("success" if self.status() else "warning")
        self.check_icon.set_tooltip_text("Optimized" if self.status() else "Unoptimized")
