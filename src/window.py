# window.py
#
# Copyright 2025 Gaël
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw
from gi.repository import Gtk

from .rtcqs import Rtcqs

@Gtk.Template(resource_path='/io/github/gaheldev/ProAudioSetup/window.ui')
class ProaudioSetupWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ProaudioSetupWindow'

    main_box = Gtk.Template.Child()
    preferences_page = Gtk.Template.Child()
    explanations_group = Gtk.Template.Child()
    user_group = Gtk.Template.Child()
    cpu_group = Gtk.Template.Child()
    kernel_group = Gtk.Template.Child()
    io_group = Gtk.Template.Child()
    diagnostic_row = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rtcqs = Rtcqs()
        self.rtcqs.main()

        # declare widgets
        self.toolbar_view = self.get_content()

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.toolbar_view.set_content(self.main_box)

        self.preferences_page = Adw.PreferencesPage()

        # Explanations and disclaimers

        self.explanations_group = Adw.PreferencesGroup()

        self.explanations = Gtk.Label()
        self.explanations.set_text("coucou")
        self.explanations_group.add(self.explanations)

        # User diagnostics

        self.user_group = Adw.PreferencesGroup()
        self.user_group.set_title("User")

        self.diagnostic_row = DiagnosticRow(self.rtcqs, "root")
        self.user_group.add(self.diagnostic_row)

        self.diagnostic_row = DiagnosticRow(self.rtcqs, "audio_group", "#audio_group")
        self.user_group.add(self.diagnostic_row)

        self.diagnostic_row = DiagnosticRow(self.rtcqs, "rt_prio", "#limitsconfaudioconf")
        self.user_group.add(self.diagnostic_row)

        # CPU diagnostics

        self.cpu_group = Adw.PreferencesGroup()
        self.cpu_group.set_title("CPU")

        self.diagnostic_row = DiagnosticRow(self.rtcqs, "governor", "#cpu_frequency_scaling")
        self.cpu_group.add(self.diagnostic_row)

        self.diagnostic_row = DiagnosticRow(self.rtcqs, "smt", "#Simultaneous_threading")
        self.cpu_group.add(self.diagnostic_row)

        self.diagnostic_row = DiagnosticRow(self.rtcqs, "power_management", "#quality_of_service_interface")
        self.cpu_group.add(self.diagnostic_row)

        # Kernel diagnostics

        self.kernel_group = Adw.PreferencesGroup()
        self.kernel_group.set_title("Kernel")

        self.diagnostic_row = DiagnosticRow(self.rtcqs, "kernel_config")
        self.kernel_group.add(self.diagnostic_row)

        self.diagnostic_row = DiagnosticRow(self.rtcqs, "high_res_timers", "#installing_a_real-time_kernel")
        self.kernel_group.add(self.diagnostic_row)

        self.diagnostic_row = DiagnosticRow(self.rtcqs, "tickless", "#installing_a_real-time_kernel")
        self.kernel_group.add(self.diagnostic_row)

        self.diagnostic_row = DiagnosticRow(self.rtcqs, "preempt_rt", "#do_i_really_need_a_real-time_kernel")
        self.kernel_group.add(self.diagnostic_row)

        self.diagnostic_row = DiagnosticRow(self.rtcqs, "mitigations", "#disabling_spectre_and_meltdown_mitigations")
        self.kernel_group.add(self.diagnostic_row)

        # I/O diagnostics

        self.io_group = Adw.PreferencesGroup()
        self.io_group.set_title("I/O")

        self.diagnostic_row = DiagnosticRow(self.rtcqs, "swappiness", "#sysctlconf")
        self.io_group.add(self.diagnostic_row)

        self.diagnostic_row = DiagnosticRow(self.rtcqs, "filesystems", "#filesystems")
        self.io_group.add(self.diagnostic_row)

        self.diagnostic_row = DiagnosticRow(self.rtcqs, "irqs")
        self.io_group.add(self.diagnostic_row)

        # self.preferences_page.add(self.explanations_group)
        self.preferences_page.add(self.user_group)
        self.preferences_page.add(self.cpu_group)
        self.preferences_page.add(self.kernel_group)
        self.preferences_page.add(self.io_group)

        self.main_box.append(self.preferences_page)

    def set_rtcqs(self, value):
        self.rtcqs = value
        self.rtcqs.main()



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
        self.info_button.set_icon_name("dialog-question-symbolic")
        self.info_button.set_sensitive(self.wiki_anchor is not None)
        self.add_suffix(self.info_button)

        self.fix_button = Gtk.Button()
        self.fix_button.add_css_class("dimmed")
        self.fix_button.add_css_class("circular")
        self.fix_button.set_margin_top(8)
        self.fix_button.set_margin_bottom(8)
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
        
# {'root': 'Root User', 'audio_group': 'Group Limits', 'governor': 'CPU Frequency Scaling', 'smt': 'Simultaneous Multithreading', 'kernel_config': 'Kernel Configuration', 'high_res_timers': 'High Resolution Timers', 'tickless': 'Tickless Kernel', 'preempt_rt': 'Preempt RT', 'mitigations': 'Spectre/Meltdown Mitigations', 'rt_prio': 'RT Priorities', 'swappiness': 'Swappiness', 'filesystems': 'Filesystems', 'irqs': 'IRQs', 'power_management': 'Power Management'}
