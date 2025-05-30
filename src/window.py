# window.py
#
# Copyright 2025 Gahel
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

from gi.repository import Adw, Gtk, GObject, GLib, Gio

from .rtcqs import Rtcqs
from .diagnostic import DiagnosticRow, DiagnosticStatus
from .rtfix.swappiness import SwappinessDialog
from .rtfix.governor import GovernorDialog
from .rtfix.hyperthreading import HyperthreadingDialog
from .rtfix.utils import is_flatpak

@Gtk.Template(resource_path='/io/github/gaheldev/Millisecond/window.ui')
class MillisecondWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'MillisecondWindow'

    quit = GObject.Signal("quit")

    refresh_button = Gtk.Template.Child("refresh-button")
    main_box = Gtk.Template.Child()
    preferences_page = Gtk.Template.Child()
    explanations_group = Gtk.Template.Child()
    user_group = Gtk.Template.Child()
    cpu_group = Gtk.Template.Child()
    kernel_group = Gtk.Template.Child()
    io_group = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rtcqs = Rtcqs()
        self.rtcqs.gui_status = True
        self.rtcqs.main()

        self.show_dangerous_optimizations = False
        self.setup_dangerous_optimizations_action()

        # declare widgets
        self.toolbar_view = self.get_content()

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.toolbar_view.set_content(self.main_box)

        # banner warning if application is run as root
        if not self.rtcqs.status["root"]:
            self.root_banner = Adw.Banner()
            self.root_banner.set_title("You are running this as root, please restart as regular user for reliable results.")
            self.root_banner.set_revealed(True)
            self.root_banner.add_css_class("error")
            self.root_banner.set_button_label("Quit")
            self.root_banner.connect("button-clicked", lambda *_: self.quit.emit())
            self.main_box.append(self.root_banner)

        # banner warning if kernel configuration couldn't be found
        self.kernel_config_found = self.rtcqs.status["kernel_config"]
        if not self.kernel_config_found:
            self.kernel_banner = Adw.Banner()
            self.kernel_banner.set_title("Could not find kernel configuration.\nImportant configuration tips cannot be displayed.")
            self.kernel_banner.set_revealed(True)
            self.kernel_banner.add_css_class("error")
            self.main_box.append(self.kernel_banner)

        self.preferences_page = Adw.PreferencesPage()

        # Explanations and wiki link

        self.explanations_group = Adw.PreferencesGroup()

        self.explanations = Gtk.Label()
        text = 'Identify possible bottlenecks for low latency audio.\nImplement some of the suggested fixes if you struggle with performance.'
        self.explanations.set_label(text)
        self.explanations.set_wrap(True)
        self.explanations.add_css_class("dimmed")
        self.explanations.set_justify(Gtk.Justification.CENTER)
        self.explanations_group.add(self.explanations)

        self.linuxaudio_link = Gtk.LinkButton()
        self.linuxaudio_link.set_uri("https://wiki.linuxaudio.org/wiki/system_configuration")
        self.linuxaudio_link.set_label("linuxaudio wiki")
        self.linuxaudio_link.add_css_class("dimmed")
        self.explanations_group.add(self.linuxaudio_link)

        # User diagnostics

        self.user_group = Adw.PreferencesGroup()
        self.user_group.set_title("User")

        self.group_diagnostic_row = DiagnosticRow(self, self.rtcqs, "audio_group", DiagnosticStatus.Required,"#audio_group")
        self.group_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.user_group.add(self.group_diagnostic_row)

        self.rt_prio_diagnostic_row = DiagnosticRow(self, self.rtcqs, "rt_prio", DiagnosticStatus.Required, "#limitsconfaudioconf")
        self.rt_prio_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.user_group.add(self.rt_prio_diagnostic_row)

        # CPU diagnostics

        self.cpu_group = Adw.PreferencesGroup()
        self.cpu_group.set_title("CPU")

        self.governor_diagnostic_row = DiagnosticRow(self, self.rtcqs, "governor", DiagnosticStatus.Unoptimized, "#cpu_frequency_scaling", GovernorDialog(self.rtcqs, "governor"))
        self.governor_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.cpu_group.add(self.governor_diagnostic_row)

        self.power_diagnostic_row = DiagnosticRow(self, self.rtcqs, "power_management", DiagnosticStatus.Unoptimized, "#quality_of_service_interface")
        self.power_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.cpu_group.add(self.power_diagnostic_row)

        self.smt_diagnostic_row = DiagnosticRow(self, self.rtcqs, "smt", DiagnosticStatus.Optional, "#simultaneous_multithreading", HyperthreadingDialog(self.rtcqs, "smt") )
        self.smt_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.cpu_group.add(self.smt_diagnostic_row)

        # Kernel diagnostics

        self.kernel_group = Adw.PreferencesGroup()
        self.kernel_group.set_title("Kernel")

        if self.kernel_config_found:
            self.timers_diagnostic_row = DiagnosticRow(self, self.rtcqs, "high_res_timers", DiagnosticStatus.Required, "#installing_a_real-time_kernel")
            self.timers_diagnostic_row.updated.connect(self._on_diagnostic_updated)
            self.kernel_group.add(self.timers_diagnostic_row)

            self.tickless_diagnostic_row = DiagnosticRow(self, self.rtcqs, "tickless", DiagnosticStatus.Required, "#installing_a_real-time_kernel")
            self.tickless_diagnostic_row.updated.connect(self._on_diagnostic_updated)
            self.kernel_group.add(self.tickless_diagnostic_row)

            self.preempt_diagnostic_row = DiagnosticRow(self, self.rtcqs, "preempt_rt", DiagnosticStatus.Required, "#do_i_really_need_a_real-time_kernel")
            self.preempt_diagnostic_row.updated.connect(self._on_diagnostic_updated)
            self.kernel_group.add(self.preempt_diagnostic_row)

            self.mitigations_diagnostic_row = DiagnosticRow(self, self.rtcqs, "mitigations",
                                                            DiagnosticStatus.Optional,
                                                            wiki_anchor="#disabling_spectre_and_meltdown_mitigations",
                                                            subtitle="Dangerous optimization")
            self.mitigations_diagnostic_row.updated.connect(self._on_diagnostic_updated)
            self.kernel_group.add(self.mitigations_diagnostic_row)
            self.mitigations_diagnostic_row.set_visible(self.show_dangerous_optimizations)

        # I/O diagnostics

        self.io_group = Adw.PreferencesGroup()
        self.io_group.set_title("I/O")

        # FIXME: make swappiness fix more reliable on recent ubuntu
        self.swap_diagnostic_row = DiagnosticRow(self, self.rtcqs, "swappiness", DiagnosticStatus.Unoptimized, "#sysctlconf", SwappinessDialog(self.rtcqs, "swappiness"))
        self.swap_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.io_group.add(self.swap_diagnostic_row)

        # FIXME: filesystem analysis from flatpak build yields weird results
        if not is_flatpak():
            self.filesystems_diagnostic_row = DiagnosticRow(self, self.rtcqs, "filesystems", DiagnosticStatus.Optional, "#filesystems")
            self.filesystems_diagnostic_row.updated.connect(self._on_diagnostic_updated)
            self.io_group.add(self.filesystems_diagnostic_row)

        self.irqs_diagnostic_row = DiagnosticRow(self, self.rtcqs, "irqs", DiagnosticStatus.Unoptimized)
        self.irqs_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.io_group.add(self.irqs_diagnostic_row)

        self.preferences_page.add(self.explanations_group)
        self.preferences_page.add(self.user_group)
        self.preferences_page.add(self.cpu_group)
        self.preferences_page.add(self.kernel_group)
        self.preferences_page.add(self.io_group)

        self.main_box.append(self.preferences_page)

    @Gtk.Template.Callback()
    def on_refresh_button_clicked(self, _):
        self.refresh()

    def set_rtcqs(self, value):
        self.rtcqs = value
        self.rtcqs.main()

    def _on_diagnostic_updated(self, _):
        self.refresh()

    def setup_dangerous_optimizations_action(self):
        toggle_action = Gio.SimpleAction.new_stateful(
            "toggle-dangerous-optimizations",
            None,  # No parameter type
            GLib.Variant.new_boolean(self.show_dangerous_optimizations)  # Initial state
        )
        toggle_action.connect("activate", self.on_toggle_dangerous_optimizations)
        self.add_action(toggle_action)

    def on_toggle_dangerous_optimizations(self, action, parameter):
        current_state = action.get_state().get_boolean()
        new_state = not current_state

        # Update the action's state (this updates the UI checkmark)
        action.set_state(GLib.Variant.new_boolean(new_state))

        if new_state:
            self.show_dangerous_optimizations_warning()

        self.show_dangerous_optimizations = new_state
        self.mitigations_diagnostic_row.set_visible(self.show_dangerous_optimizations)

        print(f"Dangerous optimizations: {'ENABLED' if new_state else 'DISABLED'}")

    def show_dangerous_optimizations_warning(self):
        dialog = Adw.MessageDialog.new(
            self,
            "⚠️ Warning:",
            "\nYou have enabled optimizations that could compromise your system's security.\n\nUse with extreme caution!"
        )

        dialog.add_response("ok", "I Understand")
        dialog.set_response_appearance("ok", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("ok")
        dialog.set_close_response("ok")

        dialog.present()

    def refresh(self):
        self.rtcqs.main()
        diagnostics = [var for var in vars(self).values() if isinstance(var,DiagnosticRow)]
        for diag in diagnostics:
            diag.refresh()
