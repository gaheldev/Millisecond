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
from .diagnostic import DiagnosticRow

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
