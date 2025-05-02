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

from gi.repository import Adw, Gtk

from .rtcqs import Rtcqs
from .diagnostic import DiagnosticRow
from .rtfix import SwappinessDialog

@Gtk.Template(resource_path='/io/github/gaheldev/ProAudioSetup/window.ui')
class ProaudioSetupWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ProaudioSetupWindow'

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

        self.root_diagnostic_row = DiagnosticRow(self, self.rtcqs, "root")
        self.root_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.user_group.add(self.root_diagnostic_row)

        self.group_diagnostic_row = DiagnosticRow(self, self.rtcqs, "audio_group", "#audio_group")
        self.group_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.user_group.add(self.group_diagnostic_row)

        self.rt_prio_diagnostic_row = DiagnosticRow(self, self.rtcqs, "rt_prio", "#limitsconfaudioconf")
        self.rt_prio_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.user_group.add(self.rt_prio_diagnostic_row)

        # CPU diagnostics

        self.cpu_group = Adw.PreferencesGroup()
        self.cpu_group.set_title("CPU")

        self.governor_diagnostic_row = DiagnosticRow(self, self.rtcqs, "governor", "#cpu_frequency_scaling")
        self.governor_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.cpu_group.add(self.governor_diagnostic_row)

        self.smt_diagnostic_row = DiagnosticRow(self, self.rtcqs, "smt", "#Simultaneous_threading")
        self.smt_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.cpu_group.add(self.smt_diagnostic_row)

        self.power_diagnostic_row = DiagnosticRow(self, self.rtcqs, "power_management", "#quality_of_service_interface")
        self.power_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.cpu_group.add(self.power_diagnostic_row)

        # Kernel diagnostics

        self.kernel_group = Adw.PreferencesGroup()
        self.kernel_group.set_title("Kernel")

        self.kernel_diagnostic_row = DiagnosticRow(self, self.rtcqs, "kernel_config")
        self.kernel_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.kernel_group.add(self.kernel_diagnostic_row)

        self.timers_diagnostic_row = DiagnosticRow(self, self.rtcqs, "high_res_timers", "#installing_a_real-time_kernel")
        self.timers_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.kernel_group.add(self.timers_diagnostic_row)

        self.tickless_diagnostic_row = DiagnosticRow(self, self.rtcqs, "tickless", "#installing_a_real-time_kernel")
        self.tickless_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.kernel_group.add(self.tickless_diagnostic_row)

        self.preempt_diagnostic_row = DiagnosticRow(self, self.rtcqs, "preempt_rt", "#do_i_really_need_a_real-time_kernel")
        self.preempt_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.kernel_group.add(self.preempt_diagnostic_row)

        self.mitigations_diagnostic_row = DiagnosticRow(self, self.rtcqs, "mitigations", "#disabling_spectre_and_meltdown_mitigations")
        self.mitigations_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.kernel_group.add(self.mitigations_diagnostic_row)

        # I/O diagnostics

        self.io_group = Adw.PreferencesGroup()
        self.io_group.set_title("I/O")

        self.swap_diagnostic_row = DiagnosticRow(self, self.rtcqs, "swappiness", "#sysctlconf", SwappinessDialog())
        self.swap_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.io_group.add(self.swap_diagnostic_row)

        self.filesystems_diagnostic_row = DiagnosticRow(self, self.rtcqs, "filesystems", "#filesystems")
        self.filesystems_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.io_group.add(self.filesystems_diagnostic_row)

        self.irqs_diagnostic_row = DiagnosticRow(self, self.rtcqs, "irqs")
        self.irqs_diagnostic_row.updated.connect(self._on_diagnostic_updated)
        self.io_group.add(self.irqs_diagnostic_row)

        # self.preferences_page.add(self.explanations_group)
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

    def refresh(self):
        self.rtcqs.main()
        diagnostics = [var for var in vars(self).values() if isinstance(var,DiagnosticRow)]
        for diag in diagnostics:
            diag.refresh()
